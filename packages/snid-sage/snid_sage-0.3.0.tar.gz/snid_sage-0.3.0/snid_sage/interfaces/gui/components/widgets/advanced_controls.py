"""
SNID SAGE - Advanced Control Widgets
====================================

Advanced parameter controls and range selectors for SNID SAGE GUI.
Provides sophisticated input controls for numerical parameters and ranges.

Part of the SNID SAGE GUI restructuring - Components Module
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Tuple, Union, Any


class ParameterControl(ttk.Frame):
    """
    Advanced parameter control widget with validation, tooltips, and presets.
    """
    
    def __init__(self, parent, label="Parameter", value=0.0, min_val=None, max_val=None, 
                 increment=1.0, format_str="{:.2f}", units="", presets=None, 
                 command=None, **kwargs):
        """
        Initialize the parameter control.
        
        Args:
            parent: Parent widget
            label: Parameter label
            value: Initial value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            increment: Increment for spinbox
            format_str: Format string for display
            units: Units label
            presets: Dict of preset values
            command: Callback function when value changes
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.label_text = label
        self.current_value = value
        self.min_val = min_val
        self.max_val = max_val
        self.increment = increment
        self.format_str = format_str
        self.units = units
        self.presets = presets or {}
        self.command = command
        self.is_valid = True
        
        self._create_widgets()
        self._setup_layout()
        self._update_display()
    
    def _create_widgets(self):
        """Create the parameter control widgets"""
        # Label
        self.label = ttk.Label(self, text=self.label_text)
        
        # Value variable and spinbox
        self.value_var = tk.StringVar()
        self.spinbox = ttk.Spinbox(
            self,
            textvariable=self.value_var,
            from_=self.min_val if self.min_val is not None else -999999,
            to=self.max_val if self.max_val is not None else 999999,
            increment=self.increment,
            width=12,
            command=self._on_spinbox_change,
            validate='key',
            validatecommand=(self.register(self._validate_input), '%P')
        )
        
        # Bind additional events
        self.value_var.trace_add('write', self._on_value_change)
        
        # Units label
        if self.units:
            self.units_label = ttk.Label(self, text=self.units)
        
        # Presets dropdown
        if self.presets:
            self.preset_var = tk.StringVar()
            self.preset_combo = ttk.Combobox(
                self,
                textvariable=self.preset_var,
                values=list(self.presets.keys()),
                state='readonly',
                width=10
            )
            self.preset_combo.bind('<<ComboboxSelected>>', self._on_preset_selected)
        
        # Validation indicator
        self.validation_label = ttk.Label(self, text="✓", foreground="green", width=2)
    
    def _setup_layout(self):
        """Setup the widget layout"""
        col = 0
        
        # Label
        self.label.grid(row=0, column=col, sticky='w', padx=(0, 5))
        col += 1
        
        # Spinbox
        self.spinbox.grid(row=0, column=col, padx=(0, 2))
        col += 1
        
        # Units
        if self.units:
            self.units_label.grid(row=0, column=col, sticky='w', padx=(2, 5))
            col += 1
        
        # Validation indicator
        self.validation_label.grid(row=0, column=col, padx=(2, 5))
        col += 1
        
        # Presets
        if self.presets:
            ttk.Label(self, text="Presets:").grid(row=0, column=col, sticky='w', padx=(5, 2))
            col += 1
            self.preset_combo.grid(row=0, column=col, padx=(0, 5))
    
    def _validate_input(self, value: str) -> bool:
        """Validate input value"""
        if not value:  # Allow empty string during editing
            return True
        
        try:
            float_val = float(value)
            
            # Check range
            if self.min_val is not None and float_val < self.min_val:
                return False
            if self.max_val is not None and float_val > self.max_val:
                return False
            
            return True
        except ValueError:
            return False
    
    def _on_spinbox_change(self):
        """Handle spinbox change"""
        try:
            value = float(self.value_var.get())
            self.current_value = value
            self._update_validation()
            
            if self.command:
                self.command(value)
        except ValueError:
            pass
    
    def _on_value_change(self, *args):
        """Handle value variable change"""
        try:
            value_str = self.value_var.get()
            if value_str:
                value = float(value_str)
                self.current_value = value
                self._update_validation()
        except ValueError:
            self._update_validation(False)
    
    def _on_preset_selected(self, event=None):
        """Handle preset selection"""
        preset_name = self.preset_var.get()
        if preset_name in self.presets:
            self.set_value(self.presets[preset_name])
    
    def _update_validation(self, valid=None):
        """Update validation indicator"""
        if valid is None:
            valid = self._validate_input(self.value_var.get())
        
        self.is_valid = valid
        
        if valid:
            self.validation_label.configure(text="✓", foreground="green")
            self.spinbox.configure(style="TSpinbox")
        else:
            self.validation_label.configure(text="✗", foreground="red")
            self.spinbox.configure(style="Invalid.TSpinbox")
    
    def _update_display(self):
        """Update the display value"""
        formatted_value = self.format_str.format(self.current_value)
        self.value_var.set(formatted_value)
    
    def get_value(self) -> float:
        """Get the current value"""
        return self.current_value
    
    def set_value(self, value: float):
        """Set the current value"""
        # Validate range
        if self.min_val is not None:
            value = max(value, self.min_val)
        if self.max_val is not None:
            value = min(value, self.max_val)
        
        self.current_value = value
        self._update_display()
        self._update_validation()
        
        if self.command:
            self.command(value)
    
    def add_preset(self, name: str, value: float):
        """Add a new preset"""
        if hasattr(self, 'preset_combo'):
            self.presets[name] = value
            self.preset_combo.configure(values=list(self.presets.keys()))
    
    def is_value_valid(self) -> bool:
        """Check if current value is valid"""
        return self.is_valid


