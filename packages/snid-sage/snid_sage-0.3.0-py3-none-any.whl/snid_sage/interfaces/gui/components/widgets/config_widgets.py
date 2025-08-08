"""
SNID SAGE - Configuration Widgets
==================================

Specialized UI widgets for configuration parameters with:
- Live validation and visual feedback
- Theme integration and modern styling
- Advanced parameter controls (sliders, validated entries, etc.)
- Tooltip and help system
- Responsive design

Part of the modular configuration architecture following SNID SAGE patterns.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, Callable, Optional, List, Union, Dict, Tuple
import threading
import time
import traceback

from snid_sage.shared.utils.config import ValidationResult, ConfigValidationRule

# Import centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.config_widgets')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.config_widgets')


class ValidationMixin:
    """Mixin for widgets with validation capabilities"""
    
    def __init__(self):
        self.validation_rule: Optional[ConfigValidationRule] = None
        self.validation_callback: Optional[Callable[[bool, str], None]] = None
        self.last_validation_result = True
        self.validation_message = ""
    
    def set_validation_rule(self, rule: ConfigValidationRule):
        """Set validation rule for this widget"""
        self.validation_rule = rule
    
    def set_validation_callback(self, callback: Callable[[bool, str], None]):
        """Set callback for validation results"""
        self.validation_callback = callback
    
    def validate_value(self, value: Any) -> Tuple[bool, str]:
        """Validate value against rule"""
        if not self.validation_rule:
            return True, ""
        
        try:
            # Check min/max values
            if (self.validation_rule.min_value is not None and 
                isinstance(value, (int, float)) and value < self.validation_rule.min_value):
                return False, self.validation_rule.error_message
            
            if (self.validation_rule.max_value is not None and 
                isinstance(value, (int, float)) and value > self.validation_rule.max_value):
                return False, self.validation_rule.error_message
            
            # Check allowed values
            if (self.validation_rule.allowed_values is not None and 
                value not in self.validation_rule.allowed_values):
                return False, self.validation_rule.error_message
            
            # Check custom validator
            if self.validation_rule.custom_validator is not None:
                if not self.validation_rule.custom_validator(value):
                    return False, self.validation_rule.error_message
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def _update_validation_state(self, is_valid: bool, message: str):
        """Update validation state and notify callback"""
        self.last_validation_result = is_valid
        self.validation_message = message
        
        if self.validation_callback:
            self.validation_callback(is_valid, message)


class ThemedFrame(ttk.Frame):
    """Frame with theme integration"""
    
    def __init__(self, parent, theme_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_manager = theme_manager
        self._apply_theme()
    
    def _apply_theme(self):
        """Theme handled by parent components"""
        pass


class ValidatedEntry(ttk.Entry, ValidationMixin):
    """Entry widget with live validation and visual feedback"""
    
    def __init__(self, parent, theme_manager=None, **kwargs):
        ttk.Entry.__init__(self, parent, **kwargs)
        ValidationMixin.__init__(self)
        
        self.theme_manager = theme_manager
        self.var = kwargs.get('textvariable', tk.StringVar())
        
        # Bind validation events
        self.var.trace_add('write', self._on_value_changed)
        self.bind('<FocusOut>', self._on_focus_out)
        
        # Create validation feedback label
        self.validation_label = None
        self._setup_validation_feedback()
    
    def _setup_validation_feedback(self):
        """Setup visual validation feedback"""
        # This will be positioned by the parent container
        pass
    
    def _on_value_changed(self, *args):
        """Handle value changes for live validation"""
        try:
            value = self.var.get()
            
            # Try to convert to appropriate type
            if self.validation_rule:
                if self.validation_rule.min_value is not None or self.validation_rule.max_value is not None:
                    try:
                        if '.' in value:
                            value = float(value) if value else 0.0
                        else:
                            value = int(value) if value else 0
                    except ValueError:
                        self._update_validation_state(False, "Invalid number format")
                        self._update_visual_state(False)
                        return
            
            is_valid, message = self.validate_value(value)
            self._update_validation_state(is_valid, message)
            self._update_visual_state(is_valid)
            
        except Exception as e:
            self._update_validation_state(False, str(e))
            self._update_visual_state(False)
    
    def _on_focus_out(self, event):
        """Handle focus out events"""
        self._on_value_changed()
    
    def _update_visual_state(self, is_valid: bool):
        """Update visual state based on validation"""
        if self.theme_manager:
            colors = self.theme_manager.get_current_colors()
            if is_valid:
                self.configure(style='Valid.TEntry')
            else:
                self.configure(style='Invalid.TEntry')
    
    def get_value(self):
        """Get the current value with proper type conversion"""
        value = self.var.get()
        
        if self.validation_rule:
            if self.validation_rule.min_value is not None or self.validation_rule.max_value is not None:
                try:
                    if '.' in value:
                        return float(value) if value else 0.0
                    else:
                        return int(value) if value else 0
                except ValueError:
                    return 0
        
        return value
    
    def set_value(self, value):
        """Set value with proper formatting"""
        self.var.set(str(value))


class ParameterSlider(ttk.Frame, ValidationMixin):
    """Advanced parameter slider with entry field and validation"""
    
    def __init__(self, parent, from_=0, to=100, resolution=1, 
                 theme_manager=None, **kwargs):
        ttk.Frame.__init__(self, parent)
        ValidationMixin.__init__(self)
        
        self.theme_manager = theme_manager
        self.from_ = from_
        self.to = to
        self.resolution = resolution
        
        self.var = tk.DoubleVar()
        self.var.trace_add('write', self._on_value_changed)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create slider and entry widgets"""
        # Value entry
        self.entry = ValidatedEntry(self, textvariable=self.var, 
                                   width=10, theme_manager=self.theme_manager)
        self.entry.pack(side='left', padx=(0, 10))
        
        # Slider
        self.slider = ttk.Scale(self, from_=self.from_, to=self.to,
                               orient='horizontal', variable=self.var,
                               command=self._on_slider_changed)
        self.slider.pack(side='left', fill='x', expand=True)
        
        # Min/max labels
        self.min_label = ttk.Label(self, text=str(self.from_), font=('Segoe UI', 8))
        self.min_label.pack(side='left', padx=(5, 0))
        
        self.max_label = ttk.Label(self, text=str(self.to), font=('Segoe UI', 8))
        self.max_label.pack(side='left', padx=(2, 0))
    
    def _on_slider_changed(self, value):
        """Handle slider value changes"""
        # Round to resolution
        rounded_value = round(float(value) / self.resolution) * self.resolution
        self.var.set(rounded_value)
    
    def _on_value_changed(self, *args):
        """Handle value changes"""
        value = self.var.get()
        is_valid, message = self.validate_value(value)
        self._update_validation_state(is_valid, message)
    
    def get_value(self):
        """Get current value"""
        return self.var.get()
    
    def set_value(self, value):
        """Set current value"""
        self.var.set(float(value))
    
    def set_validation_rule(self, rule: ConfigValidationRule):
        """Set validation rule and update range if needed"""
        ValidationMixin.set_validation_rule(self, rule)
        self.entry.set_validation_rule(rule)
        
        # Update slider range based on validation rule
        if rule.min_value is not None:
            self.from_ = rule.min_value
            self.slider.configure(from_=rule.min_value)
            self.min_label.configure(text=str(rule.min_value))
        
        if rule.max_value is not None:
            self.to = rule.max_value
            self.slider.configure(to=rule.max_value)
            self.max_label.configure(text=str(rule.max_value))


