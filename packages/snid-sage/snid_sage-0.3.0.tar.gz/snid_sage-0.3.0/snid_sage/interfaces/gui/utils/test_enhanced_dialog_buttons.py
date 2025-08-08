"""
Test Script for Enhanced Dialog Buttons
=======================================

This script demonstrates the enhanced dialog button system with various button types
and behaviors. Run this to see the button animations and styling in action.

Usage: python test_enhanced_dialog_buttons.py
"""

import sys
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
from typing import Optional

# Import the enhanced button system
try:
    from snid_sage.interfaces.gui.utils.enhanced_dialog_button_manager import EnhancedDialogButtonManager
    from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_buttons
    ENHANCED_BUTTONS_AVAILABLE = True
except ImportError:
    print("Enhanced button system not available - check imports")
    ENHANCED_BUTTONS_AVAILABLE = False


class TestDialogButtonsDialog(QtWidgets.QDialog):
    """Test dialog showcasing enhanced button functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enhanced Dialog Buttons - Test Demo")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        # Test state for toggle button
        self.test_mode = False
        
        self._setup_interface()
        self._setup_enhanced_buttons()
    
    def _setup_interface(self):
        """Create the test interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QtWidgets.QLabel("Enhanced Dialog Button System Demo")
        header.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold))
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("color: #3b82f6; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Description
        desc = QtWidgets.QLabel(
            "This demo showcases the enhanced button system with unified colors, "
            "smooth animations, and consistent sizing. Hover over and click the buttons "
            "to see the enhanced visual feedback."
        )
        desc.setWordWrap(True)
        desc.setAlignment(QtCore.Qt.AlignCenter)
        desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Create button groups
        self._create_action_buttons_group(layout)
        self._create_utility_buttons_group(layout)
        self._create_special_buttons_group(layout)
        self._create_dialog_buttons_group(layout)
    
    def _create_action_buttons_group(self, layout):
        """Create action buttons group"""
        group = QtWidgets.QGroupBox("Action Buttons")
        group_layout = QtWidgets.QGridLayout(group)
        
        # Apply/Continue actions (Green)
        apply_btn = QtWidgets.QPushButton("Apply Settings")
        apply_btn.setObjectName("apply_btn")
        apply_btn.clicked.connect(lambda: self._show_message("Apply", "Green theme for apply/continue actions"))
        group_layout.addWidget(apply_btn, 0, 0)
        
        accept_btn = QtWidgets.QPushButton("Accept Changes")
        accept_btn.setObjectName("accept_btn")
        accept_btn.clicked.connect(lambda: self._show_message("Accept", "Green theme for acceptance actions"))
        group_layout.addWidget(accept_btn, 0, 1)
        
        # Secondary actions (Blue)
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setObjectName("ok_btn")
        ok_btn.clicked.connect(lambda: self._show_message("OK", "Blue theme for secondary confirmations"))
        group_layout.addWidget(ok_btn, 1, 0)
        
        confirm_btn = QtWidgets.QPushButton("Confirm")
        confirm_btn.setObjectName("confirm_btn")
        confirm_btn.clicked.connect(lambda: self._show_message("Confirm", "Blue theme for confirmations"))
        group_layout.addWidget(confirm_btn, 1, 1)
        
        # Cancel/Destructive actions (Red)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(lambda: self._show_message("Cancel", "Red theme for cancel/destructive actions"))
        group_layout.addWidget(cancel_btn, 2, 0)
        
        remove_btn = QtWidgets.QPushButton("Remove Item")
        remove_btn.setObjectName("remove_btn")
        remove_btn.clicked.connect(lambda: self._show_message("Remove", "Red theme for removal actions"))
        group_layout.addWidget(remove_btn, 2, 1)
        
        layout.addWidget(group)
    
    def _create_utility_buttons_group(self, layout):
        """Create utility buttons group"""
        group = QtWidgets.QGroupBox("Utility Buttons")
        group_layout = QtWidgets.QGridLayout(group)
        
        # Export/Save actions (Purple)
        export_btn = QtWidgets.QPushButton("📊 Export Data")
        export_btn.setObjectName("export_btn")
        export_btn.clicked.connect(lambda: self._show_message("Export", "Purple theme for utility actions"))
        group_layout.addWidget(export_btn, 0, 0)
        
        save_btn = QtWidgets.QPushButton("💾 Save Results")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(lambda: self._show_message("Save", "Purple theme for save actions"))
        group_layout.addWidget(save_btn, 0, 1)
        
        # Reset/Refresh actions (Indigo)
        reset_btn = QtWidgets.QPushButton("🔄 Reset to Defaults")
        reset_btn.setObjectName("reset_btn")
        reset_btn.clicked.connect(lambda: self._show_message("Reset", "Indigo theme for reset actions"))
        group_layout.addWidget(reset_btn, 1, 0)
        
        refresh_btn = QtWidgets.QPushButton("Refresh Data")
        refresh_btn.setObjectName("refresh_btn")
        refresh_btn.clicked.connect(lambda: self._show_message("Refresh", "Indigo theme for refresh actions"))
        group_layout.addWidget(refresh_btn, 1, 1)
        
        layout.addWidget(group)
    
    def _create_special_buttons_group(self, layout):
        """Create special buttons group"""
        group = QtWidgets.QGroupBox("Special Buttons")
        group_layout = QtWidgets.QGridLayout(group)
        
        # Info/Help actions (Orange)
        help_btn = QtWidgets.QPushButton("❓ Help")
        help_btn.setObjectName("help_btn")
        help_btn.clicked.connect(lambda: self._show_message("Help", "Orange theme for info/help actions"))
        group_layout.addWidget(help_btn, 0, 0)
        
        info_btn = QtWidgets.QPushButton("ℹ️ Information")
        info_btn.setObjectName("info_btn")
        info_btn.clicked.connect(lambda: self._show_message("Info", "Orange theme for information"))
        group_layout.addWidget(info_btn, 0, 1)
        
        # Navigation actions (Gray)
        prev_btn = QtWidgets.QPushButton("◀ Previous")
        prev_btn.setObjectName("prev_btn")
        prev_btn.clicked.connect(lambda: self._show_message("Previous", "Gray theme for navigation"))
        group_layout.addWidget(prev_btn, 1, 0)
        
        next_btn = QtWidgets.QPushButton("Next ▶")
        next_btn.setObjectName("next_btn")
        next_btn.clicked.connect(lambda: self._show_message("Next", "Gray theme for navigation"))
        group_layout.addWidget(next_btn, 1, 1)
        
        # Toggle button demonstration
        self.toggle_btn = QtWidgets.QPushButton("Mode: Basic")
        self.toggle_btn.setObjectName("toggle_btn")
        group_layout.addWidget(self.toggle_btn, 2, 0, 1, 2)
        
        layout.addWidget(group)
    
    def _create_dialog_buttons_group(self, layout):
        """Create dialog control buttons"""
        group = QtWidgets.QGroupBox("Dialog Controls")
        group_layout = QtWidgets.QHBoxLayout(group)
        
        # Size demonstrations
        small_btn = QtWidgets.QPushButton("Small Button")
        small_btn.setObjectName("small_btn")
        small_btn.clicked.connect(lambda: self._show_message("Small", "Small size class demonstration"))
        group_layout.addWidget(small_btn)
        
        normal_btn = QtWidgets.QPushButton("Normal Button")
        normal_btn.setObjectName("normal_btn")  
        normal_btn.clicked.connect(lambda: self._show_message("Normal", "Normal size class (default)"))
        group_layout.addWidget(normal_btn)
        
        group_layout.addStretch()
        
        close_btn = QtWidgets.QPushButton("Close Demo")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.accept)
        group_layout.addWidget(close_btn)
        
        layout.addWidget(group)
    
    def _setup_enhanced_buttons(self):
        """Setup enhanced button styling and animations"""
        if not ENHANCED_BUTTONS_AVAILABLE:
            print("Enhanced buttons not available")
            return
        
        try:
            # Custom configuration for this test dialog
            custom_config = {
                # Action buttons
                'apply_btn': {'type': 'apply', 'size_class': 'normal'},
                'accept_btn': {'type': 'apply', 'size_class': 'normal'},
                'ok_btn': {'type': 'secondary', 'size_class': 'normal'},
                'confirm_btn': {'type': 'secondary', 'size_class': 'normal'},
                'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
                'remove_btn': {'type': 'cancel', 'size_class': 'normal'},
                
                # Utility buttons
                'export_btn': {'type': 'utility', 'size_class': 'normal'},
                'save_btn': {'type': 'utility', 'size_class': 'normal'},
                'reset_btn': {'type': 'reset', 'size_class': 'normal'},
                'refresh_btn': {'type': 'reset', 'size_class': 'normal'},
                
                # Special buttons
                'help_btn': {'type': 'info', 'size_class': 'normal'},
                'info_btn': {'type': 'info', 'size_class': 'normal'},
                'prev_btn': {'type': 'navigation', 'size_class': 'normal'},
                'next_btn': {'type': 'navigation', 'size_class': 'normal'},
                
                # Size demonstrations
                'small_btn': {'type': 'neutral', 'size_class': 'small'},
                'normal_btn': {'type': 'neutral', 'size_class': 'normal'},
                'close_btn': {'type': 'apply', 'size_class': 'normal'},
            }
            
            # Apply enhanced buttons
            self.button_manager = enhance_dialog_buttons(self, custom_button_configs=custom_config)
            
            # Setup toggle button with special behavior
            self.button_manager.register_toggle_button(
                button=self.toggle_btn,
                toggle_callback=self._on_mode_toggle,
                initial_state=False,
                active_text="Mode: Advanced",
                inactive_text="Mode: Basic"
            )
            
            print("Enhanced buttons successfully applied to test dialog")
            
        except Exception as e:
            print(f"Failed to setup enhanced buttons: {e}")
    
    def _on_mode_toggle(self, new_state: bool):
        """Handle mode toggle"""
        mode = "Advanced" if new_state else "Basic"
        self._show_message("Toggle", f"Switched to {mode} mode")
    
    def _show_message(self, action: str, description: str):
        """Show a message box demonstrating the button action"""
        QtWidgets.QMessageBox.information(
            self, 
            f"{action} Button Clicked",
            f"Button: {action}\n\nDescription: {description}\n\nThis demonstrates the enhanced button system with consistent colors and smooth animations."
        )


