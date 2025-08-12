"""
SNID Template Command
====================

Command for managing SNID template libraries.
"""

import argparse
import sys
import os
import glob
from pathlib import Path
from typing import Optional, List

# Import the IO functions directly since template_manager has issues
from snid_sage.snid.io import (
    read_template, get_template_info, create_template_library,
    add_template, remove_template, merge_template_libraries
)


def list_templates_func(args):
    """List templates in a library."""
    library_path = args.library
    
    if not os.path.exists(library_path):
        print(f"Error: Template library not found: {library_path}", file=sys.stderr)
        return 1
    
    # Check if it's a directory with HDF5 files or individual .lnw files
    if os.path.isdir(library_path):
        # Look for HDF5 template files
        hdf5_files = glob.glob(os.path.join(library_path, "templates_*.hdf5"))
        lnw_files = glob.glob(os.path.join(library_path, "*.lnw"))
        
        if hdf5_files:
            print(f"\nTemplate Library: {os.path.basename(library_path)}")
            print(f"Path: {library_path}")
            print(f"Format: HDF5 template libraries")
            print(f"Template libraries: {len(hdf5_files)}")
            
            if args.verbose:
                print("\nTemplate Libraries:")
                for hdf5_file in sorted(hdf5_files):
                    basename = os.path.basename(hdf5_file)
                    # Extract type from filename (templates_TYPE.hdf5)
                    template_type = basename.replace('templates_', '').replace('.hdf5', '')
                    print(f"  {basename} (Type: {template_type})")
                    
                    # Try to get template count from HDF5 file
                    try:
                        import h5py
                        with h5py.File(hdf5_file, 'r') as f:
                            if 'templates' in f:
                                template_count = len(f['templates'].keys())
                                print(f"    Contains {template_count} templates")
                    except ImportError:
                        print(f"    (h5py not available - cannot count templates)")
                    except Exception as e:
                        print(f"    (Error reading file: {e})")
                        
        elif lnw_files:
            # Original .lnw file handling
            print(f"\nTemplate Library: {os.path.basename(library_path)}")
            print(f"Path: {library_path}")
            print(f"Format: Individual .lnw files")
            print(f"Total templates: {len(lnw_files)}")
            
            if args.verbose and lnw_files:
                print("\nTemplates:")
                for template_file in sorted(lnw_files):
                    try:
                        template = read_template(template_file)
                        name = template.get('name', os.path.basename(template_file))
                        t_type = template.get('type', 'Unknown')
                        subtype = template.get('subtype', 'Unknown')
                        age = template.get('age', None)
                        age_str = f", Age: {age:.1f}" if age is not None else ""
                        print(f"  {name} ({t_type}/{subtype}{age_str})")
                    except Exception as e:
                        print(f"  {os.path.basename(template_file)} (Error reading: {e})")
        else:
            print(f"No template files found in {library_path}")
            print("Expected: templates_*.hdf5 files or *.lnw files")
            return 1
    else:
        print(f"Error: {library_path} is not a directory", file=sys.stderr)
        return 1
    
    return 0


def create_library_func(args):
    """Create a new template library."""
    try:
        library_path = create_template_library(args.output_dir, args.name)
        print(f"\nCreated template library:")
        print(f"  Name: {args.name}")
        print(f"  Path: {library_path}")
        return 0
    except Exception as e:
        print(f"Error creating library: {e}", file=sys.stderr)
        return 1


