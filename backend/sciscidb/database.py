"""
Minimal MongoDB connection for venue group counts
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import List, Dict, Any, Optional
import sqlite3

from .config import config

class DatabaseManager:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
    
    def connect(self) -> bool:
        try:
            self.client = MongoClient(config.mongo_uri)
            self.client.admin.command('ping')
            self.db = self.client[config.db_name]
            return True
        except ConnectionFailure:
            return False
    
    def get_collection(self, name: str):
        if not self.client:
            self.connect()
        return self.db[name]

# Singleton
db_manager = DatabaseManager()

def get_venue_year_counts(collection_name: str, venues: List[str] = None, 
                         estimated: bool = True, sample_size: int = 10_000_000) -> List[Dict[str, Any]]:
    """Get paper counts by venue and year - optimized for speed"""
    collection = db_manager.get_collection(collection_name)
    
    pipeline = []
    
    if estimated:
        pipeline.append({"$sample": {"size": sample_size}})
    
    # Match conditions
    match_conditions = {
        "venue": {"$exists": True, "$ne": None},
        "year": {"$exists": True, "$ne": None, "$gte": 1900, "$lte": 2030}
    }
    
    # Filter by specific venues if provided
    if venues:
        match_conditions["venue"] = {"$in": venues}
    
    pipeline.extend([
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
    ])
    
    results = list(collection.aggregate(pipeline))
    
    # Extrapolate if sampling
    if estimated and results:
        total_docs = collection.estimated_document_count()
        factor = total_docs / sample_size if sample_size < total_docs else 1
        for result in results:
            result['count'] = int(result['count'] * factor)
    
    return results

def sync_to_sqlite(data: List[Dict[str, Any]], sqlite_path: str) -> None:
    """Write venue/year counts directly to SQLite"""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            venue TEXT NOT NULL,
            year INTEGER NOT NULL, 
            count INTEGER NOT NULL,
            PRIMARY KEY (venue, year)
        )
    ''')
    
    # Clear and insert
    cursor.execute('DELETE FROM papers')
    cursor.executemany(
        'INSERT INTO papers (venue, year, count) VALUES (?, ?, ?)',
        [(row['venue'], row['year'], row['count']) for row in data]
    )
    
    conn.commit()
    conn.close()