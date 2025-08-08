"""
SNID SAGE - Custom Toggle Widgets
=================================

Custom toggle button and segmented control implementations for the SNID SAGE GUI.
Provides modern, interactive toggle controls with theme support.

Part of the SNID SAGE GUI restructuring - Components Module
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from typing import Optional, Callable, List, Any


class CustomToggleButton(ttk.Frame):
    """
    Custom toggle button with modern styling and enhanced functionality.
    """
    
    def __init__(self, parent, text="Toggle", variable=None, command=None, **kwargs):
        """
        Initialize the custom toggle button.
        
        Args:
            parent: Parent widget
            text: Button text
            variable: BooleanVar to track state
            command: Callback function when toggled
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.text = text
        self.variable = variable or tk.BooleanVar()
        self.command = command
        self.enabled = True
        
        # Create the button
        self.button = ttk.Button(
            self,
            text=self.text,
            command=self._on_toggle,
            style="Toggle.TButton"
        )
        self.button.pack(fill='both', expand=True)
        
        # Initialize appearance
        self._update_appearance()
        
        # Bind variable changes
        if self.variable:
            self.variable.trace_add('write', self._on_variable_change)
    
    def _on_toggle(self):
        """Handle button toggle"""
        if not self.enabled:
            return
            
        # Toggle the variable
        self.variable.set(not self.variable.get())
        
        # Call command if provided
        if self.command:
            self.command()
    
    def _on_variable_change(self, *args):
        """Handle variable change"""
        self._update_appearance()
    
    def _update_appearance(self):
        """Update button appearance based on state"""
        if self.variable.get():
            # Active/pressed state
            self.button.configure(style="ToggleActive.TButton")
        else:
            # Inactive state
            self.button.configure(style="Toggle.TButton")
    
    def set_state(self, enabled: bool):
        """Set the enabled state of the toggle"""
        self.enabled = enabled
        if enabled:
            self.button.configure(state='normal')
        else:
            self.button.configure(state='disabled')
    
    def get(self) -> bool:
        """Get the current toggle state"""
        return self.variable.get()
    
    def set(self, value: bool):
        """Set the toggle state"""
        self.variable.set(value)


class SegmentedControl(ttk.Frame):
    """
    Segmented control widget similar to iOS/macOS style controls.
    Allows selection of one option from multiple choices.
    """
    
    def __init__(self, parent, options: List[str], variable=None, command=None, **kwargs):
        """
        Initialize the segmented control.
        
        Args:
            parent: Parent widget
            options: List of option strings
            variable: StringVar to track selected option
            command: Callback function when selection changes
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.options = options
        self.variable = variable or tk.StringVar()
        self.command = command
        self.buttons = []
        self.enabled = True
        
        # Set default value if none set
        if not self.variable.get() and self.options:
            self.variable.set(self.options[0])
        
        # Create the buttons
        self._create_buttons()
        
        # Initialize appearance
        self._update_appearance()
        
        # Bind variable changes
        if self.variable:
            self.variable.trace_add('write', self._on_variable_change)
    
    def _create_buttons(self):
        """Create the segment buttons"""
        for i, option in enumerate(self.options):
            button = ttk.Button(
                self,
                text=option,
                command=lambda opt=option: self._on_select(opt),
                style="Segment.TButton"
            )
            
            # Pack buttons side by side
            button.pack(side='left', fill='both', expand=True)
            self.buttons.append(button)
    
    def _on_select(self, option: str):
        """Handle option selection"""
        if not self.enabled:
            return
            
        self.variable.set(option)
        
        if self.command:
            self.command()
    
    def _on_variable_change(self, *args):
        """Handle variable change"""
        self._update_appearance()
    
    def _update_appearance(self):
        """Update button appearances based on selection"""
        selected = self.variable.get()
        
        for i, button in enumerate(self.buttons):
            if self.options[i] == selected:
                # Selected state
                button.configure(style="SegmentSelected.TButton")
            else:
                # Unselected state
                button.configure(style="Segment.TButton")
    
    def set_state(self, enabled: bool):
        """Set the enabled state of the segmented control"""
        self.enabled = enabled
        state = 'normal' if enabled else 'disabled'
        
        for button in self.buttons:
            button.configure(state=state)
    
    def get(self) -> str:
        """Get the currently selected option"""
        return self.variable.get()
    
    def set(self, value: str):
        """Set the selected option"""
        if value in self.options:
            self.variable.set(value)
    
    def add_option(self, option: str):
        """Add a new option to the segmented control"""
        if option not in self.options:
            self.options.append(option)
            
            button = ttk.Button(
                self,
                text=option,
                command=lambda opt=option: self._on_select(opt),
                style="Segment.TButton"
            )
            button.pack(side='left', fill='both', expand=True)
            self.buttons.append(button)
            
            self._update_appearance()
    
    def remove_option(self, option: str):
        """Remove an option from the segmented control"""
        if option in self.options:
            index = self.options.index(option)
            self.options.remove(option)
            
            # Remove and destroy the corresponding button
            button = self.buttons.pop(index)
            button.destroy()
            
            # If removed option was selected, select first available
            if self.variable.get() == option and self.options:
                self.variable.set(self.options[0])
            
            self._update_appearance()


def setup_toggle_styles(style: ttk.Style = None):
    """
    Setup custom styles for toggle widgets.
    
    Args:
        style: TTK Style object, creates new one if None
    """
    if style is None:
        style = ttk.Style()
    
    # Toggle button styles
    style.configure(
        "Toggle.TButton",
        focuscolor='none',
        borderwidth=1,
        relief='raised'
    )
    
    style.configure(
        "ToggleActive.TButton",
        focuscolor='none',
        borderwidth=2,
        relief='sunken',
        background='#0078d4',  # Blue active color
        foreground='white'
    )
    
    # Segmented control styles
    style.configure(
        "Segment.TButton",
        focuscolor='none',
        borderwidth=1,
        relief='raised'
    )
    
    style.configure(
        "SegmentSelected.TButton",
        focuscolor='none',
        borderwidth=2,
        relief='sunken',
        background='#0078d4',  # Blue selected color
        foreground='white'
    )
    
    # Map hover states
    style.map(
        "Toggle.TButton",
        background=[('active', '#e1e1e1')],
        relief=[('pressed', 'sunken')]
    )
    
    style.map(
        "ToggleActive.TButton",
        background=[('active', '#106ebe')],
        relief=[('pressed', 'sunken')]
    )
    
    style.map(
        "Segment.TButton",
        background=[('active', '#e1e1e1')],
        relief=[('pressed', 'sunken')]
    )
    
    style.map(
        "SegmentSelected.TButton",
        background=[('active', '#106ebe')],
        relief=[('pressed', 'sunken')]
    )


class ToggleGroup:
    """
    Group of toggle buttons that can be managed together.
    Useful for creating radio-button-like behavior or managing multiple toggles.
    """
    
    def __init__(self, exclusive=False):
        """
        Initialize the toggle group.
        
        Args:
            exclusive: If True, only one toggle can be active at a time
        """
        self.toggles = []
        self.exclusive = exclusive
        self.enabled = True
    
    def add_toggle(self, toggle: CustomToggleButton):
        """Add a toggle to the group"""
        if toggle not in self.toggles:
            self.toggles.append(toggle)
            
            if self.exclusive:
                # Override the toggle's command to handle exclusivity
                original_command = toggle.command
                
                def exclusive_command():
                    # Deactivate other toggles
                    for other_toggle in self.toggles:
                        if other_toggle != toggle and other_toggle.get():
                            other_toggle.set(False)
                    
                    # Call original command
                    if original_command:
                        original_command()
                
                toggle.command = exclusive_command
    
    def remove_toggle(self, toggle: CustomToggleButton):
        """Remove a toggle from the group"""
        if toggle in self.toggles:
            self.toggles.remove(toggle)
    
    def get_active_toggles(self) -> List[CustomToggleButton]:
        """Get list of currently active toggles"""
        return [toggle for toggle in self.toggles if toggle.get()]
    
    def set_all(self, value: bool):
        """Set all toggles to the same state"""
        for toggle in self.toggles:
            toggle.set(value)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all toggles in the group"""
        self.enabled = enabled
        for toggle in self.toggles:
            toggle.set_state(enabled)
    
    def clear_all(self):
        """Deactivate all toggles"""
        self.set_all(False)


