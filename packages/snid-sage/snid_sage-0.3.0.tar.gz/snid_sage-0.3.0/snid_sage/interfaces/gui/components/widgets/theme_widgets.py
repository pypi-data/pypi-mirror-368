"""
SNID SAGE - Theme Widgets
=========================

Theme selection and color picker widgets for SNID SAGE GUI.
Provides interface elements for theme customization and visual preferences.

Part of the SNID SAGE GUI restructuring - Components Module
"""

import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Optional, Callable, Dict, Any, List


class ThemeSelector(ttk.Frame):
    """
    Theme selector widget for switching between available themes.
    """
    
    def __init__(self, parent, themes=None, current_theme='light', command=None, **kwargs):
        """
        Initialize the theme selector.
        
        Args:
            parent: Parent widget
            themes: List of available themes
            current_theme: Currently selected theme
            command: Callback function when theme changes
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.themes = themes or ['light', 'dark']
        self.current_theme = tk.StringVar(value=current_theme)
        self.command = command
        
        self._create_widgets()
        self._setup_layout()
        
        # Bind variable changes
        self.current_theme.trace_add('write', self._on_theme_change)
    
    def _create_widgets(self):
        """Create the theme selector widgets"""
        # Label
        self.label = ttk.Label(self, text="Theme:")
        
        # Theme combobox
        self.theme_combo = ttk.Combobox(
            self,
            textvariable=self.current_theme,
            values=self.themes,
            state='readonly',
            width=12
        )
    
    def _setup_layout(self):
        """Setup the widget layout"""
        self.label.pack(side='left', padx=(0, 5))
        self.theme_combo.pack(side='left')
    
    def _on_theme_change(self, *args):
        """Handle theme change"""
        if self.command:
            self.command(self.current_theme.get())
    
    def get_theme(self) -> str:
        """Get the currently selected theme"""
        return self.current_theme.get()
    
    def set_theme(self, theme: str):
        """Set the selected theme"""
        if theme in self.themes:
            self.current_theme.set(theme)
    
    def add_theme(self, theme: str):
        """Add a new theme option"""
        if theme not in self.themes:
            self.themes.append(theme)
            self.theme_combo.configure(values=self.themes)


class ColorPicker(ttk.Frame):
    """
    Color picker widget for selecting custom colors.
    """
    
    def __init__(self, parent, color='#ffffff', label='Color:', command=None, **kwargs):
        """
        Initialize the color picker.
        
        Args:
            parent: Parent widget
            color: Initial color (hex format)
            label: Label text
            command: Callback function when color changes
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.current_color = color
        self.label_text = label
        self.command = command
        
        self._create_widgets()
        self._setup_layout()
        
        self._update_color_display()
    
    def _create_widgets(self):
        """Create the color picker widgets"""
        # Label
        self.label = ttk.Label(self, text=self.label_text)
        
        # Color display button
        self.color_button = tk.Button(
            self,
            width=4,
            height=1,
            command=self._pick_color,
            relief='raised',
            borderwidth=2
        )
        
        # Color value entry
        self.color_var = tk.StringVar(value=self.current_color)
        self.color_entry = ttk.Entry(
            self,
            textvariable=self.color_var,
            width=10
        )
        
        # Bind entry changes
        self.color_var.trace_add('write', self._on_entry_change)
    
    def _setup_layout(self):
        """Setup the widget layout"""
        self.label.pack(side='left', padx=(0, 5))
        self.color_button.pack(side='left', padx=(0, 5))
        self.color_entry.pack(side='left')
    
    def _pick_color(self):
        """Open color picker dialog"""
        color = colorchooser.askcolor(
            initialcolor=self.current_color,
            title="Choose Color"
        )
        
        if color[1]:  # color[1] is the hex value
            self.set_color(color[1])
    
    def _on_entry_change(self, *args):
        """Handle manual entry of color value"""
        new_color = self.color_var.get()
        if self._is_valid_color(new_color):
            self.current_color = new_color
            self._update_color_display()
            
            if self.command:
                self.command(self.current_color)
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if color string is valid hex color"""
        if not color.startswith('#'):
            return False
        
        if len(color) not in [4, 7]:  # #RGB or #RRGGBB
            return False
        
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def _update_color_display(self):
        """Update the color button display"""
        try:
            self.color_button.configure(bg=self.current_color)
            # Update entry if it doesn't match current color
            if self.color_var.get() != self.current_color:
                self.color_var.set(self.current_color)
        except tk.TclError:
            # Invalid color, reset to white
            self.current_color = '#ffffff'
            self.color_button.configure(bg=self.current_color)
            self.color_var.set(self.current_color)
    
    def get_color(self) -> str:
        """Get the currently selected color"""
        return self.current_color
    
    def set_color(self, color: str):
        """Set the selected color"""
        if self._is_valid_color(color):
            self.current_color = color
            self._update_color_display()
            
            if self.command:
                self.command(self.current_color)


class ThemePreview(ttk.Frame):
    """
    Theme preview widget showing how UI elements look in different themes.
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the theme preview.
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self._create_preview_elements()
        self._setup_layout()
    
    def _create_preview_elements(self):
        """Create preview UI elements"""
        # Sample elements to show theme effects
        self.preview_label = ttk.Label(self, text="Sample Text")
        self.preview_button = ttk.Button(self, text="Sample Button")
        self.preview_entry = ttk.Entry(self, value="Sample Input")
        
        # Sample checkbutton and radiobutton
        self.preview_check_var = tk.BooleanVar(value=True)
        self.preview_check = ttk.Checkbutton(
            self, text="Sample Checkbox", variable=self.preview_check_var
        )
        
        self.preview_radio_var = tk.StringVar(value="option1")
        self.preview_radio1 = ttk.Radiobutton(
            self, text="Option 1", variable=self.preview_radio_var, value="option1"
        )
        self.preview_radio2 = ttk.Radiobutton(
            self, text="Option 2", variable=self.preview_radio_var, value="option2"
        )
        
        # Sample frame
        self.preview_frame = ttk.LabelFrame(self, text="Sample Frame", padding=5)
        self.preview_frame_label = ttk.Label(self.preview_frame, text="Frame content")
    
    def _setup_layout(self):
        """Setup the preview layout"""
        self.preview_label.grid(row=0, column=0, columnspan=2, pady=2, sticky='w')
        self.preview_button.grid(row=1, column=0, columnspan=2, pady=2, sticky='ew')
        self.preview_entry.grid(row=2, column=0, columnspan=2, pady=2, sticky='ew')
        
        self.preview_check.grid(row=3, column=0, columnspan=2, pady=2, sticky='w')
        self.preview_radio1.grid(row=4, column=0, pady=2, sticky='w')
        self.preview_radio2.grid(row=4, column=1, pady=2, sticky='w')
        
        self.preview_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky='ew')
        self.preview_frame_label.pack()
        
        # Configure column weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    def update_theme(self, theme: str):
        """Update the preview for the specified theme"""
        # This would apply theme-specific styling to the preview elements
        # In a real implementation, this would use the theme manager
        pass


