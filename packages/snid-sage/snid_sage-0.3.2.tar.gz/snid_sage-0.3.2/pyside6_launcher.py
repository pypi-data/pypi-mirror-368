#!/usr/bin/env python3
"""
PySide6 SNID SAGE GUI Launcher
==============================

Proper launcher for the full PySide6 SNID SAGE GUI interface.
This launcher imports and uses the complete PySide6SNIDSageGUI class.

Usage:
    python pyside6_launcher.py

Features:
- Complete PySide6 SNID SAGE GUI
- Full workflow management
- All analysis features
- Modern Qt interface
"""

import sys
import os
from pathlib import Path

# Set environment early to prevent backend conflicts and ensure WSL compatibility
os.environ['SNID_SAGE_GUI_BACKEND'] = 'PySide6'

# Comprehensive Qt software rendering for WSL/Linux compatibility
os.environ['QT_OPENGL'] = 'software'
os.environ['QT_QUICK_BACKEND'] = 'software'
os.environ['QT_XCB_FORCE_SOFTWARE_OPENGL'] = '1'
os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
os.environ['QT_DEBUG_PLUGINS'] = '0'
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.gl.debug=false'

# Add the project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Essential SNID imports
try:
    from snid_sage import __version__
except ImportError:
    __version__ = "unknown"

# Logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_launcher')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_launcher')


def main():
    """Main application entry point"""
    try:
        # Import the proper PySide6 GUI
        from snid_sage.interfaces.gui.pyside6_gui import main as pyside6_main
        
        _LOGGER.info("Launching PySide6 SNID SAGE GUI...")
        
        # Run the main PySide6 GUI
        return pyside6_main()
        
    except ImportError as e:
        _LOGGER.error(f"Failed to import PySide6 GUI: {e}")
        print(f"❌ Failed to import PySide6 GUI: {e}")
        print("💡 Install PySide6 with: pip install PySide6 pyqtgraph")
        return 1
    except Exception as e:
        _LOGGER.error(f"Error launching PySide6 GUI: {e}")
        print(f"❌ Error launching PySide6 GUI: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 