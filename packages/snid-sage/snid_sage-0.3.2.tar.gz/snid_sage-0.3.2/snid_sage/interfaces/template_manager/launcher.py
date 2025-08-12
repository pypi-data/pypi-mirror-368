"""
SNID Template Manager Launcher
=============================

Launcher script for the Template Manager GUI.
"""

import sys
import logging
from PySide6 import QtWidgets, QtCore

from .main_window import SNIDTemplateManagerGUI

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('template_manager.launcher')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('template_manager.launcher')


def setup_logging():
    """Setup logging for the template manager"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('template_manager.log')
        ]
    )


def main():
    """Main function to run the template manager GUI"""
    # Setup logging
    setup_logging()
    _LOGGER.info("Starting SNID Template Manager")
    
    # Create QApplication
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("SNID Template Manager")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("SNID SAGE")
    app.setOrganizationDomain("snid-sage.org")
    
    # Set application properties
    app.setQuitOnLastWindowClosed(True)
    
    try:
        # Create and show the main window
        window = SNIDTemplateManagerGUI()
        window.show()
        
        _LOGGER.info("Template Manager started successfully")
        
        # Run the application
        return app.exec()
        
    except Exception as e:
        _LOGGER.error(f"Error starting Template Manager: {e}")
        QtWidgets.QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start Template Manager:\n\n{str(e)}\n\nCheck the log file for details."
        )
        return 1
    finally:
        _LOGGER.info("Template Manager shutting down")


if __name__ == "__main__":
    sys.exit(main())