class RangeSelector(ttk.Frame):
    """
    Range selector widget for selecting min/max value pairs.
    """
    
    def __init__(self, parent, label="Range", min_value=0.0, max_value=100.0,
                 range_min=None, range_max=None, format_str="{:.2f}", units="",
                 command=None, **kwargs):
        """
        Initialize the range selector.
        
        Args:
            parent: Parent widget
            label: Range label
            min_value: Initial minimum value
            max_value: Initial maximum value
            range_min: Absolute minimum allowed
            range_max: Absolute maximum allowed
            format_str: Format string for display
            units: Units label
            command: Callback function when range changes
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.label_text = label
        self.current_min = min_value
        self.current_max = max_value
        self.range_min = range_min
        self.range_max = range_max
        self.format_str = format_str
        self.units = units
        self.command = command
        
        self._create_widgets()
        self._setup_layout()
        self._update_display()
    
    def _create_widgets(self):
        """Create the range selector widgets"""
        # Label
        self.label = ttk.Label(self, text=self.label_text)
        
        # Minimum value control
        self.min_var = tk.StringVar()
        self.min_spinbox = ttk.Spinbox(
            self,
            textvariable=self.min_var,
            from_=self.range_min if self.range_min is not None else -999999,
            to=self.range_max if self.range_max is not None else 999999,
            width=10,
            command=self._on_min_change
        )
        self.min_var.trace_add('write', self._on_min_var_change)
        
        # Separator
        self.separator_label = ttk.Label(self, text="to")
        
        # Maximum value control
        self.max_var = tk.StringVar()
        self.max_spinbox = ttk.Spinbox(
            self,
            textvariable=self.max_var,
            from_=self.range_min if self.range_min is not None else -999999,
            to=self.range_max if self.range_max is not None else 999999,
            width=10,
            command=self._on_max_change
        )
        self.max_var.trace_add('write', self._on_max_var_change)
        
        # Units label
        if self.units:
            self.units_label = ttk.Label(self, text=self.units)
        
        # Range validation indicator
        self.validation_label = ttk.Label(self, text="✓", foreground="green", width=2)
        
        # Quick range buttons
        self.quick_buttons_frame = ttk.Frame(self)
        
        # Common preset ranges
        presets = [
            ("Full Range", self._set_full_range),
            ("Reset", self._reset_range)
        ]
        
        for text, command in presets:
            btn = ttk.Button(self.quick_buttons_frame, text=text, command=command, width=8)
            btn.pack(side='left', padx=2)
    
    def _setup_layout(self):
        """Setup the widget layout"""
        # Main controls row
        self.label.grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.min_spinbox.grid(row=0, column=1, padx=2)
        self.separator_label.grid(row=0, column=2, padx=5)
        self.max_spinbox.grid(row=0, column=3, padx=2)
        
        col = 4
        if self.units:
            self.units_label.grid(row=0, column=col, sticky='w', padx=(5, 2))
            col += 1
        
        self.validation_label.grid(row=0, column=col, padx=(5, 2))
        
        # Quick buttons row
        self.quick_buttons_frame.grid(row=1, column=0, columnspan=col+1, pady=(5, 0), sticky='w')
    
    def _on_min_change(self):
        """Handle minimum value change"""
        try:
            value = float(self.min_var.get())
            self.current_min = value
            self._validate_range()
            self._notify_change()
        except ValueError:
            pass
    
    def _on_max_change(self):
        """Handle maximum value change"""
        try:
            value = float(self.max_var.get())
            self.current_max = value
            self._validate_range()
            self._notify_change()
        except ValueError:
            pass
    
    def _on_min_var_change(self, *args):
        """Handle minimum variable change"""
        self._validate_range()
    
    def _on_max_var_change(self, *args):
        """Handle maximum variable change"""
        self._validate_range()
    
    def _validate_range(self):
        """Validate the current range"""
        try:
            min_val = float(self.min_var.get()) if self.min_var.get() else self.current_min
            max_val = float(self.max_var.get()) if self.max_var.get() else self.current_max
            
            # Check if min <= max
            valid = min_val <= max_val
            
            # Check absolute bounds
            if self.range_min is not None:
                valid = valid and min_val >= self.range_min and max_val >= self.range_min
            if self.range_max is not None:
                valid = valid and min_val <= self.range_max and max_val <= self.range_max
            
            # Update validation indicator
            if valid:
                self.validation_label.configure(text="✓", foreground="green")
                self.min_spinbox.configure(style="TSpinbox")
                self.max_spinbox.configure(style="TSpinbox")
            else:
                self.validation_label.configure(text="✗", foreground="red")
                if min_val > max_val:
                    # Highlight both if min > max
                    self.min_spinbox.configure(style="Invalid.TSpinbox")
                    self.max_spinbox.configure(style="Invalid.TSpinbox")
            
            return valid
            
        except ValueError:
            self.validation_label.configure(text="✗", foreground="red")
            return False
    
    def _notify_change(self):
        """Notify about range change"""
        if self.command and self._validate_range():
            self.command(self.current_min, self.current_max)
    
    def _update_display(self):
        """Update the display values"""
        self.min_var.set(self.format_str.format(self.current_min))
        self.max_var.set(self.format_str.format(self.current_max))
    
    def _set_full_range(self):
        """Set to full allowed range"""
        if self.range_min is not None and self.range_max is not None:
            self.set_range(self.range_min, self.range_max)
    
    def _reset_range(self):
        """Reset to initial values"""
        self.set_range(0.0, 100.0)
    
    def get_range(self) -> Tuple[float, float]:
        """Get the current range"""
        return (self.current_min, self.current_max)
    
    def set_range(self, min_value: float, max_value: float):
        """Set the current range"""
        # Validate and constrain values
        if self.range_min is not None:
            min_value = max(min_value, self.range_min)
            max_value = max(max_value, self.range_min)
        if self.range_max is not None:
            min_value = min(min_value, self.range_max)
            max_value = min(max_value, self.range_max)
        
        # Ensure min <= max
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        
        self.current_min = min_value
        self.current_max = max_value
        self._update_display()
        self._validate_range()
        self._notify_change()
    
    def is_range_valid(self) -> bool:
        """Check if current range is valid"""
        return self._validate_range()


# Setup custom styles for validation
def setup_advanced_control_styles():
    """Setup custom styles for advanced controls"""
    try:
        style = ttk.Style()
        
        # Invalid style for spinboxes
        style.configure(
            "Invalid.TSpinbox",
            fieldbackground='#ffe6e6',  # Light red background
            bordercolor='#ff0000',      # Red border
            focuscolor='#ff0000'        # Red focus color
        )
        
    except Exception as e:
        print(f"Could not setup advanced control styles: {e}")


# Example usage and testing
if __name__ == "__main__":
    def test_advanced_controls():
        root = tk.Tk()
        root.title("Advanced Control Widgets Test")
        root.geometry("700x500")
        
        # Setup styles
        setup_advanced_control_styles()
        
        # Test ParameterControl
        param_frame = ttk.LabelFrame(root, text="Parameter Controls", padding=10)
        param_frame.pack(fill='x', padx=10, pady=5)
        
        # Simple parameter
        param1 = ParameterControl(
            param_frame,
            label="Redshift:",
            value=0.05,
            min_val=-0.01,
            max_val=2.0,
            increment=0.001,
            format_str="{:.3f}",
            command=lambda val: print(f"Redshift: {val}")
        )
        param1.pack(pady=2, anchor='w')
        
        # Parameter with units and presets
        age_presets = {
            "Maximum": -20.0,
            "Peak": 0.0,
            "Post-peak": 20.0,
            "Late": 100.0
        }
        
        param2 = ParameterControl(
            param_frame,
            label="Age:",
            value=0.0,
            min_val=-50.0,
            max_val=500.0,
            increment=1.0,
            format_str="{:.0f}",
            units="days",
            presets=age_presets,
            command=lambda val: print(f"Age: {val} days")
        )
        param2.pack(pady=2, anchor='w')
        
        # Test RangeSelector
        range_frame = ttk.LabelFrame(root, text="Range Selectors", padding=10)
        range_frame.pack(fill='x', padx=10, pady=5)
        
        # Wavelength range
        wave_range = RangeSelector(
            range_frame,
            label="Wavelength:",
            min_value=3500.0,
            max_value=7500.0,
            range_min=1000.0,
            range_max=15000.0,
            format_str="{:.0f}",
            units="Å",
            command=lambda min_val, max_val: print(f"Wavelength range: {min_val} - {max_val} Å")
        )
        wave_range.pack(pady=5, anchor='w')
        
        # Correlation range
        corr_range = RangeSelector(
            range_frame,
            label="Correlation:",
            min_value=3.0,
            max_value=20.0,
            range_min=0.0,
            range_max=50.0,
            format_str="{:.1f}",
            command=lambda min_val, max_val: print(f"Correlation range: {min_val} - {max_val}")
        )
        corr_range.pack(pady=5, anchor='w')
        
        # Control buttons
        control_frame = ttk.Frame(root)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        def get_all_values():
            print("Current values:")
            print(f"  Redshift: {param1.get_value()}")
            print(f"  Age: {param2.get_value()}")
            print(f"  Wavelength range: {wave_range.get_range()}")
            print(f"  Correlation range: {corr_range.get_range()}")
            print(f"Validation status:")
            print(f"  Redshift valid: {param1.is_value_valid()}")
            print(f"  Age valid: {param2.is_value_valid()}")
            print(f"  Wavelength range valid: {wave_range.is_range_valid()}")
            print(f"  Correlation range valid: {corr_range.is_range_valid()}")
        
        def set_test_values():
            param1.set_value(0.1)
            param2.set_value(15.0)
            wave_range.set_range(4000.0, 8000.0)
            corr_range.set_range(5.0, 15.0)
        
        def add_preset():
            param2.add_preset("Custom", 50.0)
        
        ttk.Button(control_frame, text="Get All Values", 
                  command=get_all_values).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Set Test Values", 
                  command=set_test_values).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Add Custom Preset", 
                  command=add_preset).pack(side='left', padx=5)
        
        root.mainloop()
    
    test_advanced_controls() 
