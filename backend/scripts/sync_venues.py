#!/usr/bin/env python3
"""
Sync venue publication counts to frontend SQLite database
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.database import db_manager, get_venue_year_counts, sync_to_sqlite_incremental

def preview_data(data, detailed_venue=None):
    """Show summary of data, with detailed breakdown for specific venue"""
    venues = {}
    for row in data:
        venue = row['venue']
        if venue not in venues:
            venues[venue] = {'years': 0, 'total_papers': 0, 'year_range': [], 'year_data': []}
        venues[venue]['years'] += 1
        venues[venue]['total_papers'] += row['count']
        venues[venue]['year_range'].append(row['year'])
        venues[venue]['year_data'].append((row['year'], row['count']))
    
    print(f"\nData summary ({len(data)} records):")
    print("-" * 60)
    for venue, stats in venues.items():
        min_year = min(stats['year_range'])
        max_year = max(stats['year_range'])
        method = "exact" if hasattr(data, '_exact') else "estimated"
        print(f"{venue:<20} {stats['years']} years ({min_year}-{max_year}) {stats['total_papers']:,} papers")
    
    print(f"\nTotal venues: {len(venues)}")
    
    # Show detailed breakdown for specific venue
    if detailed_venue and detailed_venue in venues:
        print(f"\nYear-by-year breakdown for {detailed_venue}:")
        print("-" * 40)
        year_data = sorted(venues[detailed_venue]['year_data'])
        for year, count in year_data:
            print(f"{year}: {count:,} papers")

def main():
    parser = argparse.ArgumentParser(description="Sync venue counts to frontend")
    parser.add_argument("--db", default="../frontend/local.db", help="SQLite database path")
    parser.add_argument("--venues", nargs="*", help="Specific venues to sync")
    parser.add_argument("--collection", default="papers", help="MongoDB collection")
    parser.add_argument("--dry-run", action="store_true", help="Show data preview only, don't sync")
    parser.add_argument("--detail", help="Show year-by-year breakdown for specific venue")
    
    args = parser.parse_args()
    
    if not db_manager.connect():
        print("Failed to connect to MongoDB")
        sys.exit(1)
    
    data = get_venue_year_counts(args.collection, venues=args.venues)
    
    if not data:
        print("No data found!")
        sys.exit(1)
    
    preview_data(data, detailed_venue=args.detail)
    
    if args.dry_run:
        print("\nDry run complete")
        return
    
    print(f"\nSyncing incrementally to {args.db}...")
    sync_to_sqlite_incremental(data, args.db)
    print("Done! (Existing records updated, new ones added)")

if __name__ == "__main__":
    main()