"""
SNID SAGE Unified Font Manager
=============================

Provides comprehensive font management for consistent typography across the entire platform:
- Platform-aware base font sizes with proper scaling
- DPI awareness for high-resolution displays
- User-configurable font scaling (100%, 125%, 150%, 200%)
- Accessibility compliance with minimum readable sizes
- Consistent font hierarchy for all UI elements

This ensures all text is properly readable across Windows, macOS, and Linux.
"""

import tkinter as tk
import platform
import sys
from typing import Dict, Tuple, Optional, Union
from enum import Enum

# Import centralized logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.fonts')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.fonts')


class FontCategory(Enum):
    """Font categories for consistent typography hierarchy"""
    HEADER_LARGE = "header_large"        # 20px+ - Main titles
    HEADER_MEDIUM = "header_medium"      # 16-18px - Section headers
    HEADER_SMALL = "header_small"        # 14px - Subsection headers
    BODY_LARGE = "body_large"            # 14px - Important body text
    BODY_NORMAL = "body_normal"          # 12px - Normal body text
    BODY_SMALL = "body_small"            # 11px - Small text (minimum readable)
    CAPTION = "caption"                  # 10px - Captions, fine print
    CODE = "code"                        # Monospace for code/data
    BUTTON = "button"                    # Button text
    LABEL = "label"                      # Form labels
    PLOT_TITLE = "plot_title"            # Plot titles (when needed)
    PLOT_AXIS = "plot_axis"              # Plot axis labels
    PLOT_LEGEND = "plot_legend"          # Plot legends
    PLOT_ANNOTATION = "plot_annotation"   # Plot annotations