def add_templates_func(args):
    """Add templates to a library."""
    library_path = args.library
    
    if not os.path.exists(library_path):
        if args.create:
            try:
                library_path = create_template_library(
                    os.path.dirname(library_path) if os.path.dirname(library_path) else ".",
                    os.path.basename(library_path)
                )
                print(f"Created new template library: {library_path}")
            except Exception as e:
                print(f"Error creating library: {e}", file=sys.stderr)
                return 1
        else:
            print(f"Error: Template library not found: {library_path}", file=sys.stderr)
            return 1
    
    # Get list of files to add
    files_to_add = []
    for pattern in args.files:
        matched_files = glob.glob(pattern)
        if not matched_files:
            print(f"Warning: No files match pattern: {pattern}")
        files_to_add.extend(matched_files)
    
    if not files_to_add:
        print("Error: No files to add", file=sys.stderr)
        return 1
    
    # Add templates
    added_count = 0
    for file_path in files_to_add:
        try:
            # Parse type, subtype, age from filename if not specified
            basename = os.path.basename(file_path)
            name_parts = os.path.splitext(basename)[0].split('_')
            
            template_info = {
                'name': name_parts[0],
                'type': args.type if args.type else (name_parts[1] if len(name_parts) > 1 else "Unknown"),
                'subtype': args.subtype if args.subtype else (name_parts[2] if len(name_parts) > 2 else "Unknown"),
                'flatten': not args.no_flatten
            }
            
            if args.age is not None:
                template_info['age'] = args.age
            elif len(name_parts) > 3:
                try:
                    template_info['age'] = float(name_parts[3])
                except ValueError:
                    pass
            
            # Add template
            template_file = add_template(
                library_path, 
                file_path, 
                template_info,
                force_rebin=args.force_rebin
            )
            
            print(f"Added template: {os.path.basename(template_file)}")
            added_count += 1
            
        except Exception as e:
            print(f"Error adding template {file_path}: {e}")
    
    print(f"\nAdded {added_count} templates to {library_path}")
    return 0


def remove_templates_func(args):
    """Remove templates from a library."""
    library_path = args.library
    
    if not os.path.exists(library_path):
        print(f"Error: Template library not found: {library_path}", file=sys.stderr)
        return 1
    
    removed_count = 0
    for template_name in args.patterns:
        try:
            if args.dry_run:
                template_file = os.path.join(library_path, f"{template_name}.lnw")
                if os.path.exists(template_file):
                    print(f"Would remove: {template_name}")
                    removed_count += 1
                else:
                    print(f"Template not found: {template_name}")
            else:
                success = remove_template(library_path, template_name)
                if success:
                    print(f"Removed template: {template_name}")
                    removed_count += 1
                else:
                    print(f"Template not found: {template_name}")
                    
        except Exception as e:
            print(f"Error removing template {template_name}: {e}")
    
    if not args.dry_run:
        print(f"\nRemoved {removed_count} templates from {library_path}")
    else:
        print(f"\nWould remove {removed_count} templates from {library_path}")
    
    return 0


def merge_libraries_func(args):
    """Merge multiple template libraries."""
    for lib_path in args.libraries:
        if not os.path.exists(lib_path):
            print(f"Error: Template library not found: {lib_path}", file=sys.stderr)
            return 1
    
    try:
        merged_path = merge_template_libraries(
            os.path.dirname(args.output), 
            args.libraries, 
            os.path.basename(args.output)
        )
        
        # Count templates in merged library
        template_files = glob.glob(os.path.join(merged_path, "*.lnw"))
        
        print(f"\nMerged {len(args.libraries)} libraries into {merged_path}")
        print(f"Total templates: {len(template_files)}")
        return 0
    except Exception as e:
        print(f"Error merging libraries: {e}", file=sys.stderr)
        return 1


def visualize_templates_func(args):
    """Visualize templates in a library."""
    print("Template visualization not yet implemented.")
    return 0


