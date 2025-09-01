#!/usr/bin/env python3
"""
CLI script to manage database indexes
"""
import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import sciscidb
sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.database import (
    create_performance_indexes, 
    list_indexes, 
    drop_index,
    list_collections,
    db_manager
)

def main():
    parser = argparse.ArgumentParser(description="Manage database indexes")
    parser.add_argument(
        "action",
        choices=["create", "list", "drop", "list-collections"],
        help="Action to perform"
    )
    parser.add_argument(
        "--collection", "-c",
        help="Collection name (for list/drop actions)"
    )
    parser.add_argument(
        "--index", "-i", 
        help="Index name (for drop action)"
    )
    
    args = parser.parse_args()
    
    # Connect to database
    if not db_manager.connect():
        print("Failed to connect to database")
        sys.exit(1)
    
    try:
        if args.action == "create":
            # Create all performance indexes
            create_performance_indexes()
            
        elif args.action == "list":
            if not args.collection:
                print("--collection required for list action")
                sys.exit(1)
            list_indexes(args.collection)
            
        elif args.action == "drop":
            if not args.collection or not args.index:
                print("Both --collection and --index required for drop action")
                sys.exit(1)
            drop_index(args.collection, args.index)
            
        elif args.action == "list-collections":
            collections = list_collections()
            print("Available collections:")
            for coll in collections:
                print(f"  - {coll}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
