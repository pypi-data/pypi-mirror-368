"""
Preview Plot Manager Module
===========================

Manages dual-plot preview visualization for preprocessing dialogs.
Handles matplotlib setup, styling, and real-time plot updates.

Features:
- Dual plot layout (before/after comparison)
- Interactive continuum overlay visualization
- Real-time plot updates
- Consistent styling and theming
"""

import numpy as np
import tkinter as tk
import time
from typing import Optional, Dict, List, Tuple, Any

# Ensure proper matplotlib backend and clean state
import matplotlib
import os

# Check if PySide6 GUI is running (environment variable set by PySide6 GUI)
pyside6_gui_running = os.environ.get('SNID_SAGE_GUI_BACKEND') == 'PySide6'

# Only set backend if not in PySide6 context and not already set to avoid conflicts
if not pyside6_gui_running and matplotlib.get_backend() != 'TkAgg':
    matplotlib.use('TkAgg')
elif pyside6_gui_running and matplotlib.get_backend() not in ['Qt5Agg', 'QtAgg']:
    # Use Qt backend when PySide6 is running
    try:
        matplotlib.use('Qt5Agg')
    except ImportError:
        try:
            matplotlib.use('QtAgg')
        except ImportError:
            # Fallback to Agg if Qt backends not available
            matplotlib.use('Agg')

# Clean import order to prevent backend conflicts
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
# Ensure any existing figures are closed
plt.close('all')

# Import unified systems for consistent plot styling
try:
    from snid_sage.interfaces.gui.utils.no_title_plot_manager import apply_no_title_styling
    UNIFIED_SYSTEMS_AVAILABLE = True
except ImportError:
    UNIFIED_SYSTEMS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Import centralized font size configuration
try:
    from snid_sage.shared.utils.plotting.font_sizes import (
        PLOT_AXIS_LABEL_FONTSIZE,
        PLOT_TICK_FONTSIZE,
        PLOT_LEGEND_FONTSIZE
    )
    DEFAULT_LABEL_FONTSIZE = PLOT_AXIS_LABEL_FONTSIZE
    DEFAULT_TICK_FONTSIZE = PLOT_TICK_FONTSIZE
    DEFAULT_LEGEND_FONTSIZE = PLOT_LEGEND_FONTSIZE
except ImportError:
    # Fallback font sizes if centralized config is not available
    DEFAULT_LABEL_FONTSIZE: int = 12  # Axis labels: "Flux", "Wavelength"
    DEFAULT_TICK_FONTSIZE: int = 10   # Axis tick numbers
    DEFAULT_LEGEND_FONTSIZE: int = 11  # Legends inside the preview plots

