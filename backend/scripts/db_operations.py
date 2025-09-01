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

def group_count(collection_name: str, field: str, limit: int = 20, estimated: bool = False, sample_size: int = 50000, filter_field: str = None, filter_value: str = None):
    """Perform group count aggregation on a field with optional filtering"""
    collection = db_manager.get_collection(collection_name)
    
    pipeline = []
    
    if estimated:
        # Use sampling for fast approximate results
        pipeline.append({"$sample": {"size": sample_size}})
    
    # Add filter conditions
    match_conditions = {field: {"$exists": True, "$ne": None}}
    
    if filter_field and filter_value:
        # Add filter condition (case-insensitive for strings)
        match_conditions[filter_field] = {"$regex": f"^{filter_value}$", "$options": "i"}
    
    pipeline.extend([
        {"$match": match_conditions},
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
    
    # Positional argument
    parser.add_argument(
        "action",
        choices=["count", "list-collections", "sample", "query", "test-connection", "group-count", "export-count"],
        help="Action to perform"
    )
    
    # Optional arguments
    parser.add_argument("--collection", "-c", help="Collection name")
    parser.add_argument("--field", "-f", help="Field to group by (for group-count action)")
    parser.add_argument("--filter-field", help="Field to filter on (e.g., 'venue')")
    parser.add_argument("--filter-value", help="Value to filter by (e.g., 'Nature')")
    parser.add_argument("--all", action="store_true", help="Apply to all collections (for count action)")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Limit for query results")
    parser.add_argument("--exact", action="store_true", help="Use exact count instead of estimated")
    parser.add_argument("--sample", "-s", type=int, default=50000, help="Sample size for estimates (default: 50000)")
    parser.add_argument("--fast", action="store_true", help="Use smaller sample for faster results (10k sample)")
    parser.add_argument("--output", "-o", help="Output file path for export-count action")
    
    args = parser.parse_args()
    
    print(f"Debug: args.limit = {args.limit}")  # Debug line
    
    try:
        if args.action == "test-connection":
            config.print_config()
            print("\n" + "="*50)
            success = config.test_database_connection()
            sys.exit(0 if success else 1)
        
        # Connect to database for other actions
        if not db_manager.connect():
            print("Failed to connect to database. Use 'test-connection' for details.")
            sys.exit(1)
        
        if args.action == "group-count":
            if not args.collection:
                print("--collection required for group-count action")
                sys.exit(1)
            if not args.field:
                print("--field required for group-count action")
                sys.exit(1)
            
            # Determine sample size
            if args.fast:
                sample_size = 10000
            else:
                sample_size = args.sample
            
            use_estimated = not args.exact
            results, was_estimated = group_count(
                args.collection, 
                args.field, 
                args.limit, 
                estimated=use_estimated, 
                sample_size=sample_size,
                filter_field=args.filter_field,
                filter_value=args.filter_value
            )
            
            if results:
                count_type = "estimated" if was_estimated else "exact"
                
                # Build description
                description = f"'{args.field}' in '{args.collection}'"
                if args.filter_field and args.filter_value:
                    description += f" (filtered by {args.filter_field}='{args.filter_value}')"
                
                if was_estimated:
                    print(f"Top {len(results)} values for {description} ({count_type}, {sample_size:,} sample):")
                else:
                    print(f"Top {len(results)} values for {description} ({count_type}):")
                
                for i, result in enumerate(results, 1):
                    value = result['_id']
                    count = result['count']
                    display_value = value if len(str(value)) <= 50 else str(value)[:50] + "..."
                    count_display = f"~{count:,}" if was_estimated else f"{count:,}"
                    print(f"  {i:2d}. {display_value}: {count_display}")
                    
                if was_estimated:
                    accuracy = "±15%" if sample_size < 25000 else "±10%" if sample_size < 75000 else "±5%"
                    print(f"Note: Estimated counts ({accuracy} accuracy). Use --exact for precise counts.")
            else:
                description = f"field '{args.field}' in collection '{args.collection}'"
                if args.filter_field and args.filter_value:
                    description += f" with {args.filter_field}='{args.filter_value}'"
                print(f"No results found for {description}")
        
        elif args.action == "export-count":
            if not args.collection:
                print("--collection required for export-count action")
                sys.exit(1)
            if not args.field:
                print("--field required for export-count action")
                sys.exit(1)
            if not args.output:
                print("--output required for export-count action")
                sys.exit(1)
            
            from sciscidb.export import export_group_count_to_file
            from pathlib import Path
            
            # Determine sample size
            if args.fast:
                sample_size = 10000
            else:
                sample_size = args.sample
            
            use_estimated = not args.exact
            output_path = Path(args.output)
            
            export_group_count_to_file(
                collection_name=args.collection,
                field=args.field,
                output_file=output_path,
                limit=args.limit,
                filter_field=args.filter_field,
                filter_value=args.filter_value,
                estimated=use_estimated,
                sample_size=sample_size
            )
            
            print(f"\nReady for frontend! You can now:")
            print(f"  cp {output_path} frontend/static/data/")
            print(f"  # Then import in your Svelte component:")
            print(f"  import data from '$lib/data/{output_path.name}';")
        
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