#!/usr/bin/env python3
"""
Update collection structure for better performance
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.database import db_manager, add_primary_s2field, create_performance_indexes

def main():
    parser = argparse.ArgumentParser(description="Update collection structure")
    parser.add_argument("action", choices=["add-primary-s2field", "create-indexes"], 
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if not db_manager.connect():
        print("Failed to connect to MongoDB")
        sys.exit(1)
    
    if args.action == "add-primary-s2field":
        add_primary_s2field()
    elif args.action == "create-indexes":
        create_performance_indexes()

if __name__ == "__main__":
    main()