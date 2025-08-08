"""
Input Controls Component for SNID GUI

This module handles file selection, parameter inputs, and other input controls.
Extracted from the main GUI to improve modularity and maintainability.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os


class InputControlsComponent:
    """Handles file selection, parameter inputs, and other input controls"""
    
    def __init__(self, parent_gui):
        """Initialize the input controls component
        
        Args:
            parent_gui: Reference to the main GUI instance
        """
        self.parent_gui = parent_gui
        self.theme_manager = parent_gui.theme_manager
        
    def browse_file(self):
        """Browse and select a spectrum file"""
        try:
            # Define supported file types
            filetypes = [
                ("All Supported", "*.txt *.dat *.ascii *.asci *.fits *.fit"),
                ("Text files", "*.txt"),
                ("Data files", "*.dat"),
                ("ASCII files", "*.ascii *.asci"),
                ("FITS files", "*.fits *.fit"),
                ("All files", "*.*")
            ]
            
            # Open file dialog
            filename = filedialog.askopenfilename(
                title="Select Spectrum File",
                filetypes=filetypes,
                initialdir=os.getcwd()
            )
            
            if filename:
                self.load_spectrum_file(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to browse for file: {str(e)}")
    
    def load_spectrum_file(self, filename):
        """Load a spectrum file and update the GUI
        
        Args:
            filename (str): Path to the spectrum file
        """
        try:
            # Update the file path variable
            self.parent_gui.file_path.set(filename)
            
            # Update file status display
            file_name = os.path.basename(filename)
            self.parent_gui.file_status_label.config(
                text=f"✅ {file_name}",
                fg=self.theme_manager.get_color('success')
            )
            
            # Update header status
            self.parent_gui.header_status_label.config(
                text=f"📁 Spectrum loaded: {file_name}"
            )
            
            # Enable dependent buttons
            if hasattr(self.parent_gui, 'redshift_selection_btn'):
                self.parent_gui.redshift_selection_btn.config(state='normal')
            if hasattr(self.parent_gui, 'preprocess_btn'):
                self.parent_gui.preprocess_btn.config(state='normal')
            
            # Try to load and display the spectrum
            self._load_and_display_spectrum(filename)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load spectrum file: {str(e)}")
            self._reset_file_status()
    
    def _load_and_display_spectrum(self, filename):
        """Load spectrum data and display it
        
        Args:
            filename (str): Path to the spectrum file
        """
        try:
            # Import required modules
            import numpy as np
            from snid_sage.shared.utils.data_io.spectrum_loader import load_spectrum
            
            # Load spectrum data
            wave, flux = load_spectrum(filename)
            
            # Store spectrum data
            self.parent_gui.original_wave = wave
            self.parent_gui.original_flux = flux
            
            # Use plot controller for proper plotting (especially after reset)
            if hasattr(self.parent_gui, 'plot_controller') and self.parent_gui.plot_controller:
                # Initialize matplotlib if needed (especially after reset)
                if not hasattr(self.parent_gui, 'ax') or self.parent_gui.ax is None:
                    print("🔧 Initializing matplotlib plot for loaded spectrum")
                    self.parent_gui.plot_controller.init_matplotlib_plot()
                
                # Use plot controller to plot original spectrum
                self.parent_gui.plot_controller.plot_original_spectrum()
            elif hasattr(self.parent_gui, 'spectrum_plotter'):
                # Fallback to spectrum plotter if available
                self.parent_gui.spectrum_plotter.plot_original_spectrum(wave, flux)
            
            print(f"✅ Spectrum loaded: {len(wave)} data points")
            
        except ImportError:
            print("⚠️ Spectrum loader not available - file loaded but not displayed")
        except Exception as e:
            print(f"⚠️ Could not display spectrum: {str(e)}")
    
    def _reset_file_status(self):
        """Reset file status displays after an error"""
        self.parent_gui.file_path.set("")
        self.parent_gui.file_status_label.config(
            text="No spectrum loaded",
            fg=self.theme_manager.get_color('text_secondary')
        )
        self.parent_gui.header_status_label.config(
            text="Ready - Load a spectrum to begin analysis"
        )
        
        # Disable dependent buttons
        if hasattr(self.parent_gui, 'redshift_selection_btn'):
            self.parent_gui.redshift_selection_btn.config(state='disabled')
        if hasattr(self.parent_gui, 'preprocess_btn'):
            self.parent_gui.preprocess_btn.config(state='disabled')
    
    def create_parameter_input(self, parent, label_text, variable, width=10, 
                              validation_func=None, tooltip=None):
        """Create a parameter input field with label
        
        Args:
            parent: Parent widget
            label_text (str): Label text
            variable: Tkinter variable to bind to
            width (int): Width of the entry field
            validation_func: Optional validation function
            tooltip (str): Optional tooltip text
            
        Returns:
            tuple: (label_widget, entry_widget)
        """
        frame = tk.Frame(parent, bg=self.theme_manager.get_color('bg_secondary'))
        frame.pack(fill='x', pady=2)
        
        # Label
        label = tk.Label(frame, text=label_text,
                        font=('Segoe UI', 11, 'normal'),
                        bg=self.theme_manager.get_color('bg_secondary'),
                        fg=self.theme_manager.get_color('text_primary'))
        label.pack(side='left')
        
        # Entry field
        entry = tk.Entry(frame, textvariable=variable, width=width,
                        font=('Segoe UI', 11, 'normal'),
                        bg=self.theme_manager.get_color('bg_primary'),
                        fg=self.theme_manager.get_color('text_primary'),
                        insertbackground=self.theme_manager.get_color('text_primary'),
                        relief='flat', bd=1)
        entry.pack(side='right', padx=(10, 0))
        
        # Add validation if provided
        if validation_func:
            entry.bind('<FocusOut>', lambda e: self._validate_input(entry, validation_func))
            entry.bind('<Return>', lambda e: self._validate_input(entry, validation_func))
        
        # Add tooltip if provided
        if tooltip:
            self._add_tooltip(entry, tooltip)
        
        return label, entry
    
    def _validate_input(self, entry, validation_func):
        """Validate input field value
        
        Args:
            entry: Entry widget
            validation_func: Validation function
        """
        try:
            value = entry.get()
            if value and not validation_func(value):
                entry.config(bg=self.theme_manager.get_color('error'))
                self.parent_gui.master.after(1000, 
                    lambda: entry.config(bg=self.theme_manager.get_color('bg_primary')))
            else:
                entry.config(bg=self.theme_manager.get_color('bg_primary'))
        except Exception as e:
            print(f"⚠️ Validation error: {str(e)}")
    
    def _add_tooltip(self, widget, text):
        """Add tooltip to a widget
        
        Args:
            widget: Widget to add tooltip to
            text (str): Tooltip text
        """
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text,
                           font=('Segoe UI', 9, 'normal'),
                           bg=self.theme_manager.get_color('bg_tooltip'),
                           fg=self.theme_manager.get_color('text_primary'),
                           relief='solid', bd=1, padx=5, pady=3)
            label.pack()
            
            # Auto-hide after 3 seconds
            tooltip.after(3000, tooltip.destroy)
        
        def hide_tooltip(event):
            pass  # Tooltip will auto-hide
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def create_file_selection_row(self, parent, label_text, variable, 
                                 browse_command, file_types=None):
        """Create a file selection row with browse button
        
        Args:
            parent: Parent widget
            label_text (str): Label text
            variable: Tkinter variable for file path
            browse_command: Command to execute when browse button is clicked
            file_types (list): List of file type tuples for file dialog
            
        Returns:
            tuple: (frame, label, entry, button)
        """
        frame = tk.Frame(parent, bg=self.theme_manager.get_color('bg_secondary'))
        frame.pack(fill='x', pady=2)
        
        # Label
        label = tk.Label(frame, text=label_text,
                        font=('Segoe UI', 11, 'normal'),
                        bg=self.theme_manager.get_color('bg_secondary'),
                        fg=self.theme_manager.get_color('text_primary'))
        label.pack(side='left')
        
        # Browse button
        button = tk.Button(frame, text="Browse...",
                          font=('Segoe UI', 10, 'normal'),
                          bg=self.theme_manager.get_color('accent_secondary'),
                          fg='white', relief='flat', bd=0, cursor='hand2',
                          command=browse_command)
        button.pack(side='right', padx=(5, 0))
        
        # Entry field (between label and button)
        entry = tk.Entry(frame, textvariable=variable,
                        font=('Segoe UI', 10, 'normal'),
                        bg=self.theme_manager.get_color('bg_primary'),
                        fg=self.theme_manager.get_color('text_primary'),
                        insertbackground=self.theme_manager.get_color('text_primary'),
                        relief='flat', bd=1, state='readonly')
        entry.pack(side='left', fill='x', expand=True, padx=(10, 5))
        
        return frame, label, entry, button
    
    def validate_float_input(self, value):
        """Validate that input is a valid float
        
        Args:
            value (str): Input value to validate
            
        Returns:
            bool: True if valid float, False otherwise
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def validate_int_input(self, value):
        """Validate that input is a valid integer
        
        Args:
            value (str): Input value to validate
            
        Returns:
            bool: True if valid integer, False otherwise
        """
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def validate_wavelength_range(self, value):
        """Validate wavelength range input (e.g., "4000-7000")
        
        Args:
            value (str): Wavelength range string
            
        Returns:
            bool: True if valid range, False otherwise
        """
        try:
            if '-' in value:
                parts = value.split('-')
                if len(parts) == 2:
                    float(parts[0])
                    float(parts[1])
                    return True
            return False
        except ValueError:
            return False 