class UnifiedFontManager:
    """
    Centralized font management system providing consistent, readable typography
    across all SNID SAGE components with platform awareness and user scaling.
    """
    
    def __init__(self):
        """Initialize the font manager with platform detection and DPI awareness"""
        self.platform = platform.system()
        self.user_scale_factor = 1.0  # User-configurable scaling (100% = 1.0)
        self.dpi_scale_factor = 1.0   # DPI-based scaling
        self.accessibility_mode = False  # Large fonts for accessibility
        
        # Detect platform and setup base configurations
        self._detect_platform()
        self._detect_dpi_scaling()
        self._setup_platform_fonts()
        self._calculate_effective_sizes()
        
        _LOGGER.info(f"🔤 Font Manager initialized - Platform: {self.platform}, "
                    f"DPI Scale: {self.dpi_scale_factor:.2f}, User Scale: {self.user_scale_factor:.2f}")
    
    def _detect_platform(self):
        """Detect platform for font selection"""
        self.is_windows = self.platform == "Windows"
        self.is_macos = self.platform == "Darwin"
        self.is_linux = self.platform == "Linux"
        
        # Windows typically needs slightly larger fonts for readability
        if self.is_windows:
            self.platform_adjustment = 1.1
        elif self.is_macos:
            self.platform_adjustment = 1.0  # macOS fonts are naturally well-sized
        else:  # Linux
            self.platform_adjustment = 1.05
    
    def _detect_dpi_scaling(self):
        """Detect DPI scaling from system"""
        try:
            # Try to get DPI scaling
            root = tk.Tk()
            root.withdraw()  # Hide the temporary window
            
            # Get DPI information
            dpi = root.winfo_fpixels('1i')  # Pixels per inch
            standard_dpi = 96.0
            self.dpi_scale_factor = max(1.0, dpi / standard_dpi)
            
            root.destroy()
            
            # Cap DPI scaling to reasonable limits
            self.dpi_scale_factor = min(self.dpi_scale_factor, 3.0)
            
        except Exception as e:
            _LOGGER.debug(f"Could not detect DPI scaling: {e}")
            self.dpi_scale_factor = 1.0
    
    def _setup_platform_fonts(self):
        """Setup platform-specific font families"""
        if self.is_windows:
            self.font_families = {
                'default': 'Segoe UI',
                'header': 'Segoe UI',
                'code': 'Consolas',
                'fallback': 'Arial'
            }
        elif self.is_macos:
            self.font_families = {
                'default': 'SF Pro Display',
                'header': 'SF Pro Display',
                'code': 'SF Mono',
                'fallback': 'Helvetica'
            }
        else:  # Linux
            self.font_families = {
                'default': 'Ubuntu',
                'header': 'Ubuntu',
                'code': 'Ubuntu Mono',
                'fallback': 'Liberation Sans'
            }
    
    def _calculate_effective_sizes(self):
        """Calculate effective font sizes with all scaling factors applied"""
        # Base sizes ensuring minimum readability (12px minimum for normal text)
        base_sizes = {
            FontCategory.HEADER_LARGE: 24,      # Main titles
            FontCategory.HEADER_MEDIUM: 18,     # Section headers  
            FontCategory.HEADER_SMALL: 16,      # Subsection headers
            FontCategory.BODY_LARGE: 14,        # Important body text
            FontCategory.BODY_NORMAL: 12,       # Normal body text
            FontCategory.BODY_SMALL: 11,        # Small text (minimum readable)
            FontCategory.CAPTION: 10,           # Captions (absolute minimum)
            FontCategory.CODE: 11,              # Monospace code
            FontCategory.BUTTON: 12,            # Button text
            FontCategory.LABEL: 12,             # Form labels
            FontCategory.PLOT_TITLE: 14,        # Plot titles
            FontCategory.PLOT_AXIS: 12,         # Plot axis labels
            FontCategory.PLOT_LEGEND: 11,       # Plot legends
            FontCategory.PLOT_ANNOTATION: 10,   # Plot annotations
        }
        
        # Linux-specific adjustments to prevent button text cutting
        if self.is_linux:
            # Reduce button font size for Linux to prevent overflow
            base_sizes[FontCategory.BUTTON] = 11  # Reduced from 12 to 11 for Linux
        
        # Apply all scaling factors
        total_scale = (self.platform_adjustment * 
                      self.dpi_scale_factor * 
                      self.user_scale_factor)
        
        # Apply accessibility scaling if enabled
        if self.accessibility_mode:
            total_scale *= 1.25  # 25% larger for accessibility
        
        # Calculate effective sizes with minimum enforcements
        self.effective_sizes = {}
        for category, base_size in base_sizes.items():
            scaled_size = int(base_size * total_scale)
            
            # Enforce minimum sizes for readability
            if category in [FontCategory.BODY_NORMAL, FontCategory.BUTTON, FontCategory.LABEL]:
                scaled_size = max(scaled_size, 12)  # Never smaller than 12px
            elif category == FontCategory.BODY_SMALL:
                scaled_size = max(scaled_size, 11)  # Never smaller than 11px
            elif category == FontCategory.CAPTION:
                scaled_size = max(scaled_size, 10)  # Never smaller than 10px
            
            self.effective_sizes[category] = scaled_size
    
    def get_font(self, category: FontCategory, weight: str = 'normal') -> Tuple[str, int, str]:
        """
        Get font tuple (family, size, weight) for a specific category
        
        Args:
            category: Font category from FontCategory enum
            weight: Font weight ('normal', 'bold', 'italic', etc.)
        
        Returns:
            Tuple of (font_family, font_size, font_weight)
        """
        # Determine font family based on category
        if category == FontCategory.CODE:
            family = self.font_families['code']
        elif category in [FontCategory.HEADER_LARGE, FontCategory.HEADER_MEDIUM, FontCategory.HEADER_SMALL]:
            family = self.font_families['header']
        else:
            family = self.font_families['default']
        
        # Get effective size
        size = self.effective_sizes.get(category, 12)
        
        return (family, size, weight)
    
    def get_font_dict(self, category: FontCategory, weight: str = 'normal') -> Dict[str, Union[str, int]]:
        """
        Get font as dictionary for tkinter font configuration
        
        Returns:
            Dictionary with 'family', 'size', 'weight' keys
        """
        family, size, weight_str = self.get_font(category, weight)
        return {
            'family': family,
            'size': size,
            'weight': weight_str
        }
    
    def get_matplotlib_font_dict(self, category: FontCategory) -> Dict[str, Union[str, int]]:
        """
        Get font configuration for matplotlib plots
        
        Returns:
            Dictionary suitable for matplotlib font properties
        """
        family, size, weight = self.get_font(category)
        
        # Convert tkinter weight to matplotlib weight
        mpl_weight = 'normal'
        if weight in ['bold']:
            mpl_weight = 'bold'
        elif weight in ['italic']:
            mpl_weight = 'normal'  # matplotlib handles italic separately
        
        return {
            'family': family,
            'size': size,
            'weight': mpl_weight
        }
    
    def set_user_scale(self, scale_factor: float):
        """
        Set user-configurable scaling factor
        
        Args:
            scale_factor: Scaling factor (1.0 = 100%, 1.25 = 125%, etc.)
        """
        # Clamp to reasonable range
        self.user_scale_factor = max(0.75, min(scale_factor, 3.0))
        self._calculate_effective_sizes()
        _LOGGER.info(f"🔤 User font scale set to {self.user_scale_factor:.0%}")
    
    def set_accessibility_mode(self, enabled: bool):
        """
        Enable/disable accessibility mode (larger fonts)
        
        Args:
            enabled: Whether to enable accessibility mode
        """
        self.accessibility_mode = enabled
        self._calculate_effective_sizes()
        _LOGGER.info(f"🔤 Accessibility mode {'enabled' if enabled else 'disabled'}")
    
    def apply_to_widget(self, widget: tk.Widget, category: FontCategory, weight: str = 'normal'):
        """
        Apply font to a tkinter widget
        
        Args:
            widget: The tkinter widget to apply font to
            category: Font category
            weight: Font weight
        """
        try:
            font_tuple = self.get_font(category, weight)
            widget.configure(font=font_tuple)
        except Exception as e:
            _LOGGER.debug(f"Could not apply font to widget: {e}")
    
    def get_scaling_info(self) -> Dict[str, float]:
        """Get current scaling information for debugging"""
        return {
            'platform_adjustment': self.platform_adjustment,
            'dpi_scale_factor': self.dpi_scale_factor,
            'user_scale_factor': self.user_scale_factor,
            'accessibility_mode': self.accessibility_mode,
            'total_scale': (self.platform_adjustment * 
                          self.dpi_scale_factor * 
                          self.user_scale_factor * 
                          (1.25 if self.accessibility_mode else 1.0))
        }
    
    def get_all_fonts(self) -> Dict[FontCategory, Tuple[str, int, str]]:
        """Get all font configurations for debugging"""
        return {category: self.get_font(category) for category in FontCategory}


# Global font manager instance
_FONT_MANAGER = None

def get_font_manager() -> UnifiedFontManager:
    """Get the global font manager instance"""
    global _FONT_MANAGER
    if _FONT_MANAGER is None:
        _FONT_MANAGER = UnifiedFontManager()
    return _FONT_MANAGER


def get_font(category: FontCategory, weight: str = 'normal') -> Tuple[str, int, str]:
    """Convenience function to get font tuple"""
    return get_font_manager().get_font(category, weight)


def apply_font_to_widget(widget: tk.Widget, category: FontCategory, weight: str = 'normal'):
    """Convenience function to apply font to widget"""
    get_font_manager().apply_to_widget(widget, category, weight)


def get_matplotlib_font(category: FontCategory) -> Dict[str, Union[str, int]]:
    """Convenience function to get matplotlib font configuration"""
    return get_font_manager().get_matplotlib_font_dict(category) 
