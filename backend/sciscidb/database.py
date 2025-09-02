"""
Minimal utilities for the MongoDB
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

##################################
# THIN WRAPPER OVER MONGO CLIENT #
##################################

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

#####################
# UPDATE COLLECTION #
#####################

def add_primary_s2field():
    """Add a primary_s2field string field to documents for faster querying"""
    if not db_manager.connect():
        print("Failed to connect to database")
        return
    
    collection = db_manager.get_collection("papers")
    
    print("Adding primary_s2field to documents...")
    
    # First, let's see how many documents need updating
    docs_needing_update = collection.count_documents({
        "s2fieldsofstudy": {"$elemMatch": {"source": "s2-fos-model"}},
        "primary_s2field": {"$exists": False}
    })
    
    print(f"Found {docs_needing_update:,} documents that need primary_s2field")
    
    if docs_needing_update == 0:
        print("All documents already have primary_s2field")
        return
    
    # Update in batches to avoid memory issues
    pipeline = [
        {"$match": {
            "s2fieldsofstudy": {"$elemMatch": {"source": "s2-fos-model"}},
            "primary_s2field": {"$exists": False}
        }},
        {"$addFields": {
            "primary_s2field": {
                "$let": {
                    "vars": {
                        "s2_fos_models": {
                            "$filter": {
                                "input": "$s2fieldsofstudy",
                                "cond": {"$eq": ["$$this.source", "s2-fos-model"]}
                            }
                        }
                    },
                    "in": {"$arrayElemAt": ["$$s2_fos_models.category", 0]}
                }
            }
        }},
        {"$merge": {"into": "papers"}}
    ]
    
    try:
        result = list(collection.aggregate(pipeline, allowDiskUse=True))
        print("✓ Successfully added primary_s2field to documents")
        
        # Verify the update
        updated_count = collection.count_documents({"primary_s2field": {"$exists": True}})
        print(f"✓ {updated_count:,} documents now have primary_s2field")
        
    except Exception as e:
        print(f"Error updating collection: {e}")

###########
# SYNCING #
###########

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

def sync_fields_to_sqlite(data: List[Dict[str, Any]], sqlite_path: str, table_name: str = "fields") -> None:
    """Write field/year counts to SQLite incrementally"""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            field TEXT NOT NULL,
            year INTEGER NOT NULL, 
            count INTEGER NOT NULL,
            PRIMARY KEY (field, year)
        )
    ''')
    
    # Insert or replace records (incremental)
    cursor.executemany(
        f'INSERT OR REPLACE INTO {table_name} (field, year, count) VALUES (?, ?, ?)',
        [(row['field'], row['year'], row['count']) for row in data]
    )
    
    conn.commit()
    conn.close()

################
# GROUP COUNTS #
################

# def find_parsed_text():
#     s2orc_collection = db_manager.get_collection("s2orc_v2")
#     s2orc_corpusid = list(s2orc_collection.aggregate([{"$project": {"corpusid": 1}}]))

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

def get_s2fieldsofstudy_year_counts_fast(fields: List[str] = None) -> List[Dict[str, Any]]:
    """Fast version using primary_s2field string"""
    collection = db_manager.get_collection("papers")
    
    match_conditions = {
        "primary_s2field": {"$exists": True, "$ne": None},
        "year": {"$exists": True, "$ne": None, "$gte": 1900, "$lte": 2030}
    }
    
    if fields:
        match_conditions["primary_s2field"] = {"$in": fields}
    
    pipeline = [
        {"$match": match_conditions},
        {"$group": {
            "_id": {"field": "$primary_s2field", "year": "$year"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "field": "$_id.field",
            "year": "$_id.year", 
            "count": 1
        }},
        {"$sort": {"field": 1, "year": 1}}
    ]
    
    return list(collection.aggregate(pipeline))

def get_s2fieldsofstudy_year_counts(fields: List[str] = None, sample_size: int = None) -> List[Dict[str, Any]]:
    """Get exact paper counts by S2 field of study and year (s2-fos-model only)"""
    collection = db_manager.get_collection("papers")
    
    pipeline = []
    
    # Add sampling at the very beginning if requested
    if sample_size:
        print(f"Using {sample_size} records")
        pipeline.append({"$sample": {"size": sample_size}})
    
    initial_match = {
        "s2fieldsofstudy": {"$exists": True, "$ne": None, "$not": {"$size": 0}},
        "year": {"$exists": True, "$ne": None, "$gte": 1900, "$lte": 2030}
    }
    
    # If filtering by specific fields, add that to the initial match
    if fields:
        initial_match["s2fieldsofstudy"] = {
            "$elemMatch": {
                "source": "s2-fos-model",
                "category": {"$in": fields}
            }
        }
    else:
        initial_match["s2fieldsofstudy"] = {
            "$elemMatch": {"source": "s2-fos-model"}
        }
    
    pipeline.extend([
        {"$match": initial_match},
        {"$unwind": "$s2fieldsofstudy"},           # FIXED: lowercase
        {"$match": {"s2fieldsofstudy.source": "s2-fos-model"}},  # FIXED: lowercase
        {"$addFields": {"field": "$s2fieldsofstudy.category"}}   # FIXED: lowercase
    ])
    
    # Additional field filter (if needed)
    if fields:
        pipeline.append({"$match": {"field": {"$in": fields}}})
    
    pipeline.extend([
        {"$group": {
            "_id": {"field": "$field", "year": "$year"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "field": "$_id.field",
            "year": "$_id.year", 
            "count": 1
        }},
        {"$sort": {"field": 1, "year": 1}}
    ])
    
    return list(collection.aggregate(pipeline))

#############
### INDEX ###
#############

def create_performance_indexes():
    """Create indexes to accelerate common queries"""
    if not db_manager.connect():
        print("Failed to connect to database")
        return
    
    print("Creating performance indexes...")
    
    papers_collection = db_manager.get_collection("papers")
    
    try:
        # Index for venue + year queries
        papers_collection.create_index([("venue", 1), ("year", 1)])
        print("  ✓ Created papers.venue + year index")
        
        # Index for year queries
        papers_collection.create_index([("year", 1)])
        print("  ✓ Created papers.year index")
        
        # Index for venue queries
        papers_collection.create_index([("venue", 1)])
        print("  ✓ Created papers.venue index")
        
        # Index for s2fieldsofstudy queries (compound)
        papers_collection.create_index([
            ("s2fieldsofstudy.source", 1), 
            ("s2fieldsofstudy.category", 1), 
            ("year", 1)
            ])
        print("  ✓ Created papers.s2fieldsofstudy compound index")
        
        # Index just for s2fieldsofstudy array
        papers_collection.create_index([("s2fieldsofstudy", 1)])
        print("  ✓ Created papers.s2fieldsofstudy array index")
        
    except Exception as e:
        print(f"  → Error creating indexes: {e}")
    
    print("✓ Performance indexes created!")

def list_indexes(collection_name: str):
    """List all indexes on a collection"""
    collection = db_manager.get_collection(collection_name)
    indexes = collection.list_indexes()
    
    print(f"Indexes on '{collection_name}' collection:")
    for idx in indexes:
        name = idx.get('name', 'Unknown')
        keys = idx.get('key', {})
        print(f"  - {name}: {keys}")

def drop_index(collection_name: str, index_name: str):
    """Drop a specific index from a collection"""
    collection = db_manager.get_collection(collection_name)
    try:
        collection.drop_index(index_name)
        print(f"✓ Dropped index '{index_name}' from '{collection_name}'")
    except Exception as e:
        print(f"Failed to drop index: {e}")
 
def list_collections() -> List[str]:
    """List all collections in database"""
    if not db_manager._connected:
        db_manager.connect()
    return db_manager.db.list_collection_names()