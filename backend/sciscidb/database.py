"""
Simple MongoDB connection and basic operations for SciSciDB
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
from typing import List, Dict, Any, Optional
import logging

from .config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Simple MongoDB connection manager"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connected = False
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.client = MongoClient(config.mongo_uri)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[config.db_name]
            self._connected = True
            logger.info(f"Connected to MongoDB: {config.db_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self._connected = False
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected and self.client is not None
    
    def get_collection(self, name: str):
        """Get a MongoDB collection"""
        if not self._connected:
            self.connect()
        return self.db[name]
    
    def list_collections(self) -> List[str]:
        """List all collections in the database"""
        if not self._connected:
            self.connect()
        return self.db.list_collection_names()

# Singleton instance
db_manager = DatabaseManager()

# Basic convenience functions
def get_collection(collection_name: str):
    """Get a MongoDB collection"""
    return db_manager.get_collection(collection_name)

def list_collections() -> List[str]:
    """List all collections"""
    return db_manager.list_collections()

def count_documents(collection_name: str, exact: bool = False) -> int:
    """
    Count documents in a collection
    
    Args:
        collection_name: Name of collection
        exact: If True, do exact count (slow). If False, use estimated count (fast)
    
    Returns:
        Document count
    """
    collection = get_collection(collection_name)
    
    if exact:
        # Exact count - scans all documents (slow for large collections)
        return collection.count_documents({})
    else:
        # Estimated count - uses collection metadata (fast)
        return collection.estimated_document_count()

def get_sample_document(collection_name: str) -> Optional[Dict]:
    """Get a sample document to see the structure"""
    collection = get_collection(collection_name)
    return collection.find_one()

def find_documents(collection_name: str, query: Dict = None, limit: int = 100) -> List[Dict]:
    """Basic find operation"""
    collection = get_collection(collection_name)
    if query is None:
        query = {}
    return list(collection.find(query).limit(limit))

def create_performance_indexes():
    """
    Create indexes to accelerate common queries
    Call this after uploading data to improve query performance
    """
    if not db_manager.connect():
        print("Failed to connect to database")
        return
    
    print("Creating performance indexes...")
    
    # Papers collection indexes
    papers_collection = get_collection("papers")
    
    try:
        # Index for venue + year queries (for venue timeline analysis)
        papers_collection.create_index([("venue", ASCENDING), ("year", ASCENDING)])
        print("  ✓ Created papers.venue + year index")
        
        # Index for year queries (for temporal analysis)
        papers_collection.create_index([("year", ASCENDING)])
        print("  ✓ Created papers.year index")
        
        # Index for venue queries (for venue-specific analysis)
        papers_collection.create_index([("venue", ASCENDING)])
        print("  ✓ Created papers.venue index")
        
        # Text search index on title and abstract (if abstract exists)
        sample = get_sample_document("papers")
        if sample and "title" in sample:
            papers_collection.create_index([
                ("title", "text"),
                ("abstract", "text") if "abstract" in sample else ("title", "text")
            ])
            print("  ✓ Created papers text search index")
        
    except Exception as e:
        print(f"  → Papers indexes: {e}")
    
    # Authors collection indexes
    try:
        authors_collection = get_collection("authors")
        
        # Index for author name searches
        authors_collection.create_index([("name", ASCENDING)])
        print("  ✓ Created authors.name index")
        
    except Exception as e:
        print(f"  → Authors indexes: {e}")
    
    # Venues collection indexes  
    try:
        venues_collection = get_collection("publication-venues")
        
        # Index for venue name searches
        venues_collection.create_index([("name", ASCENDING)])
        print("  ✓ Created venues.name index")
        
    except Exception as e:
        print(f"  → Venues indexes: {e}")
    
    print("✓ Performance indexes created!")

def list_indexes(collection_name: str):
    """List all indexes on a collection"""
    collection = get_collection(collection_name)
    indexes = collection.list_indexes()
    
    print(f"Indexes on '{collection_name}' collection:")
    for idx in indexes:
        name = idx.get('name', 'Unknown')
        keys = idx.get('key', {})
        print(f"  - {name}: {keys}")

def drop_index(collection_name: str, index_name: str):
    """Drop a specific index from a collection"""
    collection = get_collection(collection_name)
    try:
        collection.drop_index(index_name)
        print(f"✓ Dropped index '{index_name}' from '{collection_name}'")
    except Exception as e:
        print(f"Failed to drop index: {e}")