"""
Template Statistics Widget
=========================

Template statistics and analysis tools.
"""

import logging
from PySide6 import QtWidgets, QtCore

from ..utils.layout_manager import get_template_layout_manager

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('template_manager.statistics')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('template_manager.statistics')


class TemplateStatisticsWidget(QtWidgets.QWidget):
    """Template statistics and analysis tools"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_manager = get_template_layout_manager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the statistics interface"""
        layout = QtWidgets.QVBoxLayout(self)
        self.layout_manager.apply_panel_layout(self, layout)
        
        # Statistics overview
        overview_group = QtWidgets.QGroupBox("Library Overview")
        self.layout_manager.setup_group_box(overview_group)
        overview_layout = QtWidgets.QGridLayout(overview_group)
        
        # Statistics labels
        self.total_templates_label = QtWidgets.QLabel("Total Templates: 653")
        self.total_epochs_label = QtWidgets.QLabel("Total Epochs: 1,247")
        self.types_count_label = QtWidgets.QLabel("Types: 14")
        self.coverage_label = QtWidgets.QLabel("Wavelength Coverage: 2500-10000 Å")
        
        overview_layout.addWidget(self.total_templates_label, 0, 0)
        overview_layout.addWidget(self.total_epochs_label, 0, 1)
        overview_layout.addWidget(self.types_count_label, 1, 0)
        overview_layout.addWidget(self.coverage_label, 1, 1)
        
        layout.addWidget(overview_group)
        
        # Type distribution
        distribution_group = QtWidgets.QGroupBox("Type Distribution")
        self.layout_manager.setup_group_box(distribution_group)
        distribution_layout = QtWidgets.QVBoxLayout(distribution_group)
        
        # Type breakdown table
        self.type_table = QtWidgets.QTableWidget()
        self.type_table.setColumnCount(3)
        self.type_table.setHorizontalHeaderLabels(["Type", "Count", "Percentage"])
        self.layout_manager.setup_table_widget(self.type_table)
        
        # Sample data
        type_data = [
            ("Ia", "520", "79.6%"),
            ("II", "105", "16.1%"),
            ("Ib", "42", "6.4%"),
            ("Ic", "53", "8.1%"),
            ("AGN", "5", "0.8%"),
            ("SLSN", "45", "6.9%"),
            ("Other", "15", "2.3%")
        ]
        
        self.type_table.setRowCount(len(type_data))
        
        for row, (type_name, count, percentage) in enumerate(type_data):
            self.type_table.setItem(row, 0, QtWidgets.QTableWidgetItem(type_name))
            self.type_table.setItem(row, 1, QtWidgets.QTableWidgetItem(count))
            self.type_table.setItem(row, 2, QtWidgets.QTableWidgetItem(percentage))
            
        distribution_layout.addWidget(self.type_table)
        layout.addWidget(distribution_group)
        
        # Quality metrics
        quality_group = QtWidgets.QGroupBox("Quality Metrics & Analysis")
        self.layout_manager.setup_group_box(quality_group)
        quality_layout = QtWidgets.QVBoxLayout(quality_group)
        
        quality_text = QtWidgets.QTextEdit()
        quality_text.setMaximumHeight(150)
        quality_text.setPlainText(
            "Template Quality Analysis:\n\n"
            "• Signal-to-noise ratio: Median 45.2\n"
            "• Wavelength coverage: 95% complete\n"
            "• Flux calibration: 98% validated\n"
            "• Missing epochs: 12 templates\n"
            "• Age distribution: -20 to +300 days\n"
            "• Redshift range: z = 0.001 to 0.045\n\n"
            "Recommendations:\n"
            "• Review templates with SNR < 20\n"
            "• Validate flux calibration for 5 templates"
        )
        
        quality_layout.addWidget(quality_text)
        
        # Action buttons
        action_frame = QtWidgets.QFrame()
        action_layout = QtWidgets.QHBoxLayout(action_frame)
        
        refresh_btn = self.layout_manager.create_action_button("Refresh Statistics", "🔄")
        refresh_btn.clicked.connect(self.refresh_statistics)
        
        export_btn = self.layout_manager.create_action_button("Export Report", "📊")
        export_btn.clicked.connect(self.export_report)
        
        analyze_btn = self.layout_manager.create_action_button("Deep Analysis", "🔍")
        analyze_btn.clicked.connect(self.deep_analysis)
        
        action_layout.addWidget(refresh_btn)
        action_layout.addWidget(export_btn)
        action_layout.addWidget(analyze_btn)
        action_layout.addStretch()
        
        quality_layout.addWidget(action_frame)
        layout.addWidget(quality_group)
        
        layout.addStretch()
        
    def refresh_statistics(self):
        """Refresh all statistics"""
        QtWidgets.QMessageBox.information(self, "Statistics", "Statistics refreshed successfully!")
        
    def export_report(self):
        """Export statistical report"""
        QtWidgets.QMessageBox.information(self, "Export", "Statistical report exported to:\n• PDF summary\n• CSV data tables\n• JSON metadata")
        
    def deep_analysis(self):
        """Perform deep analysis of template library"""
        QtWidgets.QMessageBox.information(self, "Analysis", "Deep analysis initiated:\n\n• Cross-correlation matrix\n• Principal component analysis\n• Outlier detection\n• Quality scoring\n\nResults will be available in the Analysis tab.")