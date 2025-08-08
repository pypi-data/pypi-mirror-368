"""
PySide6 Advanced Preprocessing Dialog for SNID SAGE GUI
======================================================

Complete PySide6 implementation of the advanced preprocessing dialog,
matching all functionality from the Tkinter version with modern Qt interface.

Features:
- 6-step preprocessing workflow with split-panel UI
- Real-time spectrum preview using PyQtGraph
- Interactive masking with drag selection
- Interactive continuum editing with control points
- All preprocessing operations (filtering, rebinning, apodization)
- Professional Qt styling and theming
- Step-by-step wizard interface
"""

import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from PySide6 import QtWidgets, QtCore, QtGui

# Import flexible number input widget
from snid_sage.interfaces.gui.components.widgets.flexible_number_input import (
    create_flexible_double_input,
    create_flexible_int_input
)

# PyQtGraph for plotting
try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
    # Import simple plot widget (without save functionality for preprocessing previews)
    from snid_sage.interfaces.gui.components.plots.enhanced_plot_widget import SimplePlotWidget
    # Configure PyQtGraph for complete software rendering (consistent with other dialogs)
    pg.setConfigOptions(
        useOpenGL=False,         # Disable OpenGL completely
        antialias=True,          # Keep antialiasing for quality
        enableExperimental=False, # Disable experimental features
        crashWarning=False       # Reduce warnings
    )
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    pg = None
    SimplePlotWidget = None

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_preprocessing_dialog')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_preprocessing_dialog')

# Import SNID preprocessing functions
try:
    from snid_sage.snid.snid import NW, MINW, MAXW
    from snid_sage.snid.preprocessing import (
        init_wavelength_grid, get_grid_params, medfilt, medwfilt, 
        clip_aband, clip_sky_lines, clip_host_emission_lines,
        apply_wavelength_mask, log_rebin, fit_continuum, apodize
    )
    SNID_AVAILABLE = True
except ImportError:
    SNID_AVAILABLE = False
    _LOGGER.warning("SNID preprocessing functions not available")

# Import our custom components
from snid_sage.interfaces.gui.features.preprocessing.pyside6_preview_calculator import PySide6PreviewCalculator
from snid_sage.interfaces.gui.components.plots.pyside6_plot_manager import PySide6PlotManager
from snid_sage.interfaces.gui.components.widgets.pyside6_interactive_masking_widget import PySide6InteractiveMaskingWidget
from snid_sage.interfaces.gui.components.widgets.pyside6_interactive_continuum_widget import PySide6InteractiveContinuumWidget

# Enhanced button management
try:
    from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset
    ENHANCED_BUTTONS_AVAILABLE = True
except ImportError:
    ENHANCED_BUTTONS_AVAILABLE = False


