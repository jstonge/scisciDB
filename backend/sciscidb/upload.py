"""
Upload datasets to MongoDB
"""
import json
import gzip
import jsonlines
from pathlib import Path
from typing import List, Dict, Any, Optional
from pymongo.errors import BulkWriteError
from tqdm import tqdm
import logging

from .config import config
from .database import db_manager

logger = logging.getLogger(__name__)

class UploadError(Exception):
    """Exception raised when upload fails"""
    pass

def get_id_field_for_collection(collection_name: str, sample_doc: Dict[str, Any]) -> Optional[str]:
    """
    Determine the correct ID field for different Semantic Scholar collections
    
    Args:
        collection_name: Name of the collection
        sample_doc: Sample document to inspect
        
    Returns:
        ID field name or None if not found
    """
    # Define ID field mappings for different collections
    id_field_mappings = {
        "papers": ["corpusid", "id", "paperId"],
        "authors": ["authorid", "authorId", "id"], 
        "publication-venues": ["venueid", "venueId", "id"],
        "abstracts": ["corpusid", "id", "paperId"],
        "s2orc": ["corpusid", "id", "paperId"],
        "citations": ["citationid", "citationId", "id"]
    }
    
    # Get potential ID fields for this collection
    potential_fields = id_field_mappings.get(collection_name.lower(), ["id"])
    
    # Check which field exists in the sample document
    for field in potential_fields:
        if field in sample_doc:
            return field
    
    # Fallback: check for any field ending with 'id'
    for key in sample_doc.keys():
        if key.lower().endswith('id'):
            return key
    
    return None

def upload_to_mongodb(
    dataset_path: Path, 
    collection_name: str, 
    clean_slate: bool = False
) -> Dict[str, int]:
    """
    Upload JSON dataset files to MongoDB
    
    Args:
        dataset_path: Path to directory containing JSON files
        collection_name: Name of MongoDB collection
        clean_slate: Whether to drop existing collection first
        
    Returns:
        Dictionary with upload statistics
        
    Raises:
        UploadError: If upload fails
    """
    if not dataset_path.exists():
        raise UploadError(f"Dataset path does not exist: {dataset_path}")
    
    if not dataset_path.is_dir():
        raise UploadError(f"Dataset path is not a directory: {dataset_path}")
    
    print(f"Uploading dataset from {dataset_path} to collection '{collection_name}'")
    
    # Connect to database
    if not db_manager.connect():
        raise UploadError("Failed to connect to database")
    
    collection = db_manager.get_collection(collection_name)
    
    # Handle clean slate
    if clean_slate:
        print(f"Clean slate requested: dropping collection '{collection_name}'")
        collection.drop()
    
    # Find all JSON files in the dataset directory
    json_files = list(dataset_path.glob("*.json"))
    gz_files = list(dataset_path.glob("*.json.gz"))
    all_files = json_files + gz_files
    
    if not all_files:
        raise UploadError(f"No JSON files found in {dataset_path}")
    
    print(f"Found {len(all_files)} files to process")
    
    # Determine ID field by looking at first document
    id_field = None
    print("Determining ID field...")
    
    for file_path in all_files:
        try:
            sample_doc = _get_first_document(file_path)
            if sample_doc:
                id_field = get_id_field_for_collection(collection_name, sample_doc)
                if id_field:
                    print(f"Using ID field: '{id_field}'")
                    break
        except Exception as e:
            continue
    
    if not id_field:
        raise UploadError("Could not determine ID field from sample documents")
    
    # Create unique index on the determined ID field
    print(f"Creating unique index on '{id_field}' field...")
    try:
        collection.create_index(id_field, unique=True)
        print("  ✓ Index created successfully")
    except Exception as e:
        print(f"  → Index note: {e} (may already exist)")
    
    # Upload statistics
    total_processed = 0
    total_inserted = 0
    total_duplicates = 0
    total_errors = 0
    
    # Process each file
    for file_path in all_files:
        print(f"\nProcessing {file_path.name}...")
        
        try:
            documents = _read_json_file(file_path, id_field)
            
            if not documents:
                print(f"  No valid documents found in {file_path.name}")
                continue
            
            print(f"  Read {len(documents)} documents with '{id_field}' field")
            total_processed += len(documents)
            
            # Insert documents with duplicate handling
            insert_stats = _insert_documents(collection, documents)
            total_inserted += insert_stats['inserted']
            total_duplicates += insert_stats['duplicates'] 
            total_errors += insert_stats['errors']
            
            print(f"  ✓ Inserted: {insert_stats['inserted']}, "
                  f"Duplicates: {insert_stats['duplicates']}, "
                  f"Errors: {insert_stats['errors']}")
            
        except Exception as e:
            print(f"  ✗ Error processing {file_path.name}: {e}")
            total_errors += 1
            continue
    
    # Final statistics
    stats = {
        'files_processed': len(all_files),
        'total_processed': total_processed,
        'total_inserted': total_inserted,
        'total_duplicates': total_duplicates,
        'total_errors': total_errors,
        'id_field_used': id_field
    }
    
    print(f"\n✓ Upload complete!")
    print(f"Files processed: {stats['files_processed']}")
    print(f"Documents processed: {stats['total_processed']}")
    print(f"Documents inserted: {stats['total_inserted']}")
    print(f"Duplicates skipped: {stats['total_duplicates']}")
    print(f"Errors: {stats['total_errors']}")
    print(f"ID field used: {stats['id_field_used']}")
    
    return stats

