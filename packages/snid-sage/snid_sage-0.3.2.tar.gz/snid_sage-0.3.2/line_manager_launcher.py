"""
Top-level launcher for the SNID Line Manager GUI.
"""

import sys
from PySide6 import QtWidgets

from snid_sage.interfaces.line_manager.launcher import SNIDLineManagerGUI


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SNIDLineManagerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


