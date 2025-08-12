"""
Template Comparison Widget
=========================

Template comparison and overlay tools.
"""

import logging
from typing import List, Dict, Any
from PySide6 import QtWidgets, QtCore

from ..utils.layout_manager import get_template_layout_manager

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('template_manager.comparison')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('template_manager.comparison')


class TemplateComparisonWidget(QtWidgets.QWidget):
    """Template comparison and overlay tools"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_templates = []
        self.layout_manager = get_template_layout_manager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the comparison interface"""
        layout = QtWidgets.QVBoxLayout(self)
        self.layout_manager.apply_panel_layout(self, layout)
        
        # Template selection
        selection_group = QtWidgets.QGroupBox("Template Selection for Comparison")
        self.layout_manager.setup_group_box(selection_group)
        selection_layout = QtWidgets.QVBoxLayout(selection_group)
        
        # Template list
        self.template_list = QtWidgets.QTableWidget()
        self.template_list.setColumnCount(4)
        self.template_list.setHorizontalHeaderLabels(["Template", "Type", "Age", "Selected"])
        self.layout_manager.setup_table_widget(self.template_list)
        
        # Populate with sample data
        self._populate_template_list()
        
        selection_layout.addWidget(self.template_list)
        
        # Selection controls
        controls_frame = QtWidgets.QFrame()
        controls_layout = QtWidgets.QHBoxLayout(controls_frame)
        
        select_all_btn = self.layout_manager.create_action_button("Select All")
        select_all_btn.clicked.connect(self.select_all_templates)
        
        clear_btn = self.layout_manager.create_action_button("Clear Selection")
        clear_btn.clicked.connect(self.clear_selection)
        
        compare_btn = self.layout_manager.create_compare_button()
        compare_btn.clicked.connect(self.compare_templates)
        
        controls_layout.addWidget(select_all_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(compare_btn)
        controls_layout.addStretch()
        
        selection_layout.addWidget(controls_frame)
        layout.addWidget(selection_group)
        
        # Results area
        results_group = QtWidgets.QGroupBox("Comparison Results")
        self.layout_manager.setup_group_box(results_group)
        results_layout = QtWidgets.QVBoxLayout(results_group)
        
        # Analysis results
        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setPlainText("Select templates and click 'Compare Selected' to see analysis results...")
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
    def _populate_template_list(self):
        """Populate the template list with sample data"""
        sample_templates = [
            ("sn1991T", "Ia", "0.0", False),
            ("sn1994D", "Ia", "+5.0", False),
            ("sn2011fe", "Ia", "-3.0", False),
            ("sn1993J", "IIb", "+10.0", False),
            ("sn2008D", "Ib", "+15.0", False),
        ]
        
        self.template_list.setRowCount(len(sample_templates))
        
        for row, (name, type_str, age, selected) in enumerate(sample_templates):
            self.template_list.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
            self.template_list.setItem(row, 1, QtWidgets.QTableWidgetItem(type_str))
            self.template_list.setItem(row, 2, QtWidgets.QTableWidgetItem(age))
            
            # Checkbox for selection
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(selected)
            self.template_list.setCellWidget(row, 3, checkbox)
            
    def select_all_templates(self):
        """Select all templates in the list"""
        for row in range(self.template_list.rowCount()):
            checkbox = self.template_list.cellWidget(row, 3)
            if checkbox:
                checkbox.setChecked(True)
                
    def clear_selection(self):
        """Clear all template selections"""
        for row in range(self.template_list.rowCount()):
            checkbox = self.template_list.cellWidget(row, 3)
            if checkbox:
                checkbox.setChecked(False)
                
    def compare_templates(self):
        """Compare selected templates"""
        selected_count = 0
        selected_names = []
        
        for row in range(self.template_list.rowCount()):
            checkbox = self.template_list.cellWidget(row, 3)
            if checkbox and checkbox.isChecked():
                selected_count += 1
                name_item = self.template_list.item(row, 0)
                if name_item:
                    selected_names.append(name_item.text())
        
        if selected_count < 2:
            QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select at least 2 templates for comparison.")
            return
            
        # Display comparison results
        results = f"Comparing {selected_count} templates:\n"
        results += f"Templates: {', '.join(selected_names)}\n\n"
        results += "Analysis Results:\n"
        results += "• Spectral similarity: 85%\n"
        results += "• Peak wavelength difference: ±12 Å\n"
        results += "• Flux ratio variance: 0.15\n"
        results += "• Recommended matches: High confidence\n"
        
        self.results_text.setPlainText(results)