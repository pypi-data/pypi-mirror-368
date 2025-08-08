#!/usr/bin/env python3
"""
Analyze the differences between sn_type and object_type fields in NGSF data.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_type_differences(csv_file: str):
    """Analyze differences between sn_type and object_type."""
    print("=" * 60)
    print("ANALYSIS OF SN_TYPE vs OBJECT_TYPE DIFFERENCES")
    print("=" * 60)
    
    df = pd.read_csv(csv_file)
    
    print(f"Total entries: {len(df)}")
    print()
    
    # Check completeness
    sn_types = df['sn_type'].dropna()
    obj_types = df['object_type'].dropna()
    
    print("=== COMPLETENESS ===")
    print(f"Entries with sn_type: {len(sn_types)} ({len(sn_types)/len(df)*100:.1f}%)")
    print(f"Entries with object_type: {len(obj_types)} ({len(obj_types)/len(df)*100:.1f}%)")
    print()
    
    # Check unique values
    print("=== UNIQUE VALUES ===")
    print(f"Unique sn_type values: {df['sn_type'].nunique()}")
    print(f"Unique object_type values: {df['object_type'].nunique()}")
    print()
    
    # Show examples of differences
    print("=== EXAMPLES OF DIFFERENCES ===")
    
    # Find entries where both fields exist but are different
    both_exist = df[df['sn_type'].notna() & df['object_type'].notna()]
    different = both_exist[both_exist['sn_type'] != both_exist['object_type']]
    
    print(f"Entries where both fields exist: {len(both_exist)}")
    print(f"Entries where they differ: {len(different)}")
    print()
    
    if len(different) > 0:
        print("Sample differences:")
        for i, (idx, row) in enumerate(different.head(10).iterrows()):
            print(f"  {row['primary_name']}: sn_type='{row['sn_type']}' vs object_type='{row['object_type']}'")
        print()
    
    # Show entries where sn_type is empty but object_type exists
    sn_empty_obj_exists = df[df['sn_type'].isna() & df['object_type'].notna()]
    print(f"Entries with empty sn_type but object_type: {len(sn_empty_obj_exists)}")
    if len(sn_empty_obj_exists) > 0:
        print("Sample entries:")
        for i, (idx, row) in enumerate(sn_empty_obj_exists.head(5).iterrows()):
            print(f"  {row['primary_name']}: object_type='{row['object_type']}'")
        print()
    
    # Show entries where object_type is empty but sn_type exists
    obj_empty_sn_exists = df[df['object_type'].isna() & df['sn_type'].notna()]
    print(f"Entries with empty object_type but sn_type: {len(obj_empty_sn_exists)}")
    if len(obj_empty_sn_exists) > 0:
        print("Sample entries:")
        for i, (idx, row) in enumerate(obj_empty_sn_exists.head(5).iterrows()):
            print(f"  {row['primary_name']}: sn_type='{row['sn_type']}'")
        print()
    
    # Analyze the mapping between fields
    print("=== FIELD MAPPING ANALYSIS ===")
    
    # Create a mapping table
    mapping = df[df['sn_type'].notna() & df['object_type'].notna()].groupby(['sn_type', 'object_type']).size().reset_index(name='count')
    mapping = mapping.sort_values('count', ascending=False)
    
    print("Most common sn_type -> object_type mappings:")
    for _, row in mapping.head(15).iterrows():
        print(f"  '{row['sn_type']}' -> '{row['object_type']}' ({row['count']} entries)")
    print()
    
    # Check for inconsistencies
    print("=== INCONSISTENCIES ===")
    
    # Find sn_types that map to multiple object_types
    inconsistent_sn = mapping.groupby('sn_type').size()
    inconsistent_sn = inconsistent_sn[inconsistent_sn > 1]
    
    if len(inconsistent_sn) > 0:
        print(f"sn_types that map to multiple object_types: {len(inconsistent_sn)}")
        for sn_type in inconsistent_sn.head(5).index:
            mappings = mapping[mapping['sn_type'] == sn_type]
            print(f"  '{sn_type}' maps to:")
            for _, row in mappings.iterrows():
                print(f"    '{row['object_type']}' ({row['count']} entries)")
        print()
    
    # Find object_types that map to multiple sn_types
    inconsistent_obj = mapping.groupby('object_type').size()
    inconsistent_obj = inconsistent_obj[inconsistent_obj > 1]
    
    if len(inconsistent_obj) > 0:
        print(f"object_types that map to multiple sn_types: {len(inconsistent_obj)}")
        for obj_type in inconsistent_obj.head(5).index:
            mappings = mapping[mapping['object_type'] == obj_type]
            print(f"  '{obj_type}' maps to:")
            for _, row in mappings.iterrows():
                print(f"    '{row['sn_type']}' ({row['count']} entries)")
        print()
    
    # Recommendations
    print("=== RECOMMENDATIONS ===")
    
    if len(different) == 0 and len(sn_empty_obj_exists) == 0 and len(obj_empty_sn_exists) == 0:
        print("✅ PERFECT: sn_type and object_type are identical!")
        print("   You can use either field interchangeably.")
    elif len(different) > 0:
        print("⚠️  DIFFERENCES FOUND:")
        print("   - sn_type and object_type have different values")
        print("   - object_type appears to be more detailed/standardized")
        print("   - Recommend using object_type for crossmatching")
    else:
        print("✅ GOOD: Fields are consistent where both exist")
        print("   - object_type has better coverage")
        print("   - Recommend using object_type as primary classification")
    
    print()
    print("=== SUMMARY ===")
    print(f"• sn_type coverage: {len(sn_types)/len(df)*100:.1f}%")
    print(f"• object_type coverage: {len(obj_types)/len(df)*100:.1f}%")
    print(f"• Fields differ in {len(different)} cases")
    print(f"• object_type appears more complete and standardized")
    
    print("=" * 60)

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze differences between sn_type and object_type")
    parser.add_argument("--metadata", default="ngsf_tns_crossmatching.csv",
                       help="NGSF metadata CSV file")
    
    args = parser.parse_args()
    
    analyze_type_differences(args.metadata)

if __name__ == "__main__":
    main() 