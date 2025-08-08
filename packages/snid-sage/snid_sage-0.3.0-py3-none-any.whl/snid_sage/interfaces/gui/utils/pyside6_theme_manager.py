"""
SNID SAGE - PySide6 Unified Theme Manager
==========================================

Centralized theme management for PySide6 GUI components, providing:
- Consistent color schemes across all PySide6 widgets and dialogs
- Platform-specific theme adjustments (macOS, Windows, Linux)
- Centralized Qt stylesheet generation
- Theme color access for custom components

This manager ensures all PySide6 components use the same theming system
and eliminates duplication of theme definitions across the codebase.

Developed by Fiorenzo Stoppa for SNID SAGE
"""

from typing import Dict, Any, Optional
import platform

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_theme')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_theme')

# Import platform configuration if available
try:
    from snid_sage.shared.utils.config.platform_config import get_platform_config
    _PLATFORM_CONFIG = get_platform_config()
except ImportError:
    _PLATFORM_CONFIG = None


class PySide6ThemeManager:
    """
    Unified theme manager for all PySide6 GUI components
    
    This class provides centralized theme management including:
    - Base color palette with platform-specific adjustments
    - Workflow button colors matching Tkinter implementation
    - Complete Qt stylesheet generation
    - Theme color access methods for custom components
    """
    
    def __init__(self):
        """Initialize the PySide6 theme manager"""
        self.platform_config = _PLATFORM_CONFIG
        
        # Initialize base theme colors
        self._init_base_theme_colors()
        
        # Apply platform-specific adjustments
        self._apply_platform_adjustments()
        
        _LOGGER.debug("PySide6 Theme Manager initialized")
    
    def _init_base_theme_colors(self):
        """Initialize base theme color palette"""
        self.theme_colors = {
            # Backgrounds
            'bg_primary': '#f8fafc',      # Main background
            'bg_secondary': '#ffffff',    # Cards, dialogs  
            'bg_tertiary': '#f1f5f9',     # Subtle backgrounds
            'bg_disabled': '#e2e8f0',     # Disabled elements
            
            # Text colors
            'text_primary': '#1e293b',    # Main text
            'text_secondary': '#475569',  # Secondary text
            'text_muted': '#94a3b8',      # Disabled/muted text
            'text_on_accent': '#ffffff',  # Text on colored backgrounds
            
            # Interactive elements
            'border': '#cbd5e1',          # Borders and separators
            'hover': '#f1f5f9',           # Hover backgrounds
            'active': '#e2e8f0',          # Active/pressed states
            'focus': '#3b82f6',           # Focus indicators
            'accent_primary': '#3b82f6',  # Default accent/selection colour (blue)
            
            # Workflow button colors (matching Tkinter system exactly)
            'btn_load': '#6E6E6E',        # Load button – medium grey
            'btn_redshift': '#FFA600',    # Redshift - amber
            'btn_preprocessing': '#FF6361',    # Preprocessing - coral
            'btn_analysis': '#BC5090',    # Analysis - magenta
            'btn_advanced': '#58508D',    # Advanced features - purple
            'btn_ai': '#003F5C',          # AI features - deep blue
            'btn_settings': '#7A8585',    # Settings button - graphite
            'btn_reset': '#A65965',       # Reset button - cranberry
            
            # Standard button colors
            'btn_primary': '#3b82f6',     # Blue - main actions
            'btn_primary_hover': '#2563eb',
            'btn_secondary': '#6b7280',   # Gray - secondary actions
            'btn_secondary_hover': '#4b5563',
            'btn_success': '#10b981',     # Green - positive actions
            'btn_success_hover': '#059669',
            'btn_warning': '#f59e0b',     # Orange - warning actions
            'btn_warning_hover': '#d97706',
            'btn_danger': '#ef4444',      # Red - destructive actions
            'btn_danger_hover': '#dc2626',
            'btn_info': '#6366f1',        # Indigo - info actions
            'btn_info_hover': '#4f46e5',
            'btn_accent': '#8b5cf6',      # Purple - special features
            'btn_accent_hover': '#7c3aed',
            'btn_neutral': '#9ca3af',     # Default button color
            'btn_neutral_hover': '#6b7280',
            
            # Plot colors (for PyQtGraph and matplotlib)
            'plot_bg': '#ffffff',
            'plot_text': '#000000',
            'plot_grid': '#e2e8f0',
            'plot_line': '#3b82f6',
        }
    
    def _apply_platform_adjustments(self):
        """Apply platform-specific theme adjustments"""
        if not self.platform_config:
            return
            
        if self.platform_config.is_macos:
            # macOS-specific color adjustments
            self.theme_colors.update({
                'bg_primary': '#f5f5f5',
                'border': '#d1d1d1',
                'focus': '#007aff',
                'accent_primary': '#007aff',
                'btn_primary': '#007aff',
            })
            _LOGGER.debug("Applied macOS theme adjustments")
            
        elif self.platform_config.is_linux:
            # Linux-specific color adjustments
            self.theme_colors.update({
                'bg_primary': '#f6f6f6',
                'border': '#c0c0c0',
                'focus': '#4a90e2',
                'accent_primary': '#4a90e2',
            })
            _LOGGER.debug("Applied Linux theme adjustments")
        
        # Windows uses default colors - no adjustments needed
    
    def get_color(self, color_key: str) -> str:
        """
        Get theme color by key
        
        Args:
            color_key: Key for the desired color
            
        Returns:
            Color value as hex string, or black as fallback
        """
        return self.theme_colors.get(color_key, '#000000')
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get all theme colors as a dictionary"""
        return self.theme_colors.copy()
    
    def generate_qt_stylesheet(self) -> str:
        """
        Generate complete Qt stylesheet for the application
        
        Returns:
            Complete Qt stylesheet string with all theme colors applied
        """
        colors = self.theme_colors
        
        stylesheet = f"""
        /* Global widget styling */
        QWidget {{ 
            background: {colors['bg_primary']}; 
            color: {colors['text_primary']}; 
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 9pt;
        }}
        
        /* Frame styling for panels */
        QFrame#left_panel {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            margin: 2px;
        }}
        
        QFrame#header_frame {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px;
        }}
        
        /* Status label styling */
        QLabel#status_label {{
            background: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px;
            font-weight: bold;
        }}
        
        /* GroupBox styling */
        QGroupBox {{
            font-weight: bold;
            font-size: 10pt;
            border: 2px solid {colors['border']};
            border-radius: 4px;
            margin-top: 6px;
            padding-top: 10px;
            background: {colors['bg_secondary']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: {colors['text_primary']};
            background: {colors['bg_secondary']};
        }}
        
        /* Basic button styling - workflow manager will override specific buttons */
        QPushButton {{
            background: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 4px;
            padding: 4px 8px;
            min-height: 24px;
            font-weight: bold;
            font-size: 9pt;
        }}
        
        /* Main workflow buttons - larger size for ALL states */
        QPushButton#unified_load_spectrum_btn,
        QPushButton#unified_preprocessing_btn,
        QPushButton#unified_redshift_selection_btn,
        QPushButton#unified_analysis_btn,
        QPushButton#unified_emission_line_overlay_btn,
        QPushButton#unified_ai_assistant_btn {{
            min-height: 32px !important;
            font-size: 11pt !important;
            font-weight: bold !important;
            padding: 6px 12px !important;
            border-radius: 4px !important;
        }}
        
        /* Main workflow buttons - disabled state (keep same size) */
        QPushButton#unified_load_spectrum_btn:disabled,
        QPushButton#unified_preprocessing_btn:disabled,
        QPushButton#unified_redshift_selection_btn:disabled,
        QPushButton#unified_analysis_btn:disabled,
        QPushButton#unified_emission_line_overlay_btn:disabled,
        QPushButton#unified_ai_assistant_btn:disabled {{
            min-height: 32px !important;
            font-size: 11pt !important;
            font-weight: bold !important;
            padding: 6px 12px !important;
            border-radius: 4px !important;
        }}
        
        /* Main workflow buttons - hover state (keep same size) */
        QPushButton#unified_load_spectrum_btn:hover,
        QPushButton#unified_preprocessing_btn:hover,
        QPushButton#unified_redshift_selection_btn:hover,
        QPushButton#unified_analysis_btn:hover,
        QPushButton#unified_emission_line_overlay_btn:hover,
        QPushButton#unified_ai_assistant_btn:hover {{
            min-height: 32px !important;
            font-size: 11pt !important;
            font-weight: bold !important;
            padding: 6px 12px !important;
            border-radius: 4px !important;
        }}
        
        QPushButton:hover {{
            background: {colors['hover']};
        }}
        
        QPushButton:pressed {{
            background: {colors['active']};
        }}
        
        QPushButton:disabled {{
            background: {colors['bg_disabled']};
            color: {colors['text_muted']};
            border: 2px solid {colors['bg_disabled']};
        }}
        
        /* Remove focus outline to prevent rectangle artifacts */
        QPushButton:focus {{
            outline: none;
        }}
        
        /* Navigation buttons */
        QPushButton#nav_btn {{
            background: {colors['btn_secondary']};
            color: white;
            border: 2px solid {colors['btn_secondary']};
            font-size: 12pt;
            font-weight: bold;
            border-radius: 4px;
            padding: 2px;
        }}
        
        QPushButton#nav_btn:hover {{
            background: {colors['btn_secondary_hover']};
            border: 2px solid {colors['btn_secondary_hover']};
        }}
        
        QPushButton#nav_btn:disabled {{
            background: {colors['bg_disabled']};
            color: {colors['text_muted']};
            border: 2px solid {colors['bg_disabled']};
        }}
        
        /* View toggle buttons - DISABLED: Main GUI has specific styling for flux_btn/flat_btn */
        /* 
        QPushButton:checkable {{
            background: {colors['bg_disabled']};
            color: {colors['text_primary']};
        }}
        
        QPushButton:checked {{
            background: {colors['btn_primary']};
            color: {colors['text_on_accent']};
            border: 2px solid {colors['btn_primary']};
        }}
        
        QPushButton:checkable:hover {{
            background: {colors['hover']};
        }}
        
        QPushButton:checked:hover {{
            background: {colors['btn_primary_hover']};
        }}
        */
        
        /* Info button special styling */
        QPushButton#info_btn {{
            background: {colors['btn_primary']};
            color: {colors['text_on_accent']};
            border: 2px solid {colors['btn_primary']};
            border-radius: 7px;
            min-width: 14px;
            max-width: 14px;
            min-height: 17px;
            max-height: 17px;
            font-size: 9pt;
            font-weight: bold;
        }}
        
        QPushButton#info_btn:hover {{
            background: {colors['btn_primary_hover']};
        }}
        
        /* Label styling */
        QLabel {{
            background: transparent;
            color: {colors['text_primary']};
        }}
        
        QLabel#file_status_label {{
            font-style: italic;
            color: {colors['text_secondary']};
        }}
        
        QLabel#redshift_status_label {{
            font-style: italic;
            color: {colors['text_secondary']};
        }}
        
        QLabel#ai_status_label {{
            font-style: italic;
            color: {colors['text_secondary']};
        }}
        
        /* Plot frame styling */
        QFrame#plot_frame {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
        }}
        
        /* Dialog-specific styling */
        QDialog {{
            background: {colors['bg_primary']};
            color: {colors['text_primary']};
        }}
        
        /* Input widgets styling */
        QLineEdit {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px;
            color: {colors['text_primary']};
        }}
        
        QLineEdit:focus {{
            border: 2px solid {colors['focus']};
        }}
        
        QTextEdit {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            color: {colors['text_primary']};
        }}
        
        QComboBox {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px;
            color: {colors['text_primary']};
        }}
        
        QSpinBox, QDoubleSpinBox {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px;
            color: {colors['text_primary']};
        }}
        
        /* Table and list styling */
        QTableWidget {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            gridline-color: {colors['border']};
            color: {colors['text_primary']};
        }}
        
        QListWidget {{
            background: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            color: {colors['text_primary']};
        }}
        
        /* Tab widget styling */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            background: {colors['bg_secondary']};
        }}
        
        QTabBar::tab {{
            background: {colors['bg_tertiary']};
            border: 1px solid {colors['border']};
            padding: 8px 16px;
            color: {colors['text_primary']};
        }}
        
        QTabBar::tab:selected {{
            background: {colors['bg_secondary']};
            border-bottom: 2px solid {colors['accent_primary']};
        }}
        
        QTabBar::tab:hover {{
            background: {colors['hover']};
        }}
        """
        
        return stylesheet
    
    def get_workflow_button_style(self, button_type: str) -> str:
        """
        Get specific styling for workflow buttons
        
        Args:
            button_type: Type of workflow button (load, preprocessing, analysis, etc.)
            
        Returns:
            Qt stylesheet for the specific button type
        """
        color_map = {
            'load': self.theme_colors['btn_load'],
            'preprocessing': self.theme_colors['btn_preprocessing'],
            'redshift': self.theme_colors['btn_redshift'],
            'analysis': self.theme_colors['btn_analysis'],
            'advanced': self.theme_colors['btn_advanced'],
            'ai': self.theme_colors['btn_ai'],
            'settings': self.theme_colors['btn_settings'],
            'reset': self.theme_colors['btn_reset'],
            'neutral': self.theme_colors['btn_neutral'],  # Add neutral mapping for navigation buttons
        }
        
        bg_color = color_map.get(button_type, self.theme_colors['btn_neutral'])
        
        # HEIGHT AND STYLING IS HANDLED BY CSS - only colors here
        return f"""
        background: {bg_color} !important;
        color: {self.theme_colors['text_on_accent']} !important;
        border: 2px solid {bg_color} !important;
        """
    
    def generate_cross_platform_styles(self) -> str:
        """
        Generate cross-platform specific styles for enhanced compatibility
        
        Returns:
            CSS stylesheet string with cross-platform enhancements
        """
        return """
        /* Cross-platform font and sizing improvements */
        QWidget {
            font-family: "Segoe UI", "Arial", "Helvetica", sans-serif;
        }
        QPushButton {
            font-size: 9pt;
            padding: 4px 8px;
            min-height: 24px;
        }
        QGroupBox {
            font-size: 11pt;
            font-weight: bold;
            padding-top: 12px;
        }
        QLabel {
            font-size: 10pt;
        }
        
        /* Enhanced navigation button styling */
        QPushButton[objectName="nav_btn"] {
            background-color: #f8fafc;
            border: 2px solid #cbd5e1;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14pt;
            color: #374151;
            padding: 2px;
        }
        
        /* Navigation arrow buttons - left/right arrows */
        QPushButton[objectName="unified_prev_btn"], 
        QPushButton[objectName="unified_next_btn"] {
            padding: 2px 4px !important;
            font-size: 10pt !important;
            font-weight: bold !important;
            min-height: 24px !important;
            background-color: #f3f4f6;
            border: 2px solid #e5e7eb;
            color: #9ca3af;
            border-radius: 4px;
        }
        
        /* Navigation arrow buttons when enabled - match advanced button color */
        QPushButton[objectName="unified_prev_btn"]:enabled, 
        QPushButton[objectName="unified_next_btn"]:enabled {
            background-color: #58508D !important;
            border: 2px solid #58508D !important;
            color: white !important;
        }
        
        QPushButton[objectName="unified_prev_btn"]:enabled:hover, 
        QPushButton[objectName="unified_next_btn"]:enabled:hover {
            background-color: #4c4577 !important;
            border: 2px solid #4c4577 !important;
        }
        
        /* Navigation arrow buttons when disabled - add hover effects */
        QPushButton[objectName="unified_prev_btn"]:disabled:hover,
        QPushButton[objectName="unified_next_btn"]:disabled:hover {
            background-color: #e5e7eb !important;
            border: 2px solid #d1d5db !important;
        }
        
        /* Navigation arrow buttons - pressed effects for click feedback */
        QPushButton[objectName="unified_prev_btn"]:enabled:pressed,
        QPushButton[objectName="unified_next_btn"]:enabled:pressed {
            background-color: #3d3465 !important;
            border: 2px solid #3d3465 !important;
        }
        
        QPushButton[objectName="unified_prev_btn"]:disabled:pressed,
        QPushButton[objectName="unified_next_btn"]:disabled:pressed {
            background-color: #d1d5db !important;
            border: 2px solid #9ca3af !important;
        }
        
        /* Removed: Micro navigation buttons - up/down arrows are no longer used */
        QPushButton[objectName="nav_btn"]:hover {
            background-color: #e2e8f0;
            border-color: #94a3b8;
            color: #1f2937;
        }
        QPushButton[objectName="nav_btn"]:pressed {
            background-color: #d1d5db;
            border-color: #6b7280;
        }
        QPushButton[objectName="nav_btn"]:enabled {
            background-color: #3b82f6;
            border-color: #2563eb;
            color: white;
        }
        QPushButton[objectName="nav_btn"]:enabled:hover {
            background-color: #2563eb;
            border-color: #1d4ed8;
        }
        QPushButton[objectName="nav_btn"]:disabled {
            background-color: #f3f4f6;
            border-color: #e5e7eb;
            color: #9ca3af;
        }
        
        /* View toggle buttons - high specificity styling */
        QPushButton[objectName="flux_btn"], QPushButton[objectName="flat_btn"] {
            background-color: #f1f5f9 !important;
            border: 2px solid #cbd5e1 !important;
            border-radius: 4px !important;
            font-weight: bold !important;
            font-size: 9pt !important;
            color: #475569 !important;
            padding: 4px 8px !important;
            min-height: 24px !important;
        }
        QPushButton[objectName="flux_btn"]:checked, QPushButton[objectName="flat_btn"]:checked {
            background-color: #3b82f6 !important;
            border-color: #2563eb !important;
            color: white !important;
        }
        QPushButton[objectName="flux_btn"]:hover, QPushButton[objectName="flat_btn"]:hover {
            background-color: #e2e8f0 !important;
            border-color: #94a3b8 !important;
        }
        QPushButton[objectName="flux_btn"]:checked:hover, QPushButton[objectName="flat_btn"]:checked:hover {
            background-color: #2563eb !important;
            border-color: #1d4ed8 !important;
        }
        QPushButton[objectName="flux_btn"]:disabled, QPushButton[objectName="flat_btn"]:disabled {
            background-color: #f3f4f6 !important;
            border-color: #e5e7eb !important;
            color: #9ca3af !important;
        }
        
        /* Flux/Flat buttons when disabled - add hover effects */
        QPushButton[objectName="flux_btn"]:disabled:hover, QPushButton[objectName="flat_btn"]:disabled:hover {
            background-color: #e5e7eb !important;
            border-color: #d1d5db !important;
        }
        
        /* Flux/Flat buttons - pressed effects for click feedback */
        QPushButton[objectName="flux_btn"]:pressed, QPushButton[objectName="flat_btn"]:pressed {
            background-color: #d1d5db !important;
            border-color: #9ca3af !important;
        }
        
        QPushButton[objectName="flux_btn"]:checked:pressed, QPushButton[objectName="flat_btn"]:checked:pressed {
            background-color: #1d4ed8 !important;
            border-color: #1e40af !important;
        }
        
        /* Analysis buttons - cluster summary, GMM, redshift age, subtype proportions */
        QPushButton[objectName="unified_cluster_summary_btn"],
        QPushButton[objectName="unified_gmm_btn"],
        QPushButton[objectName="unified_redshift_age_btn"],
        QPushButton[objectName="unified_subtype_proportions_btn"] {
            background-color: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 4px;
            color: #374151;
            padding: 2px 4px !important;
            min-height: 24px !important;
            font-weight: bold;
        }
        
        /* Analysis buttons emoji size variants */
        QPushButton[objectName="unified_cluster_summary_btn"] {
            font-size: 12pt;
        }
        
        QPushButton[objectName="unified_gmm_btn"],
        QPushButton[objectName="unified_redshift_age_btn"],
        QPushButton[objectName="unified_subtype_proportions_btn"] {
            font-size: 14pt;
        }
        
        QPushButton[objectName="unified_cluster_summary_btn"]:enabled,
        QPushButton[objectName="unified_gmm_btn"]:enabled,
        QPushButton[objectName="unified_redshift_age_btn"]:enabled,
        QPushButton[objectName="unified_subtype_proportions_btn"]:enabled {
            background-color: #58508D !important;
            border: 2px solid #58508D !important;
            color: white !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        QPushButton[objectName="unified_cluster_summary_btn"]:enabled:hover,
        QPushButton[objectName="unified_gmm_btn"]:enabled:hover,
        QPushButton[objectName="unified_redshift_age_btn"]:enabled:hover,
        QPushButton[objectName="unified_subtype_proportions_btn"]:enabled:hover {
            background-color: #4c4577 !important;
            border: 2px solid #4c4577 !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        /* Analysis buttons when disabled - add hover effects */
        QPushButton[objectName="unified_cluster_summary_btn"]:disabled:hover,
        QPushButton[objectName="unified_gmm_btn"]:disabled:hover,
        QPushButton[objectName="unified_redshift_age_btn"]:disabled:hover,
        QPushButton[objectName="unified_subtype_proportions_btn"]:disabled:hover {
            background-color: #e5e7eb !important;
            border: 2px solid #d1d5db !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        /* Analysis buttons - pressed effects for click feedback */
        QPushButton[objectName="unified_cluster_summary_btn"]:enabled:pressed,
        QPushButton[objectName="unified_gmm_btn"]:enabled:pressed,
        QPushButton[objectName="unified_redshift_age_btn"]:enabled:pressed,
        QPushButton[objectName="unified_subtype_proportions_btn"]:enabled:pressed {
            background-color: #3d3465 !important;
            border: 2px solid #3d3465 !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        QPushButton[objectName="unified_cluster_summary_btn"]:disabled:pressed,
        QPushButton[objectName="unified_gmm_btn"]:disabled:pressed,
        QPushButton[objectName="unified_redshift_age_btn"]:disabled:pressed,
        QPushButton[objectName="unified_subtype_proportions_btn"]:disabled:pressed {
            background-color: #d1d5db !important;
            border: 2px solid #9ca3af !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        QPushButton[objectName="unified_cluster_summary_btn"]:disabled,
        QPushButton[objectName="unified_gmm_btn"]:disabled,
        QPushButton[objectName="unified_redshift_age_btn"]:disabled,
        QPushButton[objectName="unified_subtype_proportions_btn"]:disabled {
            background-color: #f3f4f6 !important;
            border: 2px solid #e5e7eb !important;
            color: #9ca3af !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        /* Reset and Settings buttons - utility buttons with consistent styling */
        QPushButton[objectName="unified_reset_btn"],
        QPushButton[objectName="unified_settings_btn"] {
            background-color: #f8fafc !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 4px !important;
            color: #374151 !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
            font-weight: bold !important;
            font-size: 9pt !important;
        }
        
        QPushButton[objectName="unified_reset_btn"]:enabled,
        QPushButton[objectName="unified_settings_btn"]:enabled {
            background-color: #6366f1 !important;
            border: 2px solid #6366f1 !important;
            color: white !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        QPushButton[objectName="unified_reset_btn"]:enabled:hover,
        QPushButton[objectName="unified_settings_btn"]:enabled:hover {
            background-color: #5448c8 !important;
            border: 2px solid #5448c8 !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        QPushButton[objectName="unified_reset_btn"]:enabled:pressed,
        QPushButton[objectName="unified_settings_btn"]:enabled:pressed {
            background-color: #4338ca !important;
            border: 2px solid #4338ca !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        QPushButton[objectName="unified_reset_btn"]:disabled,
        QPushButton[objectName="unified_settings_btn"]:disabled {
            background-color: #f3f4f6 !important;
            border: 2px solid #e5e7eb !important;
            color: #9ca3af !important;
            padding: 2px 4px !important;
            min-height: 24px !important;
        }
        
        /* Info button - utility button with specific styling */
        QPushButton[objectName="unified_info_btn"] {
            background-color: #3b82f6 !important;
            border: 1px solid #2563eb !important;
            border-radius: 4px !important;
            color: white !important;
            padding: 2px 4px !important;
            font-weight: bold !important;
            font-family: "Segoe UI", "Arial", sans-serif !important;
            font-size: 14px !important;
            min-width: 24px !important;
            max-width: 24px !important;
        }
        
        QPushButton[objectName="unified_info_btn"]:hover {
            background-color: #2563eb !important;
            border: 1px solid #1d4ed8 !important;
        }
        
        QPushButton[objectName="unified_info_btn"]:pressed {
            background-color: #1d4ed8 !important;
            border: 1px solid #1e40af !important;
        }
        
        /* Remove focus outline for all buttons to prevent rectangle artifacts */
        QPushButton:focus {
            outline: none !important;
        }
        """
    
    def generate_complete_stylesheet(self) -> str:
        """
        Generate complete stylesheet including base theme and cross-platform enhancements
        
        Returns:
            Complete CSS stylesheet string ready for application
        """
        base_stylesheet = self.generate_qt_stylesheet()
        cross_platform_styles = self.generate_cross_platform_styles()
        return base_stylesheet + cross_platform_styles
    
    def create_enhanced_button_manager(self):
        """
        Create an enhanced button manager instance with this theme manager
        
        Returns:
            EnhancedButtonManager instance configured with this theme
        """
        from .enhanced_button_manager import EnhancedButtonManager
        return EnhancedButtonManager(self)


# Global theme manager instance
_theme_manager = None


def get_pyside6_theme_manager() -> PySide6ThemeManager:
    """
    Get the global PySide6 theme manager instance
    
    Returns:
        Global PySide6ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = PySide6ThemeManager()
    return _theme_manager


def apply_theme_to_widget(widget, theme_manager: Optional[PySide6ThemeManager] = None):
    """
    Apply theme to a specific widget
    
    Args:
        widget: Qt widget to apply theme to
        theme_manager: Optional theme manager instance (uses global if None)
    """
    if theme_manager is None:
        theme_manager = get_pyside6_theme_manager()
    
    stylesheet = theme_manager.generate_qt_stylesheet()
    widget.setStyleSheet(stylesheet) 