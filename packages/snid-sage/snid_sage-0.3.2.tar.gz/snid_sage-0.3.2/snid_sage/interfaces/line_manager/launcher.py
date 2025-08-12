"""
SNID Line Manager Launcher
=========================

Launcher script for the Line Manager GUI.
"""

import sys
from PySide6 import QtWidgets

from .main_window import SNIDLineManagerGUI

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('line_manager.launcher')
except Exception:
    import logging
    _LOGGER = logging.getLogger('line_manager.launcher')


def main():
    _LOGGER.info("Starting SNID Line Manager")
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("SNID Line Manager")
    app.setOrganizationName("SNID SAGE")
    window = SNIDLineManagerGUI()
    window.show()
    rc = app.exec()
    _LOGGER.info("Line Manager shutting down")
    return rc


if __name__ == "__main__":
    sys.exit(main())


