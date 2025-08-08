#!/usr/bin/env python3
"""
Check Template Filtering - Verify -999.0 Age Filtering
=====================================================

This script checks if the H5 template storage is properly filtering out
templates with -999.0 ages as intended.

Usage:
    python scripts/check_template_filtering.py
"""

import sys
import json
import h5py
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from snid_sage.snid.io import read_template

def check_template_index():
    """Check the template index for templates with -999.0 age."""
    index_file = Path("templates/template_index.json")
    
    if not index_file.exists():
        print("❌ Template index file not found!")
        return
    
    print("🔍 Checking template index for -999.0 ages...")
    
    with open(index_file, 'r') as f:
        index = json.load(f)
    
    templates = index.get('templates', {})
    total_templates = len(templates)
    minus_999_templates = []
    
    for name, info in templates.items():
        age = info.get('age', 0)
        if abs(age - (-999.0)) < 0.1:  # Use same tolerance as filtering code
            minus_999_templates.append({
                'name': name,
                'type': info.get('type', 'Unknown'),
                'age': age,
                'epochs': info.get('epochs', 1)
            })
    
    print(f"📊 Found {len(minus_999_templates)} templates with age -999.0 out of {total_templates} total templates")
    
    if minus_999_templates:
        print("\n❌ TEMPLATES WITH -999.0 AGE (SHOULD BE FILTERED OUT):")
        print("-" * 80)
        for template in minus_999_templates[:20]:  # Show first 20
            print(f"  {template['name']:<20} {template['type']:<10} age={template['age']:<8} epochs={template['epochs']}")
        
        if len(minus_999_templates) > 20:
            print(f"  ... and {len(minus_999_templates) - 20} more")
        
        return True
    else:
        print("✅ No templates with -999.0 age found in index!")
        return False

def check_original_template_files():
    """Check original template files to see which ones have -999.0 ages."""
    template_dir = Path("templates/Individual_templates")
    
    if not template_dir.exists():
        print("❌ Individual templates directory not found!")
        return
    
    print("\n🔍 Checking original template files for -999.0 ages...")
    
    template_files = list(template_dir.glob('*.lnw'))
    total_files = len(template_files)
    minus_999_files = []
    
    for i, template_file in enumerate(template_files):
        if i % 100 == 0:
            print(f"  Processing {i+1}/{total_files}...")
        
        try:
            template_data = read_template(str(template_file))
            ages = template_data.get('ages', [])
            
            # Check if all ages are -999.0
            all_minus_999 = all(abs(age - (-999.0)) < 0.1 for age in ages)
            
            if all_minus_999 and ages:
                minus_999_files.append({
                    'name': template_file.stem,
                    'type': template_data.get('type', 'Unknown'),
                    'ages': ages,
                    'epochs': len(ages)
                })
        
        except Exception as e:
            print(f"  ⚠️  Error reading {template_file.name}: {e}")
    
    print(f"📊 Found {len(minus_999_files)} template files with all ages -999.0 out of {total_files} total files")
    
    if minus_999_files:
        print("\n📋 TEMPLATE FILES WITH ALL AGES -999.0:")
        print("-" * 80)
        for template in minus_999_files[:20]:  # Show first 20
            print(f"  {template['name']:<20} {template['type']:<10} epochs={template['epochs']}")
        
        if len(minus_999_files) > 20:
            print(f"  ... and {len(minus_999_files) - 20} more")
        
        return minus_999_files
    else:
        print("✅ No template files with all ages -999.0 found!")
        return []

def check_h5_files():
    """Check H5 files for templates with -999.0 age."""
    template_dir = Path("templates")
    h5_files = list(template_dir.glob('templates_*.hdf5'))
    
    if not h5_files:
        print("❌ No H5 template files found!")
        return
    
    print(f"\n🔍 Checking {len(h5_files)} H5 files for -999.0 ages...")
    
    total_templates_in_h5 = 0
    minus_999_templates_in_h5 = 0
    
    for h5_file in h5_files:
        try:
            with h5py.File(h5_file, 'r') as f:
                templates_group = f.get('templates', {})
                
                for template_name in templates_group.keys():
                    template_group = templates_group[template_name]
                    age = template_group.attrs.get('age', 0)
                    total_templates_in_h5 += 1
                    
                    if abs(age - (-999.0)) < 0.1:
                        minus_999_templates_in_h5 += 1
                        print(f"  ❌ {template_name} in {h5_file.name}: age={age}")
        
        except Exception as e:
            print(f"  ⚠️  Error reading {h5_file.name}: {e}")
    
    print(f"📊 H5 files contain {minus_999_templates_in_h5} templates with -999.0 age out of {total_templates_in_h5} total templates")
    
    return minus_999_templates_in_h5 > 0

def main():
    """Main function to check template filtering."""
    print("=" * 80)
    print("🔍 SNID SAGE - Template Filtering Check")
    print("=" * 80)
    
    # Check template index
    index_has_issues = check_template_index()
    
    # Check original template files
    minus_999_files = check_original_template_files()
    
    # Check H5 files
    h5_has_issues = check_h5_files()
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    
    if index_has_issues or h5_has_issues:
        print("❌ FILTERING ISSUES DETECTED:")
        print("   - Templates with -999.0 age are still present in H5 storage")
        print("   - The filtering logic is not working correctly")
        print("   - Need to rebuild template storage with proper filtering")
        print("\n💡 SOLUTION:")
        print("   Run: python scripts/rebuild_template_storage.py --force")
        return 1
    else:
        print("✅ FILTERING WORKING CORRECTLY:")
        print("   - No templates with -999.0 age found in H5 storage")
        print("   - All invalid templates have been properly filtered out")
        return 0

if __name__ == '__main__':
    sys.exit(main()) 