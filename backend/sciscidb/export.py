"""
Export data from MongoDB to static JSON files for frontend
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

from .database import get_collection, db_manager
from .config import config

logger = logging.getLogger(__name__)

class ExportError(Exception):
    """Exception raised when export fails"""
    pass

def export_papers_sample(limit: int = 10000) -> Dict[str, Any]:
    """
    Export a sample of papers for frontend visualization
    
    Args:
        limit: Maximum number of papers to export
        
    Returns:
        Dictionary with papers data and metadata
    """
    try:
        collection = get_collection("papers")
        
        # Get a random sample of papers
        pipeline = [
            {"$sample": {"size": limit}},
            {"$project": {
                "_id": 0,  # Exclude MongoDB ObjectId
                # Include all fields for now - we'll adjust based on actual data structure
            }}
        ]
        
        papers = list(collection.aggregate(pipeline))
        
        return {
            "data": papers,
            "count": len(papers),
            "exported_at": datetime.now().isoformat(),
            "description": f"Random sample of {len(papers)} papers",
            "source": "papers collection"
        }
        
    except Exception as e:
        logger.error(f"Failed to export papers sample: {e}")
        raise ExportError(f"Papers export failed: {e}")

def export_venue_timeline() -> Dict[str, Any]:
    """
    Export venue publication timeline data
    
    Returns:
        Dictionary with timeline data and metadata
    """
    try:
        collection = get_collection("papers")
        
        # First, let's see what fields actually exist
        sample = collection.find_one()
        if not sample:
            raise ExportError("No papers found in collection")
        
        print("Available fields in papers:", list(sample.keys()))
        
        # Try to find year and venue fields (common names)
        year_field = None
        venue_field = None
        
        for field in sample.keys():
            if 'year' in field.lower():
                year_field = field
            if 'venue' in field.lower() or 'journal' in field.lower():
                venue_field = field
        
        if not year_field:
            raise ExportError("No year field found in papers collection")
        if not venue_field:
            raise ExportError("No venue field found in papers collection")
        
        print(f"Using year field: {year_field}, venue field: {venue_field}")
        
        # Aggregate papers by venue and year
        pipeline = [
            {"$match": {
                year_field: {"$exists": True, "$ne": None},
                venue_field: {"$exists": True, "$ne": None}
            }},
            {"$group": {
                "_id": {
                    "venue": f"${venue_field}",
                    "year": f"${year_field}"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1}},
            {"$project": {
                "_id": 0,
                "venue": "$_id.venue",
                "year": "$_id.year",
                "count": 1
            }}
        ]
        
        timeline = list(collection.aggregate(pipeline))
        
        return {
            "data": timeline,
            "count": len(timeline),
            "exported_at": datetime.now().isoformat(),
            "description": "Paper counts by venue and year",
            "source": "papers collection",
            "fields_used": {"year": year_field, "venue": venue_field}
        }
        
    except Exception as e:
        logger.error(f"Failed to export venue timeline: {e}")
        raise ExportError(f"Venue timeline export failed: {e}")

def export_top_venues(limit: int = 50) -> Dict[str, Any]:
    """
    Export top venues by paper count
    
    Args:
        limit: Maximum number of venues to export
        
    Returns:
        Dictionary with venue data and metadata
    """
    try:
        collection = get_collection("papers")
        
        # Get sample to find venue field
        sample = collection.find_one()
        if not sample:
            raise ExportError("No papers found in collection")
        
        venue_field = None
        for field in sample.keys():
            if 'venue' in field.lower() or 'journal' in field.lower():
                venue_field = field
                break
        
        if not venue_field:
            raise ExportError("No venue field found in papers collection")
        
        pipeline = [
            {"$match": {venue_field: {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": f"${venue_field}",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "venue": "$_id",
                "count": 1
            }}
        ]
        
        venues = list(collection.aggregate(pipeline))
        
        return {
            "data": venues,
            "count": len(venues),
            "exported_at": datetime.now().isoformat(),
            "description": f"Top {len(venues)} venues by paper count",
            "source": "papers collection",
            "field_used": venue_field
        }
        
    except Exception as e:
        logger.error(f"Failed to export top venues: {e}")
        raise ExportError(f"Top venues export failed: {e}")

def export_collection_info() -> Dict[str, Any]:
    """
    Export basic information about all collections
    
    Returns:
        Dictionary with collection info
    """
    try:
        from .database import list_collections, count_documents, get_sample_document
        
        collections = list_collections()
        collection_info = []
        
        for coll_name in collections:
            try:
                count = count_documents(coll_name)
                sample = get_sample_document(coll_name)
                
                info = {
                    "name": coll_name,
                    "document_count": count,
                    "sample_fields": list(sample.keys()) if sample else [],
                    "has_data": count > 0
                }
                collection_info.append(info)
                
            except Exception as e:
                logger.warning(f"Could not get info for collection {coll_name}: {e}")
                collection_info.append({
                    "name": coll_name,
                    "document_count": 0,
                    "sample_fields": [],
                    "has_data": False,
                    "error": str(e)
                })
        
        return {
            "collections": collection_info,
            "total_collections": len(collections),
            "exported_at": datetime.now().isoformat(),
            "description": "Information about all collections in the database"
        }
        
    except Exception as e:
        logger.error(f"Failed to export collection info: {e}")
        raise ExportError(f"Collection info export failed: {e}")

def export_all_datasets(export_dir: Path = None) -> Path:
    """
    Export all datasets for frontend
    
    Args:
        export_dir: Directory to save exports (defaults to config.export_dir)
        
    Returns:
        Path to export directory
        
    Raises:
        ExportError: If export fails
    """
    if export_dir is None:
        export_dir = config.export_dir
    
    export_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Exporting datasets to {export_dir}...")
    
    # Connect to database
    if not db_manager.connect():
        raise ExportError("Failed to connect to database")
    
    # Define exports to generate
    exports = {
        "collection_info.json": export_collection_info,
        "papers_sample.json": lambda: export_papers_sample(10000),
        "venue_timeline.json": export_venue_timeline,
        "top_venues.json": lambda: export_top_venues(50),
    }
    
    successful_exports = 0
    
    for filename, export_func in exports.items():
        print(f"\nExporting {filename}...")
        try:
            data = export_func()
            
            file_path = export_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Calculate file size
            file_size = file_path.stat().st_size
            
            print(f"  ✓ Exported {len(data.get('data', []))} items to {filename}")
            print(f"  ✓ File size: {file_size / 1024:.1f} KB")
            
            successful_exports += 1
            
        except Exception as e:
            print(f"  ✗ Failed to export {filename}: {e}")
            logger.error(f"Export failed for {filename}: {e}")
    
    print(f"\n✓ Export completed: {successful_exports}/{len(exports)} successful")
    print(f"📁 Files saved in: {export_dir}")
    
    if successful_exports > 0:
        print("\nTo use in SvelteKit frontend:")
        print(f"  cp {export_dir}/*.json frontend/static/data/")
        print("  git add frontend/static/data/ && git commit -m 'Update data exports'")
    
    return export_dir

# Convenience functions
def quick_export() -> Path:
    """Quick export with default settings"""
    return export_all_datasets()

def export_for_frontend(frontend_data_dir: Path) -> None:
    """
    Export data directly to frontend directory
    
    Args:
        frontend_data_dir: Path to frontend/static/data/ directory
    """
    # Export to temp directory first
    temp_exports = export_all_datasets()
    
    # Copy to frontend directory
    frontend_data_dir.mkdir(parents=True, exist_ok=True)
    
    for json_file in temp_exports.glob("*.json"):
        destination = frontend_data_dir / json_file.name
        destination.write_text(json_file.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"Copied {json_file.name} to {destination}")
    
    print(f"✓ All exports copied to {frontend_data_dir}")

# Debug function
def explore_data_structure():
    """
    Explore the actual data structure in your collections
    (useful for understanding what fields are available)
    """
    try:
        from .database import list_collections, get_sample_document
        
        collections = list_collections()
        print(f"Found {len(collections)} collections:")
        
        for coll_name in collections:
            print(f"\n📁 Collection: {coll_name}")
            sample = get_sample_document(coll_name)
            
            if sample:
                print(f"   Sample fields: {list(sample.keys())}")
                # Show first few characters of each field value
                for key, value in list(sample.items())[:10]:  # First 10 fields
                    if isinstance(value, str):
                        preview = value[:50] + "..." if len(str(value)) > 50 else value
                    else:
                        preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"   {key}: {preview}")
                
                if len(sample.keys()) > 10:
                    print(f"   ... and {len(sample.keys()) - 10} more fields")
            else:
                print("   No documents found")
                
    except Exception as e:
        print(f"Error exploring data: {e}")

if __name__ == "__main__":
    # If run directly, do a quick export
    explore_data_structure()
    print("\n" + "="*50)
    quick_export()