def convert_spectrum_func(args):
    """Convert spectrum to template format."""
    print("Spectrum conversion not yet implemented.")
    return 0


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the template command."""
    subparsers = parser.add_subparsers(
        dest="template_command", 
        help="Template management commands",
        metavar="SUBCOMMAND"
    )
    
    # List templates command
    list_parser = subparsers.add_parser(
        'list', 
        help='List templates in a library'
    )
    list_parser.add_argument(
        'library', 
        help='Path to template library'
    )
    list_parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='Show detailed information'
    )
    
    # Create library command
    create_parser = subparsers.add_parser(
        'create', 
        help='Create a new template library'
    )
    create_parser.add_argument(
        'name', 
        help='Name of the template library'
    )
    create_parser.add_argument(
        '-o', '--output-dir', 
        help='Output directory', 
        default='.'
    )
    
    # Add templates command
    add_parser = subparsers.add_parser(
        'add', 
        help='Add templates to a library'
    )
    add_parser.add_argument(
        'library', 
        help='Path to template library'
    )
    add_parser.add_argument(
        'files', 
        nargs='+', 
        help='Files to add as templates (supports wildcards)'
    )
    add_parser.add_argument(
        '-t', '--type', 
        help='SN type for the templates'
    )
    add_parser.add_argument(
        '-s', '--subtype', 
        help='SN subtype for the templates'
    )
    add_parser.add_argument(
        '-a', '--age', 
        type=float, 
        help='SN age in days'
    )
    add_parser.add_argument(
        '--no-flatten', 
        action='store_true', 
        help='Do not flatten the spectra'
    )
    add_parser.add_argument(
        '--force-rebin', 
        action='store_true', 
        help='Force rebinning even for .lnw files'
    )
    add_parser.add_argument(
        '--create', 
        action='store_true', 
        help='Create library if it does not exist'
    )
    
    # Remove templates command
    remove_parser = subparsers.add_parser(
        'remove', 
        help='Remove templates from a library'
    )
    remove_parser.add_argument(
        'library', 
        help='Path to template library'
    )
    remove_parser.add_argument(
        'patterns', 
        nargs='+', 
        help='Template name patterns to remove'
    )
    remove_parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Show what would be removed without actually removing'
    )
    
    # Merge libraries command
    merge_parser = subparsers.add_parser(
        'merge', 
        help='Merge multiple template libraries'
    )
    merge_parser.add_argument(
        'output', 
        help='Output library path'
    )
    merge_parser.add_argument(
        'libraries', 
        nargs='+', 
        help='Input libraries to merge'
    )
    merge_parser.add_argument(
        '--overwrite', 
        action='store_true', 
        help='Overwrite output library if it exists'
    )
    
    # Visualize templates command
    visualize_parser = subparsers.add_parser(
        'visualize', 
        help='Visualize templates in a library'
    )
    visualize_parser.add_argument(
        'library', 
        help='Path to template library'
    )
    visualize_parser.add_argument(
        '-o', '--output', 
        help='Output plot file'
    )
    visualize_parser.add_argument(
        '--type-filter', 
        nargs='+', 
        help='Only show templates of these types'
    )
    visualize_parser.add_argument(
        '--age-range', 
        nargs=2, 
        type=float, 
        metavar=('MIN', 'MAX'),
        help='Age range to display'
    )
    
    # Convert spectrum command
    convert_parser = subparsers.add_parser(
        'convert', 
        help='Convert spectrum to template format'
    )
    convert_parser.add_argument(
        'input', 
        help='Input spectrum file'
    )
    convert_parser.add_argument(
        '-o', '--output', 
        help='Output file'
    )
    convert_parser.add_argument(
        '--flatten', 
        action='store_true', 
        help='Flatten the spectrum'
    )


def main(argv: Optional[List[str]] = None) -> int:
    """Main function for the template command."""
    if argv is None:
        argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        description="SNID Template Management",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    add_arguments(parser)
    
    # If no arguments provided, show help
    if not argv:
        parser.print_help()
        return 0
    
    args = parser.parse_args(argv)
    
    try:
        if args.template_command == "list":
            return list_templates_func(args)
        elif args.template_command == "create":
            return create_library_func(args)
        elif args.template_command == "add":
            return add_templates_func(args)
        elif args.template_command == "remove":
            return remove_templates_func(args)
        elif args.template_command == "merge":
            return merge_libraries_func(args)
        elif args.template_command == "visualize":
            return visualize_templates_func(args)
        elif args.template_command == "convert":
            return convert_spectrum_func(args)
        else:
            print("Error: No template subcommand specified", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1 