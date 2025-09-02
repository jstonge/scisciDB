#!/usr/bin/env python3
"""
Examine MongoDB collections
"""
import argparse
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.database import db_manager, find_one_sample, list_collections, get_collection_count

def main():
    parser = argparse.ArgumentParser(description="Examine MongoDB data")
    parser.add_argument("action", choices=["sample", "collections", "count"], help="Action to perform")
    parser.add_argument("--collection", help="Collection name (required for sample and count)")
    
    args = parser.parse_args()
    
    if not db_manager.connect():
        print("Failed to connect to MongoDB")
        sys.exit(1)
    
    if args.action == "collections":
        collections = list_collections()
        print(f"Collections ({len(collections)}):")
        for name in collections:
            print(f"  {name}")
    
    elif args.action == "sample":
        if not args.collection:
            print("--collection required for sample action")
            sys.exit(1)
        
        doc = find_one_sample(args.collection)
        if doc:
            print(f"Sample document from '{args.collection}':")
            print(json.dumps(doc, indent=2, default=str))
        else:
            print(f"No documents found in '{args.collection}'")
    
    elif args.action == "count":
        if not args.collection:
            print("--collection required for count action")
            sys.exit(1)
        
        count = get_collection_count(args.collection)
        print(f"Estimated document count for '{args.collection}': {count:,}")

if __name__ == "__main__":
    main()