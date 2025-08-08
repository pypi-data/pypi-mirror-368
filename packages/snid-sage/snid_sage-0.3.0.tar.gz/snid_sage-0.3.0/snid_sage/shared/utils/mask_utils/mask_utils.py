"""
Mask region utility functions for spectrum analysis
"""
import os
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.widgets import SpanSelector

def update_mask_listbox(self):
    """Update the listbox with current mask regions."""
    self.region_listbox.delete(0, tk.END)
    for start, end in self.mask_regions:
        self.region_listbox.insert(tk.END, f"{start:.2f} - {end:.2f} Å")

def add_manual_mask(self):
    """Add a manually entered mask region."""
    class AddMaskDialog(tk.Toplevel):
        def __init__(self, parent, callback):
            super().__init__(parent)
            self.callback = callback
            self.title("Add Mask Region")
            self.transient(parent)
            self.grab_set()
            
            # Main frame
            frame = ttk.Frame(self, padding=10)
            frame.pack(fill='both', expand=True)
            
            # Create entry fields
            ttk.Label(frame, text="Start wavelength (Å):").grid(row=0, column=0, padx=5, pady=5)
            self.start_entry = ttk.Entry(frame, width=10)
            self.start_entry.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(frame, text="End wavelength (Å):").grid(row=1, column=0, padx=5, pady=5)
            self.end_entry = ttk.Entry(frame, width=10)
            self.end_entry.grid(row=1, column=1, padx=5, pady=5)
            
            # Button frame
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
            
            ttk.Button(btn_frame, text="Add", command=self._add).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side='left', padx=5)
            
            # Center on parent
            self.update_idletasks()
            x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{x}+{y}")
            
            self.wait_window()
        
        def _add(self):
            """Process the manually added region."""
            try:
                start = float(self.start_entry.get().strip())
                end = float(self.end_entry.get().strip())
                if start >= end:
                    messagebox.showerror("Invalid Range", "Start must be less than end.")
                    return
                self.callback(start, end)
                self.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers.")
    
    # Create the dialog - use the adapter pattern
    AddMaskDialog(self.master, lambda start, end: add_mask_region(self, start, end))

def add_mask_region(self, start, end):
    """Add a region and update the display"""
    self.mask_regions.append((start, end))
    update_mask_listbox(self)
    update_plot_with_masks(self)

def remove_selected_mask(self):
    """Remove the selected region."""
    sel = self.region_listbox.curselection()
    if sel:
        index = sel[0]
        del self.mask_regions[index]
        update_mask_listbox(self)
        update_plot_with_masks(self)

def clear_all_masks(self):
    """Clear all mask regions."""
    if messagebox.askyesno("Confirm", "Clear all mask regions?"):
        self.mask_regions.clear()
        update_mask_listbox(self)
        update_plot_with_masks(self)

def select_on_plot(self, mask_dialog):
    """Enable selection of regions on the plot."""
    # Show instructions
    show_mask_instructions(self, mask_dialog)
    
    # Enable masking mode
    self.is_masking_active = True
    
    # Clean up any existing span selector
    if hasattr(self, 'span_selector') and self.span_selector is not None:
        try:
            self.span_selector.disconnect_events()
        except:
            pass
        self.span_selector = None
    
    # Create a new span selector
    def handle_span_select(xmin, xmax):
        """Wrapper to handle span selection events"""
        print(f"Span selected: {xmin:.2f} - {xmax:.2f}")
        on_span_select(self, xmin, xmax)
    
    try:
        # Create the span selector with proper parameters
        from matplotlib.widgets import SpanSelector
        self.span_selector = SpanSelector(
            self.ax, 
            handle_span_select,
            'horizontal',
            useblit=True, 
            button=1,
            props=dict(alpha=0.2, facecolor='red', edgecolor='none', linewidth=0),
            interactive=True,
            drag_from_anywhere=True
        )
        
        # Force redraw of the canvas
        self.canvas.draw()
        
        print("Span selector created successfully")
    except Exception as e:
        print(f"Error creating span selector: {str(e)}")
        messagebox.showerror("Error", f"Failed to enable masking: {str(e)}")
        self.is_masking_active = False
    
    # Update status
    self.status_label.config(text="Mask selection mode: ON - Drag to select regions to mask")

def show_mask_instructions(self, mask_dialog):
    """Show instructions for masking."""
    instructions = tk.Toplevel(self.master)
    instructions.title("Masking Instructions")
    instructions.transient(self.master)
    instructions.grab_set()
    
    # Set a fixed size for the window
    instructions.geometry("400x200")
    
    # Create a frame with padding
    frame = ttk.Frame(instructions, padding=10)
    frame.pack(fill='both', expand=True)
    
    # Instructions text with better formatting
    ttk.Label(frame, text="How to Mask Regions:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
    
    msg = """1. Click and drag on the plot to select a wavelength range
2. Release to add the region
3. Repeat for additional regions
4. Click 'Apply' when done to save all regions"""
    
    ttk.Label(frame, text=msg, justify='left').pack(fill='both', expand=True)
    
    # Bottom frame for button
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill='x', pady=(10, 0))
    
    # OK button with proper sizing
    ttk.Button(btn_frame, text="OK", command=instructions.destroy, width=10).pack(side='right')
    
    # Center on parent
    instructions.update_idletasks()
    x = self.master.winfo_rootx() + (self.master.winfo_width() - instructions.winfo_width()) // 2
    y = self.master.winfo_rooty() + (self.master.winfo_height() - instructions.winfo_height()) // 2
    instructions.geometry(f"+{x}+{y}")