def _get_first_document(file_path: Path) -> Optional[Dict[str, Any]]:
    """Get the first document from a file to inspect its structure"""
    try:
        if file_path.name.endswith('.json.gz'):
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                line = f.readline().strip()
                if line:
                    return json.loads(line)
        elif file_path.name.endswith('.json'):
            # Try multiple approaches for .json files
            
            # First try: JSON Lines
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line:
                        return json.loads(first_line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            
            # Second try: Regular JSON array
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        return data[0]
                    elif isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            
            # Third try: jsonlines library (sometimes works when manual doesn't)
            try:
                with jsonlines.open(file_path) as reader:
                    return reader.read()
            except Exception:
                pass
                
    except Exception as e:
        logger.warning(f"Could not read first document from {file_path}: {e}")
    
    return None

def _read_json_file(file_path: Path, id_field: str) -> List[Dict[str, Any]]:
    """Read JSON documents from a file (handles both .json and .json.gz)"""
    documents = []
    
    if file_path.name.endswith('.json.gz'):
        # Compressed file - always JSON Lines format
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            for line in tqdm(f, desc=f"Reading {file_path.name}"):
                try:
                    doc = json.loads(line.strip())
                    if id_field in doc:
                        documents.append(doc)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON line in {file_path}: {e}")
                    continue
    
    elif file_path.name.endswith('.json'):
        # Uncompressed JSON - try multiple formats
        
        # Method 1: Try line-by-line reading (JSON Lines)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(tqdm(f, desc=f"Reading {file_path.name}")):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        doc = json.loads(line)
                        if id_field in doc:
                            documents.append(doc)
                    except json.JSONDecodeError:
                        # If first few lines fail, it's probably not JSON Lines
                        if line_num < 5:
                            break
                        continue
            
            # If we got documents, return them
            if documents:
                return documents
                
        except Exception as e:
            logger.warning(f"Line-by-line reading failed for {file_path}: {e}")
        
        # Method 2: Try regular JSON (array or single object)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    documents = [doc for doc in tqdm(data, desc=f"Processing {file_path.name}") if id_field in doc]
                elif isinstance(data, dict) and id_field in data:
                    documents = [data]
        except json.JSONDecodeError as e:
            logger.error(f"Could not parse JSON file {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []
    
    return documents

def _insert_documents(collection, documents: List[Dict[str, Any]]) -> Dict[str, int]:
    """Insert documents into MongoDB collection with duplicate handling"""
    if not documents:
        return {'inserted': 0, 'duplicates': 0, 'errors': 0}
    
    try:
        # Use insert_many with ordered=False to continue on duplicate key errors
        result = collection.insert_many(documents, ordered=False)
        return {
            'inserted': len(result.inserted_ids),
            'duplicates': 0,
            'errors': 0
        }
    
    except BulkWriteError as e:
        # Handle bulk write errors (mainly duplicates)
        successful_inserts = e.details['nInserted']
        
        # Count different error types
        duplicate_errors = 0
        other_errors = 0
        
        for error in e.details.get('writeErrors', []):
            if error['code'] == 11000:  # Duplicate key error
                duplicate_errors += 1
            else:
                other_errors += 1
        
        return {
            'inserted': successful_inserts,
            'duplicates': duplicate_errors,
            'errors': other_errors
        }
    
    except Exception as e:
        logger.error(f"Unexpected error during insert: {e}")
        return {
            'inserted': 0,
            'duplicates': 0, 
            'errors': len(documents)
        }

def upload_dataset_by_name(dataset_name: str, clean_slate: bool = False) -> Dict[str, int]:
    """
    Upload a dataset by name (convenience function)
    
    Args:
        dataset_name: Name of dataset (papers, authors, publication-venues, etc.)
        clean_slate: Whether to drop existing collection first
        
    Returns:
        Dictionary with upload statistics
    """
    dataset_path = config.get_dataset_path(dataset_name)
    return upload_to_mongodb(dataset_path, dataset_name, clean_slate)

# Convenience functions for common datasets
def upload_papers(clean_slate: bool = False) -> Dict[str, int]:
    """Upload papers dataset"""
    return upload_dataset_by_name("papers", clean_slate)

def upload_authors(clean_slate: bool = False) -> Dict[str, int]:
    """Upload authors dataset"""
    return upload_dataset_by_name("authors", clean_slate)

def upload_venues(clean_slate: bool = False) -> Dict[str, int]:
    """Upload publication-venues dataset"""
    return upload_dataset_by_name("publication-venues", clean_slate)