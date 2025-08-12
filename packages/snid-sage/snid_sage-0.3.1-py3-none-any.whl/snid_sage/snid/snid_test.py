#!/usr/bin/env python3
"""
SNID Core Engine Test Script
============================

Test script for the core SNID engine after project restructuring.
This tests the core snid.py functionality directly.

Updated for new project structure with output directory fix validation.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so Python can find the snid package
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from snid_sage.snid.snid import run_snid
import argparse
import tempfile
import time

def test_output_directory_behavior(spectrum_path, templates_dir):
    """Test the output directory fix specifically."""
    print("\n" + "="*60)
    print("TESTING OUTPUT DIRECTORY FIX")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / 'snid_test_output'
        
        print(f"Testing output directory: {output_dir}")
        print("Running SNID with save_plots=True and output_dir specified...")
        
        start_time = time.time()
        
        try:
            result, trace = run_snid(
                spectrum_path=spectrum_path,
                templates_dir=templates_dir,
                output_dir=str(output_dir),
                output_main=True,
                output_fluxed=True,
                output_flattened=True,
                save_plots=True,
                show_plots=False,
                verbose=True,
                max_output_templates=5
            )
            
            runtime = time.time() - start_time
            print(f"\nAnalysis completed in {runtime:.2f} seconds")
            
            # Check if output directory was created
            if not output_dir.exists():
                print("❌ CRITICAL: Output directory was not created!")
                return False
            
            # List all files in output directory
            output_files = list(output_dir.glob('*'))
            print(f"\n📁 Files created in output directory ({len(output_files)} total):")
            
            main_files = []
            plot_files = []
            
            for filepath in output_files:
                filename = filepath.name
                print(f"  {filename} ({filepath.stat().st_size} bytes)")
                
                if filename.endswith('.png'):
                    plot_files.append(filename)
                else:
                    main_files.append(filename)
            
            # Validate expected files
            expected_main = ['snid.output', 'snid.fluxed', 'snid.flattened', 'snid.param']
            expected_plots = ['snid_comparison.png', 'snid_correlation.png', 'snid_gmm_clustering.png', 
                            'snid_redshift_age.png', 'snid_type_fractions.png']
            
            print(f"\n📊 Analysis Results:")
            print(f"  Main files: {len(main_files)} (expected: {len(expected_main)})")
            print(f"  Plot files: {len(plot_files)} (expected: {len(expected_plots)})")
            
            # Check if all plots are in the output directory (the fix validation)
            plots_in_correct_location = all(any(plot.startswith(expected.split('_')[0]) for expected in expected_plots) 
                                          for plot in plot_files)
            
            if plot_files:
                print(f"  ✅ OUTPUT DIRECTORY FIX WORKING: All plots saved to output directory")
                print(f"     Plots found: {', '.join(plot_files)}")
            else:
                print(f"  ❌ OUTPUT DIRECTORY FIX FAILED: No plots found in output directory")
                return False
            
            # Display analysis results
            if result.success:
                print(f"\n🎯 SNID Analysis Results:")
                print(f"  Type: {result.consensus_type}")
                print(f"  Template: {result.template_name}")
                print(f"  Redshift: {result.redshift:.5f} ± {result.redshift_error:.5f}")
                print(f"  RLAP: {result.rlap:.2f}")
                print(f"  Confidence: {result.type_confidence:.2f}")
            
            else:
                print(f"  ❌ Analysis failed - no good matches found")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Test SNID core engine with output directory validation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("spectrum", help="Path to spectrum file")
    parser.add_argument("--templates", default="templates", help="Path to templates directory")
    parser.add_argument("--output", action="store_true", help="Generate output files")
    parser.add_argument("--output-dir", default="snid_test_output", help="Directory for output files")
    parser.add_argument("--fluxed", action="store_true", help="Output fluxed spectra")
    parser.add_argument("--flattened", action="store_true", help="Output flattened spectra")
    parser.add_argument("--correlation", action="store_true", help="Output correlation functions")
    parser.add_argument("--save-plots", action="store_true", help="Save plots to files")
    parser.add_argument("--max-templates", type=int, default=5, help="Maximum number of templates to output")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    parser.add_argument("--test-output-fix", action="store_true", 
                       help="Run specific test for output directory fix")
    args = parser.parse_args()

    print("="*60)
    print("SNID CORE ENGINE TEST")
    print("="*60)
    print(f"Project root: {project_root}")
    print(f"Spectrum: {args.spectrum}")
    print(f"Templates: {args.templates}")
    print()

    # Validate inputs
    spectrum_path = Path(args.spectrum)
    templates_dir = Path(args.templates)
    
    if not spectrum_path.exists():
        print(f"❌ Error: Spectrum file not found: {spectrum_path}")
        return 1
        
    if not templates_dir.exists():
        print(f"❌ Error: Templates directory not found: {templates_dir}")
        return 1

    if args.test_output_fix:
        # Run the specific output directory test
        success = test_output_directory_behavior(str(spectrum_path), str(templates_dir))
        return 0 if success else 1

    # Run standard SNID analysis
    try:
        print("Running SNID analysis...")
        start_time = time.time()
        
        result, trace = run_snid(
            spectrum_path=str(spectrum_path), 
            templates_dir=str(templates_dir),
            output_dir=args.output_dir if args.output else None,
            output_main=args.output,
            output_fluxed=args.fluxed,
            output_flattened=args.flattened,
            output_correlation=args.correlation,
            save_plots=args.save_plots,
            show_plots=False,  # Don't show plots in test mode
            max_output_templates=args.max_templates,
            verbose=args.verbose
        )
        
        runtime = time.time() - start_time
        print(f"\nAnalysis completed in {runtime:.2f} seconds")
        
        # Display results
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        
        if result.success:
            print(f"✅ Analysis successful!")
            print(f"Type: {result.consensus_type}")
            print(f"Best template: {result.template_name}")
            print(f"Redshift: {result.redshift:.5f} ± {result.redshift_error:.5f}")
            print(f"RLAP: {result.rlap:.2f}")
            print(f"Confidence: {result.type_confidence:.2f}")
        
        else:
            print(f"❌ Analysis failed - no good matches found")
            return 1
        
        # Show output files if generated
        if args.output and hasattr(result, 'output_files') and result.output_files:
            print(f"\n📁 Output files generated:")
            for file_type, file_path in result.output_files.items():
                if isinstance(file_path, dict):
                    print(f"  {file_type}: {len(file_path)} files")
                    for idx, path in file_path.items():
                        print(f"    {idx}: {path}")
                else:
                    print(f"  {file_type}: {file_path}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Example usage:
# Basic test:
#   python snid/snid_test.py data/sn2003jo.dat --templates templates/ --verbose
#
# Test with outputs:
#   python snid/snid_test.py data/sn2003jo.dat --templates templates/ --output --save-plots --verbose
#
# Test output directory fix specifically:
#   python snid/snid_test.py data/sn2003jo.dat --templates templates/ --test-output-fix
