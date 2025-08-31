#!/usr/bin/env python3
"""
CLI script to download datasets from Semantic Scholar
"""
import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import sciscidb
sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.download import (
    download_semantic_scholar, 
    download_dataset, 
    get_dataset_info,
    list_available_datasets
)
from sciscidb.config import config

def main():
    parser = argparse.ArgumentParser(description="Download datasets from Semantic Scholar")
    parser.add_argument(
        "dataset_name",
        help="Name of dataset to download (papers, authors, publication-venues, etc.)"
    )
    parser.add_argument(
        "--clean-slate",
        action="store_true",
        help="Remove existing dataset directory before downloading"
    )
    parser.add_argument(
        "--source", 
        default="semantic_scholar",
        choices=["semantic_scholar", "openalex"],
        help="Data source (default: semantic_scholar)"
    )
    parser.add_argument(
        "--info",
        action="store_true", 
        help="Show information about downloaded dataset"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available datasets for the source"
    )
    
    args = parser.parse_args()
    
    # List available datasets
    if args.list:
        try:
            datasets = list_available_datasets(args.source)
            print(f"Available datasets from {args.source}:")
            for dataset in datasets:
                print(f"  - {dataset}")
        except Exception as e:
            print(f"❌ Failed to list datasets: {e}")
            sys.exit(1)
        return
    
    # Show dataset info
    if args.info:
        try:
            info = get_dataset_info(args.dataset_name)
            print(f"Dataset: {args.dataset_name}")
            print(f"Exists: {info['exists']}")
            if info['exists']:
                print(f"Path: {info['path']}")
                print(f"Files: {info['total_files']} ({info['total_size_mb']} MB)")
                print(f"Sample files: {info['sample_files']}")
        except Exception as e:
            print(f"❌ Failed to get dataset info: {e}")
            sys.exit(1)
        return
    
    # Download dataset
    try:
        print(f"Downloading {args.dataset_name} from {args.source}...")
        
        dataset_path = download_dataset(
            source=args.source,
            dataset_name=args.dataset_name,
            clean_slate=args.clean_slate
        )
        
        print(f"\n🎉 Download completed successfully!")
        print(f"📁 Dataset saved to: {dataset_path}")
        
        # Show dataset info
        info = get_dataset_info(args.dataset_name)
        print(f"📊 Downloaded {info['total_files']} files ({info['total_size_mb']} MB)")
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()