class PathSelector(ttk.Frame, ValidationMixin):
    """Path selector widget with browse button and validation"""
    
    def __init__(self, parent, path_type='directory', theme_manager=None, **kwargs):
        ttk.Frame.__init__(self, parent)
        ValidationMixin.__init__(self)
        
        self.theme_manager = theme_manager
        self.path_type = path_type  # 'directory' or 'file'
        
        self.var = tk.StringVar()
        self.var.trace_add('write', self._on_value_changed)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create entry and browse button"""
        # Path entry
        self.entry = ValidatedEntry(self, textvariable=self.var,
                                   theme_manager=self.theme_manager)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Browse button
        self.browse_btn = ttk.Button(self, text="Browse", command=self._browse)
        self.browse_btn.pack(side='right')
    
    def _apply_theme(self):
        """Apply current theme"""
        if self.theme_manager:
            # Apply theme to this widget only to prevent interference with workflow-managed buttons
            self.theme_manager.apply_theme(target_widget=self)
    
    def _browse(self):
        """Open file/directory browser"""
        try:
            if self.path_type == 'directory':
                path = filedialog.askdirectory(
                    title="Select Directory",
                    initialdir=self.var.get() or "."
                )
            else:
                path = filedialog.askopenfilename(
                    title="Select File",
                    initialdir=self.var.get() or "."
                )
            
            if path:
                self.var.set(path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to browse: {e}")
    
    def _on_value_changed(self, *args):
        """Handle path changes"""
        value = self.var.get()
        is_valid, message = self.validate_value(value)
        self._update_validation_state(is_valid, message)
    
    def get_value(self):
        """Get current path"""
        return self.var.get()
    
    def set_value(self, value):
        """Set current path"""
        self.var.set(str(value))
    
    def set_validation_rule(self, rule: ConfigValidationRule):
        """Set validation rule"""
        ValidationMixin.set_validation_rule(self, rule)
        self.entry.set_validation_rule(rule)


class ThemedCombobox(ttk.Combobox, ValidationMixin):
    """Themed combobox with validation"""
    
    def __init__(self, parent, values=None, theme_manager=None, **kwargs):
        ttk.Combobox.__init__(self, parent, values=values or [], **kwargs)
        ValidationMixin.__init__(self)
        
        self.theme_manager = theme_manager
        self.var = kwargs.get('textvariable', tk.StringVar())
        
        self.var.trace_add('write', self._on_value_changed)
        self.bind('<<ComboboxSelected>>', self._on_selection_changed)
    
    def _apply_theme(self):
        """Apply current theme"""
        if self.theme_manager:
            # Apply theme to this widget only to prevent interference with workflow-managed buttons
            self.theme_manager.apply_theme(target_widget=self)
    
    def _on_value_changed(self, *args):
        """Handle value changes"""
        value = self.var.get()
        is_valid, message = self.validate_value(value)
        self._update_validation_state(is_valid, message)
    
    def _on_selection_changed(self, event):
        """Handle selection changes"""
        self._on_value_changed()
    
    def get_value(self):
        """Get current value"""
        return self.var.get()
    
    def set_value(self, value):
        """Set current value"""
        self.var.set(str(value))


class ValidationLabel(ttk.Label):
    """Label for displaying validation messages"""
    
    def __init__(self, parent, theme_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_manager = theme_manager
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply current theme"""
        if self.theme_manager:
            # Apply theme to this widget only to prevent interference with workflow-managed buttons
            self.theme_manager.apply_theme(target_widget=self)
    
    def show_validation_message(self, is_valid: bool, message: str):
        """Show validation message with appropriate styling"""
        if message:
            self.configure(text=message)
            if self.theme_manager:
                colors = self.theme_manager.get_current_colors()
                color = colors.get('success', '#10b981') if is_valid else colors.get('danger', '#ef4444')
                self.configure(foreground=color)
        else:
            self.configure(text="")


