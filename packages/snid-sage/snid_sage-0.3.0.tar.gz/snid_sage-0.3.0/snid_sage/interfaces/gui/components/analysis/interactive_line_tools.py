"""
SNID SAGE - Interactive Line Analysis Tools
==========================================

Interactive plot tools for manual region selection, point selection,
and real-time analysis feedback in the emission line dialog.
"""

import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector, SpanSelector
from typing import Dict, List, Tuple, Optional, Any, Callable
import logging

_LOGGER = logging.getLogger(__name__)


class InteractiveLineTools:
    """Interactive tools for manual line analysis"""
    
    def __init__(self, parent_dialog, canvas, ax_main):
        self.parent = parent_dialog
        self.canvas = canvas
        self.ax_main = ax_main
        
        # Current state
        self.current_mode = 'select'
        self.selected_line = None
        self.manual_selections = {}
        
        # Interactive widgets
        self.region_selector = None
        self.point_selector_active = False
        
        # Visual elements
        self.selection_artists = []
        
        # Callbacks
        self.analysis_callback = None
        self.status_callback = None
        
        # Connect events
        self._setup_event_connections()
    
    def _delayed_focus_set(self):
        """Delayed focus setting for when window is ready"""
        try:
            if self.canvas.get_tk_widget().winfo_exists():
                self.canvas.get_tk_widget().focus_set()
        except Exception as e:
            _LOGGER.debug(f"Delayed focus set failed: {e}")
    
    def _setup_event_connections(self):
        """Set up matplotlib event connections"""
        self.canvas.mpl_connect('button_press_event', self._on_click)
        self.canvas.mpl_connect('key_press_event', self._on_key_press)
        
        # Enable keyboard focus (with error handling for window state)
        try:
            if self.canvas.get_tk_widget().winfo_exists():
                self.canvas.get_tk_widget().focus_set()
        except Exception as e:
            _LOGGER.warning(f"Could not set canvas focus: {e}")
            # Try to set focus later when window is ready
            self.canvas.get_tk_widget().after_idle(self._delayed_focus_set)
    
    def set_analysis_callback(self, callback: Callable):
        """Set callback function for triggering analysis updates"""
        self.analysis_callback = callback
    
    def set_status_callback(self, callback: Callable):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def set_analysis_mode(self, mode: str):
        """Set the current analysis mode"""
        valid_modes = ['select', 'region', 'points', 'baseline', 'peak']
        if mode not in valid_modes:
            _LOGGER.warning(f"Invalid analysis mode: {mode}")
            return
        
        # Clean up previous mode
        self._cleanup_mode_widgets()
        
        self.current_mode = mode
        
        # Set up new mode
        if mode == 'region':
            self._setup_region_selection()
        elif mode == 'points':
            self._setup_point_selection()
        
        self._update_status(f"Mode: {mode.title()}")
    
    def set_selected_line(self, line_name: str):
        """Set the currently selected line for analysis"""
        self.selected_line = line_name
        self._update_status(f"Selected line: {line_name}")
    
    def get_manual_selection(self, line_name: str) -> Dict[str, Any]:
        """Get manual selection data for a line"""
        return self.manual_selections.get(line_name, {})
    
    def clear_selections(self, line_name: Optional[str] = None):
        """Clear manual selections"""
        if line_name:
            self.manual_selections.pop(line_name, None)
        else:
            self.manual_selections.clear()
        
        self._clear_visual_elements()
    
    def _cleanup_mode_widgets(self):
        """Clean up widgets from previous mode"""
        if self.region_selector:
            self.region_selector.set_active(False)
            self.region_selector = None
        
        self.point_selector_active = False
    
    def _setup_region_selection(self):
        """Set up rectangular region selection"""
        self.region_selector = RectangleSelector(
            self.ax_main, 
            self._on_region_selected,
            useblit=True,
            button=[1],
            minspanx=5, minspany=5,
            spancoords='pixels',
            interactive=True
        )
        self._update_status("Click and drag to select analysis region")
    
    def _setup_point_selection(self):
        """Set up point-by-point selection"""
        self.point_selector_active = True
        self._update_status("Ctrl+Click to select points, Alt+Click to remove")
    
    def _on_click(self, event):
        """Handle mouse click events"""
        if event.inaxes != self.ax_main:
            return
        
        if self.current_mode == 'points' and self.point_selector_active:
            self._handle_point_selection(event)
        elif self.current_mode == 'peak' and event.dblclick:
            self._handle_peak_marking(event)
    
    def _on_key_press(self, event):
        """Handle key press events"""
        if event.key == 'escape':
            self._cancel_current_selection()
        elif event.key == 'delete':
            self._delete_current_selection()
    
    def _on_region_selected(self, eclick, erelease):
        """Handle region selection completion"""
        if self.selected_line is None:
            self._update_status("No line selected for region definition")
            return
        
        x1, x2 = sorted([eclick.xdata, erelease.xdata])
        
        # Store the region selection
        if self.selected_line not in self.manual_selections:
            self.manual_selections[self.selected_line] = {}
        
        self.manual_selections[self.selected_line]['region'] = (x1, x2)
        self.manual_selections[self.selected_line]['type'] = 'manual_region'
        
        # Visual feedback
        self._add_region_visual(x1, x2)
        
        # Trigger analysis update
        if self.analysis_callback:
            self.analysis_callback(self.selected_line)
        
        self._update_status(f"Region selected: {x1:.2f} - {x2:.2f} Å")
    
    def _handle_point_selection(self, event):
        """Handle individual point selection"""
        if self.selected_line is None:
            self._update_status("No line selected for point selection")
            return
        
        if self.selected_line not in self.manual_selections:
            self.manual_selections[self.selected_line] = {}
        
        if 'points' not in self.manual_selections[self.selected_line]:
            self.manual_selections[self.selected_line]['points'] = []
        
        point = (event.xdata, event.ydata)
        
        if event.key == 'control':
            # Add point
            self.manual_selections[self.selected_line]['points'].append(point)
            self.manual_selections[self.selected_line]['type'] = 'manual_points'
            self._add_point_visual(event.xdata, event.ydata)
            self._update_status(f"Point added: ({event.xdata:.2f}, {event.ydata:.3e})")
            
        elif event.key == 'alt':
            # Remove nearest point
            self._remove_nearest_point(event.xdata, event.ydata)
            self._update_status(f"Point removed near: ({event.xdata:.2f}, {event.ydata:.3e})")
        
        # Trigger analysis update
        if self.analysis_callback:
            self.analysis_callback(self.selected_line)
    
    def _handle_peak_marking(self, event):
        """Handle peak position marking"""
        if self.selected_line is None:
            self._update_status("No line selected for peak marking")
            return
        
        if self.selected_line not in self.manual_selections:
            self.manual_selections[self.selected_line] = {}
        
        self.manual_selections[self.selected_line]['peak'] = event.xdata
        self.manual_selections[self.selected_line]['type'] = 'manual_peak'
        
        # Visual feedback
        self._add_peak_visual(event.xdata)
        
        # Trigger analysis update
        if self.analysis_callback:
            self.analysis_callback(self.selected_line)
        
        self._update_status(f"Peak marked at: {event.xdata:.2f} Å")
    
    def _remove_nearest_point(self, x, y):
        """Remove the nearest manually selected point"""
        if self.selected_line not in self.manual_selections:
            return
        
        points = self.manual_selections[self.selected_line].get('points', [])
        if not points:
            return
        
        # Find nearest point
        distances = [np.sqrt((px - x)**2 + (py - y)**2) for px, py in points]
        nearest_idx = np.argmin(distances)
        
        # Remove the point
        points.pop(nearest_idx)
        
        # Update visual
        self._update_point_visuals()
    
    def _add_region_visual(self, x1, x2):
        """Add visual indicator for selected region"""
        self._clear_visual_elements()
        
        region_patch = self.ax_main.axvspan(x1, x2, alpha=0.2, color='cyan')
        left_line = self.ax_main.axvline(x1, color='cyan', linestyle='--', alpha=0.7)
        right_line = self.ax_main.axvline(x2, color='cyan', linestyle='--', alpha=0.7)
        
        self.selection_artists.extend([region_patch, left_line, right_line])
        self.canvas.draw_idle()
    
    def _add_point_visual(self, x, y):
        """Add visual indicator for selected point"""
        point_marker = self.ax_main.plot(x, y, marker='o', color='red', 
                                        markersize=8, alpha=0.8)[0]
        
        self.selection_artists.append(point_marker)
        self.canvas.draw_idle()
    
    def _add_peak_visual(self, x):
        """Add visual indicator for marked peak"""
        self._clear_visual_elements()
        
        peak_line = self.ax_main.axvline(x, color='red', linestyle='-', linewidth=3, alpha=0.8)
        self.selection_artists.append(peak_line)
        self.canvas.draw_idle()
    
    def _update_point_visuals(self):
        """Update visual display of all selected points"""
        # Clear existing point visuals
        self._clear_visual_elements()
        
        if self.selected_line in self.manual_selections:
            points = self.manual_selections[self.selected_line].get('points', [])
            for x, y in points:
                self._add_point_visual(x, y)
    
    def _clear_visual_elements(self):
        """Clear visual elements"""
        for artist in self.selection_artists:
            try:
                artist.remove()
            except:
                pass
        self.selection_artists.clear()
        self.canvas.draw_idle()
    
    def _cancel_current_selection(self):
        """Cancel current selection operation"""
        if self.selected_line and self.selected_line in self.manual_selections:
            del self.manual_selections[self.selected_line]
        
        self._clear_visual_elements()
        self._update_status("Selection cancelled")
    
    def _delete_current_selection(self):
        """Delete current selection"""
        if self.selected_line:
            self.manual_selections.pop(self.selected_line, None)
            self._clear_visual_elements()
            self._update_status(f"Selections cleared for {self.selected_line}")
    
    def _update_status(self, message: str):
        """Update status message"""
        if self.status_callback:
            self.status_callback(message)
        else:
            _LOGGER.debug(f"Status: {message}")


