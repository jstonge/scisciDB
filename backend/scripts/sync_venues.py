#!/usr/bin/env python3
"""
Sync venue publication counts to frontend SQLite database
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.database import db_manager, get_venue_year_counts, sync_to_sqlite

def main():
    parser = argparse.ArgumentParser(description="Sync venue counts to frontend")
    parser.add_argument("--db", default="../frontend/local.db", help="SQLite database path")
    parser.add_argument("--venues", nargs="*", help="Specific venues to sync")
    parser.add_argument("--collection", default="papers", help="MongoDB collection")
    parser.add_argument("--exact", action="store_true", help="Use exact counts (slower)")
    parser.add_argument("--sample", type=int, default=100000, help="Sample size for estimates")
    
    args = parser.parse_args()
    
    if not db_manager.connect():
        print("Failed to connect to MongoDB")
        sys.exit(1)
    
    print(f"Fetching venue counts from {args.collection}...")
    data = get_venue_year_counts(
        args.collection,
        venues=args.venues,
        estimated=not args.exact,
        sample_size=args.sample
    )
    
    print(f"Syncing {len(data)} records to {args.db}...")
    sync_to_sqlite(data, args.db)
    
    venues = set(row['venue'] for row in data)
    print(f"Done! Synced {len(venues)} venues: {sorted(venues)}")

if __name__ == "__main__":
    main()