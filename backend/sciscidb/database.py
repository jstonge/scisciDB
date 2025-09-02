"""
Minimal MongoDB connection for venue group counts
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import List, Dict, Any, Optional
import sqlite3

from .config import config

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
            return True
        except ConnectionFailure:
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

# Singleton instance
db_manager = DatabaseManager()

def sync_to_sqlite_incremental(data: List[Dict[str, Any]], sqlite_path: str) -> None:
    """Write venue/year counts to SQLite incrementally (INSERT OR REPLACE)"""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            venue TEXT NOT NULL,
            year INTEGER NOT NULL, 
            count INTEGER NOT NULL,
            PRIMARY KEY (venue, year)
        )
    ''')
    
    # Insert or replace records (incremental)
    cursor.executemany(
        'INSERT OR REPLACE INTO papers (venue, year, count) VALUES (?, ?, ?)',
        [(row['venue'], row['year'], row['count']) for row in data]
    )
    
    conn.commit()
    conn.close()

def get_venue_year_counts(collection_name: str, venues: List[str] = None) -> List[Dict[str, Any]]:
    """Get exact paper counts by venue and year"""
    collection = db_manager.get_collection(collection_name)
    
    # Match conditions
    match_conditions = {
        "venue": {"$exists": True, "$ne": None},
        "year": {"$exists": True, "$ne": None, "$gte": 1900, "$lte": 2030}
    }
    
    # Filter by specific venues if provided
    if venues:
        match_conditions["venue"] = {"$in": venues}
    
    pipeline = [
        {"$match": match_conditions},
        {"$group": {
            "_id": {"venue": "$venue", "year": "$year"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "venue": "$_id.venue",
            "year": "$_id.year", 
            "count": 1
        }},
        {"$sort": {"venue": 1, "year": 1}}
    ]
    
    return list(collection.aggregate(pipeline))

def find_one_sample(collection_name: str) -> Optional[Dict[str, Any]]:
    """Get one sample document from collection"""
    collection = db_manager.get_collection(collection_name)
    doc = collection.find_one()
    if doc:
        doc.pop('_id', None)  # Remove MongoDB ObjectId
    return doc

def get_collection_count(collection_name: str) -> int:
    """Get estimated document count for collection"""
    collection = db_manager.get_collection(collection_name)
    return collection.estimated_document_count()

def list_collections() -> List[str]:
    """List all collections in database"""
    if not db_manager._connected:
        db_manager.connect()
    return db_manager.db.list_collection_names()