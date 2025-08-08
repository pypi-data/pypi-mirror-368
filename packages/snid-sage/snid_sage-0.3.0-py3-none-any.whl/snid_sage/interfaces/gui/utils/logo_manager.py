"""
Logo Manager Module for SNID SAGE GUI
=====================================

Handles loading and management of logo images for both light and dark themes.
Provides automatic theme switching and fallback handling.

Features:
- Light/dark mode logo support
- Automatic theme detection
- Graceful fallbacks for missing images
- PIL/Pillow integration for image handling
"""

import os
import tkinter as tk

# Defer PIL import until needed to speed up startup
_pil_imported = False

# Use centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.utils.logo_manager')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.utils.logo_manager')

def _import_pil():
    """Lazy import of PIL to speed up startup"""
    global _pil_imported
    if not _pil_imported:
        try:
            from PIL import Image, ImageTk
            globals()['Image'] = Image
            globals()['ImageTk'] = ImageTk
        except ImportError:
            # Fallback if PIL not available
            globals()['Image'] = None
            globals()['ImageTk'] = None
        _pil_imported = True
        return Image, ImageTk
    else:
        return globals()['Image'], globals()['ImageTk']


class LogoManager:
    """Manager for handling logos and branding elements"""
    
    def __init__(self, gui_instance):
        """Initialize logo manager"""
        self.gui = gui_instance
        self.logo_light = None
        self.logo_dark = None
        self.current_logo = None
        self.logo_label = None
        self.logo_height = 100  # Increased back to better size now that we have proper space allocation
    
    def load_logos(self):
        """Load SNID SAGE logos for light and dark modes"""
        try:
            # Import PIL for image handling
            Image, ImageTk = _import_pil()
            
            # Get the path to the images directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # From interfaces/gui/utils -> interfaces/gui -> interfaces -> project_root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            images_dir = os.path.join(project_root, 'snid_sage', 'images')
            
            # Support multiple naming conventions for logos - prioritize icon.png
            light_logo_candidates = [
                os.path.join(images_dir, 'icon.png'),       # PRIMARY: icon.png should be first choice
                os.path.join(images_dir, 'light.png'),
                os.path.join(images_dir, 'logo.png'),
                os.path.join(images_dir, 'snid_logo.png')
            ]
            
            dark_logo_candidates = [
                os.path.join(images_dir, 'icon_dark.png'),  # PRIMARY: icon_dark.png should be first choice
                os.path.join(images_dir, 'dark.png'),       # Standard dark variant
                os.path.join(images_dir, '@dark.png'),      # iOS/macOS convention
                os.path.join(images_dir, 'logo@dark.png'),  # Alternative iOS convention
                os.path.join(images_dir, 'snid_logo_dark.png')
            ]
            
            # Find and load light mode logo
            self.logo_light = self._load_logo_file(light_logo_candidates, "light")
            
            # Find and load dark mode logo
            self.logo_dark = self._load_logo_file(dark_logo_candidates, "dark")
            
            # Fallback to light logo for dark mode if no dark variant exists
            if not self.logo_dark and self.logo_light:
                self.logo_dark = self.logo_light
            
            # Set initial logo based on current mode
            self._set_initial_logo()
            
        except Exception as e:
            _LOGGER.warning(f"Error loading logos: {e}")
            _LOGGER.debug("Logo loading error details:", exc_info=True)
            self.logo_light = None
            self.logo_dark = None
            self.current_logo = None
    
    def _load_logo_file(self, candidates, mode_name):
        """Load logo from candidate file paths"""
        try:
            Image, ImageTk = _import_pil()
            
            # Find existing logo file
            logo_path = None
            for path in candidates:
                if os.path.exists(path):
                    logo_path = path
                    break
            
            if logo_path:
                try:
                    image = Image.open(logo_path)
                    # Resize logo to appropriate size (maintain aspect ratio) with proper space allocation
                    aspect_ratio = image.width / image.height
                    logo_width = int(self.logo_height * aspect_ratio)
                    
                    # More generous width limit since we now have dedicated space
                    max_logo_width = 180  # Increased from 120 to 180 for better logo display
                    if logo_width > max_logo_width:
                        logo_width = max_logo_width
                        self.logo_height = int(max_logo_width / aspect_ratio)
                    
                    image = image.resize((logo_width, self.logo_height), Image.Resampling.LANCZOS)
                    logo_image = ImageTk.PhotoImage(image)
                    _LOGGER.info(f"✅ Logo loaded: {logo_width}x{self.logo_height} from {logo_path}")
                    return logo_image
                except Exception as e:
                    _LOGGER.warning(f"Failed to load {mode_name} logo: {e}")
                    return None
            else:
                # Only log if no logo files found at all
                return None
                
        except Exception as e:
            _LOGGER.warning(f"Error loading {mode_name} logo file: {e}")
            return None
    
    def _set_initial_logo(self):
        """Set initial logo - always light mode"""
        try:
            # Always use light mode
            self.current_logo = self.logo_light
                
        except Exception as e:
            _LOGGER.warning(f"Error setting initial logo: {e}")
            self.current_logo = self.logo_light
    
    def update_logo(self, dark_mode_enabled=None):
        """Update the logo - simplified for light mode only"""
        try:
            # Always use light logo (since we removed dark/light toggle)
            new_logo = self.logo_light if self.logo_light else None
            theme_name = 'light'
            
            _LOGGER.debug(f"Updating logo for {theme_name} theme")
            
            # Update current_logo reference
            if new_logo:
                self.current_logo = new_logo
                _LOGGER.debug(f"Logo updated for {theme_name} theme")
            
            # Only update if we have a new logo and a logo label
            if new_logo and self.logo_label and self.logo_label.winfo_exists():
                try:
                    self.logo_label.configure(image=self.current_logo, text="")  # Clear text when image is set
                    _LOGGER.info(f"✅ Logo label updated with icon.png for {theme_name} mode")
                    
                    # Force a refresh of the GUI to ensure changes are visible
                    self.logo_label.update_idletasks()
                    self.gui.master.update_idletasks()
                    
                except Exception as e:
                    _LOGGER.warning(f"Error updating logo label: {e}")
                    
            elif not new_logo:
                _LOGGER.warning(f"❌ No logo available for {theme_name} mode - check if icon.png exists")
                # Fallback to text display
                if self.logo_label and self.logo_label.winfo_exists():
                    self.logo_label.configure(image="", text="SNID SAGE")
            elif not self.logo_label:
                _LOGGER.debug(f"Logo label not initialized yet (will be set when interface is created)")
            else:
                _LOGGER.debug(f"Logo label no longer exists")
                
        except Exception as e:
            _LOGGER.warning(f"Error updating logo: {e}")
            _LOGGER.debug("Logo update error details:", exc_info=True)
    
    def set_logo_label(self, logo_label):
        """Set the logo label widget reference"""
        self.logo_label = logo_label
    
    def get_current_logo(self):
        """Get the current logo for display"""
        return self.current_logo
    
    def has_logos(self):
        """Check if any logos are available"""
        return self.logo_light is not None or self.logo_dark is not None
    
    def create_logo_widget(self, parent, bg_color):
        """Create and return a logo widget for the given parent"""
        try:
            if self.current_logo:
                logo_label = tk.Label(parent, image=self.current_logo, bg=bg_color)
                self.set_logo_label(logo_label)
                return logo_label
            else:
                # Fallback to text if logos not available
                logo_label = tk.Label(parent, text="SNID SAGE",
                                    font=('Segoe UI', 20, 'bold'),
                                    bg=bg_color)
                return logo_label
                
        except Exception as e:
            _LOGGER.warning(f"Error creating logo widget: {e}")
            # Return a simple text label as fallback
            return tk.Label(parent, text="SNID SAGE", 
                          font=('Segoe UI', 16, 'bold'), bg=bg_color)
    
    def cleanup(self):
        """Clean up logo resources"""
        try:
            self.logo_light = None
            self.logo_dark = None
            self.current_logo = None
            self.logo_label = None
            _LOGGER.debug("Logo manager cleanup completed")
            
        except Exception as e:
            _LOGGER.warning(f"Error during logo manager cleanup: {e}") 