class LivePreviewManager:
    """Manages live preview of analysis results"""
    
    def __init__(self, preview_figure, preview_ax):
        self.preview_figure = preview_figure
        self.preview_ax = preview_ax
        self.current_line = None
        self.current_result = None
    
    def update_preview(self, line_name: str, wavelength: np.ndarray, flux: np.ndarray, 
                      analysis_result: Dict[str, Any]):
        """Update the live preview with analysis results"""
        
        self.current_line = line_name
        self.current_result = analysis_result
        
        # Clear previous plot
        self.preview_ax.clear()
        
        if 'error' in analysis_result:
            # Show error message
            self.preview_ax.text(0.5, 0.5, f"Error: {analysis_result['error']}", 
                               transform=self.preview_ax.transAxes, 
                               ha='center', va='center', 
                               fontsize=10, color='red')
            self.preview_ax.set_title(f"{line_name} - Analysis Failed")
            
        else:
            # Plot the fitted result
            self.preview_ax.plot(wavelength, flux, 'k-', alpha=0.7, label='Data')
            
            # Plot fit if available
            if 'fitted_flux' in analysis_result:
                fitted_flux = analysis_result['fitted_flux']
                self.preview_ax.plot(wavelength, fitted_flux, 'r-', linewidth=2, 
                                   label=f"Fit ({analysis_result.get('method', 'unknown')})")
            
            # Show FWHM
            if 'fwhm_angstrom' in analysis_result:
                fwhm = analysis_result['fwhm_angstrom']
                center = analysis_result.get('fitted_center', wavelength[len(wavelength)//2])
                
                # Mark FWHM span
                self.preview_ax.axvspan(center - fwhm/2, center + fwhm/2, 
                                      alpha=0.2, color='yellow', 
                                      label=f'FWHM: {fwhm:.2f} Å')
            
            self.preview_ax.set_xlabel('Wavelength (Å)')
            self.preview_ax.set_ylabel('Flux')
            self.preview_ax.set_title(f"{line_name} - FWHM Analysis")
            self.preview_ax.legend(fontsize=8)
            self.preview_ax.grid(True, alpha=0.3)
        
        # Refresh display
        self.preview_figure.tight_layout()
        self.preview_figure.canvas.draw_idle()
    
    def clear_preview(self):
        """Clear the preview display"""
        self.preview_ax.clear()
        self.preview_ax.text(0.5, 0.5, "Select a line for analysis preview", 
                           transform=self.preview_ax.transAxes, 
                           ha='center', va='center', 
                           fontsize=12, alpha=0.7)
        self.preview_figure.canvas.draw_idle() 
