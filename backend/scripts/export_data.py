#!/usr/bin/env python3
"""
CLI script to export data for frontend
"""
import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import sciscidb
sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.export import export_all_datasets, explore_data_structure, export_for_frontend
from sciscidb.config import config

def main():
    parser = argparse.ArgumentParser(description="Export data for frontend")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=config.export_dir,
        help="Output directory for exports"
    )
    parser.add_argument(
        "--explore", 
        action="store_true",
        help="Explore data structure first"
    )
    parser.add_argument(
        "--frontend", 
        type=Path,
        help="Export directly to frontend static/data directory"
    )
    
    args = parser.parse_args()
    
    if args.explore:
        print("Exploring data structure...")
        explore_data_structure()
        print("\n" + "="*50 + "\n")
    
    if args.frontend:
        print(f"Exporting data for frontend to {args.frontend}")
        export_for_frontend(args.frontend)
    else:
        print(f"Exporting data to {args.output}")
        export_dir = export_all_datasets(args.output)
        print(f"\nExports saved to: {export_dir}")

if __name__ == "__main__":
    main()