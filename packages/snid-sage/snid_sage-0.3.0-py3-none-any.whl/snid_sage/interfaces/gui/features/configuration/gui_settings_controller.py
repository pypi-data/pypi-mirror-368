"""
SNID SAGE - GUI Settings Controller
===================================

Controller for managing GUI-specific settings including fonts, display options,
theme preferences, and interface customization. Integrates with the existing
configuration system and provides a bridge between the settings dialog and
the main application.

Part of the modular configuration architecture following SNID SAGE patterns.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
import tkinter as tk
from tkinter import messagebox
import tkinter.font

# Import centralized logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.settings_controller')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.settings_controller')

# Import existing configuration system
try:
    from snid_sage.shared.utils.config import config_manager
    _HAS_CONFIG_MANAGER = True
except ImportError:
    _HAS_CONFIG_MANAGER = False
    _LOGGER.warning("Config manager not available - using local settings storage")

from snid_sage.shared.exceptions.core_exceptions import ConfigurationError


class GUISettingsController:
    """
    Controller for GUI-specific settings management.
    
    Handles:
    - Loading and saving GUI settings
    - Integration with main application components
    - Font and display settings application
    - Theme preferences coordination
    - Settings persistence and validation
    """
    
    def __init__(self, main_gui):
        """
        Initialize GUI settings controller.
        
        Args:
            main_gui: Main GUI instance (ModernSNIDSageGUI)
        """
        self.main_gui = main_gui
        self.current_settings = {}
        self.settings_file = self._get_settings_file_path()
        
        # Initialize settings
        self._load_settings()
        
        # Settings change callbacks
        self.settings_changed_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        _LOGGER.debug("GUI Settings Controller initialized")
    
    def _get_settings_file_path(self) -> Path:
        """Get the path for GUI settings file (Cross-platform)"""
        if _HAS_CONFIG_MANAGER:
            # Use config manager's directory
            config_dir = config_manager.config_dir
        else:
            # Try to use Qt's QStandardPaths for cross-platform config directories
            try:
                from PySide6.QtCore import QStandardPaths
                config_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
                config_dir = Path(config_path) / 'SNID_SAGE'
            except ImportError:
                # Fallback to legacy OS detection
                if os.name == 'nt':  # Windows
                    config_dir = Path(os.environ.get('APPDATA', Path.home())) / 'SNID_SAGE'
                else:  # Unix-like systems
                    config_dir = Path.home() / '.config' / 'snid_sage'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'gui_settings.json'
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default GUI settings"""
        return {
            # Font and display
            'font_family': 'Segoe UI',
            'font_size': 12,
            'dpi_scale': 100,
            'button_height': 40,
            'widget_padding': 8,
            'icon_size': 'Medium',
            
            # Window behavior
            'remember_position': True,
            'remember_size': True,
            'minimize_to_tray': False,
            'auto_save_settings': True,
            
            # Plot settings
            'plot_dpi': 150,
            'animation_speed': 5,
            'grid_opacity': 30,
            
            # Performance
            'reduce_animations': False
            
            # Removed obsolete optimization settings
        }
    
    def _load_settings(self):
        """Load GUI settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                defaults = self._get_default_settings()
                self.current_settings = {**defaults, **saved_settings}
                
                _LOGGER.info(f"Loaded GUI settings from {self.settings_file}")
            else:
                # Use defaults
                self.current_settings = self._get_default_settings()
                _LOGGER.info("Using default GUI settings")
                
        except (json.JSONDecodeError, OSError) as e:
            _LOGGER.error(f"Error loading GUI settings: {e}")
            self.current_settings = self._get_default_settings()
    
    def save_settings(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save GUI settings to file.
        
        Args:
            settings: Settings to save (uses current if None)
            
        Returns:
            True if successful, False otherwise
        """
        if settings is not None:
            self.current_settings = settings
        
        try:
            # Add metadata
            settings_to_save = self.current_settings.copy()
            settings_to_save['_metadata'] = {
                'version': '1.0',
                'last_modified': self._get_timestamp(),
                'created_by': 'SNID SAGE GUI'
            }
            
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=2, ensure_ascii=False)
            
            _LOGGER.info(f"Saved GUI settings to {self.settings_file}")
            
            # Notify callbacks
            self._notify_settings_changed()
            
            return True
            
        except (OSError, json.JSONEncodeError) as e:
            _LOGGER.error(f"Error saving GUI settings: {e}")
            return False
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current GUI settings"""
        return self.current_settings.copy()
    
    def update_setting(self, key: str, value: Any, auto_save: bool = None) -> bool:
        """
        Update a single setting.
        
        Args:
            key: Setting key
            value: New value
            auto_save: Whether to auto-save (uses setting if None)
            
        Returns:
            True if successful
        """
        try:
            self.current_settings[key] = value
            
            # Auto-save if enabled
            if auto_save is None:
                auto_save = self.current_settings.get('auto_save_settings', True)
            
            if auto_save:
                return self.save_settings()
            
            # Still notify even if not saving
            self._notify_settings_changed()
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error updating setting {key}: {e}")
            return False
    
    def show_settings_dialog(self) -> Optional[Dict[str, Any]]:
        """Show the GUI settings dialog"""
        try:
            from snid_sage.interfaces.gui.components.dialogs.settings_dialog import show_gui_settings_dialog
            
            # Show dialog with current settings
            result = show_gui_settings_dialog(self.main_gui, self.current_settings)
            
            if result is not None:
                # Apply the new settings
                self.apply_settings(result)
                
                # Save if auto-save is enabled
                if result.get('auto_save_settings', True):
                    self.save_settings(result)
                
                _LOGGER.info("GUI settings updated from dialog")
                return result
            
            return None
            
        except Exception as e:
            _LOGGER.error(f"Error showing settings dialog: {e}")
            messagebox.showerror("Settings Error", 
                               f"Error opening settings dialog:\n\n{str(e)}")
            return None
    
    def apply_settings(self, settings: Dict[str, Any]):
        """
        Apply settings to the main GUI.
        
        Args:
            settings: Settings dictionary to apply
        """
        try:
            # Update current settings
            self.current_settings.update(settings)
            
            # Apply font settings
            self._apply_font_settings(settings)
            
            # Apply display settings
            self._apply_display_settings(settings)
            
            # Apply window settings
            self._apply_window_settings(settings)
            
            # Apply plot settings
            self._apply_plot_settings(settings)
            
            # Apply performance settings
            self._apply_performance_settings(settings)
            
            _LOGGER.info("GUI settings applied successfully")
            
        except Exception as e:
            _LOGGER.error(f"Error applying GUI settings: {e}")
    
    def _apply_font_settings(self, settings: Dict[str, Any]):
        """Apply font and text settings"""
        try:
            font_family = settings.get('font_family', 'Segoe UI')
            font_size = settings.get('font_size', 12)
            
            # Update default font for new widgets
            try:
                default_font = tk.font.nametofont("TkDefaultFont")
                default_font.configure(family=font_family, size=font_size)
            except tk.TclError:
                # Fallback if default font not available
                pass
            
            # Update specific GUI fonts if available and method exists
            if hasattr(self.main_gui, 'theme_manager'):
                theme_manager = self.main_gui.theme_manager
                if hasattr(theme_manager, 'update_fonts'):
                    theme_manager.update_fonts(font_family, font_size)
                else:
                    # Store font settings for theme manager to use
                    if not hasattr(theme_manager, 'custom_font_family'):
                        theme_manager.custom_font_family = font_family
                        theme_manager.custom_font_size = font_size
            
            _LOGGER.debug(f"Applied font settings: {font_family}, {font_size}pt")
            
        except Exception as e:
            _LOGGER.error(f"Error applying font settings: {e}")
    
    def _apply_display_settings(self, settings: Dict[str, Any]):
        """Apply display and resolution settings"""
        try:
            dpi_scale = settings.get('dpi_scale', 100)
            button_height = settings.get('button_height', 40)
            widget_padding = settings.get('widget_padding', 8)
            
            # Apply DPI scaling
            if hasattr(self.main_gui.master, 'tk'):
                try:
                    scale_factor = dpi_scale / 100.0
                    self.main_gui.master.tk.call('tk', 'scaling', scale_factor)
                except tk.TclError:
                    _LOGGER.debug("DPI scaling not supported on this platform")
            
            _LOGGER.debug(f"Applied display settings: DPI {dpi_scale}%, button height {button_height}px")
            
        except Exception as e:
            _LOGGER.error(f"Error applying display settings: {e}")
    
    def _apply_theme_settings(self, settings: Dict[str, Any]):
        """Apply theme and appearance settings"""
        try:
            watercolor_effects = settings.get('watercolor_effects', True)
            color_saturation = settings.get('color_saturation', 100)
            
            # Watercolor toggle removed - light mode only
            
            # Apply color saturation to theme manager
            if hasattr(self.main_gui, 'theme_manager'):
                theme_manager = self.main_gui.theme_manager
                if hasattr(theme_manager, 'set_color_saturation'):
                    theme_manager.set_color_saturation(color_saturation / 100.0)
                else:
                    # Store saturation setting for theme manager to use
                    theme_manager.custom_color_saturation = color_saturation / 100.0
            
            _LOGGER.debug(f"Applied theme settings: watercolor={watercolor_effects}, saturation={color_saturation}%")
            
        except Exception as e:
            _LOGGER.error(f"Error applying theme settings: {e}")
    
    def _apply_window_settings(self, settings: Dict[str, Any]):
        """Apply window behavior settings"""
        try:
            # FORCE SOLID WINDOW: Always set to 100% opacity (user requested no transparency)
            if hasattr(self.main_gui.master, 'attributes'):
                try:
                    self.main_gui.master.attributes('-alpha', 1.0)  # Always solid
                    _LOGGER.debug("Window explicitly set to 100% opacity (solid)")
                except tk.TclError:
                    _LOGGER.debug("Window transparency not supported on this platform")
            
            # No longer store or restore window geometry – main GUI always centers
            _LOGGER.debug("Applied window settings: forced solid window (centering always)")
            
        except Exception as e:
            _LOGGER.error(f"Error applying window settings: {e}")
    
    def _apply_plot_settings(self, settings: Dict[str, Any]):
        """Apply plot display settings"""
        try:
            plot_dpi = settings.get('plot_dpi', 150)
            grid_opacity = settings.get('grid_opacity', 30)
            
            # Apply to matplotlib if available
            try:
                import matplotlib.pyplot as plt
                import matplotlib as mpl
                
                # Update DPI
                mpl.rcParams['figure.dpi'] = plot_dpi
                mpl.rcParams['savefig.dpi'] = plot_dpi
                
                # Update grid opacity
                mpl.rcParams['grid.alpha'] = grid_opacity / 100.0
                
                _LOGGER.debug(f"Applied plot settings: DPI={plot_dpi}, grid_opacity={grid_opacity}%")
                
            except ImportError:
                _LOGGER.debug("Matplotlib not available for plot settings")
            
        except Exception as e:
            _LOGGER.error(f"Error applying plot settings: {e}")
    
    def _apply_performance_settings(self, settings: Dict[str, Any]):
        """Apply performance settings"""
        try:
            reduce_animations = settings.get('reduce_animations', False)
            
            # Apply animation settings
            if hasattr(self.main_gui, 'theme_manager'):
                theme_manager = self.main_gui.theme_manager
                if hasattr(theme_manager, 'set_animations_enabled'):
                    theme_manager.set_animations_enabled(not reduce_animations)
                else:
                    # Store animation preference
                    theme_manager.animations_enabled = not reduce_animations
            
            _LOGGER.debug(f"Applied performance settings: animations={not reduce_animations}")
            
        except Exception as e:
            _LOGGER.error(f"Error applying performance settings: {e}")
    
    def _apply_optimization_settings(self, settings: Dict[str, Any]):
        """Apply optimization settings (now using unified storage system)"""
        try:
            # The unified storage system is now handled automatically
            # This method is kept for backward compatibility but simplified
            
            _LOGGER.info("Unified storage system is handled automatically")
            
            # Check if unified storage is available
            try:
                from snid_sage.snid.template_fft_storage import TemplateFFTStorage
                from pathlib import Path
                
                # Check if unified storage file exists
                storage_path = Path("templates.h5")
                if storage_path.exists():
                    _LOGGER.info(f"Unified FFT storage available at {storage_path}")
                    
                    # Update GUI status if possible
                    if hasattr(self.main_gui, 'update_header_status'):
                        self.main_gui.update_header_status(f"🚀 Unified FFT Storage Active - Ready for analysis")
                else:
                    _LOGGER.info("Unified storage file not found - will be built when needed")
                    if hasattr(self.main_gui, 'update_header_status'):
                        self.main_gui.update_header_status("⚙️ Unified Storage - Will build on first use")
                
            except ImportError as e:
                _LOGGER.warning(f"Unified storage system not available: {e}")
                if hasattr(self.main_gui, 'update_header_status'):
                    self.main_gui.update_header_status("⚠️ Storage System Not Available")
            except Exception as e:
                _LOGGER.debug(f"Note: Unified storage check: {e}")
                if hasattr(self.main_gui, 'update_header_status'):
                    self.main_gui.update_header_status("⚙️ Standard Template Loading")
            
        except Exception as e:
            _LOGGER.debug(f"Storage system check completed: {e}")
            
            # Update GUI with standard status (no error)
            if hasattr(self.main_gui, 'update_header_status'):
                self.main_gui.update_header_status("⚙️ Ready for Analysis")
    
    def _store_window_state(self):
        pass
    
    def restore_window_state(self):
        pass
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def _notify_settings_changed(self):
        """Notify all callbacks that settings have changed"""
        for callback in self.settings_changed_callbacks:
            try:
                callback(self.current_settings)
            except Exception as e:
                _LOGGER.error(f"Error in settings change callback: {e}")
    
    def add_settings_changed_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback to be called when settings change"""
        self.settings_changed_callbacks.append(callback)
    
    def remove_settings_changed_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove settings change callback"""
        if callback in self.settings_changed_callbacks:
            self.settings_changed_callbacks.remove(callback)
    
    def reset_to_defaults(self) -> bool:
        """Reset all GUI settings to defaults"""
        try:
            defaults = self._get_default_settings()
            self.apply_settings(defaults)
            
            if self.current_settings.get('auto_save_settings', True):
                self.save_settings(defaults)
            
            _LOGGER.info("GUI settings reset to defaults")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error resetting settings: {e}")
            return False
    
    def export_settings(self, file_path: Path) -> bool:
        """Export current settings to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)
            
            _LOGGER.info(f"Exported GUI settings to {file_path}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: Path) -> bool:
        """Import settings from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validate and merge with defaults
            defaults = self._get_default_settings()
            merged_settings = {**defaults, **imported_settings}
            
            self.apply_settings(merged_settings)
            
            if merged_settings.get('auto_save_settings', True):
                self.save_settings(merged_settings)
            
            _LOGGER.info(f"Imported GUI settings from {file_path}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error importing settings: {e}")
            return False 
