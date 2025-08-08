"""
Interactive Tools Component

Handles all interactive plotting tools for the SNID GUI including masking, zoom, etc.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import SpanSelector

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.interactive_tools')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.interactive_tools')


class InteractiveTools:
    """Handles interactive plotting tools"""
    
    def __init__(self, gui_instance):
        """Initialize the interactive tools with reference to main GUI"""
        self.gui = gui_instance
        self.span_selector = None
        self.masking_active = False
    
    @property
    def ax(self):
        """Get the matplotlib axes from the main GUI"""
        return self.gui.ax
    
    @property
    def fig(self):
        """Get the matplotlib figure from the main GUI"""
        return self.gui.fig
    
    @property
    def canvas(self):
        """Get the matplotlib canvas from the main GUI"""
        return self.gui.canvas
    
    @property
    def theme_manager(self):
        """Get the theme manager from the main GUI"""
        return self.gui.theme_manager
    
    @property
    def masked_regions(self):
        """Get mask regions from the GUI"""
        return getattr(self.gui, 'mask_regions', [])
    
    @masked_regions.setter
    def masked_regions(self, value):
        """Set mask regions on the GUI"""
        if hasattr(self.gui, 'mask_regions'):
            self.gui.mask_regions = value
        else:
            self.gui.mask_regions = []
    
    def toggle_interactive_masking(self):
        """Toggle interactive masking mode"""
        if self.masking_active:
            self.stop_interactive_masking()
        else:
            self.start_interactive_masking()
    
    def start_interactive_masking(self):
        """Start interactive masking mode"""
        if not self.masking_active:
            self.masking_active = True
            
            # Create span selector for wavelength masking
            def onselect(xmin, xmax):
                """Handle wavelength range selection"""
                if xmin != xmax:  # Valid selection
                    self._add_mask_region(xmin, xmax)
                    # _add_mask_region will handle display updates internally
            
            # Set up span selector
            self.span_selector = SpanSelector(
                self.ax, 
                onselect, 
                'horizontal',
                useblit=True,
                props=dict(alpha=0.3, facecolor='red'),
                minspan=1.0  # Minimum span in wavelength units
            )
            
            # Update GUI state
            self._update_masking_ui_state(True)
            
            _LOGGER.info("✅ Interactive masking activated. Click and drag to select wavelength ranges to mask.")
    
    def stop_interactive_masking(self):
        """Stop interactive masking mode"""
        if self.masking_active:
            self.masking_active = False
            
            # Remove span selector
            if self.span_selector:
                self.span_selector.disconnect_events()
                self.span_selector = None
            
            # Update GUI state
            self._update_masking_ui_state(False)
            
            _LOGGER.info("✅ Interactive masking deactivated.")
    
    def clear_interactive_masking(self):
        """Clear all interactive masks"""
        if hasattr(self.gui, 'mask_regions'):
            self.gui.mask_regions.clear()
        
        # Update GUI's mask parameters for SNID
        if hasattr(self.gui, 'params'):
            self.gui.params['wavelength_masks'] = ''
        
        self._update_mask_display()
        self._update_mask_entry()
        
        # Sync with mask manager dialog if open
        if hasattr(self.gui, 'mask_manager_dialog') and self.gui.mask_manager_dialog:
            try:
                self.gui.mask_manager_dialog._update_mask_listbox()
            except:
                pass
        
        _LOGGER.info("✅ All interactive masks cleared.")
    
    def start_interactive_masking_dialog(self, dialog_window):
        """Start interactive masking with dialog window"""
        # Create a dialog for interactive masking instructions
        mask_dialog = tk.Toplevel(dialog_window)
        mask_dialog.title("Interactive Masking")
        mask_dialog.geometry("400x300")
        
        # Set dialog theme
        if hasattr(self.gui, 'theme_manager'):
            theme = self.gui.theme_manager.get_current_theme()
            mask_dialog.configure(bg=theme['bg_color'])
        
        # Instructions
        instructions = tk.Label(
            mask_dialog,
            text="Interactive Masking Mode\n\n"
                 "• Click and drag on the plot to select wavelength ranges\n"
                 "• Selected regions will be masked (excluded from analysis)\n"
                 "• Use 'Clear Masks' to remove all selections\n"
                 "• Click 'Stop Masking' when finished",
            justify=tk.LEFT,
            wraplength=350,
            font=('Arial', 10)
        )
        instructions.pack(pady=20, padx=20)
        
        # Current masks display
        masks_frame = ttk.LabelFrame(mask_dialog, text="Current Masks")
        masks_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.mask_listbox = tk.Listbox(masks_frame, height=6)
        self.mask_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Update the listbox with current masks
        self._update_mask_listbox()
        
        # Buttons
        button_frame = ttk.Frame(mask_dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        clear_btn = ttk.Button(
            button_frame,
            text="Clear All Masks",
            command=self.clear_interactive_masking
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = ttk.Button(
            button_frame,
            text="Stop Masking",
            command=lambda: self._close_masking_dialog(mask_dialog)
        )
        stop_btn.pack(side=tk.RIGHT, padx=5)
        
        # Start interactive masking
        self.start_interactive_masking()
        
        return mask_dialog
    
    def _add_mask_region(self, xmin, xmax):
        """Add a new mask region"""
        # Ensure xmin < xmax
        if xmin > xmax:
            xmin, xmax = xmax, xmin
        
        # Add to GUI's mask regions
        if hasattr(self.gui, 'mask_regions'):
            self.gui.mask_regions.append((xmin, xmax))
        else:
            self.gui.mask_regions = [(xmin, xmax)]
        
        # Update GUI's mask parameters for SNID
        if hasattr(self.gui, 'params'):
            mask_str = ','.join([f"{start:.2f}:{end:.2f}" for start, end in self.gui.mask_regions])
            self.gui.params['wavelength_masks'] = mask_str
        
        _LOGGER.debug(f"✅ Added mask region: {xmin:.2f} - {xmax:.2f} Å")
        
        # Update display and UI elements
        self._update_mask_display()
        self._update_mask_entry()
        self._update_mask_listbox()
        
        # Sync with mask manager dialog if open
        if hasattr(self.gui, 'mask_manager_dialog') and self.gui.mask_manager_dialog:
            try:
                self.gui.mask_manager_dialog._update_mask_listbox()
            except:
                pass
    
    def _update_mask_display(self):
        """Update the visual display of masked regions"""
        # Save current axis limits to preserve plot range
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # Remove existing mask patches
        for patch in getattr(self, 'mask_patches', []):
            try:
                patch.remove()
            except:
                pass
        
        self.mask_patches = []
        
        # Add new mask patches
        theme = self.theme_manager.get_current_theme()
        
        for xmin, xmax in self.masked_regions:
            # Add semi-transparent overlay
            patch = self.ax.axvspan(
                xmin, xmax,
                alpha=0.3,
                color='red',
                label='Masked Region' if not self.mask_patches else ""
            )
            self.mask_patches.append(patch)
        
        # Restore original axis limits to prevent range shifting
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        
        # Refresh canvas
        self.canvas.draw()
    
    def _update_mask_entry(self):
        """Update the wavelength mask entry in the GUI"""
        if hasattr(self.gui, 'wavelength_mask_entry'):
            # Convert masked regions to string format
            mask_strings = []
            for xmin, xmax in self.masked_regions:
                mask_strings.append(f"{xmin:.2f}-{xmax:.2f}")
            
            mask_text = ",".join(mask_strings)
            
            # Update the entry
            self.gui.wavelength_mask_entry.delete(0, tk.END)
            self.gui.wavelength_mask_entry.insert(0, mask_text)
    
    def _update_mask_listbox(self):
        """Update the mask listbox in the dialog"""
        if hasattr(self, 'mask_listbox'):
            self.mask_listbox.delete(0, tk.END)
            
            for i, (xmin, xmax) in enumerate(self.masked_regions):
                self.mask_listbox.insert(tk.END, f"Mask {i+1}: {xmin:.2f} - {xmax:.2f} Å")
    
    def _update_masking_ui_state(self, masking_active):
        """Update the GUI state for masking mode"""
        # Update button text/state if masking button exists
        if hasattr(self.gui, 'interactive_masking_button'):
            if masking_active:
                self.gui.interactive_masking_button.configure(text="🔴 Stop Masking")
            else:
                self.gui.interactive_masking_button.configure(text="🎯 Interactive Masking")
    
    def _close_masking_dialog(self, dialog):
        """Close the masking dialog and stop masking"""
        self.stop_interactive_masking()
        dialog.destroy()
    
    def get_current_masks(self):
        """Get the current mask regions"""
        return self.masked_regions.copy()
    
    def set_masks(self, mask_regions):
        """Set mask regions programmatically"""
        if hasattr(self.gui, 'mask_regions'):
            self.gui.mask_regions = mask_regions.copy()
        else:
            self.gui.mask_regions = mask_regions.copy()
        
        # Update GUI's mask parameters for SNID
        if hasattr(self.gui, 'params'):
            mask_str = ','.join([f"{start:.2f}:{end:.2f}" for start, end in self.gui.mask_regions])
            self.gui.params['wavelength_masks'] = mask_str
        
        self._update_mask_display()
        self._update_mask_entry()
    
    def apply_masks_to_spectrum(self, wavelength, flux):
        """Apply current masks to a spectrum"""
        if not self.masked_regions:
            return wavelength, flux
        
        # Create a mask array
        mask = np.ones(len(wavelength), dtype=bool)
        
        for xmin, xmax in self.masked_regions:
            region_mask = (wavelength >= xmin) & (wavelength <= xmax)
            mask &= ~region_mask  # Invert to exclude masked regions
        
        # Apply mask
        return wavelength[mask], flux[mask]
    
    def export_masks(self):
        """Export current masks as a string"""
        mask_strings = []
        for xmin, xmax in self.masked_regions:
            mask_strings.append(f"{xmin:.2f}-{xmax:.2f}")
        return ",".join(mask_strings)
    
    def import_masks(self, mask_string):
        """Import masks from a string"""
        try:
            # Clear existing masks
            if hasattr(self.gui, 'mask_regions'):
                self.gui.mask_regions.clear()
            else:
                self.gui.mask_regions = []
            
            if mask_string.strip():
                # Parse mask string
                mask_ranges = mask_string.split(',')
                
                for mask_range in mask_ranges:
                    mask_range = mask_range.strip()
                    if ':' in mask_range:  # Handle both : and - separators
                        parts = mask_range.split(':')
                    elif '-' in mask_range:
                        parts = mask_range.split('-')
                    else:
                        continue
                        
                    if len(parts) == 2:
                        try:
                            xmin = float(parts[0])
                            xmax = float(parts[1])
                            self.gui.mask_regions.append((xmin, xmax))
                        except ValueError:
                            continue
            
            # Update GUI's mask parameters for SNID
            if hasattr(self.gui, 'params'):
                mask_str = ','.join([f"{start:.2f}:{end:.2f}" for start, end in self.gui.mask_regions])
                self.gui.params['wavelength_masks'] = mask_str
            
            self._update_mask_display()
            self._update_mask_entry()
            
            _LOGGER.info(f"✅ Imported {len(self.gui.mask_regions)} mask regions")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error importing masks: {str(e)}")
    
    def cleanup(self):
        """Clean up interactive tools"""
        self.stop_interactive_masking()
        
        # Remove any remaining patches
        for patch in getattr(self, 'mask_patches', []):
            try:
                patch.remove()
            except:
                pass
        
        self.mask_patches = [] 