# Example usage and testing
if __name__ == "__main__":
    def test_theme_widgets():
        root = tk.Tk()
        root.title("Theme Widgets Test")
        root.geometry("500x400")
        
        # Test ThemeSelector
        theme_frame = ttk.LabelFrame(root, text="Theme Selector", padding=10)
        theme_frame.pack(fill='x', padx=10, pady=5)
        
        def on_theme_change(theme):
            print(f"Theme changed to: {theme}")
            preview.update_theme(theme)
        
        theme_selector = ThemeSelector(
            theme_frame,
            themes=['light', 'dark', 'blue', 'green'],
            current_theme='light',
            command=on_theme_change
        )
        theme_selector.pack(side='left')
        
        # Test ColorPicker
        color_frame = ttk.LabelFrame(root, text="Color Pickers", padding=10)
        color_frame.pack(fill='x', padx=10, pady=5)
        
        def on_bg_color_change(color):
            print(f"Background color: {color}")
        
        def on_fg_color_change(color):
            print(f"Foreground color: {color}")
        
        bg_picker = ColorPicker(
            color_frame,
            color='#ffffff',
            label='Background:',
            command=on_bg_color_change
        )
        bg_picker.pack(pady=2, anchor='w')
        
        fg_picker = ColorPicker(
            color_frame,
            color='#000000',
            label='Foreground:',
            command=on_fg_color_change
        )
        fg_picker.pack(pady=2, anchor='w')
        
        # Test ThemePreview
        preview_frame = ttk.LabelFrame(root, text="Theme Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        preview = ThemePreview(preview_frame)
        preview.pack(fill='both', expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(root)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            control_frame,
            text="Get Current Theme",
            command=lambda: print(f"Current theme: {theme_selector.get_theme()}")
        ).pack(side='left', padx=5)
        
        ttk.Button(
            control_frame,
            text="Get Colors",
            command=lambda: print(f"BG: {bg_picker.get_color()}, FG: {fg_picker.get_color()}")
        ).pack(side='left', padx=5)
        
        ttk.Button(
            control_frame,
            text="Add Custom Theme",
            command=lambda: theme_selector.add_theme("custom")
        ).pack(side='left', padx=5)
        
        root.mainloop()
    
    test_theme_widgets() 