class PreviewPlotManager:
    """
    Manages matplotlib plotting for preprocessing preview visualization
    
    This class handles all aspects of the dual-plot preview system, including
    setup, styling, updates, and cleanup.
    """
    
    def __init__(self, parent_frame: tk.Frame, colors: Dict[str, str]):
        """
        Initialize plot manager
        
        Args:
            parent_frame: Tkinter frame to contain the plots
            colors: Color scheme dictionary for theming
        """
        self.parent_frame = parent_frame
        self.colors = colors
        self.fig = None
        self.canvas = None
        self.ax1 = None  # Top plot
        self.ax2 = None  # Bottom plot
        
        # Add update throttling to prevent rapid successive updates
        self._last_update_time = 0
        self._update_throttle_ms = 50  # Minimum 50ms between updates
        
        # Setup the matplotlib visualization
        self.setup_plots()
    
    def _filter_zero_padding(self, wave: np.ndarray, flux: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Filter out zero-padded regions from spectrum data
        
        Args:
            wave: Wavelength array
            flux: Flux array
            
        Returns:
            Tuple of (filtered_wave, filtered_flux) with zero padding removed
        """
        try:
            if len(wave) == 0 or len(flux) == 0:
                return wave, flux
            
            # Use the same logic as GUIHelpers.filter_nonzero_spectrum
            # Look for positive flux values (zero-padded regions have flux = 0)
            nonzero_mask = flux > 0
            
            if not np.any(nonzero_mask):
                return wave, flux
            
            # Find first and last non-zero indices
            left_edge = np.argmax(nonzero_mask)
            right_edge = len(flux) - 1 - np.argmax(nonzero_mask[::-1])
            
            # Return trimmed arrays
            return wave[left_edge:right_edge+1], flux[left_edge:right_edge+1]
            
        except Exception as e:
            # Silently handle errors and return original arrays
            return wave, flux
    
    def setup_plots(self):
        """Setup dual matplotlib plots with proper styling"""
        # Create matplotlib figure with dynamic sizing
        self.fig = Figure(facecolor=self.colors['bg_panel'], edgecolor='none')
        self.fig.patch.set_facecolor(self.colors['bg_panel'])
        
        # Create subplots that explicitly share the x-axis so that any
        # navigation/zooming performed on one plot automatically updates the
        # other.  The shared x-axis is a prerequisite for the x-only zoom
        # enforcement implemented further below.
        self.ax1 = self.fig.add_subplot(2, 1, 1)            # Top plot
        self.ax2 = self.fig.add_subplot(2, 1, 2, sharex=self.ax1)  # Bottom plot (share x-axis)
        
        # Apply consistent styling BEFORE creating canvas
        self.configure_plot_styling()
        
        # Create and embed canvas with proper configuration
        self.canvas = FigureCanvasTkAgg(self.fig, self.parent_frame)
        canvas_widget = self.canvas.get_tk_widget()
        
        # Configure canvas widget for proper filling
        canvas_widget.configure(bg=self.colors['bg_panel'], highlightthickness=0)
        # Reduce vertical padding so the plots sit closer to the top and bottom
        # edges of the containing frame while keeping a small horizontal
        # margin for aesthetics.
        canvas_widget.pack(fill='both', expand=True, padx=4, pady=(2, 0))
        
        # ------------------------------------------------------------------
        # Add the standard Matplotlib navigation toolbar (Home / Pan / Zoom …)
        # underneath the plots.  The toolbar enables familiar mouse/keyboard
        # shortcuts for end-users such as scroll-wheel zoom, rectangle zoom,
        # saving, etc.
        # ------------------------------------------------------------------
        try:
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

            toolbar_frame = tk.Frame(self.parent_frame, bg=self.colors['bg_panel'])
            toolbar_frame.pack(fill='x')

            # Disable auto-packing so we can control layout, then pack manually.
            self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame, pack_toolbar=False)
            self.toolbar.config(bg=self.colors['bg_panel'])

            # Pack the toolbar so it is visible; fill horizontally at the
            # bottom of the plot area.
            self.toolbar.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Call update after packing so that buttons render correctly.
            self.toolbar.update()

        except Exception as e:
            # Silently ignore toolbar creation issues (headless environments, …)
            self.toolbar = None
        
        # ------------------------------------------------------------------
        # Initial geometry update: compute real canvas size (in pixels) so we
        # can set a sensible initial figure size and subplot layout before
        # the first draw.  This keeps the plots looking crisp regardless of
        # the window dimensions.
        # ------------------------------------------------------------------
        canvas_widget.update_idletasks()

        canvas_width = canvas_widget.winfo_width()
        canvas_height = canvas_widget.winfo_height()

        if canvas_width > 1 and canvas_height > 1:
            dpi = self.fig.dpi
            fig_width = max(6, canvas_width / dpi)
            fig_height = max(4, canvas_height / dpi)
            self.fig.set_size_inches(fig_width, fig_height)

        # Fine-tune subplot layout to maximise the available space while
        # leaving room for axis labels and the toolbar.
        self.fig.subplots_adjust(
            left=0.05,
            right=0.95,
            top=0.99,    # tiny whitespace above top plot
            bottom=0.01, # minimal whitespace below bottom plot
            hspace=0.2, # more space between the two plots
        )
        
        # ------------------------------------------------------------------
        # Enforce x-only zoom behaviour.  Whenever the user changes the x-lim
        # (which happens for both pan & zoom actions when the axes share x),
        # we automatically rescale the y-axis individually for each subplot
        # so that they always display their full flux range.  This prevents
        # accidental y-zooming and keeps both plots visually independent in
        # the vertical direction while remaining locked horizontally.
        # ------------------------------------------------------------------
        def _on_xlim_change(event_ax):
            try:
                for _ax in (self.ax1, self.ax2):
                    _ax.relim()                       # Recalculate data limits for current x-range
                    _ax.autoscale_view(scalex=False, scaley=True)  # Only autoscale y
                # Use idle draw for efficiency
                self.canvas.draw_idle()
            except Exception:
                pass

        # Connect the callback to both axes (sharex duplicates events but that
        # is harmless and keeps the code symmetric).
        self.ax1.callbacks.connect('xlim_changed', _on_xlim_change)
        self.ax2.callbacks.connect('xlim_changed', _on_xlim_change)
        
        # Draw once everything is properly configured
        self.canvas.draw()
    
    def _force_layout_recalculation(self):
        """Force matplotlib to recalculate layout geometry for dynamic resizing"""
        try:
            # Get current canvas dimensions
            canvas_widget = self.canvas.get_tk_widget()
            canvas_widget.update_idletasks()
            
            width = canvas_widget.winfo_width()
            height = canvas_widget.winfo_height()
            
            # Only proceed if we have reasonable dimensions
            if width > 100 and height > 100:
                # Update figure size to match canvas
                dpi = self.fig.dpi
                fig_width = width / dpi
                fig_height = height / dpi
                
                # Set new figure size
                self.fig.set_size_inches(fig_width, fig_height, forward=False)
                
                # Readjust subplot layout for new size
                self.fig.subplots_adjust(
                    left=0.05,
                    right=0.95,
                    top=0.99,
                    bottom=0.01,
                    hspace=0.2
                )
                
                # Use draw_idle for smooth updates
                self.canvas.draw_idle()
                
        except Exception as e:
            # Just continue without layout update
            pass
    
    def configure_plot_styling(self):
        """Apply consistent styling to both plots"""
        # Use a clean white background for both plots for better print-friendliness
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#ffffff')
            ax.tick_params(colors=self.colors['text_secondary'], labelsize=DEFAULT_TICK_FONTSIZE)
            for spine in ax.spines.values():
                spine.set_color(self.colors['text_secondary'])
            ax.grid(True, alpha=0.3, linewidth=0.6)
        
        # Hide the x-axis on the top plot (ax1) since it is redundant with the bottom plot
        self.ax1.get_xaxis().set_visible(False)
        
        # ------------------------------------------------------------------
        # Apply the common (large-font) no-title styling, **then** override
        # axis-label and tick sizes so that the advanced-preview window has
        # its own (smaller) typography independent of the main GUI.
        # ------------------------------------------------------------------
        if UNIFIED_SYSTEMS_AVAILABLE:
            theme_manager = getattr(self, 'theme_manager', None)
            apply_no_title_styling(self.fig, self.ax1, "Wavelength (Å)", "Flux", theme_manager)
            apply_no_title_styling(self.fig, self.ax2, "Wavelength (Å)", "Flux", theme_manager)

            # Immediately shrink fonts back down after the helper has applied
            # its default (larger) sizes.  This keeps global GUI plots large
            # while giving the preview window compact labels.
            for _ax in (self.ax1, self.ax2):
                _ax.xaxis.label.set_fontsize(DEFAULT_LABEL_FONTSIZE)
                _ax.yaxis.label.set_fontsize(DEFAULT_LABEL_FONTSIZE)
                _ax.tick_params(axis='both', labelsize=DEFAULT_TICK_FONTSIZE)
        else:
            # Fallback styling (no helper available)
            self.ax1.set_ylabel('Flux', color=self.colors['text_secondary'], fontsize=DEFAULT_LABEL_FONTSIZE)
            self.ax2.set_xlabel('Wavelength (Å)', color=self.colors['text_secondary'], fontsize=DEFAULT_LABEL_FONTSIZE)
            self.ax2.set_ylabel('Flux', color=self.colors['text_secondary'], fontsize=DEFAULT_LABEL_FONTSIZE)
    
    def update_standard_preview(self, before_wave: np.ndarray, before_flux: np.ndarray,
                               preview_wave: np.ndarray, preview_flux: np.ndarray, mask_regions=None):
        """
        Update plots with standard before/after preview
        
        Args:
            before_wave: Wavelength array for current state
            before_flux: Flux array for current state
            preview_wave: Wavelength array for preview
            preview_flux: Flux array for preview
            mask_regions: Optional list of (start, end) tuples for masked regions
        """
        try:
            # Throttle updates to prevent rapid successive calls
            current_time = time.time() * 1000  # Convert to milliseconds
            if current_time - self._last_update_time < self._update_throttle_ms:
                return
            self._last_update_time = current_time
            
            # Clear axes completely - including legends
            self.ax1.clear()
            self.ax2.clear()
            
            # Filter zero padding
            before_wave, before_flux = self._filter_zero_padding(before_wave, before_flux)
            preview_wave, preview_flux = self._filter_zero_padding(preview_wave, preview_flux)
            
            # Plot before (top subplot)
            if len(before_wave) > 0 and len(before_flux) > 0:
                self.ax1.plot(before_wave, before_flux, self.colors.get('accent', 'blue'), linewidth=1, alpha=0.8)
            
            # Plot preview (bottom subplot)
            if len(preview_wave) > 0 and len(preview_flux) > 0:
                self.ax2.plot(preview_wave, preview_flux, self.colors.get('success', 'green'), linewidth=1, alpha=0.8)
            
            # Add mask regions visualization ONLY if provided
            if mask_regions:
                self._add_mask_visualization(mask_regions, before_wave, before_flux, preview_wave, preview_flux)
            
            # Apply no-title styling per user requirement (titles removed)
            primary_color = self.colors.get('text_primary', '#ffffff')
            self.ax1.set_ylabel('Flux', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            
            self.ax2.set_xlabel('Wavelength (Å)', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            self.ax2.set_ylabel('Flux', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            
            # Restore axis styling
            self.configure_plot_styling()
            
            # Only use draw_idle, no layout recalculation during updates
            self.canvas.draw_idle()
            
        except Exception as e:
            # Silently handle preview update errors
            pass
    
    def _add_mask_visualization(self, mask_regions, before_wave, before_flux, preview_wave, preview_flux):
        """Add red bands to visualize masked regions"""
        try:
            for start, end in mask_regions:
                # For both plots, add red bands to show masked regions
                for ax, wave, flux in [(self.ax1, before_wave, before_flux), (self.ax2, preview_wave, preview_flux)]:
                    if len(wave) > 0 and len(flux) > 0:
                        # First ensure we have proper y-limits by plotting data
                        if not ax.lines:  # If no data plotted yet, plot it first
                            ax.plot(wave, flux, alpha=0)  # Invisible plot just to set limits
                        
                        # Get the actual data range for y-limits
                        y_min, y_max = ax.get_ylim()
                        
                        # Expand y-limits slightly to ensure mask bands are fully visible
                        y_range = y_max - y_min
                        if y_range > 0:
                            y_min -= y_range * 0.05
                            y_max += y_range * 0.05
                            ax.set_ylim(y_min, y_max)
                        
                        # Add red vertical band for masked region
                        ax.axvspan(start, end, alpha=0.3, color='red', zorder=10, 
                                  label=f'Masked: {start:.1f}-{end:.1f}Å' if ax == self.ax1 else "")
            
            # Add legend to top plot if we have mask regions
            if mask_regions and hasattr(self.ax1, 'get_legend_handles_labels'):
                handles, labels = self.ax1.get_legend_handles_labels()
                # Filter out any invisible/empty handles and only show mask-related labels
                mask_handles = []
                mask_labels = []
                for handle, label in zip(handles, labels):
                    if 'Masked:' in label:
                        mask_handles.append(handle)
                        mask_labels.append(label)
                
                # Only show first few mask regions in legend to avoid clutter
                if len(mask_labels) > 0:
                    max_legend_items = 3
                    if len(mask_labels) > max_legend_items:
                        mask_labels = mask_labels[:max_legend_items] + [f'...+{len(mask_labels)-max_legend_items} more masks']
                        mask_handles = mask_handles[:max_legend_items] + [mask_handles[-1]]
                    
                    legend = self.ax1.legend(mask_handles, mask_labels, loc='upper right', fontsize=DEFAULT_LEGEND_FONTSIZE, 
                                           facecolor=self.colors['bg_step'], 
                                           edgecolor='white',
                                           labelcolor=self.colors['text_primary'])
                    legend.set_alpha(0.9)
                    
        except Exception as e:
            # Silently handle mask visualization errors
            pass
    
    def update_interactive_preview(self, spectrum_wave: np.ndarray, spectrum_flux: np.ndarray,
                                  continuum_points: List[Tuple[float, float]],
                                  preview_wave: np.ndarray, preview_flux: np.ndarray,
                                  interactive_mode: bool = False):
        """
        Update plots with interactive continuum overlay
        
        Args:
            spectrum_wave: Original spectrum wavelength
            spectrum_flux: Original spectrum flux
            continuum_points: List of (wavelength, flux) continuum points
            preview_wave: Preview wavelength array
            preview_flux: Preview flux array (flattened)
            interactive_mode: Whether interactive editing mode is active
        """
        try:
            # Throttle updates to prevent rapid successive calls
            current_time = time.time() * 1000  # Convert to milliseconds
            if current_time - self._last_update_time < self._update_throttle_ms:
                return
            self._last_update_time = current_time
            
            # Clear axes completely
            self.ax1.clear()
            self.ax2.clear()
            
            # Filter zero padding
            spectrum_wave, spectrum_flux = self._filter_zero_padding(spectrum_wave, spectrum_flux)
            preview_wave, preview_flux = self._filter_zero_padding(preview_wave, preview_flux)
            
            # TOP PLOT: Show original spectrum with continuum overlay
            if len(spectrum_wave) > 0 and len(spectrum_flux) > 0:
                self.ax1.plot(spectrum_wave, spectrum_flux, self.colors.get('accent', 'blue'), linewidth=1, alpha=0.8, 
                            label='Original Spectrum')
            
            # Add continuum overlay on TOP plot
            if continuum_points and len(continuum_points) >= 1:
                x_points = [p[0] for p in continuum_points]
                y_points = [p[1] for p in continuum_points]
                
                if interactive_mode:
                    # Interactive mode: Show individual points that can be dragged
                    self.ax1.scatter(x_points, y_points, c='red', s=30, alpha=1.0,
                                   zorder=20, edgecolors='darkred', linewidth=1,
                                   marker='o', label='Continuum Points')
                    
                    # Connect points with thicker line for better visibility during editing
                    if len(continuum_points) >= 2:
                        self.ax1.plot(x_points, y_points, 'r-', alpha=0.8, linewidth=2, 
                                    zorder=15, label='Interactive Continuum')
                else:
                    # Non-interactive mode: Show only fainter continuum line
                    if len(continuum_points) >= 2:
                        # Plot smooth continuum line with reduced opacity
                        self.ax1.plot(x_points, y_points, 'r-', alpha=0.4, linewidth=2, 
                                    zorder=15, label='Fitted Continuum')
                
                # Add legend - use compatible parameters only
                legend = self.ax1.legend(loc='upper right', fontsize=DEFAULT_LEGEND_FONTSIZE, 
                                       facecolor=self.colors['bg_step'], 
                                       edgecolor='white',
                                       labelcolor=self.colors['text_primary'])
                # Set alpha using set_alpha method for compatibility
                legend.set_alpha(0.9)
            
            # BOTTOM PLOT: Show flattened spectrum preview
            if len(preview_wave) > 0 and len(preview_flux) > 0:
                self.ax2.plot(preview_wave, preview_flux, self.colors.get('success', 'green'), linewidth=1, alpha=0.8)
            
            # Apply no-title styling per user requirement (titles removed)
            primary_color = self.colors.get('text_primary', '#ffffff')
            self.ax1.set_ylabel('Flux', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            
            self.ax2.set_xlabel('Wavelength (Å)', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            self.ax2.set_ylabel('Flux', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            
            # Restore axis styling
            self.configure_plot_styling()
            
            # Only use draw_idle, no layout recalculation during updates
            self.canvas.draw_idle()
            
        except Exception as e:
            # Silently handle preview update errors
            pass
    
    def clear_plots(self):
        """Clear both plots"""
        if self.ax1 and self.ax2:
            self.ax1.clear()
            self.ax2.clear()
            self.configure_plot_styling()
            self.canvas.draw_idle()
    
    def get_canvas(self) -> Optional[FigureCanvasTkAgg]:
        """Get the matplotlib canvas for event handling"""
        return self.canvas
    
    def get_top_axis(self):
        """Get the top subplot axis for interactive event handling"""
        return self.ax1
    
    def get_bottom_axis(self):
        """Get the bottom subplot axis"""
        return self.ax2
    
    def connect_event(self, event_type: str, callback):
        """
        Connect matplotlib event to callback
        
        Args:
            event_type: Type of matplotlib event ('button_press_event', etc.)
            callback: Function to call on event
            
        Returns:
            Event connection ID for disconnection
        """
        if self.canvas:
            return self.canvas.mpl_connect(event_type, callback)
        return None
    
    def disconnect_event(self, connection_id):
        """
        Disconnect matplotlib event
        
        Args:
            connection_id: ID returned from connect_event
        """
        if self.canvas and connection_id:
            try:
                self.canvas.mpl_disconnect(connection_id)
            except:
                pass
    
    def force_layout_update(self):
        """Public method to force layout recalculation - useful after window resize"""
        try:
            # Only update if the canvas is ready and has valid dimensions
            canvas_widget = self.canvas.get_tk_widget()
            width = canvas_widget.winfo_width()
            height = canvas_widget.winfo_height()
            
            if width > 1 and height > 1:
                self._force_layout_recalculation()
        except Exception as e:
            # Silently handle force layout update warning
            pass
    
    def cleanup(self):
        """Clean up matplotlib resources"""
        try:
            # Destroy tkinter canvas widget first
            if self.canvas:
                canvas_widget = self.canvas.get_tk_widget()
                if canvas_widget and canvas_widget.winfo_exists():
                    canvas_widget.destroy()
                self.canvas = None
            
            # Clear and close the specific figure
            if self.fig:
                self.fig.clear()
                # Properly close figure without using close_event
                plt.close(self.fig)
                
            # Reset figure references
            self.fig = None
            self.ax1 = None
            self.ax2 = None
            
            # Close any remaining matplotlib windows/figures
            plt.close('all')
            
            # Force garbage collection of matplotlib objects
            import gc
            gc.collect()
            
        except Exception as e:
            # Silently handle cleanup errors
            pass
    
    def show_final_spectrum_comparison(self, original_wave: np.ndarray, original_flux: np.ndarray,
                                      final_wave: np.ndarray, final_flux: np.ndarray):
        """
        Show final comparison between original and fully preprocessed spectrum
        
        Args:
            original_wave: Original spectrum wavelength array
            original_flux: Original spectrum flux array
            final_wave: Final preprocessed wavelength array
            final_flux: Final preprocessed flux array
        """
        try:
            # Clear axes completely
            self.ax1.clear()
            self.ax2.clear()
            
            # Filter zero padding
            original_wave, original_flux = self._filter_zero_padding(original_wave, original_flux)
            final_wave, final_flux = self._filter_zero_padding(final_wave, final_flux)
            
            # TOP PLOT: Original spectrum
            if len(original_wave) > 0 and len(original_flux) > 0:
                self.ax1.plot(original_wave, original_flux, 'lightblue', linewidth=1.5, alpha=0.9,
                            label='Original Spectrum')
            
            # BOTTOM PLOT: Final preprocessed spectrum
            if len(final_wave) > 0 and len(final_flux) > 0:
                self.ax2.plot(final_wave, final_flux, 'lime', linewidth=1.5, alpha=0.9,
                            label='Final Preprocessed Spectrum')
            
            # Set titles for final comparison
            # self.ax1.set_title('Original Spectrum',
            #                  color=self.colors['text_primary'], fontsize=11)
            primary_color = self.colors.get('text_primary', '#ffffff')
            self.ax1.set_ylabel('Flux', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            
            # self.ax2.set_title('Final Preprocessed Spectrum (Ready for SNID Analysis)',
            #                  color=self.colors['text_primary'], fontsize=11)
            self.ax2.set_xlabel('Wavelength (Å)', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            self.ax2.set_ylabel('Flux', color=primary_color, fontsize=DEFAULT_LABEL_FONTSIZE)
            
            # Add legends
            legend1 = self.ax1.legend(loc='upper right', fontsize=DEFAULT_LEGEND_FONTSIZE, 
                                    facecolor=self.colors['bg_step'], 
                                    edgecolor='lightblue',
                                    labelcolor=self.colors['text_primary'])
            legend1.set_alpha(0.9)
            
            legend2 = self.ax2.legend(loc='upper right', fontsize=DEFAULT_LEGEND_FONTSIZE, 
                                    facecolor=self.colors['bg_step'], 
                                    edgecolor='lime',
                                    labelcolor=self.colors['text_primary'])
            legend2.set_alpha(0.9)
            
            # Apply enhanced styling for final display
            self.configure_plot_styling()
            
            # Make plots more prominent for final view
            self.ax1.grid(True, alpha=0.3, color=self.colors['text_secondary'])
            self.ax2.grid(True, alpha=0.3, color=self.colors['text_secondary'])
            
            # Only use draw_idle, no layout recalculation
            self.canvas.draw_idle()
            
        except Exception as e:
            # Silently handle final spectrum comparison errors
            pass

    def export_figure(self, filename: str, dpi: int = 300):
        """
        Export current figure to file
        
        Args:
            filename: Output filename
            dpi: Resolution for export
        """
        try:
            if self.fig:
                self.fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                               facecolor=self.colors['bg_panel'])
                return True
        except Exception as e:
            # Silently handle export errors
            pass
        return False 
