"""
SNID SAGE GUI Launcher
======================

This module provides the entry point for launching the SNID SAGE GUI.
Only supports PySide6/Qt backend for modern cross-platform interface.
"""

import os
import sys

# CRITICAL: Set environment variables for PySide6 backend and WSL compatibility
# This must be set before any GUI imports happen
os.environ['SNID_SAGE_GUI_BACKEND'] = 'PySide6'

# Comprehensive Qt software rendering for WSL/Linux compatibility
os.environ['QT_OPENGL'] = 'software'
os.environ['QT_QUICK_BACKEND'] = 'software'
os.environ['QT_XCB_FORCE_SOFTWARE_OPENGL'] = '1'
os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
os.environ['QT_DEBUG_PLUGINS'] = '0'
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.gl.debug=false'

# Suppress Qt WM_ACTIVATEAPP warnings and other non-critical messages
os.environ['QT_LOGGING_RULES'] += ';qt.qpa.windows.debug=false;*.debug=false'
os.environ['QT_QUIET_WINDOWS_WARNINGS'] = '1'

import argparse

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="SNID SAGE GUI")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    parser.add_argument("--silent", "-s", action="store_true", help="Silent mode")
    
    # Check environment variables for defaults
    args = parser.parse_args()
    
    if os.environ.get('SNID_DEBUG', '').lower() in ('1', 'true', 'yes'):
        args.debug = True
        args.verbose = True
    elif os.environ.get('SNID_VERBOSE', '').lower() in ('1', 'true', 'yes'):
        args.verbose = True
    elif os.environ.get('SNID_QUIET', '').lower() in ('1', 'true', 'yes'):
        args.quiet = True
    
    return args

def launch_pyside6_gui(args=None):
    """Launch PySide6 GUI"""
    try:
        if args and args.verbose:
            print("Launching SNID SAGE PySide6 GUI...")
        
        # Import PySide6 GUI
        from snid_sage.interfaces.gui.pyside6_gui import main as pyside6_main
        
        if args and args.verbose:
            print("✅ PySide6 GUI loaded successfully")
        
        return pyside6_main(args)
        
    except ImportError as e:
        print(f"❌ PySide6 not available: {e}")
        print("💡 Install PySide6 with: pip install PySide6 pyqtgraph")
        return 1
    except Exception as e:
        print(f"❌ Error launching PySide6 GUI: {e}")
        return 1

def main():
    """
    Main entry point for snid-sage and snid-gui commands
    
    Only supports PySide6 (modern Qt interface) for cross-platform compatibility.
    """
    args = parse_arguments()
    
    if args.verbose:
        print("🎯 Using PySide6/Qt GUI backend")
    
    return launch_pyside6_gui(args)

def main_with_args():
    """
    Alternative entry point that accepts command line arguments
    """
    try:
        return main()
        
    except Exception as e:
        print(f"❌ Error launching SNID SAGE GUI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 