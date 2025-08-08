"""
SNID SAGE - Enhanced PlotWidget
===============================

Enhanced PyQtGraph PlotWidget with:
- Disabled right-click context menus
- Built-in save functionality with emoji button
- High-resolution image export (300 DPI)
- SVG vector export
- Consistent theming support

Based on custom_autoscale_with_export.py demo, adapted for SNID SAGE.

Developed by Fiorenzo Stoppa for SNID SAGE
"""

import os
import sys
from typing import Optional, Dict, Any

# PySide6 imports
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets

# PyQtGraph imports
try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    pg = None

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.enhanced_plot_widget')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.enhanced_plot_widget')


class SimplePlotWidget(pg.PlotWidget):
    """
    Simple PyQtGraph PlotWidget with only disabled context menus (no save functionality)
    
    Used for dialogs where save functionality is not desired, like preprocessing previews.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize simple plot widget"""
        super().__init__(*args, **kwargs)
        
        # Disable context menus completely
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        
        # Disable plot item and viewbox menus
        plot_item = self.getPlotItem()
        if plot_item:
            plot_item.setMenuEnabled(False)
            vb = plot_item.getViewBox()
            if vb:
                vb.setMenuEnabled(False)


class EnhancedPlotWidget(pg.PlotWidget):
    """
    Enhanced PyQtGraph PlotWidget with disabled context menus and save functionality
    
    Features:
    - Disabled right-click context menus on plot and viewbox
    - Save emoji button in bottom-right corner
    - Export menu with high-resolution PNG/JPG (300 DPI) and SVG options
    - Automatic positioning and theming support
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize enhanced plot widget"""
        super().__init__(*args, **kwargs)
        
        # Disable context menus completely
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        
        # Disable plot item and viewbox menus
        plot_item = self.getPlotItem()
        if plot_item:
            plot_item.setMenuEnabled(False)
            vb = plot_item.getViewBox()
            if vb:
                vb.setMenuEnabled(False)
        
        # Track whether save button should be shown
        self.save_proxy = None
        self._show_save_button = False
        
        # Initialize save functionality after a short delay to ensure plot is ready
        QtCore.QTimer.singleShot(100, self._setup_save_functionality)
    
    def _setup_save_functionality(self):
        """Setup save button after plot is fully initialized"""
        try:
            self._add_save_button()
        except Exception as e:
            _LOGGER.warning(f"Failed to setup save functionality: {e}")
    
    def _add_save_button(self):
        """Add a save emoji button using QGraphicsProxyWidget approach"""
        plot_item = self.getPlotItem()
        if not plot_item:
            return
        
        # Create a QLabel with save emoji - no button background for clean look
        save_emoji = QtWidgets.QLabel("💾")
        save_emoji.setFixedSize(14, 14)  # Made one point smaller
        save_emoji.setToolTip("Save plot as image")
        save_emoji.setAlignment(QtCore.Qt.AlignCenter)
        save_emoji.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                font-size: 13px;
                color: #333;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: rgba(200, 200, 200, 0.5);
                border-radius: 8px;
            }
        """)
        
        # Make it clickable
        save_emoji.mousePressEvent = lambda event: self._show_export_menu()
        
        # Wrap in QGraphicsProxyWidget for scene integration
        self.save_proxy = QtWidgets.QGraphicsProxyWidget()
        self.save_proxy.setWidget(save_emoji)
        
        # Add to plot scene
        plot_item.scene().addItem(self.save_proxy)
        
        def position_save_emoji():
            """Position save emoji in bottom-right corner"""
            try:
                plot_rect = plot_item.sceneBoundingRect()
                
                # Position at bottom-right corner with margin
                x_pos = plot_rect.right() - 16  
                y_pos = plot_rect.bottom() - 16 
                
                self.save_proxy.setPos(x_pos, y_pos)
                self.save_proxy.setZValue(1000)  # Ensure it's on top
            except Exception as e:
                _LOGGER.debug(f"Error positioning save emoji: {e}")
        
        # Connect positioning to layout changes
        plot_item.vb.sigResized.connect(position_save_emoji)
        QtCore.QTimer.singleShot(200, position_save_emoji)  # Initial positioning
        
        # Hide save button initially (will be shown when data is plotted)
        self.save_proxy.hide()
    
    def _show_export_menu(self):
        """Show context menu with export options"""
        menu = QtWidgets.QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 12px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
            }
        """)
        
        # Add image export action
        image_action = menu.addAction("📷 Save as High-Res Image (300 DPI)")
        image_action.triggered.connect(self._save_high_res_image)
        
        # Add SVG export action
        svg_action = menu.addAction("📄 Save as Vector Graphics (SVG)")
        svg_action.triggered.connect(self._save_svg)
        
        # Position menu near the save button
        if hasattr(self, 'save_proxy'):
            try:
                proxy_pos = self.save_proxy.pos()
                global_pos = self.mapToGlobal(QtCore.QPoint(int(proxy_pos.x()), int(proxy_pos.y())))
                menu.exec(global_pos)
            except Exception:
                menu.exec(QtWidgets.QCursor.pos())
        else:
            menu.exec(QtWidgets.QCursor.pos())
    
    def _save_high_res_image(self):
        """Save plot as high-resolution image (300 DPI)"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Plot as High-Resolution Image", "snid_sage_plot.png",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if filename:
            try:
                # Hide save button during export
                if hasattr(self, 'save_proxy'):
                    self.save_proxy.hide()
                
                # Import here to avoid circular dependencies
                import pyqtgraph.exporters
                plot_item = self.getPlotItem()
                
                # Calculate 300 DPI resolution for ~8 inch width
                exporter = pyqtgraph.exporters.ImageExporter(plot_item)
                exporter.parameters()['width'] = 2400  # 300 DPI for 8-inch width
                exporter.export(filename)
                
                _LOGGER.info(f"Plot saved as high-resolution image: {filename}")
                
                # Show success message
                QtWidgets.QMessageBox.information(
                    self, "Export Successful", 
                    f"Plot saved successfully:\n{os.path.basename(filename)}"
                )
                
            except Exception as e:
                error_msg = f"Failed to save image: {str(e)}"
                _LOGGER.error(error_msg)
                QtWidgets.QMessageBox.warning(self, "Export Failed", error_msg)
            finally:
                # Show button again
                if hasattr(self, 'save_proxy'):
                    self.save_proxy.show()
    
    def _save_svg(self):
        """Save plot as SVG vector graphics"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Plot as Vector Graphics", "snid_sage_plot.svg",
            "SVG Files (*.svg);;All Files (*)"
        )
        
        if filename:
            try:
                # Hide save button during export
                if hasattr(self, 'save_proxy'):
                    self.save_proxy.hide()
                
                # Import here to avoid circular dependencies
                import pyqtgraph.exporters
                plot_item = self.getPlotItem()
                
                # Export as SVG vector format
                exporter = pyqtgraph.exporters.SVGExporter(plot_item)
                exporter.export(filename)
                
                _LOGGER.info(f"Plot saved as SVG: {filename}")
                
                # Show success message
                QtWidgets.QMessageBox.information(
                    self, "Export Successful", 
                    f"Plot saved successfully:\n{os.path.basename(filename)}"
                )
                
            except Exception as e:
                error_msg = f"Failed to save SVG: {str(e)}"
                _LOGGER.error(error_msg)
                QtWidgets.QMessageBox.warning(self, "Export Failed", error_msg)
            finally:
                # Show button again
                if hasattr(self, 'save_proxy'):
                    self.save_proxy.show()
    
    def show_save_button(self):
        """Show the save button (call when data is plotted)"""
        if hasattr(self, 'save_proxy') and self.save_proxy:
            self.save_proxy.show()
            self._show_save_button = True
    
    def hide_save_button(self):
        """Hide the save button (call when plot is cleared)"""
        if hasattr(self, 'save_proxy') and self.save_proxy:
            self.save_proxy.hide()
            self._show_save_button = False
    
    def apply_theme_colors(self, theme_colors: Optional[Dict[str, str]] = None):
        """Apply theme colors to the plot if needed"""
        if not theme_colors:
            return
        
        try:
            # Update save button styling based on theme if needed
            if hasattr(self, 'save_proxy') and self.save_proxy.widget():
                # You can customize the save button appearance based on theme here
                pass
        except Exception as e:
            _LOGGER.debug(f"Error applying theme to save button: {e}")