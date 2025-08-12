#!/usr/bin/env python3
"""
SNID Template Manager - Standalone Launcher
==========================================

Standalone launcher for the SNID Template Manager GUI.
This file can be run directly to start the Template Manager.

Usage:
    python template_manager_launcher.py

Requirements:
    - PySide6
    - PyQtGraph (optional, for plotting)
    - NumPy
    - H5PY (optional, for template data loading)
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Main launcher function"""
    try:
        # Import the template manager launcher
        from snid_sage.interfaces.template_manager import main as template_manager_main
        
        # Run the template manager
        return template_manager_main()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nMake sure you have the required dependencies installed:")
        print("  pip install PySide6 pyqtgraph numpy h5py")
        print("\nAlso ensure you're running from the correct directory.")
        return 1
    
    except Exception as e:
        print(f"Error starting Template Manager: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())