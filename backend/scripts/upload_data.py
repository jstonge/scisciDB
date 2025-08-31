#!/usr/bin/env python3
"""
CLI script to upload data to MongoDB
"""
import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import sciscidb
sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.upload import upload_to_mongodb, upload_dataset_by_name
from sciscidb.config import config

def main():
    parser = argparse.ArgumentParser(description="Upload data to MongoDB")
    parser.add_argument(
        "-i", "--input",
        type=str,  # Change to string, we'll resolve the path
        help="Dataset name or directory path containing JSON files",
        required=True,
    )
    parser.add_argument(
        "-c", "--collection", 
        type=str, 
        help="MongoDB collection name", 
        required=True
    )
    parser.add_argument(
        "--clean-slate",
        action="store_true",
        help="Drop existing collection and start fresh"
    )
    
    args = parser.parse_args()
    
    # Smart path resolution
    input_path = args.input
    
    # If it looks like a dataset name (no slashes), use config path
    if '/' not in input_path and not Path(input_path).is_absolute():
        # Remove trailing slash if present
        dataset_name = input_path.rstrip('/')
        resolved_path = config.get_dataset_path(dataset_name)
        print(f"Resolving '{dataset_name}' to: {resolved_path}")
    else:
        # Use as literal path
        resolved_path = Path(input_path)
        print(f"Using literal path: {resolved_path}")
    
    try:
        stats = upload_to_mongodb(
            dataset_path=resolved_path,
            collection_name=args.collection,
            clean_slate=args.clean_slate
        )
        
        print(f"\n🎉 Upload completed successfully!")
        print(f"📊 Final stats: {stats}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()