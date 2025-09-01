#!/usr/bin/env python3
"""
CLI script for basic database operations
"""
import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import sciscidb
sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.database import (
    list_collections,
    count_documents,
    get_sample_document,
    find_documents,
    db_manager
)
from sciscidb.config import config

def group_count(collection_name: str, field: str, limit: int = 20, estimated: bool = False, sample_size: int = 100000):
    """Perform group count aggregation on a field"""
    collection = db_manager.get_collection(collection_name)
    
    pipeline = []
    
    if estimated:
        # Use sampling for fast approximate results
        pipeline.append({"$sample": {"size": sample_size}})
    
    pipeline.extend([
        {"$match": {field: {"$exists": True, "$ne": None}}},  # Filter out missing values
        {"$group": {
            "_id": f"${field}",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},  # Sort by count descending
        {"$limit": limit}
    ])
    
    results = list(collection.aggregate(pipeline))
    
    # If using sampling, extrapolate the counts
    if estimated and results:
        # Get total document count for extrapolation
        total_docs = collection.estimated_document_count()
        extrapolation_factor = total_docs / sample_size if sample_size < total_docs else 1
        
        # Scale up the counts
        for result in results:
            result['count'] = int(result['count'] * extrapolation_factor)
            result['estimated'] = True
    
    return results, estimated

def main():
    parser = argparse.ArgumentParser(description="Basic database operations")
    parser.add_argument(
        "action",
        choices=["count", "list-collections", "sample", "query", "test-connection", "group-count"],
        help="Action to perform"
    )
    parser.add_argument(
        "--collection", "-c",
        help="Collection name"
    )
    parser.add_argument(
        "--field", "-f",
        help="Field to group by (for group-count action)"
    )
    parser.add_argument(
        "--all", 
        action="store_true",
        help="Apply to all collections (for count action)"
    )
    parser.add_argument(
        "--exact",
        action="store_true",
        help="Use exact count (slow) instead of estimated count (fast)"
    )
    parser.add_argument("--limit", "-l", type=int, default=20, help="Limit for query results")
    
    args = parser.parse_args()
    
    try:
        if args.action == "test-connection":
            # Test database connection with detailed info
            config.print_config()
            print("\n" + "="*50)
            success = config.test_database_connection()
            sys.exit(0 if success else 1)
        
        # For other actions, connect to database
        if not db_manager.connect():
            print("Failed to connect to database. Use 'test-connection' for details.")
            sys.exit(1)
        
        if args.action == "list-collections":
            collections = list_collections()
            print("Available collections:")
            for coll in collections:
                print(f"  - {coll}")
        
        elif args.action == "count":
            count_type = "exact" if args.exact else "estimated"
            
            if args.all:
                # Count all collections
                collections = list_collections()
                print(f"Document counts ({count_type}):")
                total = 0
                for coll in collections:
                    count = count_documents(coll, exact=args.exact)
                    print(f"  {coll}: {count:,} documents")
                    total += count
                print(f"  Total: {total:,} documents")
                
            elif args.collection:
                # Count specific collection
                count = count_documents(args.collection, exact=args.exact)
                print(f"{args.collection}: {count:,} documents ({count_type})")
                
            else:
                print("Either --collection or --all required for count action")
                sys.exit(1)
        
        elif args.action == "group-count":
            if not args.collection:
                print("--collection required for group-count action")
                sys.exit(1)
            if not args.field:
                print("--field required for group-count action")
                sys.exit(1)
            
            # Use estimated count for large collections unless --exact is specified
            use_estimated = not args.exact
            
            results, was_estimated = group_count(
                args.collection, 
                args.field, 
                args.limit, 
                estimated=use_estimated
            )
            
            if results:
                count_type = "estimated" if was_estimated else "exact"
                print(f"Top {len(results)} values for '{args.field}' in '{args.collection}' ({count_type}):")
                total_shown = sum(r['count'] for r in results)
                
                for i, result in enumerate(results, 1):
                    value = result['_id']
                    count = result['count']
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 50:
                        display_value = value[:50] + "..."
                    else:
                        display_value = value
                    
                    # Show ~ for estimated counts
                    count_display = f"~{count:,}" if was_estimated else f"{count:,}"
                    print(f"  {i:2d}. {display_value}: {count_display}")
                
                total_display = f"~{total_shown:,}" if was_estimated else f"{total_shown:,}"
                print(f"\nTotal documents shown: {total_display}")
                
                if was_estimated:
                    print("Note: Counts are estimated based on 100k sample. Use --exact for precise counts.")
                
                # Show what fields are available for this collection
                sample = get_sample_document(args.collection)
                if sample:
                    available_fields = list(sample.keys())[:10]  # First 10 fields
                    print(f"Available fields: {', '.join(available_fields)}")
                    if len(sample.keys()) > 10:
                        print(f"... and {len(sample.keys()) - 10} more")
            else:
                print(f"No results found for field '{args.field}' in collection '{args.collection}'")
        
        elif args.action == "sample":
            if not args.collection:
                print("--collection required for sample action")
                sys.exit(1)
            
            sample = get_sample_document(args.collection)
            if sample:
                print(f"Sample document from '{args.collection}':")
                print(f"Fields: {list(sample.keys())}")
                print("\nFirst few fields:")
                for key, value in list(sample.items())[:5]:
                    if isinstance(value, str) and len(value) > 100:
                        preview = value[:100] + "..."
                    else:
                        preview = str(value)[:100]
                    print(f"  {key}: {preview}")
            else:
                print(f"No documents found in '{args.collection}'")
        
        elif args.action == "query":
            if not args.collection:
                print("--collection required for query action")
                sys.exit(1)
            
            # Use different default limit for query vs group-count
            query_limit = args.limit if args.limit != 20 else 10
            docs = find_documents(args.collection, limit=query_limit)
            print(f"First {len(docs)} documents from '{args.collection}':")
            for i, doc in enumerate(docs, 1):
                # Show just the first few fields of each doc
                preview = {k: v for k, v in list(doc.items())[:3]}
                print(f"  {i}. {preview}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()