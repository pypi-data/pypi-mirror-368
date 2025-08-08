"""
GUI Components Package

This package contains reusable GUI components organized by functionality.
"""

# Import plot components
from .plots import SpectrumPlotter

# Import dialog components
# Old tkinter dialogs moved to OLD_ - use PySide6 versions instead
# from .dialogs import MaskManagerDialog, AISummaryDialog

# Import analysis components
from .analysis import AnalysisPlotter

__all__ = ['SpectrumPlotter', 'MaskManagerDialog', 'AISummaryDialog', 'AnalysisPlotter'] 