def on_span_select(self, xmin, xmax):
    """Callback for when a span region is selected on the plot."""
    # Print debug information
    print(f"on_span_select called with xmin={xmin:.2f}, xmax={xmax:.2f}")
    
    # Validate the selection
    if xmin >= xmax:
        print("Invalid selection: xmin >= xmax")
        return  # Invalid selection
    
    # Ensure we have a minimum width to avoid tiny selections
    if abs(xmax - xmin) < 1.0:
        print("Selection too small")
        return  # Selection too small
    
    # Add the region to our mask list
    self.mask_regions.append((xmin, xmax))
    print(f"Added mask region: {xmin:.2f} - {xmax:.2f} Å (Total: {len(self.mask_regions)})")
    
    # Update the plot with the new mask
    update_plot_with_masks(self)
    
    # Update status
    self.status_label.config(text=f"Added mask region: {xmin:.2f} - {xmax:.2f} Å. Total: {len(self.mask_regions)} region(s)")
    
    # Update the listbox if it exists
    if hasattr(self, 'region_listbox'):
        update_mask_listbox(self)

def update_plot_with_masks(self):
    """Update the current plot to show masked regions."""
    print(f"Updating plot with {len(self.mask_regions)} mask regions")
    
    # Get the current displayed spectrum (either original or template comparison)
    if not hasattr(self, 'ax') or not self.ax:
        print("No plot available to update")
        return  # No plot to update
    
    # Store current axis limits
    xlim = self.ax.get_xlim()
    ylim = self.ax.get_ylim()
    
    # Clear existing mask highlights by removing patches with our custom tag
    patches_to_remove = []
    for artist in self.ax.patches:
        if hasattr(artist, 'is_mask_patch'):
            patches_to_remove.append(artist)
    
    if patches_to_remove:
        print(f"Removing {len(patches_to_remove)} existing mask patches")
    
    for patch in patches_to_remove:
        patch.remove()
    
    # Add new mask regions - always show when update_plot_with_masks is called during masking
    for i, (start, end) in enumerate(self.mask_regions):
        try:
            # Create a semi-transparent patch for the masked region with consistent styling
            patch = self.ax.axvspan(start, end, alpha=0.2, color='red', zorder=1, edgecolor='none')
            patch.is_mask_patch = True  # Mark this as a mask patch
            print(f"Added mask patch {i+1}: {start:.2f} - {end:.2f}")
        except Exception as e:
            print(f"Error highlighting mask region {start}-{end}: {str(e)}")
    
    # Restore the original limits
    self.ax.set_xlim(xlim)
    self.ax.set_ylim(ylim)
    
    # Update the canvas
    self.canvas.draw_idle()  # Using draw_idle which is more efficient for interactive updates
    print("Canvas updated")

def apply_masks(self, mask_dialog):
    """Apply the mask regions and close the dialog."""
    # Disable masking mode
    self.is_masking_active = False
    
    # Clean up span selector if it exists
    if hasattr(self, 'span_selector') and self.span_selector is not None:
        try:
            self.span_selector.disconnect_events()
        except Exception as e:
            print(f"Error disconnecting span selector: {str(e)}")
        finally:
            self.span_selector = None
    
    # Store current mask regions in case they need to be accessed later
    print(f"Applying {len(self.mask_regions)} mask region(s)")
    
    # Update the status bar
    msg = f"{len(self.mask_regions)} mask region(s)" if self.mask_regions else "No mask regions"
    self.status_label.config(text=msg)
    
    # Close the dialog
    mask_dialog.destroy()

def create_mask_file(self):
    """Create a temporary file with mask regions for SNID."""
    if not self.mask_regions:
        self.mask_file = None
        return None
    
    # Create a temporary mask file
    try:
        mask_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.mask', delete=False)
        
        # Write mask regions to the file
        mask_file.write("# Wavelength mask regions (start end)\n")
        for start, end in self.mask_regions:
            mask_file.write(f"{start:.2f} {end:.2f}\n")
        
        mask_file.close()
        self.mask_file = mask_file.name
        
        return self.mask_file
    except Exception as e:
        messagebox.showerror("Mask Error", f"Failed to create mask file: {str(e)}")
        if hasattr(self, 'mask_file') and self.mask_file and os.path.exists(self.mask_file):
            try:
                os.unlink(self.mask_file)
            except:
                pass
        self.mask_file = None
        return None 