#!/usr/bin/env python3
"""
Sync field of study counts to frontend SQLite database
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sciscidb.database import db_manager, get_s2fieldsofstudy_year_counts, sync_fields_to_sqlite

def preview_data(data, detailed_field=None):
    """Show summary of field data"""
    fields = {}
    for row in data:
        field = row['field']
        if field not in fields:
            fields[field] = {'years': 0, 'total_papers': 0, 'year_range': [], 'year_data': []}
        fields[field]['years'] += 1
        fields[field]['total_papers'] += row['count']
        fields[field]['year_range'].append(row['year'])
        fields[field]['year_data'].append((row['year'], row['count']))
    
    print(f"\nData summary ({len(data)} records):")
    print("-" * 70)
    for field, stats in sorted(fields.items()):
        min_year = min(stats['year_range'])
        max_year = max(stats['year_range'])
        print(f"{field:<25} {stats['years']} years ({min_year}-{max_year}) {stats['total_papers']:,} papers")
    
    print(f"\nTotal fields: {len(fields)}")
    
    # Show detailed breakdown for specific field
    if detailed_field and detailed_field in fields:
        print(f"\nYear-by-year breakdown for {detailed_field}:")
        print("-" * 40)
        year_data = sorted(fields[detailed_field]['year_data'])
        for year, count in year_data:
            print(f"{year}: {count:,} papers")

def main():
    parser = argparse.ArgumentParser(description="Sync field of study counts to frontend")
    parser.add_argument("--db", default="../frontend/local.db", help="SQLite database path")
    parser.add_argument("--fields", nargs="*", help="Specific fields to sync")
    parser.add_argument("--dry-run", action="store_true", help="Show data preview only, don't sync")
    parser.add_argument("--detail", help="Show year-by-year breakdown for specific field")
    parser.add_argument("--table", default="fields", help="SQLite table name")
    parser.add_argument("--sample", type=int, help="Test with sample size (for performance testing)")
    
    args = parser.parse_args()
    
    if not db_manager.connect():
        print("Failed to connect to MongoDB")
        sys.exit(1)
    
    print(f"Fetching field of study counts from papers...")
    data = get_s2fieldsofstudy_year_counts(fields=args.fields, sample_size=args.sample)
    
    if not data:
        print("No data found!")
        sys.exit(1)
    
    preview_data(data, detailed_field=args.detail)
    
    if args.dry_run:
        print("\nDry run complete")
        return
    
    print(f"\nSyncing incrementally to {args.db} (table: {args.table})...")
    sync_fields_to_sqlite(data, args.db, args.table)
    print("Done!")

if __name__ == "__main__":
    main()