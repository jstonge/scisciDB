"""
Simple MongoDB connection and basic operations for SciSciDB
"""
from pymongo import MongoClient
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

def count_documents(collection_name: str) -> int:
    """Count documents in a collection"""
    collection = get_collection(collection_name)
    return collection.count_documents({})

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