class TestMainWindow(QtWidgets.QMainWindow):
    """Main window for the test application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SNID SAGE - Enhanced Dialog Buttons Test")
        self.setMinimumSize(400, 300)
        self.resize(500, 400)
        
        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title = QtWidgets.QLabel("Enhanced Dialog Button System")
        title.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #3b82f6; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Description
        desc = QtWidgets.QLabel(
            "This test application demonstrates the enhanced dialog button system "
            "with unified colors, smooth animations, and consistent behavior.\n\n"
            "Features:\n"
            "• Unified color system by button meaning\n"
            "• Smooth hover and click animations\n"  
            "• Consistent sizing for dialog buttons\n"
            "• Special toggle button support\n"
            "• Easy integration with existing dialogs"
        )
        desc.setWordWrap(True)
        desc.setAlignment(QtCore.Qt.AlignCenter)
        desc.setStyleSheet("color: #64748b; font-size: 12pt; line-height: 1.4;")
        layout.addWidget(desc)
        
        layout.addStretch()
        
        # Test button
        test_btn = QtWidgets.QPushButton("Open Test Dialog")
        test_btn.setObjectName("test_btn")
        test_btn.clicked.connect(self._open_test_dialog)
        test_btn.setMinimumHeight(40)
        test_btn.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        layout.addWidget(test_btn)
        
        # Apply basic styling to the test button
        if ENHANCED_BUTTONS_AVAILABLE:
            try:
                self.button_manager = enhance_dialog_buttons(
                    self, 
                    custom_button_configs={'test_btn': {'type': 'apply', 'size_class': 'normal'}}
                )
            except Exception as e:
                print(f"Failed to enhance main window button: {e}")
    
    def _open_test_dialog(self):
        """Open the test dialog"""
        dialog = TestDialogButtonsDialog(self)
        dialog.exec()


def main():
    """Main function"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Enhanced Dialog Buttons Test")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("SNID SAGE")
    
    # Check if enhanced buttons are available
    if not ENHANCED_BUTTONS_AVAILABLE:
        QtWidgets.QMessageBox.critical(
            None,
            "Enhanced Buttons Not Available",
            "The enhanced dialog button system is not available.\n"
            "Please check that the snid_sage.interfaces.gui.utils modules are properly installed."
        )
        return 1
    
    # Create and show main window
    window = TestMainWindow()
    window.show()
    
    # Center the window
    screen = app.primaryScreen()
    if screen:
        screen_geometry = screen.availableGeometry()
        window_geometry = window.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        window.move(x, y)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())