class PySide6PreprocessingDialog(QtWidgets.QDialog):
    """PySide6 dialog for comprehensive preprocessing configuration"""
    
    def __init__(self, parent=None, spectrum_data=None):
        """Initialize preprocessing dialog"""
        super().__init__(parent)
        
        self.parent_gui = parent
        self.spectrum_data = spectrum_data  # (wave, flux) tuple
        self.result = None
        
        # Preprocessing state
        self.current_step = 0
        self.total_steps = 6
        self.step_names = [
            "Masking & Clipping Operations",
            "Savitzky-Golay Filtering", 
            "Log-wavelength Rebinning & Flux Scaling",
            "Continuum Fitting & Interactive Editing",
            "Apodization",
            "Final Review"
        ]
        
        # Preview data
        self.original_wave = None
        self.original_flux = None
        self.preview_wave = None
        self.preview_flux = None
        
        # Processing components
        self.preview_calculator = None
        self.plot_manager = None
        self.masking_widget = None
        self.continuum_widget = None
        
        # Processing parameters - Initialize with exact defaults from original Tkinter version
        self.processing_params = self._get_default_params()
        
        # UI components
        self.left_panel = None
        self.right_panel = None
        self.step_widgets = []
        self.options_frame = None
        
        # Theme colors
        self.colors = self._get_theme_colors()
        
        # Initialize wavelength grid for preprocessing
        if SNID_AVAILABLE:
            init_wavelength_grid()
        
        # Load spectrum data if provided
        if spectrum_data:
            self.original_wave, self.original_flux = spectrum_data
            self.preview_wave = self.original_wave.copy()
            self.preview_flux = self.original_flux.copy()
            
            # Initialize preview calculator with proper PySide6 version
            self.preview_calculator = PySide6PreviewCalculator(
                self.original_wave, self.original_flux
            )
            
            # Stage memory no longer used for UI controls (revert removed)
        
        self.setup_ui()
        self._initialize_components()
        self._update_preview()
        
        # Debug logging
        _LOGGER.debug(f"PyQtGraph available: {PYQTGRAPH_AVAILABLE}")
        if self.plot_manager:
            top_plot, bottom_plot = self.plot_manager.get_plot_widgets()
            _LOGGER.debug(f"Plot widgets available: top={top_plot is not None}, bottom={bottom_plot is not None}")
    
    def _get_theme_colors(self) -> Dict[str, str]:
        """Get theme colors from parent or defaults"""
        if hasattr(self.parent_gui, 'theme_colors'):
            return self.parent_gui.theme_colors
        else:
            return {
                'bg_primary': '#f8fafc',
                'bg_secondary': '#ffffff',
                'bg_tertiary': '#f1f5f9',
                'text_primary': '#1e293b',
                'text_secondary': '#475569',
                'border': '#cbd5e1',
                'accent_primary': '#3b82f6',
                'btn_primary': '#3b82f6',
                'btn_success': '#10b981',
                'btn_warning': '#f59e0b',
                'btn_danger': '#ef4444'
            }
    
    def _get_default_params(self) -> Dict[str, Any]:
        """Get default preprocessing parameters matching original Tkinter version"""
        return {
            # Step 0: Masking & Clipping
            'clip_negative': True,
            'clip_aband': False,
            'clip_sky_lines': False,
            'clip_host_emission': False,
            'sky_width': 40.0,
            'custom_masks': [],
            
            # Step 1: Filtering  
            'filter_type': 'none',  # none, fixed, wavelength
            'filter_window': 11,
            'filter_order': 3,
            'filter_fwhm': 5.0,
            
            # Step 2: Rebinning & Scaling (always applied)
            'log_rebin': True,  # Always true - required for SNID
            'flux_scaling': True,  # Scale to mean
            
            # Step 3: Continuum
            'continuum_method': 'spline',  # spline, gaussian
            'continuum_sigma': 10.0,
            'spline_knots': 13,
            'interactive_continuum': False,
            
            # Step 4: Apodization
            'apply_apodization': True,
            'apod_percent': 10.0,
            
            # Output
            'save_intermediate': False,
            'output_format': 'ascii'
        }
    
    def setup_ui(self):
        """Setup the dialog UI with split-panel layout matching original design"""
        self.setWindowTitle("Advanced Spectrum Preprocessing - SNID SAGE")
        self.setMinimumSize(900, 500)  # Match SN Emission Lines minimum size
        self.resize(1000, 600)  # Match SN Emission Lines default size
        self.setModal(True)
        
        # Apply global styling with reduced font sizes for left panel
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.colors['bg_primary']};
                color: {self.colors['text_primary']};
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 10pt;  /* Reduced from default */
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                margin-top: 6px;  /* Reduced spacing */
                padding-top: 10px;  /* Reduced padding */
                background: {self.colors['bg_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;  /* Reduced */
                padding: 0 6px;  /* Reduced */
                background: {self.colors['bg_secondary']};
                font-size: 10pt;  /* Reduced */
            }}
            QLabel {{
                font-size: 9pt;  /* Reduced for all labels */
            }}
            QCheckBox {{
                font-size: 9pt;  /* Reduced for checkboxes */
                spacing: 4px;  /* Reduced spacing */
            }}
            QRadioButton {{
                font-size: 9pt;  /* Reduced for radio buttons */
                spacing: 4px;  /* Reduced spacing */
            }}
            QComboBox {{
                font-size: 9pt;  /* Reduced for combo boxes */
                padding: 2px 6px;  /* Reduced padding */
            }}
            QSpinBox, QDoubleSpinBox {{
                font-size: 9pt;  /* Reduced for spin boxes */
                padding: 2px 4px;  /* Reduced padding */
            }}
            QPushButton {{
                padding: 6px 12px;  /* Reduced padding */
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;  /* Reduced button font */
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        
        # Main layout - split panel exactly like Tkinter version
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create left panel (controls) and right panel (plots)
        self._create_left_panel(main_layout)
        self._create_right_panel(main_layout)
        
        _LOGGER.debug("PySide6 Advanced Preprocessing dialog created")
    
    def _create_left_panel(self, main_layout):
        """Create the left control panel with step header only"""
        self.left_panel = QtWidgets.QFrame()
        self.left_panel.setFixedWidth(300)  # Increased slightly for wider layout
        self.left_panel.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['bg_secondary']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
            }}
        """)
        
        left_layout = QtWidgets.QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)  # Further reduced margins
        left_layout.setSpacing(6)  # Further reduced spacing
        
        # Simple step header with progress indicator - no navigation controls
        self.step_header = QtWidgets.QLabel(f"Step {self.current_step + 1}/{self.total_steps}: {self.step_names[self.current_step]}")
        self.step_header.setStyleSheet("font-size: 12pt; font-weight: bold; color: #1e293b; margin-bottom: 8px;")  # Reduced font size
        self.step_header.setWordWrap(True)
        left_layout.addWidget(self.step_header)
        
        # Options frame (will be populated based on current step)
        self.options_frame = QtWidgets.QFrame()
        options_layout = QtWidgets.QVBoxLayout(self.options_frame)
        options_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.options_frame)
        
        # Add stretch to push control buttons to bottom
        left_layout.addStretch()
        
        # Control buttons
        self._create_buttons(left_layout)
        
        main_layout.addWidget(self.left_panel)
    
    def _create_right_panel(self, main_layout):
        """Create the right visualization panel with dual plots"""
        self.right_panel = QtWidgets.QFrame()
        self.right_panel.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['bg_secondary']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
            }}
        """)
        
        right_layout = QtWidgets.QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(10)
        
        # Header
        viz_header = QtWidgets.QLabel("Live Preview")
        viz_header.setStyleSheet("font-size: 16pt; font-weight: bold; color: #1e293b;")
        right_layout.addWidget(viz_header)
        
        # Create dual plots directly without using PySide6PlotManager
        self._create_dual_preview_plots(right_layout)
        
        main_layout.addWidget(self.right_panel)
    
    def _create_dual_preview_plots(self, parent_layout):
        """Create dual preview plots directly using PyQtGraph"""
        try:
            if not PYQTGRAPH_AVAILABLE:
                fallback_label = QtWidgets.QLabel("PyQtGraph not available\n\nInstall with: pip install pyqtgraph")
                fallback_label.setAlignment(QtCore.Qt.AlignCenter)
                fallback_label.setStyleSheet("color: #ef4444; font-size: 12pt;")
                parent_layout.addWidget(fallback_label)
                self.plot_manager = None
                return
            
            # Create container for dual plots
            plots_container = QtWidgets.QFrame()
            plots_layout = QtWidgets.QVBoxLayout(plots_container)
            plots_layout.setContentsMargins(5, 5, 5, 5)
            plots_layout.setSpacing(10)
            parent_layout.addWidget(plots_container)
            
            # Create top plot
            top_label = QtWidgets.QLabel("Current State")
            top_label.setStyleSheet("font-weight: bold; color: #1e293b; font-size: 12pt;")
            plots_layout.addWidget(top_label)
            
            self.top_plot_widget = SimplePlotWidget()
            self.top_plot_widget.setLabel('left', 'Flux')
            self.top_plot_widget.setLabel('bottom', 'Wavelength (Å)')
            self.top_plot_widget.showGrid(x=True, y=True, alpha=0.3)
            self._configure_plot_widget(self.top_plot_widget)
            plots_layout.addWidget(self.top_plot_widget)
            
            # Create bottom plot
            bottom_label = QtWidgets.QLabel("Preview (After Current Step)")
            bottom_label.setStyleSheet("font-weight: bold; color: #1e293b; font-size: 12pt;")
            plots_layout.addWidget(bottom_label)
            
            self.bottom_plot_widget = SimplePlotWidget()
            self.bottom_plot_widget.setLabel('left', 'Flux')
            self.bottom_plot_widget.setLabel('bottom', 'Wavelength (Å)')
            self.bottom_plot_widget.showGrid(x=True, y=True, alpha=0.3)
            self._configure_plot_widget(self.bottom_plot_widget)
            plots_layout.addWidget(self.bottom_plot_widget)
            
            # Create a simple plot manager object for compatibility
            class SimplePreviewPlotManager:
                def __init__(self, parent_dialog):
                    self.parent = parent_dialog
                
                def get_plot_widgets(self):
                    return (self.parent.top_plot_widget, self.parent.bottom_plot_widget)
                
                def update_standard_preview(self, *args, **kwargs):
                    return self.parent._update_standard_preview(*args, **kwargs)
                
                def update_interactive_preview(self, *args, **kwargs):
                    return self.parent._update_interactive_preview(*args, **kwargs)
            
            self.plot_manager = SimplePreviewPlotManager(self)
            
            _LOGGER.debug("Dual preview plots created successfully")
            
        except Exception as e:
            _LOGGER.error(f"Error creating dual preview plots: {e}")
            fallback_label = QtWidgets.QLabel("Plot preview not available")
            fallback_label.setAlignment(QtCore.Qt.AlignCenter)
            fallback_label.setStyleSheet("color: #666; font-size: 12pt;")
            parent_layout.addWidget(fallback_label)
            self.plot_manager = None
    
    def _configure_plot_widget(self, plot_widget):
        """Configure a plot widget with proper theme and settings"""
        try:
            # Note: Global PyQtGraph configuration is already set at module level
            # Set background color
            plot_widget.setBackground('white')
            
            # Get plot item and configure colors
            plot_item = plot_widget.getPlotItem()
            if plot_item:
                # Set axis colors
                plot_item.getAxis('left').setPen(pg.mkPen(color='black', width=1))
                plot_item.getAxis('bottom').setPen(pg.mkPen(color='black', width=1))
                plot_item.getAxis('left').setTextPen(pg.mkPen(color='black'))
                plot_item.getAxis('bottom').setTextPen(pg.mkPen(color='black'))
                
        except Exception as e:
            _LOGGER.debug(f"Error configuring plot widget: {e}")
    
    def _update_standard_preview(self, current_wave, current_flux, preview_wave, preview_flux, mask_regions=None):
        """Update standard preview with current and preview data"""
        try:
            # Update top plot with current data
            if hasattr(self, 'top_plot_widget') and self.top_plot_widget:
                top_plot_item = self.top_plot_widget.getPlotItem()
                top_plot_item.clear()
                
                if current_wave is not None and current_flux is not None:
                    top_plot_item.plot(current_wave, current_flux, pen=pg.mkPen(color='#3b82f6', width=2), name="Current")
                
                # Show mask regions (red bands) only in step 0 (Masking step)
                if mask_regions and self.current_step == 0:
                    for start, end in mask_regions:
                        # Create red fill region
                        mask_item = pg.LinearRegionItem(
                            values=[start, end],
                            orientation='vertical',
                            brush=pg.mkBrush(255, 100, 100, 100),  # Semi-transparent red
                            pen=pg.mkPen(255, 0, 0, 150),  # Red border
                            movable=False
                        )
                        top_plot_item.addItem(mask_item)
            
            # Update bottom plot with preview data
            if hasattr(self, 'bottom_plot_widget') and self.bottom_plot_widget:
                bottom_plot_item = self.bottom_plot_widget.getPlotItem()
                bottom_plot_item.clear()
                
                if preview_wave is not None and preview_flux is not None:
                    bottom_plot_item.plot(preview_wave, preview_flux, pen=pg.mkPen(color='#10b981', width=2), name="Preview")
                
            _LOGGER.debug("Standard preview updated with dual plots")
            
        except Exception as e:
            _LOGGER.error(f"Error updating standard preview: {e}")
    
    def _update_interactive_preview(self, current_wave, current_flux, continuum_points, preview_wave, preview_flux, interactive_mode=False):
        """Update interactive preview with continuum overlay"""
        try:
            # Update top plot with current data and continuum points
            if hasattr(self, 'top_plot_widget') and self.top_plot_widget:
                top_plot_item = self.top_plot_widget.getPlotItem()
                top_plot_item.clear()
                
                if current_wave is not None and current_flux is not None:
                    top_plot_item.plot(current_wave, current_flux, pen=pg.mkPen(color='#3b82f6', width=2), name="Current")
                
                # Plot continuum points if available (line only, no symbols)
                if continuum_points:
                    x_points = [p[0] for p in continuum_points]
                    y_points = [p[1] for p in continuum_points]
                    top_plot_item.plot(x_points, y_points, pen=pg.mkPen(color='red', width=2, style=QtCore.Qt.DashLine), 
                                     name="Continuum")
            
            # Update bottom plot with preview data
            if hasattr(self, 'bottom_plot_widget') and self.bottom_plot_widget:
                bottom_plot_item = self.bottom_plot_widget.getPlotItem()
                bottom_plot_item.clear()
                
                if preview_wave is not None and preview_flux is not None:
                    bottom_plot_item.plot(preview_wave, preview_flux, pen=pg.mkPen(color='#10b981', width=2), name="Preview")
                
            _LOGGER.debug("Interactive preview updated with dual plots")
            
        except Exception as e:
            _LOGGER.error(f"Error updating interactive preview: {e}")
    
    def _create_buttons(self, layout):
        """Create action buttons in a compact layout (removed navigation buttons)"""
        button_frame = QtWidgets.QFrame()
        button_layout = QtWidgets.QVBoxLayout(button_frame)
        button_layout.setSpacing(6)  # Reduced spacing
        
        # Action buttons row - Apply and Restart
        action_layout = QtWidgets.QHBoxLayout()
        
        # Apply Step button (becomes "Finish" on final step)
        self.apply_btn = QtWidgets.QPushButton("Apply Step")
        self.apply_btn.setObjectName("apply_btn")
        self.apply_btn.clicked.connect(self.apply_current_step)
        action_layout.addWidget(self.apply_btn)
        
        # Restart button (resets workflow to Step 1)
        self.restart_btn = QtWidgets.QPushButton("⟲ Restart")
        self.restart_btn.setObjectName("restart_btn")
        self.restart_btn.clicked.connect(self.restart_to_step_one)
        action_layout.addWidget(self.restart_btn)
        
        button_layout.addLayout(action_layout)
        
        layout.addWidget(button_frame)
    
    def _initialize_components(self):
        """Initialize interactive components after UI setup"""
        if not self.preview_calculator or not self.plot_manager:
            _LOGGER.warning("Preview calculator or plot manager not available")
            return
        
        # Get plot widgets for interactive components
        top_plot, bottom_plot = self.plot_manager.get_plot_widgets()
        
        if top_plot and PYQTGRAPH_AVAILABLE:
            # Initialize masking widget with proper connection
            self.masking_widget = PySide6InteractiveMaskingWidget(top_plot, self.colors)
            self.masking_widget.set_update_callback(self._on_mask_updated)
            
            # Initialize continuum widget with proper connection
            self.continuum_widget = PySide6InteractiveContinuumWidget(
                self.preview_calculator, top_plot, self.colors
            )
            self.continuum_widget.set_update_callback(self._on_continuum_updated)
            
            _LOGGER.debug("Interactive components initialized successfully")
        else:
            _LOGGER.warning("Plot widgets not available - interactive features will be limited")
        
        # Update step display
        self._update_step_display()
        
        # Initialize cleanup tracking
        self._plot_widgets_initialized = True
        
        # Setup enhanced buttons
        self._setup_enhanced_buttons()
    
    def _setup_enhanced_buttons(self):
        """Setup enhanced button styling and animations"""
        if not ENHANCED_BUTTONS_AVAILABLE:
            _LOGGER.info("Enhanced buttons not available, using standard styling")
            return

        try:
            # Use the preprocessing dialog preset
            self.button_manager = enhance_dialog_with_preset(
                self, 'preprocessing_dialog'
            )

            _LOGGER.info("Enhanced buttons successfully applied to preprocessing dialog")
            
            # Setup masking toggle button if available
            self._setup_masking_toggle_button()
            
            # Initial button state update
            self._update_button_states()

        except Exception as e:
            _LOGGER.error(f"Failed to setup enhanced buttons: {e}")
    
    def _setup_masking_toggle_button(self):
        """Setup the interactive masking toggle button with enhanced styling"""
        if hasattr(self, 'masking_widget') and self.masking_widget and hasattr(self, 'button_manager'):
            masking_controls = self.masking_widget.controls_frame
            if masking_controls:
                # Find all buttons in the masking controls
                all_buttons = masking_controls.findChildren(QtWidgets.QPushButton)
                
                for button in all_buttons:
                    button_text = button.text()
                    
                    if "Interactive Masking" in button_text:
                        # This is the main toggle button
                        button.setObjectName("masking_toggle_btn")
                        
                        # Register with enhanced button system
                        self.button_manager.register_button(
                            button, 
                            'neutral',
                            {
                                'is_toggle': True,
                                'toggle_state': False,
                                'size_class': 'normal'
                            }
                        )
                        
                        # Store reference for state updates
                        self.masking_toggle_button = button
                        
                        # Connect to masking state changes
                        if hasattr(self.masking_widget, 'masking_mode_changed'):
                            self.masking_widget.masking_mode_changed.connect(self._on_masking_mode_changed)
                    
                    elif button_text == "Remove Selected":
                        # Register the Remove Selected button to prevent styling conflicts
                        button.setObjectName("masking_remove_btn")
                        self.button_manager.register_button(
                            button, 
                            'cancel',
                            {'size_class': 'normal'}
                        )
                    
                    elif button_text == "Clear All":
                        # Register the Clear All button
                        button.setObjectName("masking_clear_btn") 
                        self.button_manager.register_button(
                            button, 
                            'reset',
                            {'size_class': 'normal'}
                        )
                    
                    elif button_text == "Add":
                        # Register the Add button
                        button.setObjectName("masking_add_btn")
                        self.button_manager.register_button(
                            button, 
                            'apply',
                            {'size_class': 'normal'}
                        )
    
    def _on_masking_mode_changed(self, is_active: bool):
        """Handle masking mode state changes"""
        if hasattr(self, 'masking_toggle_button') and hasattr(self, 'button_manager'):
            # Use the proper toggle button update method
            self.button_manager.update_toggle_button(self.masking_toggle_button, is_active)
    
    def _on_mask_updated(self):
        """Callback when mask regions are updated"""
        _LOGGER.debug("Mask regions updated, refreshing preview")
        self._update_preview()
    
    def _on_continuum_updated(self):
        """Callback when continuum is updated"""
        _LOGGER.debug("Continuum updated, refreshing preview")
        # Add a small delay to prevent excessive updates during rapid mouse movements
        if hasattr(self, '_continuum_update_timer'):
            self._continuum_update_timer.stop()
        
        self._continuum_update_timer = QtCore.QTimer()
        self._continuum_update_timer.setSingleShot(True)
        self._continuum_update_timer.timeout.connect(self._update_preview)
        self._continuum_update_timer.start(16)  # ~60 FPS update rate
    
    def _update_step_display(self):
        """Update the UI to show options for the current step"""
        if not self.options_frame:
            return
        
        # Ensure interactive continuum mode is disabled when leaving step 3
        if self.current_step != 3 and self.continuum_widget:
            if self.continuum_widget.is_interactive_mode():
                self.continuum_widget.disable_interactive_mode()
        
        # Clear current options
        layout = self.options_frame.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            layout = QtWidgets.QVBoxLayout(self.options_frame)
        
        # Create options for current step
        if self.current_step == 0:
            self._create_step_0_masking_clipping(layout)
        elif self.current_step == 1:
            self._create_step_1_filtering(layout)
        elif self.current_step == 2:
            self._create_step_2_rebinning(layout)
        elif self.current_step == 3:
            self._create_step_3_continuum(layout)
        elif self.current_step == 4:
            self._create_step_4_apodization(layout)
        elif self.current_step == 5:
            self._create_step_5_review(layout)
        
        # Update button states
        self._update_button_states()
        
        # Update step header with progress indicator
        if hasattr(self, 'step_header'):
            self.step_header.setText(f"Step {self.current_step + 1}/{self.total_steps}: {self.step_names[self.current_step]}")
    
    def _create_step_0_masking_clipping(self, layout):
        """Create step 0: Masking & Clipping Operations exactly like original"""
        # Description
        desc = QtWidgets.QLabel("Mask wavelength regions and apply clipping operations to exclude unwanted features from analysis.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Interactive masking section - now properly connected
        if self.masking_widget:
            masking_controls = self.masking_widget.create_masking_controls(self.options_frame)
            layout.addWidget(masking_controls)
            # Re-register masking toggle/button styling whenever step 0 is rebuilt
            if hasattr(self, 'button_manager') and self.button_manager:
                self._setup_masking_toggle_button()
        else:
            # Fallback when interactive masking is not available
            unavailable_group = QtWidgets.QGroupBox("Interactive Masking (Unavailable)")
            unavailable_layout = QtWidgets.QVBoxLayout(unavailable_group)
            
            msg = QtWidgets.QLabel("Interactive masking requires PyQtGraph.\nInstall with: pip install pyqtgraph")
            msg.setStyleSheet("color: #f59e0b; font-style: italic;")
            msg.setWordWrap(True)
            unavailable_layout.addWidget(msg)
            
            layout.addWidget(unavailable_group)
        
        # Clipping operations exactly matching original
        clipping_group = QtWidgets.QGroupBox("Clipping Operations")
        clipping_layout = QtWidgets.QVBoxLayout(clipping_group)
        
        # A-band removal
        self.aband_cb = QtWidgets.QCheckBox("Remove telluric A-band (7575-7675Å)")
        self.aband_cb.setChecked(self.processing_params['clip_aband'])
        self.aband_cb.toggled.connect(self._update_preview)
        clipping_layout.addWidget(self.aband_cb)
        
        # Sky line removal
        sky_layout = QtWidgets.QHBoxLayout()
        self.sky_cb = QtWidgets.QCheckBox("Remove sky lines, width:")
        self.sky_cb.setChecked(self.processing_params['clip_sky_lines'])
        self.sky_cb.toggled.connect(self._update_preview)
        sky_layout.addWidget(self.sky_cb)
        
        self.sky_width_spin = create_flexible_double_input(min_val=1.0, max_val=200.0, suffix=" Å", default=30.0)
        self.sky_width_spin.setValue(self.processing_params['sky_width'])
        self.sky_width_spin.valueChanged.connect(self._update_preview)
        sky_layout.addWidget(self.sky_width_spin)
        
        sky_layout.addStretch()
        clipping_layout.addLayout(sky_layout)
        
        layout.addWidget(clipping_group)
    
    def _create_step_1_filtering(self, layout):
        """Create step 1: Savitzky-Golay Filtering exactly like original"""
        # Description
        desc = QtWidgets.QLabel("Apply Savitzky-Golay smoothing filter to reduce noise in the spectrum.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Filter options
        filter_group = QtWidgets.QGroupBox("Filter Configuration")
        filter_layout = QtWidgets.QVBoxLayout(filter_group)
        
        # Filter type selection using radio buttons like original
        self.filter_type_group = QtWidgets.QButtonGroup()
        
        self.no_filter_rb = QtWidgets.QRadioButton("No filtering")
        self.no_filter_rb.setChecked(self.processing_params['filter_type'] == 'none')
        self.no_filter_rb.toggled.connect(self._on_filter_type_changed)
        self.filter_type_group.addButton(self.no_filter_rb, 0)
        filter_layout.addWidget(self.no_filter_rb)
        
        # Fixed window filter
        fixed_layout = QtWidgets.QHBoxLayout()
        self.fixed_filter_rb = QtWidgets.QRadioButton("Fixed window:")
        self.fixed_filter_rb.setChecked(self.processing_params['filter_type'] == 'fixed')
        self.fixed_filter_rb.toggled.connect(self._on_filter_type_changed)
        self.filter_type_group.addButton(self.fixed_filter_rb, 1)
        fixed_layout.addWidget(self.fixed_filter_rb)
        
        self.fixed_window_spin = create_flexible_int_input(min_val=3, max_val=101, suffix=" pixels", default=11)
        # Set the value explicitly to ensure proper display
        filter_window = self.processing_params.get('filter_window', 11)
        self.fixed_window_spin.setValue(filter_window)
        self.fixed_window_spin.valueChanged.connect(self._update_preview)
        fixed_layout.addWidget(self.fixed_window_spin)
        
        fixed_layout.addWidget(QtWidgets.QLabel("order:"))
        self.polyorder_spin = create_flexible_int_input(min_val=1, max_val=10, default=3)
        self.polyorder_spin.setValue(self.processing_params['filter_order'])
        self.polyorder_spin.valueChanged.connect(self._update_preview)
        fixed_layout.addWidget(self.polyorder_spin)
        
        fixed_layout.addStretch()
        filter_layout.addLayout(fixed_layout)
        
        # Wavelength-based filter
        wave_layout = QtWidgets.QHBoxLayout()
        self.wave_filter_rb = QtWidgets.QRadioButton("Wavelength-based:")
        self.wave_filter_rb.setChecked(self.processing_params['filter_type'] == 'wavelength')
        self.wave_filter_rb.toggled.connect(self._on_filter_type_changed)
        self.filter_type_group.addButton(self.wave_filter_rb, 2)
        wave_layout.addWidget(self.wave_filter_rb)
        
        self.wave_fwhm_spin = create_flexible_double_input(min_val=0.1, max_val=50.0, suffix=" Å FWHM", default=10.0)
        self.wave_fwhm_spin.setValue(self.processing_params['filter_fwhm'])
        self.wave_fwhm_spin.valueChanged.connect(self._update_preview)
        wave_layout.addWidget(self.wave_fwhm_spin)
        
        wave_layout.addStretch()
        filter_layout.addLayout(wave_layout)
        
        layout.addWidget(filter_group)
    
    def _on_filter_type_changed(self):
        """Handle filter type radio button changes"""
        if self.no_filter_rb.isChecked():
            self.processing_params['filter_type'] = 'none'
        elif self.fixed_filter_rb.isChecked():
            self.processing_params['filter_type'] = 'fixed'
        elif self.wave_filter_rb.isChecked():
            self.processing_params['filter_type'] = 'wavelength'
        self._update_preview()
    
    def _create_step_2_rebinning(self, layout):
        """Create step 2: Log-wavelength Rebinning & Flux Scaling exactly like original"""
        # Description
        desc = QtWidgets.QLabel("Apply log-wavelength rebinning (required for SNID) and optional flux scaling.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Rebinning options
        rebin_group = QtWidgets.QGroupBox("Rebinning Configuration")
        rebin_layout = QtWidgets.QVBoxLayout(rebin_group)
        
        # Log rebinning (always enabled like original)
        self.log_rebin_cb = QtWidgets.QCheckBox("Apply log-wavelength rebinning (required)")
        self.log_rebin_cb.setChecked(True)
        self.log_rebin_cb.setEnabled(False)  # Always required
        rebin_layout.addWidget(self.log_rebin_cb)
        
        # Flux scaling - properly synchronized and connected
        self.flux_scaling_cb = QtWidgets.QCheckBox("Scale flux to mean value")
        self.flux_scaling_cb.setChecked(self.processing_params['flux_scaling'])
        # Connect to both parameter update AND preview update
        self.flux_scaling_cb.toggled.connect(self._on_flux_scaling_changed)
        rebin_layout.addWidget(self.flux_scaling_cb)
        
        layout.addWidget(rebin_group)
        
        # Grid information
        info_group = QtWidgets.QGroupBox("Grid Information")
        info_layout = QtWidgets.QVBoxLayout(info_group)
        
        info_text = QtWidgets.QLabel(
            f"Target grid: {NW if SNID_AVAILABLE else 1024} points\n"
            f"Wavelength range: {MINW if SNID_AVAILABLE else 2500} - {MAXW if SNID_AVAILABLE else 10000} Å\n"
            "Log-spacing: uniform in log(wavelength)"
        )
        info_text.setStyleSheet("color: #64748b; font-size: 10pt;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
    
    def _on_flux_scaling_changed(self):
        """Handle flux scaling checkbox changes"""
        self.processing_params['flux_scaling'] = self.flux_scaling_cb.isChecked()
        self._update_preview()
    
    def _on_spline_knots_changed(self):
        """Handle spline knots parameter changes"""
        if self.current_step == 3 and self.continuum_widget and \
           self.processing_params['continuum_method'] == 'spline':
            # Update continuum if not in interactive mode or no manual changes
            if not self.continuum_widget.is_interactive_mode() or not self.continuum_widget.has_manual_changes():
                knotnum = self.spline_knots_spin.value()
                self.continuum_widget.update_continuum_from_fit(knotnum)
        self._update_preview()
    
    def _on_gauss_sigma_changed(self):
        """Handle Gaussian sigma parameter changes"""
        if self.current_step == 3 and self.continuum_widget and \
           self.processing_params['continuum_method'] == 'gaussian':
            # Update continuum if not in interactive mode or no manual changes
            if not self.continuum_widget.is_interactive_mode() or not self.continuum_widget.has_manual_changes():
                sigma = self.gauss_sigma_spin.value()
                self.continuum_widget.update_continuum_from_fit(sigma)
        self._update_preview()
    
    def _create_step_3_continuum(self, layout):
        """Create step 3: Continuum Fitting & Interactive Editing exactly like original"""
        # Description
        desc = QtWidgets.QLabel("Fit and subtract the continuum. Use interactive editing for fine-tuning.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Continuum fitting method
        method_group = QtWidgets.QGroupBox("Continuum Fitting Method")
        method_layout = QtWidgets.QVBoxLayout(method_group)
        
        self.continuum_method_group = QtWidgets.QButtonGroup()
        
        # Spline method (default)
        spline_layout = QtWidgets.QHBoxLayout()
        self.spline_rb = QtWidgets.QRadioButton("Spline, knots:")
        self.spline_rb.setChecked(self.processing_params['continuum_method'] == 'spline')
        self.spline_rb.toggled.connect(self._on_continuum_method_changed)
        self.continuum_method_group.addButton(self.spline_rb, 0)
        spline_layout.addWidget(self.spline_rb)
        
        self.spline_knots_spin = create_flexible_int_input(min_val=3, max_val=50, default=13)
        self.spline_knots_spin.setValue(self.processing_params['spline_knots'])
        self.spline_knots_spin.valueChanged.connect(self._on_spline_knots_changed)
        spline_layout.addWidget(self.spline_knots_spin)
        
        spline_layout.addStretch()
        method_layout.addLayout(spline_layout)
        
        # Gaussian filter
        gauss_layout = QtWidgets.QHBoxLayout()
        self.gaussian_rb = QtWidgets.QRadioButton("Gaussian filter, σ:")
        self.gaussian_rb.setChecked(self.processing_params['continuum_method'] == 'gaussian')
        self.gaussian_rb.toggled.connect(self._on_continuum_method_changed)
        self.continuum_method_group.addButton(self.gaussian_rb, 1)
        gauss_layout.addWidget(self.gaussian_rb)
        
        self.gauss_sigma_spin = create_flexible_double_input(min_val=0.1, max_val=100.0, default=10.0)
        self.gauss_sigma_spin.setValue(self.processing_params['continuum_sigma'])
        self.gauss_sigma_spin.valueChanged.connect(self._on_gauss_sigma_changed)
        gauss_layout.addWidget(self.gauss_sigma_spin)
        
        auto_sigma_btn = QtWidgets.QPushButton("Auto")
        auto_sigma_btn.setObjectName("auto_sigma_btn")
        auto_sigma_btn.clicked.connect(self._set_auto_sigma)
        gauss_layout.addWidget(auto_sigma_btn)
        
        gauss_layout.addStretch()
        method_layout.addLayout(gauss_layout)
        
        layout.addWidget(method_group)
        
        # Interactive continuum editing - now properly connected
        if self.continuum_widget:
            continuum_controls = self.continuum_widget.create_interactive_controls(self.options_frame)
            layout.addWidget(continuum_controls)
            
            # Initialize continuum points when entering this step
            self._initialize_continuum_points_if_needed()
        else:
            # Fallback when interactive continuum editing is not available
            unavailable_group = QtWidgets.QGroupBox("Interactive Continuum Editing (Unavailable)")
            unavailable_layout = QtWidgets.QVBoxLayout(unavailable_group)
            
            msg = QtWidgets.QLabel("Interactive continuum editing requires PyQtGraph.\nInstall with: pip install pyqtgraph")
            msg.setStyleSheet("color: #f59e0b; font-style: italic;")
            msg.setWordWrap(True)
            unavailable_layout.addWidget(msg)
            
            layout.addWidget(unavailable_group)
    
    def _on_continuum_method_changed(self):
        """Handle continuum method radio button changes"""
        if self.spline_rb.isChecked():
            self.processing_params['continuum_method'] = 'spline'
        elif self.gaussian_rb.isChecked():
            self.processing_params['continuum_method'] = 'gaussian'
        
        # Update continuum widget with new method BEFORE preview update
        if self.current_step == 3 and self.continuum_widget:
            # Inform the widget about the method change
            self.continuum_widget.set_current_method(self.processing_params['continuum_method'])
            
            # If not in interactive mode or no manual changes, recalculate continuum
            if not self.continuum_widget.is_interactive_mode() or not self.continuum_widget.has_manual_changes():
                # Get current parameter value
                if self.processing_params['continuum_method'] == 'gaussian':
                    try:
                        sigma_str = self.gauss_sigma_spin.value() if hasattr(self, 'gauss_sigma_spin') else 10.0
                        sigma = sigma_str if sigma_str != "auto" else None
                    except:
                        sigma = None
                    self.continuum_widget.update_continuum_from_fit(sigma)
                elif self.processing_params['continuum_method'] == 'spline':
                    try:
                        knotnum = self.spline_knots_spin.value() if hasattr(self, 'spline_knots_spin') else 13
                    except:
                        knotnum = 13
                    self.continuum_widget.update_continuum_from_fit(knotnum)
        
        # Then update preview
        self._update_preview()
        
        # Update continuum points for new method
        if self.current_step == 3:
            self._initialize_continuum_points_if_needed()
    
    def _initialize_continuum_points_if_needed(self):
        """Initialize continuum points when first entering step 3"""
        if self.current_step == 3 and self.continuum_widget:
            # Check if we already have continuum points
            current_points = self.continuum_widget.get_continuum_points()
            if not current_points:
                # Force calculation of initial continuum with current settings
                self._update_continuum_points_for_current_settings()
                
                # Also trigger a preview update to show the continuum
                self._update_preview()
    
    def _update_continuum_points_for_current_settings(self):
        """Update continuum points based on current method and parameters"""
        if self.current_step == 3 and self.continuum_widget:
            # Check if we have manual changes - don't overwrite them
            if hasattr(self.continuum_widget, 'has_manual_changes') and \
               self.continuum_widget.has_manual_changes():
                return
            
            method = self.processing_params['continuum_method']
            
            # Set the current method in the interactive widget
            self.continuum_widget.set_current_method(method)
            
            # Force reset to recalculate continuum with current parameters
            self.continuum_widget.reset_to_fitted_continuum()
            
            _LOGGER.debug(f"Updated continuum points for {method} method")
    
    def _create_step_4_apodization(self, layout):
        """Create step 4: Apodization exactly like original"""
        # Description
        desc = QtWidgets.QLabel("Apply edge tapering to prevent artifacts at spectrum boundaries.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Apodization options
        apod_group = QtWidgets.QGroupBox("Apodization Configuration")
        apod_layout = QtWidgets.QVBoxLayout(apod_group)
        
        self.apodize_cb = QtWidgets.QCheckBox("Apply edge apodization")
        self.apodize_cb.setChecked(self.processing_params['apply_apodization'])
        self.apodize_cb.toggled.connect(self._update_preview)
        apod_layout.addWidget(self.apodize_cb)
        
        # Apodization parameters
        param_layout = QtWidgets.QHBoxLayout()
        param_layout.addWidget(QtWidgets.QLabel("Edge fraction:"))
        
        self.apod_percent_spin = create_flexible_double_input(min_val=1.0, max_val=50.0, suffix=" %", default=10.0)
        self.apod_percent_spin.setValue(self.processing_params['apod_percent'])
        self.apod_percent_spin.valueChanged.connect(self._update_preview)
        param_layout.addWidget(self.apod_percent_spin)
        
        param_layout.addStretch()
        apod_layout.addLayout(param_layout)
        
        layout.addWidget(apod_group)
        
        # Information
        info_text = QtWidgets.QLabel(
            "Apodization applies a smooth taper to the spectrum edges, "
            "preventing discontinuities that could affect Fourier-based analysis."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #64748b; font-size: 10pt; font-style: italic;")
        layout.addWidget(info_text)
    
    def _create_step_5_review(self, layout):
        """Create step 5: Final Review exactly like original"""
        # Description
        desc = QtWidgets.QLabel("Review the complete preprocessing pipeline and finalize settings.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 11pt; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Summary
        summary_group = QtWidgets.QGroupBox("Preprocessing Summary")
        summary_layout = QtWidgets.QVBoxLayout(summary_group)
        
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        self._update_summary()
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        # Export options removed to simplify final step
    
    # Note: Previous/Next navigation methods removed - steps only advance via Apply button
    
    def apply_current_step(self):
        """Apply the current step's configuration exactly like original"""
        if not self.preview_calculator:
            return
        
        try:
            # CRITICAL FIX: Cache current step to avoid accessing potentially deleted widgets
            step_to_apply = self.current_step
            _LOGGER.debug(f"Applying step {step_to_apply}")
            
            # Apply the step processing
            if step_to_apply == 0:  # Masking & Clipping
                self._apply_step_0()
            elif step_to_apply == 1:  # Filtering
                self._apply_step_1()
            elif step_to_apply == 2:  # Rebinning
                self._apply_step_2()
            elif step_to_apply == 3:  # Continuum
                self._apply_step_3()
            elif step_to_apply == 4:  # Apodization
                self._apply_step_4()
            
            # Update preview after applying - wrapped in try-catch for button deletion issues
            try:
                self._update_preview()
            except RuntimeError as e:
                if "Internal C++ object" in str(e):
                    _LOGGER.warning(f"Widget deletion during preview update: {e}")
                    # Try to continue without preview update
                else:
                    raise
            
            # Update button states to enable/disable restart button - wrapped in try-catch
            try:
                self._update_button_states()
            except RuntimeError as e:
                if "Internal C++ object" in str(e):
                    _LOGGER.warning(f"Widget deletion during button state update: {e}")
                    # Try to continue without button state update
                else:
                    raise
            
            # Auto-advance to next step only if not on final step
            # (Final step button becomes "Finish" and doesn't auto-advance)
            if step_to_apply < self.total_steps - 1:  # Not on final step (step 5)
                # Stop any active masking mode before moving to next step
                if hasattr(self, 'masking_widget') and self.masking_widget:
                    try:
                        self.masking_widget.stop_masking_mode()
                    except RuntimeError as e:
                        if "Internal C++ object" in str(e):
                            _LOGGER.warning(f"Widget deletion during masking stop: {e}")
                        else:
                            raise
                
                self.current_step += 1
                
                # Update step display - wrapped in try-catch for button deletion issues
                try:
                    self._update_step_display()
                except RuntimeError as e:
                    if "Internal C++ object" in str(e):
                        _LOGGER.warning(f"Widget deletion during step display update: {e}")
                        # Try to continue without step display update
                    else:
                        raise
                
                # Final preview update - wrapped in try-catch
                try:
                    self._update_preview()
                except RuntimeError as e:
                    if "Internal C++ object" in str(e):
                        _LOGGER.warning(f"Widget deletion during final preview update: {e}")
                        # Continue without final preview update
                    else:
                        raise
            
        except RuntimeError as e:
            if "Internal C++ object" in str(e):
                _LOGGER.error(f"C++ object deletion error in step {self.current_step}: {e}")
                QtWidgets.QMessageBox.warning(self, "Widget Error", 
                    "A widget was unexpectedly deleted. The operation may have partially completed. Please try again.")
            else:
                _LOGGER.error(f"Runtime error applying step {self.current_step}: {e}")
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to apply step: {str(e)}")
        except Exception as e:
            _LOGGER.error(f"Error applying step {self.current_step}: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to apply step: {str(e)}")
    
    def restart_to_step_one(self):
        """Restart the advanced preprocessing workflow back to Step 1 (initial state)."""
        if not self.preview_calculator:
            return
        try:
            # Reset calculator state completely
            self.preview_calculator.reset()
            
            # Reset UI workflow to first step
            self.current_step = 0
            
            # Ensure interactive widgets are reset
            if self.continuum_widget and self.continuum_widget.is_interactive_mode():
                try:
                    self.continuum_widget.disable_interactive_mode()
                except Exception:
                    pass
            # Reset masking widget state and visuals like fresh start
            if hasattr(self, 'masking_widget') and self.masking_widget:
                try:
                    if getattr(self.masking_widget, 'masking_active', False):
                        self.masking_widget.stop_masking_mode()
                    self.masking_widget.clear_all_masks()
                except Exception:
                    pass
            
            # Update UI and preview
            self._update_step_display()
            self._update_preview()
            
            _LOGGER.info("Advanced preprocessing restarted to Step 1 (initial state)")
        except Exception as e:
            _LOGGER.error(f"Failed to restart preprocessing: {e}")
            QtWidgets.QMessageBox.warning(self, "Restart Failed", "Could not restart preprocessing. Please try again.")
    
    def finish_preprocessing(self):
        """Finish preprocessing and return results exactly like original"""
        if self.preview_calculator:
            # Get final processed spectrum directly from preview calculator
            final_wave, final_flux = self.preview_calculator.get_current_state()
            

            
            # CRITICAL FIX: Get the continuum from the step history instead of stored_continuum
            # which seems to get corrupted during GUI interactions
            continuum = None
            applied_steps = self.preview_calculator.applied_steps
            
            # Look for the continuum step in applied steps and extract the continuum
            for step in applied_steps:
                if step['type'] == 'continuum_fit':
                    # Re-run the continuum fitting to get the correct continuum
                    try:
                        method = step['kwargs'].get('method', 'spline')
                        if method == 'spline':
                            knotnum = step['kwargs'].get('knotnum', 13)

                            
                            # Get the state before continuum fitting
                            # This requires reconstructing the flux before continuum removal
                            log_rebin_step_idx = None
                            for i, s in enumerate(applied_steps):
                                if s['type'] == 'log_rebin_with_scaling':
                                    log_rebin_step_idx = i
                                    break
                            
                            if log_rebin_step_idx is not None:
                                # Get flux state right after log rebinning (before continuum fitting)
                                # We need to reconstruct this from the current flat flux
                                from snid_sage.snid.preprocessing import fit_continuum
                                
                                # The final_flux is the continuum-removed version
                                # We need to get the flux before continuum removal
                                # Let's recompute the continuum using the same logic as original
                                
                                # Find the flux before continuum step by re-running preprocessing up to that point
                                temp_calc = type(self.preview_calculator)(self.original_wave, self.original_flux)
                                
                                # Replay steps up to (but not including) continuum fitting
                                for i, step in enumerate(applied_steps):
                                    if step['type'] == 'continuum_fit':
                                        break
                                    step_kwargs = step['kwargs'].copy()
                                    step_kwargs.pop('step_index', None)  # Remove step_index if present
                                    temp_calc.apply_step(step['type'], **step_kwargs)
                                
                                # Now get the flux before continuum removal
                                _, flux_before_continuum = temp_calc.get_current_state()
                                
                                # Fit continuum to this flux
                                flat_flux, continuum = fit_continuum(flux_before_continuum, method=method, knotnum=knotnum)

                                break
                        elif method == 'gaussian':
                            sigma = step['kwargs'].get('sigma', None)

                            # Similar logic for gaussian...
                            
                    except Exception as e:

                        continuum = None
                        break
                        
                elif step['type'] == 'interactive_continuum':
                    # Handle manual continuum editing
                    try:

                        # Get the manual continuum from the step
                        manual_continuum = step['kwargs'].get('manual_continuum', None)
                        if manual_continuum is not None:
                            continuum = manual_continuum.copy()

                            break
                        else:
                            # Try to get it from the continuum widget
                            if self.continuum_widget and hasattr(self.continuum_widget, 'get_manual_continuum_array'):
                                _, manual_continuum = self.continuum_widget.get_manual_continuum_array()
                                if len(manual_continuum) > 0:
                                    continuum = manual_continuum.copy()

                                    break
                    except Exception as e:

                        continuum = None
                        break
            
            # Fallback to stored continuum if recomputation failed
            if continuum is None:
                continuum_wave, stored_continuum = self.preview_calculator.get_continuum_from_fit()
                continuum = stored_continuum

            

            
            # Get edge information from preview calculator (properly tracked through steps)
            left_edge, right_edge = self.preview_calculator.get_current_edges()
            
            # Fallback to calculation if edges weren't tracked properly
            if left_edge is None or right_edge is None:
                # For continuum-subtracted spectra, negative values are valid
                valid_mask = (final_flux != 0) & np.isfinite(final_flux)
                if np.any(valid_mask):
                    left_edge = np.argmax(valid_mask)
                    right_edge = len(final_flux) - 1 - np.argmax(valid_mask[::-1])
                else:
                    left_edge = 0
                    right_edge = len(final_flux) - 1

            
            # Determine what the final_flux actually represents based on the applied steps
            has_continuum_step = any(step['type'] in ['continuum_fit', 'interactive_continuum'] 
                                   for step in applied_steps)
            

            
            if has_continuum_step and continuum is not None:
                # final_flux is the flattened (continuum-removed) spectrum after continuum step
                flat_spectrum = final_flux.copy()  # This is already flat (continuum-removed)
                
                # Generate display versions using the correct logic
                # display_flux: Reconstruct flux using (flat + 1) * continuum
                display_flux = (flat_spectrum + 1.0) * continuum
                display_flat = flat_spectrum  # Already flattened
                
                # For log_flux, we need to reconstruct what the flux was before continuum removal
                # This represents the scaled flux on log grid (after log rebinning and scaling)
                log_flux = display_flux.copy()  # Reconstructed flux represents the log_flux
                
            else:
                # No continuum step applied - final_flux represents the scaled flux after log rebinning
                # This happens when only log rebinning + scaling steps are applied
                log_flux = final_flux.copy()  # This is the scaled flux on log grid
                flat_spectrum = np.zeros_like(final_flux)  # No actual flattening occurred
                continuum = np.ones_like(final_flux)  # Unity continuum (no continuum removal)
                
                # For display versions when no continuum removal
                display_flux = final_flux.copy()  # Scaled flux
                display_flat = final_flux.copy()  # Same data (no actual flattening occurred)
            

            
            # CRITICAL FIX: Apply proper apodization to create tapered_flux
            # This matches what standard preprocessing does and is required for forced redshift analysis
            nz = np.nonzero(flat_spectrum)[0]
            if nz.size:
                l1, l2 = nz[0], nz[-1]
            else:
                l1, l2 = 0, len(flat_spectrum) - 1
                
            # Import apodization function from SNID preprocessing
            from snid_sage.snid.preprocessing import apodize
            apodize_percent = 10.0  # Default apodization percentage
            tapered_flux = apodize(flat_spectrum, l1, l2, percent=apodize_percent)
            


            # CRITICAL FIX: Update display versions to use apodized data like quick preprocessing
            # Quick preprocessing uses: display_flat = tapered_flux (apodized continuum-removed)
            # We need to match this behavior for consistency
            if has_continuum_step and continuum is not None:
                # For continuum case: display_flat should be the apodized flat spectrum (tapered_flux)
                display_flat = tapered_flux  # Use apodized version like quick preprocessing
                # display_flux should also be reconstructed from the apodized version
                display_flux = (tapered_flux + 1.0) * continuum  # Reconstruct from apodized flat
            else:
                # For no-continuum case: both should use the apodized version
                display_flat = tapered_flux  # Use apodized version
                display_flux = tapered_flux  # Same data since no continuum

            # Create processed spectrum dictionary like old GUI with proper display versions
            processed_spectrum = {
                'log_wave': final_wave,
                'log_flux': log_flux,  # Scaled flux on log grid (or reconstructed if continuum was applied)
                'flat_flux': flat_spectrum,  # Continuum-removed version (or same as log_flux if no continuum) - REQUIRED BY ANALYSIS
                'tapered_flux': tapered_flux,  # FIXED: Properly apodized final version for FFT correlation - REQUIRED BY ANALYSIS
                'continuum': continuum,  # Stored or unity continuum
                'nonzero_mask': slice(left_edge, right_edge + 1),  # Slice for non-zero region - REQUIRED BY ANALYSIS
                # Generate display versions correctly - NOW CONSISTENT WITH QUICK PREPROCESSING
                'display_flux': display_flux,  # For flux view - reconstructed from apodized data
                'display_flat': display_flat,  # For flat view - apodized continuum-removed (like quick preprocessing)
                'advanced_preprocessing': True,
                'preprocessing_type': 'advanced',
                'left_edge': left_edge,  # Proper edge information for zero filtering
                'right_edge': right_edge,  # Proper edge information for zero filtering
                'input_spectrum': {'wave': self.original_wave, 'flux': self.original_flux},  # Store original input
                'grid_params': {
                    'NW': 1024,  # Standard SNID grid size
                    'W0': 2500.0,  # Standard min wavelength
                    'W1': 10000.0,  # Standard max wavelength 
                    'DWLOG': np.log(10000.0 / 2500.0) / 1024  # Standard DWLOG calculation
                }
            }
            

            
            # Store in parent GUI's app controller
            if hasattr(self.parent(), 'app_controller'):
                self.parent().app_controller.set_processed_spectrum(processed_spectrum)
                _LOGGER.info("Processed spectrum stored in app controller")
            
            # Store results for dialog
            self.result = {
                'processed_wave': final_wave,
                'processed_flux': final_flux,
                'processing_steps': self.preview_calculator.applied_steps.copy(),
                'mask_regions': self.masking_widget.get_mask_regions() if self.masking_widget else [],
                'success': True
            }
            
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No preprocessing data available.")
    
    # Step application methods matching original exactly
    def _apply_step_0(self):
        """Apply masking and clipping operations exactly like original"""
        # Apply masking if any regions are defined
        if self.masking_widget:
            mask_regions = self.masking_widget.get_mask_regions()
            if mask_regions:
                self.preview_calculator.apply_step("masking", mask_regions=mask_regions, step_index=0)
        
        # Apply clipping operations with safe widget access
        # CRITICAL FIX: Cache widget values safely to avoid accessing deleted C++ objects
        apply_aband = False
        apply_sky = False
        sky_width = 40.0  # default fallback
        
        if hasattr(self, 'aband_cb') and self.aband_cb is not None:
            try:
                apply_aband = self.aband_cb.isChecked()
            except RuntimeError as e:
                _LOGGER.warning(f"Widget access error for aband_cb: {e}, using default value {apply_aband}")
        
        if hasattr(self, 'sky_cb') and self.sky_cb is not None:
            try:
                apply_sky = self.sky_cb.isChecked()
            except RuntimeError as e:
                _LOGGER.warning(f"Widget access error for sky_cb: {e}, using default value {apply_sky}")
        
        if hasattr(self, 'sky_width_spin') and self.sky_width_spin is not None:
            try:
                sky_width = self.sky_width_spin.value()
            except RuntimeError as e:
                _LOGGER.warning(f"Widget access error for sky_width_spin: {e}, using default value {sky_width}")
        
        if apply_aband:
            self.preview_calculator.apply_step("clipping", clip_type="aband", step_index=0)
        
        if apply_sky:
            self.preview_calculator.apply_step("clipping", clip_type="sky", width=sky_width, step_index=0)
    
    def _apply_step_1(self):
        """Apply Savitzky-Golay filtering exactly like original"""
        filter_type = self.processing_params['filter_type']
        
        # CRITICAL FIX: Cache widget values immediately to avoid accessing deleted C++ objects
        # This prevents the "Internal C++ object already deleted" error when widgets are cleaned up
        try:
            if filter_type == 'fixed':
                # Cache values safely with proper error handling
                window = 11  # default fallback
                polyorder = 3  # default fallback
                
                if hasattr(self, 'fixed_window_spin') and self.fixed_window_spin is not None:
                    try:
                        window = self.fixed_window_spin.value()
                    except RuntimeError as e:
                        _LOGGER.warning(f"Widget access error for fixed_window_spin: {e}, using default value {window}")
                
                if hasattr(self, 'polyorder_spin') and self.polyorder_spin is not None:
                    try:
                        polyorder = self.polyorder_spin.value()
                    except RuntimeError as e:
                        _LOGGER.warning(f"Widget access error for polyorder_spin: {e}, using default value {polyorder}")
                
                self.preview_calculator.apply_step("savgol_filter", filter_type="fixed", 
                                                 value=window, polyorder=polyorder, step_index=1)
                
            elif filter_type == 'wavelength':
                # Cache values safely with proper error handling
                fwhm = 5.0  # default fallback
                polyorder = 3  # default fallback
                
                if hasattr(self, 'wave_fwhm_spin') and self.wave_fwhm_spin is not None:
                    try:
                        fwhm = self.wave_fwhm_spin.value()
                    except RuntimeError as e:
                        _LOGGER.warning(f"Widget access error for wave_fwhm_spin: {e}, using default value {fwhm}")
                
                if hasattr(self, 'polyorder_spin') and self.polyorder_spin is not None:
                    try:
                        polyorder = self.polyorder_spin.value()
                    except RuntimeError as e:
                        _LOGGER.warning(f"Widget access error for polyorder_spin: {e}, using default value {polyorder}")
                
                self.preview_calculator.apply_step("savgol_filter", filter_type="wavelength",
                                                 value=fwhm, polyorder=polyorder, step_index=1)
            # If filter_type == 'none', don't apply anything
            
        except Exception as e:
            _LOGGER.error(f"Error in _apply_step_1: {e}")
            # Fallback: apply no filtering to prevent complete failure
            pass
    
    def _apply_step_2(self):
        """Apply log-wavelength rebinning and flux scaling exactly like original"""
        # Log rebinning is always applied (required for SNID)
        # CRITICAL FIX: Cache widget values safely to avoid accessing deleted C++ objects
        scale_flux = True  # default fallback
        
        if hasattr(self, 'flux_scaling_cb') and self.flux_scaling_cb is not None:
            try:
                scale_flux = self.flux_scaling_cb.isChecked()
            except RuntimeError as e:
                _LOGGER.warning(f"Widget access error for flux_scaling_cb: {e}, using default value {scale_flux}")
        
        self.preview_calculator.apply_step("log_rebin_with_scaling", scale_to_mean=scale_flux, step_index=2)
    
    def _apply_step_3(self):
        """Apply continuum fitting exactly like original"""
        # Check if interactive continuum editing is active
        if self.continuum_widget and self.continuum_widget.is_interactive_mode():
            # Apply interactive continuum
            wave_grid, manual_continuum = self.continuum_widget.get_manual_continuum_array()
            if len(manual_continuum) > 0:
                self.preview_calculator.apply_step("interactive_continuum", 
                                                 manual_continuum=manual_continuum,
                                                 wave_grid=wave_grid, step_index=3)
        else:
            # Apply automatic continuum fitting
            method = self.processing_params['continuum_method']
            
            if method == 'spline':
                # CRITICAL FIX: Cache widget values safely to avoid accessing deleted C++ objects
                knotnum = 13  # default fallback
                
                if hasattr(self, 'spline_knots_spin') and self.spline_knots_spin is not None:
                    try:
                        knotnum = self.spline_knots_spin.value()
                    except RuntimeError as e:
                        _LOGGER.warning(f"Widget access error for spline_knots_spin: {e}, using default value {knotnum}")
                
                self.preview_calculator.apply_step("continuum_fit", method="spline", 
                                                 knotnum=knotnum, step_index=3)
                                                 
            elif method == 'gaussian':
                # CRITICAL FIX: Cache widget values safely to avoid accessing deleted C++ objects
                sigma = 10.0  # default fallback
                
                if hasattr(self, 'gauss_sigma_spin') and self.gauss_sigma_spin is not None:
                    try:
                        sigma = self.gauss_sigma_spin.value()
                    except RuntimeError as e:
                        _LOGGER.warning(f"Widget access error for gauss_sigma_spin: {e}, using default value {sigma}")
                
                self.preview_calculator.apply_step("continuum_fit", method="gaussian",
                                                 sigma=sigma, step_index=3)
    
    def _apply_step_4(self):
        """Apply apodization exactly like original"""
        # CRITICAL FIX: Cache widget values safely to avoid accessing deleted C++ objects
        apply_apodization = False  # default fallback
        percent = 10.0  # default fallback
        
        if hasattr(self, 'apodize_cb') and self.apodize_cb is not None:
            try:
                apply_apodization = self.apodize_cb.isChecked()
            except RuntimeError as e:
                _LOGGER.warning(f"Widget access error for apodize_cb: {e}, using default value {apply_apodization}")
        
        if apply_apodization:
            if hasattr(self, 'apod_percent_spin') and self.apod_percent_spin is not None:
                try:
                    percent = self.apod_percent_spin.value()
                except RuntimeError as e:
                    _LOGGER.warning(f"Widget access error for apod_percent_spin: {e}, using default value {percent}")
            
            self.preview_calculator.apply_step("apodization", percent=percent, step_index=4)
    
    # UI update methods
    def _update_button_states(self):
        """Update button states and text based on current step"""
        # Update Apply button text for final step
        if hasattr(self, 'apply_btn'):
            if self.current_step == self.total_steps - 1:  # Final step (Review)
                self.apply_btn.setText("Finish")
                # Disconnect and reconnect signals properly
                try:
                    self.apply_btn.clicked.disconnect()
                except:
                    pass  # Ignore if no connections exist
                self.apply_btn.clicked.connect(self.finish_preprocessing)
                # Update styling for finish button - enhanced buttons will handle styling
            else:
                self.apply_btn.setText("Apply Step")
                # Disconnect and reconnect signals properly
                try:
                    self.apply_btn.clicked.disconnect()
                except:
                    pass  # Ignore if no connections exist
                self.apply_btn.clicked.connect(self.apply_current_step)
                # Restore normal apply button styling - enhanced buttons will handle styling
        
        # Restart button is enabled when any step beyond the first is active or any steps were applied
        if hasattr(self, 'restart_btn'):
            can_restart = False
            if hasattr(self, 'preview_calculator') and self.preview_calculator:
                try:
                    can_restart = (self.current_step > 0) or (len(getattr(self.preview_calculator, 'applied_steps', [])) > 0)
                except Exception:
                    can_restart = self.current_step > 0
            # Use enhanced button state management if available
            if hasattr(self, 'button_manager') and self.button_manager:
                self.button_manager.update_button_state(self.restart_btn, can_restart)
            else:
                self.restart_btn.setEnabled(can_restart)
    
    def _update_preview(self):
        """Update the plot preview with dual plots exactly like original Tkinter version"""
        if not self.preview_calculator or not self.plot_manager:
            return
        
        try:
            # Get current state (what's already applied)
            current_wave, current_flux = self.preview_calculator.get_current_state()
            
            # For continuum step, show interactive preview ONLY if we're on step 3 AND continuum hasn't been applied yet
            if self.current_step == 3 and self.continuum_widget and not self._is_continuum_step_applied():
                # Check if we have continuum data to show
                continuum_points = self.continuum_widget.get_continuum_points()
                if continuum_points:
                    # CRITICAL FIX: Get preview data using the current manual continuum
                    # This ensures real-time updates during dragging
                    if self.continuum_widget.is_interactive_mode():
                        # Use the manual continuum for real-time preview during interactive editing
                        wave_grid, manual_continuum = self.continuum_widget.get_manual_continuum_array()
                        if len(manual_continuum) > 0:
                            preview_wave, preview_flux = self.preview_calculator._calculate_manual_continuum_preview(manual_continuum)
                        else:
                            preview_wave, preview_flux = self.continuum_widget.get_preview_data()
                    else:
                        preview_wave, preview_flux = self.continuum_widget.get_preview_data()
                    
                    # Apply zero padding removal for clean spectrum display
                    preview_wave, preview_flux = self._apply_zero_padding_removal(preview_wave, preview_flux)
                    # FIXED: Also apply zero padding removal to current state (top plot)
                    current_wave, current_flux = self._apply_zero_padding_removal(current_wave, current_flux)
                    
                    interactive_mode = self.continuum_widget.is_interactive_mode()
                    
                    self.plot_manager.update_interactive_preview(
                        current_wave, current_flux, continuum_points, 
                        preview_wave, preview_flux, interactive_mode
                    )
                    return
            
            # Standard preview update: current state vs preview of current step
            # Calculate preview for the current step (what would happen if we apply it)
            preview_wave, preview_flux = self._calculate_current_step_preview()
            
            # Apply zero padding removal for ALL steps to ensure clean spectrum display
            preview_wave, preview_flux = self._apply_zero_padding_removal(preview_wave, preview_flux)
            # FIXED: Also apply zero padding removal to current state (top plot) for ALL steps
            current_wave, current_flux = self._apply_zero_padding_removal(current_wave, current_flux)
            
            # Get mask regions for visualization - ONLY in step 0
            mask_regions = []
            if self.current_step == 0 and self.masking_widget:
                mask_regions = self.masking_widget.get_mask_regions()
            
            # Show current state in top plot, preview in bottom plot
            self.plot_manager.update_standard_preview(
                current_wave, current_flux, preview_wave, preview_flux, mask_regions
            )
            
        except Exception as e:
            _LOGGER.error(f"Error updating preview: {e}")
    
    def _apply_zero_padding_removal(self, wave, flux):
        """Apply zero padding removal like the main GUI"""
        try:
            if wave is None or flux is None:
                _LOGGER.debug("Zero padding removal: wave or flux is None")
                return wave, flux
                
            # Find valid regions manually (including negative values for continuum-subtracted spectra)
            valid_mask = (flux != 0) & np.isfinite(flux)
            if np.any(valid_mask):
                left_edge = np.argmax(valid_mask)
                right_edge = len(flux) - 1 - np.argmax(valid_mask[::-1])
                filtered_wave = wave[left_edge:right_edge+1]
                filtered_flux = flux[left_edge:right_edge+1]
                _LOGGER.debug(f"Zero padding removal: {len(wave)} -> {len(filtered_wave)} points (removed {len(wave) - len(filtered_wave)} points)")
                return filtered_wave, filtered_flux
            
            # If no nonzero data found, return original arrays
            _LOGGER.debug("Zero padding removal: no nonzero data found")
            return wave, flux
            
        except Exception as e:
            _LOGGER.warning(f"Error applying zero padding removal: {e}")
            return wave, flux
    
    def _calculate_current_step_preview(self):
        """Calculate preview for current step using PreviewCalculator exactly like original"""
        if self.current_step == 0:  # Masking & Clipping Operations
            # Start with current state
            preview_wave, preview_flux = self.preview_calculator.get_current_state()
            
            # Apply masking first if any masks exist
            if self.masking_widget:
                mask_regions = self.masking_widget.get_mask_regions()
                if mask_regions:
                    preview_wave, preview_flux = self.preview_calculator.preview_step("masking", mask_regions=mask_regions)
            
            # Then apply clipping operations
            if hasattr(self, 'aband_cb') and self.aband_cb.isChecked():
                temp_calc = type(self.preview_calculator)(preview_wave, preview_flux)
                preview_wave, preview_flux = temp_calc.preview_step("clipping", clip_type="aband")
            
            if hasattr(self, 'sky_cb') and self.sky_cb.isChecked():
                try:
                    width = self.sky_width_spin.value() if hasattr(self, 'sky_width_spin') else 40.0
                    temp_calc = type(self.preview_calculator)(preview_wave, preview_flux)
                    preview_wave, preview_flux = temp_calc.preview_step("clipping", clip_type="sky", width=width)
                except:
                    pass
            
            return preview_wave, preview_flux
            
        elif self.current_step == 1:  # Savitzky-Golay Filtering
            # Get filter parameters from UI
            filter_type = self.processing_params['filter_type']
            if filter_type == "none":
                return self.preview_calculator.get_current_state()
            
            try:
                polyorder = self.polyorder_spin.value() if hasattr(self, 'polyorder_spin') else 3
                
                if filter_type == "fixed":
                    value = self.fixed_window_spin.value() if hasattr(self, 'fixed_window_spin') else 11
                    return self.preview_calculator.preview_step("savgol_filter", 
                                                              filter_type=filter_type, value=value, polyorder=polyorder)
                elif filter_type == "wavelength":
                    value = self.wave_fwhm_spin.value() if hasattr(self, 'wave_fwhm_spin') else 5.0
                    return self.preview_calculator.preview_step("savgol_filter", 
                                                              filter_type=filter_type, value=value, polyorder=polyorder)
            except:
                pass
            
            return self.preview_calculator.get_current_state()
            
        elif self.current_step == 2:  # Log-wavelength Rebinning & Flux Scaling
            # Use the synchronized flux scaling parameter
            scale_to_mean = self.processing_params['flux_scaling']
            return self.preview_calculator.preview_step("log_rebin_with_scaling", scale_to_mean=scale_to_mean)
            
        elif self.current_step == 3:  # Continuum Fitting & Interactive Editing
            # Get continuum parameters from UI
            method = self.processing_params['continuum_method']
            if method == "gaussian":
                try:
                    sigma = self.gauss_sigma_spin.value() if hasattr(self, 'gauss_sigma_spin') else 10.0
                    return self.preview_calculator.preview_step("continuum_fit", method="gaussian", sigma=sigma)
                except:
                    pass
            elif method == "spline":
                try:
                    knotnum = self.spline_knots_spin.value() if hasattr(self, 'spline_knots_spin') else 13
                    return self.preview_calculator.preview_step("continuum_fit", method="spline", knotnum=knotnum)
                except:
                    pass
            
            return self.preview_calculator.get_current_state()
            
        elif self.current_step == 4:  # Apodization
            if hasattr(self, 'apodize_cb') and self.apodize_cb.isChecked():
                try:
                    percent = self.apod_percent_spin.value() if hasattr(self, 'apod_percent_spin') else 10.0
                    if 0 <= percent <= 50:
                        return self.preview_calculator.preview_step("apodization", percent=percent)
                except:
                    pass
        
        # Fallback: return current state
        return self.preview_calculator.get_current_state()
    
    def _is_continuum_step_applied(self):
        """Check if the continuum step has been applied"""
        if not self.preview_calculator:
            return False
        
        # Check if any continuum-related steps have been applied
        for step in self.preview_calculator.applied_steps:
            step_type = step.get('type', '')
            if step_type in ['continuum_fit', 'interactive_continuum']:
                return True
        return False
    
    def _update_summary(self):
        """Update the preprocessing summary exactly like original"""
        if not hasattr(self, 'summary_text') or not self.preview_calculator:
            return
        
        summary = "Applied Preprocessing Steps:\n\n"
        
        if len(self.preview_calculator.applied_steps) == 0:
            summary += "No preprocessing steps applied yet.\n"
        else:
            for i, step in enumerate(self.preview_calculator.applied_steps):
                summary += f"{i+1}. {step['type'].replace('_', ' ').title()}\n"
                if 'kwargs' in step:
                    for key, value in step['kwargs'].items():
                        if key != 'step_index':
                            summary += f"   {key}: {value}\n"
                summary += "\n"
        
        self.summary_text.setPlainText(summary)
    
    # Utility methods
    def _set_auto_sigma(self):
        """Set automatic sigma for Gaussian continuum fitting"""
        if hasattr(self, 'gauss_sigma_spin') and self.preview_calculator:
            try:
                # Calculate automatic sigma based on current flux
                current_wave, current_flux = self.preview_calculator.get_current_state()
                if SNID_AVAILABLE:
                    from snid_sage.snid.preprocessing import calculate_auto_gaussian_sigma
                    auto_sigma = calculate_auto_gaussian_sigma(current_flux)
                    self.gauss_sigma_spin.setValue(auto_sigma)
                    
                    # Trigger continuum update if we're on step 3
                    if self.current_step == 3 and self.continuum_widget and \
                       self.processing_params['continuum_method'] == 'gaussian':
                        if not self.continuum_widget.is_interactive_mode() or not self.continuum_widget.has_manual_changes():
                            self.continuum_widget.update_continuum_from_fit(auto_sigma)
                else:
                    # Fallback estimation
                    auto_sigma = len(current_flux) * 0.01
                    self.gauss_sigma_spin.setValue(auto_sigma)
            except Exception as e:
                _LOGGER.error(f"Error calculating auto sigma: {e}")
    
    # Export functionality removed
    
    def _cleanup_resources(self):
        """Clean up PyQtGraph widgets and interactive components"""
        try:
            _LOGGER.debug("Cleaning up preprocessing dialog resources...")
            
            # Clean up interactive widgets
            if hasattr(self, 'masking_widget') and self.masking_widget:
                try:
                    if hasattr(self.masking_widget, 'cleanup'):
                        self.masking_widget.cleanup()
                    self.masking_widget = None
                except Exception as e:
                    _LOGGER.debug(f"Error cleaning up masking widget: {e}")
            
            if hasattr(self, 'continuum_widget') and self.continuum_widget:
                try:
                    if hasattr(self.continuum_widget, 'cleanup'):
                        self.continuum_widget.cleanup()
                    self.continuum_widget = None
                except Exception as e:
                    _LOGGER.debug(f"Error cleaning up continuum widget: {e}")
            
            # Clean up PyQtGraph plot widgets
            if hasattr(self, 'top_plot_widget') and self.top_plot_widget:
                try:
                    self.top_plot_widget.clear()
                    # Force close any OpenGL contexts
                    if hasattr(self.top_plot_widget, 'close'):
                        self.top_plot_widget.close()
                    self.top_plot_widget = None
                except Exception as e:
                    _LOGGER.debug(f"Error cleaning up top plot widget: {e}")
            
            if hasattr(self, 'bottom_plot_widget') and self.bottom_plot_widget:
                try:
                    self.bottom_plot_widget.clear()
                    # Force close any OpenGL contexts
                    if hasattr(self.bottom_plot_widget, 'close'):
                        self.bottom_plot_widget.close()
                    self.bottom_plot_widget = None
                except Exception as e:
                    _LOGGER.debug(f"Error cleaning up bottom plot widget: {e}")
            
            # Clean up preview calculator
            if hasattr(self, 'preview_calculator') and self.preview_calculator:
                try:
                    # Disconnect signals
                    if hasattr(self.preview_calculator, 'stage_memory_updated'):
                        self.preview_calculator.stage_memory_updated.disconnect()
                    self.preview_calculator = None
                except Exception as e:
                    _LOGGER.debug(f"Error cleaning up preview calculator: {e}")
            
            # Clean up plot manager
            if hasattr(self, 'plot_manager') and self.plot_manager:
                try:
                    if hasattr(self.plot_manager, 'cleanup'):
                        self.plot_manager.cleanup()
                    self.plot_manager = None
                except Exception as e:
                    _LOGGER.debug(f"Error cleaning up plot manager: {e}")
            
            _LOGGER.debug("Preprocessing dialog cleanup completed")
            
        except Exception as e:
            _LOGGER.debug(f"Error during preprocessing dialog cleanup: {e}")
    
    def closeEvent(self, event):
        """Handle dialog closing with proper cleanup"""
        try:
            _LOGGER.debug("Preprocessing dialog closing, cleaning up resources...")
            self._cleanup_resources()
            super().closeEvent(event)
        except Exception as e:
            _LOGGER.debug(f"Error during preprocessing dialog close: {e}")
            # Accept event even if cleanup fails
            event.accept()
    
    def reject(self):
        """Handle dialog rejection with cleanup"""
        try:
            self._cleanup_resources()
            super().reject()
        except Exception:
            # Call parent reject even if cleanup fails
            try:
                super().reject()
            except:
                pass
    
    def accept(self):
        """Handle dialog acceptance with cleanup"""
        try:
            self._cleanup_resources()
            super().accept()
        except Exception:
            # Call parent accept even if cleanup fails
            try:
                super().accept()
            except:
                pass 