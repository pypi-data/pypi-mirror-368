#!/usr/bin/env python3
"""
SNID SAGE Command Line Interface
================================

Main entry point for the SNID SAGE CLI application.
This provides comprehensive command-line access to SNID SAGE functionality.

Version 1.0.0 - Developed by Fiorenzo Stoppa
Based on the original Fortran SNID by Stéphane Blondin & John L. Tonry
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List

# Import the core SNID functionality
from snid_sage.snid.snid import run_snid
import snid_sage.interfaces.cli.identify as identify_module
import snid_sage.interfaces.cli.template as template_module
import snid_sage.interfaces.cli.batch as batch_module
import snid_sage.interfaces.cli.config as config_module

# Import version
try:
    from snid_sage import __version__
except ImportError:
    __version__ = "unknown"


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="SNID SAGE: SuperNova IDentification with Spectrum Analysis and Guided Enhancement",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Developed by Fiorenzo Stoppa, based on the original Fortran SNID by Stéphane Blondin & John L. Tonry"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"SNID SAGE v{__version__}"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command", 
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Identify command (main SNID functionality)
    identify_parser = subparsers.add_parser(
        "identify", 
        help="Identify supernova spectrum",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    identify_module.add_arguments(identify_parser)
    
    # Template management commands
    template_parser = subparsers.add_parser(
        "template", 
        help="Manage template libraries",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    template_module.add_arguments(template_parser)
    
    # Batch processing commands
    batch_parser = subparsers.add_parser(
        "batch", 
        help="Batch process multiple spectra",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    batch_module.add_arguments(batch_parser)
    
    # Configuration commands
    config_parser = subparsers.add_parser(
        "config", 
        help="Manage SNID SAGE configuration",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    config_module.add_arguments(config_parser)
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('-o', '--output-dir',
                       help='Output directory for results')
    output_group.add_argument('--output-main', action='store_true',
                       help='Generate main output file')
    output_group.add_argument('--output-fluxed', action='store_true',
                       help='Generate fluxed spectrum file')
    output_group.add_argument('--output-flattened', action='store_true',
                       help='Generate flattened spectrum file')
    output_group.add_argument('--output-correlation', action='store_true',
                       help='Generate correlation data files for templates')
    output_group.add_argument('--output-plots', action='store_true',
                       help='Generate plots for all templates')
    output_group.add_argument('--plot-types', nargs='+', 
                       choices=['flux', 'flat', 'all'],
                       default=['flux'],
                       help='Types of plots to generate')
    output_group.add_argument('--max-templates', type=int, default=5,
                       help='Maximum number of templates for data output')
    output_group.add_argument('--max-plot-templates', type=int, default=20,
                       help='Maximum number of templates for plot generation')
    output_group.add_argument('--plot-figsize', nargs=2, type=int, default=[10, 8],
                       help='Figure size for plots in inches [width height]')
    output_group.add_argument('--plot-dpi', type=int, default=150,
                       help='DPI for saved plots')
    
    # Plotting options
    plot_group = parser.add_argument_group('Plotting Options')
    plot_group.add_argument('--show-plots', action='store_true',
                     help='Display plots during analysis')
    plot_group.add_argument('--save-plots', action='store_true',
                     help='Save plots to files')
    plot_group.add_argument('--plot-dir',
                     help='Directory for saving plots')
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    if argv is None:
        argv = sys.argv[1:]
    
    parser = create_parser()
    
    # If no arguments provided, show help
    if not argv:
        parser.print_help()
        return 0
    
    # Special case: if first argument looks like a spectrum file, 
    # assume it's the legacy "identify" command
    if len(argv) >= 2 and not argv[0].startswith('-') and argv[0] not in ['identify', 'template', 'batch', 'config']:
        # Legacy mode: snid spectrum.dat templates/
        argv = ['identify'] + argv
    
    args = parser.parse_args(argv)
    
    try:
        if args.command == "identify":
            return identify_module.main(args)
        elif args.command == "template":
            return template_module.main(args)
        elif args.command == "batch":
            return batch_module.main(args)
        elif args.command == "config":
            return config_module.main(args)
        else:
            parser.print_help()
            return 0
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 