class TooltipMixin:
    """Mixin for adding tooltips to widgets"""
    
    def __init__(self):
        self.tooltip = None
        self.tooltip_text = ""
    
    def set_tooltip(self, text: str):
        """Set tooltip text"""
        self.tooltip_text = text
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Motion>', self._on_motion)
    
    def _on_enter(self, event):
        """Show tooltip on enter"""
        if self.tooltip_text:
            self._show_tooltip(event)
    
    def _on_leave(self, event):
        """Hide tooltip on leave"""
        self._hide_tooltip()
    
    def _on_motion(self, event):
        """Update tooltip position"""
        if self.tooltip:
            self._update_tooltip_position(event)
    
    def _show_tooltip(self, event):
        """Show tooltip window"""
        if self.tooltip:
            return
        
        x = event.x_root + 10
        y = event.y_root + 10
        
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.tooltip_text,
                         background='#ffffe0', relief='solid', borderwidth=1,
                         font=('Segoe UI', 9), padding=5)
        label.pack()
    
    def _hide_tooltip(self):
        """Hide tooltip window"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def _update_tooltip_position(self, event):
        """Update tooltip position"""
        if self.tooltip:
            x = event.x_root + 10
            y = event.y_root + 10
            self.tooltip.wm_geometry(f"+{x}+{y}")


class ConfigParameterWidget(ttk.Frame):
    """Complete parameter widget with label, control, validation, and tooltip"""
    
    def __init__(self, parent, param_name: str, param_config: Dict[str, Any],
                 theme_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.param_name = param_name
        self.param_config = param_config
        self.theme_manager = theme_manager
        
        self.control_widget = None
        self.validation_label = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create complete parameter widget"""
        # Parameter label
        label_text = self.param_config.get('label', self.param_name.replace('_', ' ').title())
        self.label = ttk.Label(self, text=f"{label_text}:")
        self.label.pack(anchor='w', pady=(5, 2))
        
        # Control widget frame
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', pady=(0, 2))
        
        # Create appropriate control widget
        widget_type = self.param_config.get('widget_type', 'entry')
        
        if widget_type == 'entry':
            self.control_widget = ValidatedEntry(control_frame, theme_manager=self.theme_manager)
            self.control_widget.pack(fill='x')
            
        elif widget_type == 'slider':
            slider_config = self.param_config.get('slider_config', {})
            self.control_widget = ParameterSlider(
                control_frame, 
                theme_manager=self.theme_manager,
                **slider_config
            )
            self.control_widget.pack(fill='x')
            
        elif widget_type == 'combobox':
            values = self.param_config.get('values', [])
            self.control_widget = ThemedCombobox(
                control_frame, 
                values=values,
                theme_manager=self.theme_manager
            )
            self.control_widget.pack(fill='x')
            
        elif widget_type == 'path':
            path_type = self.param_config.get('path_type', 'directory')
            self.control_widget = PathSelector(
                control_frame,
                path_type=path_type,
                theme_manager=self.theme_manager
            )
            self.control_widget.pack(fill='x')
        
        # Validation label
        self.validation_label = ValidationLabel(self, theme_manager=self.theme_manager)
        self.validation_label.pack(anchor='w', pady=(0, 5))
        
        # Setup validation callback
        if hasattr(self.control_widget, 'set_validation_callback'):
            self.control_widget.set_validation_callback(self._on_validation_result)
        
        # Setup validation rule
        validation_rule = self.param_config.get('validation_rule')
        if validation_rule and hasattr(self.control_widget, 'set_validation_rule'):
            self.control_widget.set_validation_rule(validation_rule)
        
        # Setup tooltip
        tooltip_text = self.param_config.get('tooltip')
        if tooltip_text and hasattr(self.control_widget, 'set_tooltip'):
            self.control_widget.set_tooltip(tooltip_text)
    
    def _on_validation_result(self, is_valid: bool, message: str):
        """Handle validation results"""
        if self.validation_label:
            self.validation_label.show_validation_message(is_valid, message)
    
    def get_value(self):
        """Get current parameter value"""
        if self.control_widget and hasattr(self.control_widget, 'get_value'):
            return self.control_widget.get_value()
        return None
    
    def set_value(self, value):
        """Set parameter value"""
        if self.control_widget and hasattr(self.control_widget, 'set_value'):
            self.control_widget.set_value(value)
    
    def is_valid(self) -> bool:
        """Check if current value is valid"""
        if hasattr(self.control_widget, 'last_validation_result'):
            return self.control_widget.last_validation_result
        return True 
