"""
Interactive Continuum Widget Module
===================================

Handles interactive continuum editing functionality for preprocessing dialogs.
Manages mouse events, point manipulation, and real-time continuum updates.

Features:
- Direct continuum editing on full wavelength grid
- Mouse event handling (click, drag)
- Real-time continuum updates
- Visual feedback and state management
"""

import numpy as np
import tkinter as tk
from typing import List, Tuple, Optional, Callable, Dict, Any

# ===== Logging Setup =====
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.interactive_continuum')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.interactive_continuum')

# Print function redirection removed - using standard print for cleaner output

from snid_sage.interfaces.gui.features.preprocessing.preview_calculator import PreviewCalculator


class InteractiveContinuumWidget:
    """
    Handles interactive continuum editing functionality
    
    This widget manages direct continuum editing on the full wavelength grid,
    allowing users to modify continuum values by dragging points up and down.
    """
    
    def __init__(self, preview_calculator: PreviewCalculator, 
                 plot_manager, colors: Dict[str, str]):
        """
        Initialize interactive continuum widget
        
        Args:
            preview_calculator: Calculator for mathematical operations
            plot_manager: Plot manager for visualization
            colors: Color scheme dictionary
        """
        self.preview_calculator = preview_calculator
        self.plot_manager = plot_manager
        self.colors = colors
        
        # Interactive state
        self.interactive_mode = False
        self.manual_continuum = None  # Full continuum array matching wavelength grid
        self.wave_grid = None  # Wavelength grid
        self.original_continuum = None  # Store original fitted continuum for reset
        
        # Mouse interaction state
        self.selected_point_index = None  # Index in the wavelength grid
        self.dragging = False
        
        # Event connections
        self.click_connection = None
        self.motion_connection = None
        self.release_connection = None
        
        # Callbacks
        self.update_callback = None  # Called when continuum changes
        
        # UI Components for controls
        self.controls_frame = None
        
        # Additional state
        self._current_method: str = "spline"  # Track current continuum method
        
        self._interactive_step: int = 16  # Visible point spacing (>=1) 
        
        self._has_manual_changes: bool = False
        
    def set_update_callback(self, callback: Callable):
        """
        Set callback function to call when continuum is updated
        
        Args:
            callback: Function to call on continuum updates
        """
        self.update_callback = callback
    
    def create_interactive_controls(self, parent_frame: tk.Frame) -> tk.Frame:
        """
        Create UI controls for interactive continuum editing
        
        Args:
            parent_frame: Parent frame to contain controls
            
        Returns:
            Frame containing interactive controls
        """
        self.controls_frame = tk.Frame(parent_frame, bg=self.colors['bg_panel'])
        
        # Control buttons frame
        buttons_frame = tk.Frame(self.controls_frame, bg=self.colors['bg_panel'])
        buttons_frame.pack()
        
        # Enable/Disable button
        self.toggle_button = tk.Button(
            buttons_frame,
            text="Modify",
            command=self.toggle_interactive_mode,
            bg=self.colors.get('accent', '#3b82f6'),  # Nice blue color
            fg='white',
            font=('Arial', 11),  # Back to 11pt
            relief='raised',
            bd=2,
            padx=8
        )
        self.toggle_button.pack(side='left', padx=(0, 8))
        
        # Reset button
        reset_button = tk.Button(
            buttons_frame,
            text="Reset",
            command=self.reset_to_fitted_continuum,
            bg=self.colors.get('warning', '#f59e0b'),  # Nice amber color
            fg='white',
            font=('Arial', 11),  # Back to 11pt
            relief='raised',
            bd=2,
            padx=8
        )
        reset_button.pack(side='left', padx=(0, 8))
        
        # Double Points button (always visible)
        self.double_points_button = tk.Button(
            buttons_frame,
            text="More Points",
            command=self.double_visible_points,
            bg=self.colors.get('success', '#10b981'),  # Nice green color
            fg='white',
            font=('Arial', 11),  # Back to 11pt
            relief='raised',
            bd=2,
            padx=8
        )
        self.double_points_button.pack(side='left', padx=(0, 8))
        # Always visible - removed pack_forget()
        
        # Status label
        self.status_label = tk.Label(
            self.controls_frame,
            text="Interactive mode disabled",
            bg=self.colors['bg_panel'],
            fg=self.colors['text_secondary'],
            font=('Arial', 12)  # Increased from 8 to 12
        )
        self.status_label.pack(pady=(5, 0))
        
        return self.controls_frame
    
    def toggle_interactive_mode(self):
        """Toggle interactive continuum editing mode"""
        if self.interactive_mode:
            self.disable_interactive_mode()
        else:
            self.enable_interactive_mode()
    
    def enable_interactive_mode(self):
        """Enable interactive continuum editing"""
        self.interactive_mode = True
        
        # Update button appearance
        self.toggle_button.config(
            text="Stop",
            bg=self.colors['bg_step_active'],
            relief='sunken'
        )
        
        # Update status
        self.status_label.config(
            text="Interactive mode enabled",
            fg=self.colors['text_primary']
        )
        
        # Update button state and text
        self._update_double_points_button()
        
        # Connect mouse events
        self._connect_mouse_events()
        
        # CRITICAL FIX: Always get the CURRENT stored continuum when enabling interactive mode
        # This ensures we use the exact same continuum that was just calculated for the preview
        try:
            wave, current_continuum = self.preview_calculator.get_continuum_from_fit()
            if len(current_continuum) > 0:
                self.wave_grid = wave.copy()
                self.manual_continuum = current_continuum.copy()
                self.original_continuum = current_continuum.copy()
                self._has_manual_changes = False
            else:
                self.reset_to_fitted_continuum()
        except Exception as e:
            self.reset_to_fitted_continuum()
        
        # Update display
        self._trigger_update()
    
    def disable_interactive_mode(self):
        """Disable interactive continuum editing"""
        self.interactive_mode = False
        
        # Update button appearance
        self.toggle_button.config(
            text="Modify",
            bg=self.colors.get('accent', '#3b82f6'),  # Use original accent color
            relief='raised'
        )
        
        # Update status
        self.status_label.config(
            text="Continuum modification complete",
            fg=self.colors['text_secondary']
        )
        
        # Double points button is always visible now
        
        # Disconnect mouse events
        self._disconnect_mouse_events()
        
        # Reset selection state
        self.selected_point_index = None
        self.dragging = False
        
        # Keep manual_continuum for potential future use
        # Update display (standard preview)
        self._trigger_update()
    
    def reset_to_fitted_continuum(self):
        """Reset continuum to automatically fitted continuum"""
        try:
            # CRITICAL FIX: Use the EXACT same continuum that was already calculated and stored
            # by the preview calculator during the preview calculation
            wave, continuum = self.preview_calculator.get_continuum_from_fit()
            
            # Validate that we have usable continuum data
            if len(continuum) == 0 or wave is None or len(wave) != len(continuum):
                raise ValueError("Invalid stored continuum data")
            
            # Store the continuum arrays (these are the EXACT same arrays used in preview)
            self.wave_grid = wave.copy()
            self.manual_continuum = continuum.copy()
            self.original_continuum = continuum.copy()
            self._has_manual_changes = False
            
            # Update display
            self._trigger_update()
            
        except Exception as e:
            # Fallback: calculate fresh using the same improved method as preview calculator
            try:
                current_wave, current_flux = self.preview_calculator.get_current_state()
                
                # Determine current method and parameters
                method = getattr(self, '_current_method', 'spline')
                
                # Use the same _fit_continuum_improved method that preview calculator uses
                if method == "gaussian":
                    sigma = None
                    if hasattr(self.preview_calculator, 'continuum_kwargs') and self.preview_calculator.continuum_kwargs:
                        sigma = self.preview_calculator.continuum_kwargs.get('sigma', None)
                    flat_flux, continuum = self.preview_calculator._fit_continuum_improved(current_flux, method="gaussian", sigma=sigma)
                else:  # spline
                    knotnum = 13  # default
                    if hasattr(self.preview_calculator, 'continuum_kwargs') and self.preview_calculator.continuum_kwargs:
                        knotnum = self.preview_calculator.continuum_kwargs.get('knotnum', 13)
                    flat_flux, continuum = self.preview_calculator._fit_continuum_improved(current_flux, method="spline", knotnum=knotnum)
                
                # Store the continuum arrays
                self.wave_grid = current_wave.copy()
                self.manual_continuum = continuum.copy()
                self.original_continuum = continuum.copy()
                self._has_manual_changes = False
                self._trigger_update()
                
            except Exception as fallback_error:
                pass  # Fallback continuum calculation failed
    
    def get_manual_continuum_array(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the current manual continuum as full arrays
        
        Returns:
            Tuple of (wavelength_array, continuum_array)
        """
        if self.wave_grid is not None and self.manual_continuum is not None:
            return self.wave_grid.copy(), self.manual_continuum.copy()
        else:
            return np.array([]), np.array([])
    
    def set_manual_continuum(self, wave: np.ndarray, continuum: np.ndarray):
        """
        Set the manual continuum arrays
        
        Args:
            wave: Wavelength array
            continuum: Continuum array
        """
        if len(wave) == len(continuum):
            self.wave_grid = wave.copy()
            self.manual_continuum = continuum.copy()
            if self.original_continuum is None:
                self.original_continuum = continuum.copy()
            self._has_manual_changes = False
            self._trigger_update()
    
    def _connect_mouse_events(self):
        """Connect matplotlib mouse events"""
        if self.plot_manager and self.plot_manager.get_canvas():
            self.click_connection = self.plot_manager.connect_event('button_press_event', self._on_mouse_click)
            self.motion_connection = self.plot_manager.connect_event('motion_notify_event', self._on_mouse_motion)
            self.release_connection = self.plot_manager.connect_event('button_release_event', self._on_mouse_release)
    
    def _disconnect_mouse_events(self):
        """Disconnect matplotlib mouse events"""
        if self.plot_manager:
            self.plot_manager.disconnect_event(self.click_connection)
            self.plot_manager.disconnect_event(self.motion_connection)
            self.plot_manager.disconnect_event(self.release_connection)
        
        self.click_connection = None
        self.motion_connection = None
        self.release_connection = None
    
    def _on_mouse_click(self, event):
        """Handle mouse click events"""
        if not self.interactive_mode or not event.inaxes:
            return
        
        # Only handle clicks on top plot
        if event.inaxes != self.plot_manager.get_top_axis():
            return
        
        if event.button == 1:  # Left click only
            self._handle_left_click(event)
    
    def _handle_left_click(self, event):
        """Handle left mouse click - find nearest wavelength point"""
        if self.wave_grid is None or self.manual_continuum is None:
            return
            
        click_x = event.xdata
        click_y = event.ydata
        if click_x is None:
            return
        
        # Find nearest wavelength point with precise click detection
        nearest_index = self._find_nearest_wavelength_index(click_x, click_y)
        
        if nearest_index is not None:
            # Start dragging
            self.selected_point_index = nearest_index
            self.dragging = True
    
    def _on_mouse_motion(self, event):
        """Handle mouse motion - drag continuum value up/down"""
        if not self.interactive_mode or not self.dragging or self.selected_point_index is None:
            return
        
        if not event.inaxes or event.inaxes != self.plot_manager.get_top_axis():
            return
        
        # Update continuum value at selected wavelength
        if event.ydata is not None and 0 <= self.selected_point_index < len(self.manual_continuum):
            # Ensure positive continuum values
            new_value = max(0.01, event.ydata)  # Avoid zero-division later

            # --- Improved behaviour: smooth interpolation for surrounding hidden points ---------
            # We calculate the scaling factor and apply it with a smooth falloff
            # to all *hidden* points that lie between this point and its neighbours.
            # This creates a more natural interpolation instead of uniform scaling.

            old_value = self.manual_continuum[self.selected_point_index]
            if old_value <= 0:
                old_value = 0.01  # Safety fallback

            scale_factor = new_value / old_value

            step = max(1, self._interactive_step)

            # Mark that we have user modifications
            self._has_manual_changes = True

            # Apply smooth interpolation to forward indices (selected+1 .. selected+step-1)
            for offset in range(1, step):
                idx = self.selected_point_index + offset
                if idx < len(self.manual_continuum):
                    # Calculate distance-based scaling factor (1.0 at selected point, 0.0 at step distance)
                    distance_ratio = offset / step
                    # Use cosine interpolation for smooth falloff
                    smooth_factor = 0.5 * (1.0 + np.cos(np.pi * distance_ratio))
                    # Apply interpolated scaling
                    local_scale = 1.0 + (scale_factor - 1.0) * smooth_factor
                    self.manual_continuum[idx] *= local_scale

            # Apply smooth interpolation to backward indices (selected-1 .. selected-step+1)
            for offset in range(1, step):
                idx = self.selected_point_index - offset
                if idx >= 0:
                    # Calculate distance-based scaling factor (1.0 at selected point, 0.0 at step distance)
                    distance_ratio = offset / step
                    # Use cosine interpolation for smooth falloff
                    smooth_factor = 0.5 * (1.0 + np.cos(np.pi * distance_ratio))
                    # Apply interpolated scaling
                    local_scale = 1.0 + (scale_factor - 1.0) * smooth_factor
                    self.manual_continuum[idx] *= local_scale

            # Finally set the exact value for the selected index
            self.manual_continuum[self.selected_point_index] = new_value
            
            self._trigger_update()
    
    def _on_mouse_release(self, event):
        """Handle mouse release - end dragging"""
        if self.dragging:
            self.dragging = False
            self.selected_point_index = None
    
    def _find_nearest_wavelength_index(self, wavelength: float, flux_value: float = None) -> Optional[int]:
        """
        Find nearest wavelength index in the grid with precise click detection
        
        Args:
            wavelength: Target wavelength
            flux_value: Target flux/continuum value (for Y-coordinate checking)
            
        Returns:
            Index of nearest wavelength point or None if not found
        """
        if self.wave_grid is None or len(self.wave_grid) == 0:
            return None
        
        
        # indices (i.e. those spaced by ``self._interactive_step``) when
        # determining which point a user is attempting to drag.  This avoids
        # selecting a hidden point that does not have a marker on the plot.

        if self.interactive_mode:
            step = max(1, self._interactive_step)
            visible_indices = np.arange(0, len(self.wave_grid), step)
            
            # Calculate distances for visible points only
            distances_visible = np.abs(self.wave_grid[visible_indices] - wavelength)
            nearest_visible_pos = int(np.argmin(distances_visible))
            nearest_index = int(visible_indices[nearest_visible_pos])
            min_x_distance = float(distances_visible[nearest_visible_pos])
            
            # If we have flux value, also check Y-distance for precise clicking
            if flux_value is not None and self.manual_continuum is not None:
                nearest_flux = self.manual_continuum[nearest_index]
                min_y_distance = abs(nearest_flux - flux_value)
            else:
                min_y_distance = 0.0
        else:
            distances_full = np.abs(self.wave_grid - wavelength)
            nearest_index = int(np.argmin(distances_full))
            min_x_distance = float(distances_full[nearest_index])
            min_y_distance = 0.0
        
        # Get plot dimensions for precise threshold calculation
        ax = self.plot_manager.get_top_axis()
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        
        # Calculate precise thresholds based on marker size
        # The scatter points have size=30, which corresponds to approximately 
        # 30 points^2 in matplotlib. We need to convert this to data coordinates.
        # A rough approximation: marker size in data coordinates ≈ size_in_points / 72 * axis_range
        marker_size_data_x = (30 / 72) * x_range * 0.1  # Conservative estimate
        marker_size_data_y = (30 / 72) * y_range * 0.1  # Conservative estimate
        
        # Use smaller threshold for more precise clicking
        x_threshold = marker_size_data_x * 0.5  # Half the marker size for precise clicking
        y_threshold = marker_size_data_y * 0.5  # Half the marker size for precise clicking
        
        # Check both X and Y distances for precise point selection
        if min_x_distance <= x_threshold and min_y_distance <= y_threshold:
            return int(nearest_index)
        
        return None
    
    def _trigger_update(self):
        """Trigger update callback if set"""
        if self.update_callback:
            self.update_callback()
    
    def is_interactive_mode(self) -> bool:
        """Check if interactive mode is enabled"""
        return self.interactive_mode
    
    def get_preview_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get preview data using current manual continuum
        
        Returns:
            Tuple of (wave, flattened_flux)
        """
        if self.interactive_mode and self.manual_continuum is not None:
            return self._calculate_manual_continuum_preview()
        else:
            return self.preview_calculator.get_current_state()
    
    def get_continuum_for_display(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get continuum for display purposes, only in valid spectrum range
        
        Returns:
            Tuple of (wave, continuum) trimmed to valid data range
        """
        if self.wave_grid is None or self.manual_continuum is None:
            return np.array([]), np.array([])
        
        # Get current spectrum to find valid range
        current_wave, current_flux = self.preview_calculator.get_current_state()
        
        # Find valid data range (where spectrum > 0)
        positive_mask = current_flux > 0
        if not np.any(positive_mask):
            return np.array([]), np.array([])
        
        positive_indices = np.where(positive_mask)[0]
        start_idx = positive_indices[0]
        end_idx = positive_indices[-1]
        
        # Return continuum only in valid range
        valid_wave = self.wave_grid[start_idx:end_idx+1]
        valid_continuum = self.manual_continuum[start_idx:end_idx+1]
        
        return valid_wave, valid_continuum
    
    def _calculate_manual_continuum_preview(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate preview using manual continuum
        
        Returns:
            Tuple of (wave, flattened_flux)
        """
        try:
            # Get current spectrum state
            current_wave, current_flux = self.preview_calculator.get_current_state()
            
            if self.manual_continuum is None or len(self.manual_continuum) != len(current_wave):
                return current_wave, current_flux
            
            # Apply manual continuum division (same logic as preview calculator)
            positive_mask = current_flux > 0
            if not np.any(positive_mask):
                return current_wave, np.zeros_like(current_flux)
            
            positive_indices = np.where(positive_mask)[0]
            i0, i1 = positive_indices[0], positive_indices[-1]
            
            # Apply continuum division with proper centering around 0
            flat_flux = np.zeros_like(current_flux)
            
            # Only apply continuum division where we have valid data and positive continuum
            valid_mask = positive_mask & (self.manual_continuum > 0)
            flat_flux[valid_mask] = (current_flux[valid_mask] / self.manual_continuum[valid_mask]) - 1.0
            
            # Zero out regions outside the valid data range
            flat_flux[:i0] = 0.0
            flat_flux[i1+1:] = 0.0
            
            return current_wave, flat_flux
            
        except Exception as e:
            print(f"Manual continuum preview error: {e}")
            return self.preview_calculator.get_current_state()
    
    def cleanup(self):
        """Clean up resources"""
        self._disconnect_mouse_events()
        self.manual_continuum = None
        self.wave_grid = None
        self.original_continuum = None
        self.selected_point_index = None
        self.dragging = False
        self.interactive_mode = False
    
    def update_continuum_from_fit(self, parameter_value):
        """
        Update continuum from current method and parameters
        
        Args:
            parameter_value: Sigma value for gaussian or knotnum for spline (None for auto)
        """
        try:
            # Get current spectrum state
            current_wave, current_flux = self.preview_calculator.get_current_state()
            
            # Determine method
            method = "spline"  # Default
            if hasattr(self, '_current_method'):
                method = self._current_method
            elif hasattr(self.preview_calculator, 'continuum_method'):
                method = self.preview_calculator.continuum_method
            
            # Use the same _fit_continuum_improved method that preview calculator uses
            # This ensures 100% consistency with the preview calculation
            if method == "gaussian":
                if parameter_value is None:
                    # Auto sigma calculation
                    flat_flux, continuum = self.preview_calculator._fit_continuum_improved(current_flux, method="gaussian", sigma=None)
                else:
                    # Specific sigma value
                    flat_flux, continuum = self.preview_calculator._fit_continuum_improved(current_flux, method="gaussian", sigma=parameter_value)
            elif method == "spline":
                knotnum = parameter_value if parameter_value is not None else 13
                flat_flux, continuum = self.preview_calculator._fit_continuum_improved(current_flux, method="spline", knotnum=knotnum)
            else:
                # Fallback
                flat_flux, continuum = self.preview_calculator._fit_continuum_improved(current_flux, method="spline")
            
            # Store the continuum arrays (identical to what preview calculator would store)
            self.wave_grid = current_wave.copy()
            self.manual_continuum = continuum.copy()
            self.original_continuum = continuum.copy()
            
        except Exception as e:
            print(f"Error updating continuum from fit: {e}")
            # Fallback: try to get any available continuum or create unity continuum
            try:
                current_wave, current_flux = self.preview_calculator.get_current_state()
                unity_continuum = np.ones_like(current_flux)
                self.wave_grid = current_wave.copy()
                self.manual_continuum = unity_continuum.copy()
                self.original_continuum = unity_continuum.copy()
            except:
                pass
    
    def set_current_method(self, method: str):
        """Set the current continuum fitting method for updates"""
        self._current_method = method
    
    # Legacy compatibility methods for existing code
    def get_continuum_points(self) -> List[Tuple[float, float]]:
        """
        Get continuum as points for display purposes
        
        Returns:
            List of (wavelength, flux) tuples - full resolution when in interactive mode,
            downsampled when just showing fitted continuum
        """
        if self.wave_grid is None or self.manual_continuum is None:
            return []
        
        # Get valid data range only
        valid_wave, valid_continuum = self.get_continuum_for_display()
        if len(valid_wave) == 0:
            return []
        
        points = []
        
        if self.interactive_mode:
            # In interactive mode, show only a subset of points to avoid
            # overcrowding.  The subset spacing is controlled by
            # ``self._interactive_step``.
            step = max(1, self._interactive_step)
            for i in range(0, len(valid_wave), step):
                points.append((float(valid_wave[i]), float(valid_continuum[i])))
        else:
            # When not in interactive mode, downsample for smooth line display
            step = max(1, len(valid_wave) // 100)  # Up to 100 points for smooth line
            for i in range(0, len(valid_wave), step):
                if i < len(valid_wave):
                    points.append((float(valid_wave[i]), float(valid_continuum[i])))
        
        return points
    
    def set_continuum_points(self, points: List[Tuple[float, float]]):
        """
        Set continuum from points (legacy compatibility)
        
        Args:
            points: List of (wavelength, flux) tuples
        """
        if not points:
            return
        
        # If we have existing wave_grid, interpolate points to it
        if self.wave_grid is not None:
            try:
                from scipy.interpolate import interp1d
                x_points = [p[0] for p in points]
                y_points = [p[1] for p in points]
                
                f = interp1d(x_points, y_points, kind='linear', 
                           bounds_error=False, fill_value='extrapolate')
                
                self.manual_continuum = f(self.wave_grid)
                self._trigger_update()
            except:
                pass

    def double_continuum_points(self):
        """Legacy method - not needed with full grid approach"""
        # This method is not needed since we work with the full grid
        # but kept for compatibility
        pass
    
    def clear_continuum_points(self):
        """Clear manual continuum and reset to fitted"""
        self.reset_to_fitted_continuum()
    
    def populate_continuum_from_fit(self, wave: np.ndarray, continuum: np.ndarray):
        """
        Legacy compatibility method
        """
        self.set_manual_continuum(wave, continuum) 

    # ------------------------------------------------------------------
    # External helpers
    # ------------------------------------------------------------------

    def has_manual_changes(self) -> bool:
        """Return True if the user has manually modified the continuum."""
        return self._has_manual_changes

    def double_visible_points(self):
        """Double the number of visible points by halving the step size"""
        if self._interactive_step > 1:
            self._interactive_step = max(1, self._interactive_step // 2)
            # Update button text to show current point count
            self._update_double_points_button()
            # Trigger update to refresh the display with more points
            self._trigger_update()

    def _update_double_points_button(self):
        """Update the double points button text and state"""
        if self._interactive_step <= 1:
            # At maximum resolution - disable button
            self.double_points_button.config(
                text="Max Resolution",
                state='disabled',
                bg=self.colors.get('disabled', '#e2e8f0')
            )
        else:
            # Show current point count and enable button
            point_count = self.get_visible_point_count()
            self.double_points_button.config(
                text=f"Double Points ({point_count})",
                state='normal',
                bg=self.colors.get('success', '#10b981')  # Use original success color
            )

    def get_visible_point_count(self) -> int:
        """Get the current number of visible points"""
        if self.wave_grid is None:
            return 0
        return len(self.wave_grid) // self._interactive_step