# Example usage and testing
if __name__ == "__main__":
    # Create test window
    root = tk.Tk()
    root.title("Custom Toggle Widgets Test")
    root.geometry("600x400")
    
    # Setup styles
    setup_toggle_styles()
    
    # Test custom toggle button
    toggle_frame = ttk.LabelFrame(root, text="Custom Toggle Buttons", padding=10)
    toggle_frame.pack(fill='x', padx=10, pady=5)
    
    toggle_var1 = tk.BooleanVar()
    toggle1 = CustomToggleButton(
        toggle_frame,
        text="Enable Feature A",
        variable=toggle_var1,
        command=lambda: print(f"Toggle A: {toggle_var1.get()}")
    )
    toggle1.pack(side='left', padx=5)
    
    toggle_var2 = tk.BooleanVar()
    toggle2 = CustomToggleButton(
        toggle_frame,
        text="Enable Feature B",
        variable=toggle_var2,
        command=lambda: print(f"Toggle B: {toggle_var2.get()}")
    )
    toggle2.pack(side='left', padx=5)
    
    # Test segmented control
    segment_frame = ttk.LabelFrame(root, text="Segmented Control", padding=10)
    segment_frame.pack(fill='x', padx=10, pady=5)
    
    segment_var = tk.StringVar()
    segment_control = SegmentedControl(
        segment_frame,
        options=["Flux", "Flat", "Template"],
        variable=segment_var,
        command=lambda: print(f"Selected: {segment_var.get()}")
    )
    segment_control.pack(fill='x', pady=5)
    
    # Test toggle group
    group_frame = ttk.LabelFrame(root, text="Exclusive Toggle Group", padding=10)
    group_frame.pack(fill='x', padx=10, pady=5)
    
    toggle_group = ToggleGroup(exclusive=True)
    
    for i, option in enumerate(["Option 1", "Option 2", "Option 3"]):
        var = tk.BooleanVar()
        toggle = CustomToggleButton(
            group_frame,
            text=option,
            variable=var,
            command=lambda opt=option: print(f"Exclusive selection: {opt}")
        )
        toggle.pack(side='left', padx=5)
        toggle_group.add_toggle(toggle)
    
    # Control buttons
    control_frame = ttk.Frame(root)
    control_frame.pack(fill='x', padx=10, pady=10)
    
    ttk.Button(
        control_frame,
        text="Disable All",
        command=lambda: [toggle1.set_state(False), toggle2.set_state(False), 
                        segment_control.set_state(False), toggle_group.set_enabled(False)]
    ).pack(side='left', padx=5)
    
    ttk.Button(
        control_frame,
        text="Enable All",
        command=lambda: [toggle1.set_state(True), toggle2.set_state(True), 
                        segment_control.set_state(True), toggle_group.set_enabled(True)]
    ).pack(side='left', padx=5)
    
    ttk.Button(
        control_frame,
        text="Clear All",
        command=lambda: [toggle1.set(False), toggle2.set(False), toggle_group.clear_all()]
    ).pack(side='left', padx=5)
    
    root.mainloop() 
