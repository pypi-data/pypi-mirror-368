"""
Spectrum Preprocessor Module
===========================

Core preprocessing functionality for SNID GUI, providing interactive preprocessing 
capabilities for spectrum preparation before SNID analysis.

Features:
- Interactive preprocessing pipeline
- Step-by-step spectrum modifications
- Real-time visualization updates
- Comprehensive preprocessing history tracking
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from tkinter import messagebox

# Import SNID preprocessing functions
from snid_sage.snid.preprocessing import (
    medfilt, medwfilt, clip_aband, clip_sky_lines, clip_host_emission_lines,
    apply_wavelength_mask, log_rebin, fit_continuum, apodize, pad_to_NW,
    init_wavelength_grid, get_grid_params
)
from snid_sage.snid.io import read_spectrum

# snid_sage.snid.py
from snid_sage.snid.snid import NW, MINW, MAXW

# ===== Logging Setup =====
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.spectrum_preprocessor')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.spectrum_preprocessor')


class SpectrumPreprocessor:
    """
    Interactive spectrum preprocessing for SNID GUI
    
    This class provides a comprehensive preprocessing pipeline that can be used
    independently or integrated with GUI dialogs for interactive preprocessing.
    """
    
    def __init__(self, gui_parent):
        """Initialize the preprocessor with reference to the main GUI"""
        self.gui = gui_parent
        self.original_wave = None
        self.original_flux = None
        self.current_wave = None
        self.current_flux = None
        self.preprocessing_steps = []
        self.step_history = []
        
        # Continuum information
        self.current_continuum = None
        self.continuum_method = None
        self.continuum_params = None
        
        # Preprocessing state
        self.preprocessing_enabled = False
        self.auto_update = True
        
        # Initialize wavelength grid for log rebinning
        init_wavelength_grid()
        
        # Try to load spectrum data from parent GUI if available
        self.load_from_gui()
        
    def load_from_gui(self):
        """Try to load spectrum data from the parent GUI if available"""
        try:
            if self.gui and hasattr(self.gui, 'file_path') and self.gui.file_path:
                wave, flux = self.gui.get_current_spectrum()
                self.current_wave = wave.copy()
                self.current_flux = flux.copy()
                self.original_wave = wave.copy()
                self.original_flux = flux.copy()
            else:
                raise ValueError("No spectrum loaded in GUI")
        except Exception as e:
            raise RuntimeError(f"Could not load spectrum from GUI: {e}")
        
        # Update all UI elements to reflect the loaded spectrum
        self.update_ui_with_spectrum()
    
    def update_ui_with_spectrum(self):
        """
        Update UI elements to reflect the loaded spectrum data.
        
        This is a base implementation that can be overridden by dialog classes
        that have specific UI elements to update. The base SpectrumPreprocessor
        class doesn't have UI elements, so this is a placeholder.
        """
        try:
            # If we have spectrum data and auto_update is enabled, update the plot
            if self.has_spectrum_data() and self.auto_update:
                self.update_plot()
        except Exception as e:
            # Don't raise exceptions here since this is called during initialization
            _LOGGER.warning(f"Could not update UI with spectrum: {e}")
    
    def load_spectrum(self, file_path: str) -> bool:
        """Load a spectrum file for preprocessing"""
        try:
            wave, flux = read_spectrum(file_path)
            self.original_wave = wave.copy()
            self.original_flux = flux.copy()
            self.current_wave = wave.copy()
            self.current_flux = flux.copy()
            self.preprocessing_steps = []
            self.step_history = []
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load spectrum: {str(e)}")
            return False
    
    def has_spectrum_data(self) -> bool:
        """Check if spectrum data is available for preprocessing"""
        return (self.current_wave is not None and 
                self.current_flux is not None and 
                len(self.current_wave) > 0)
    
    def reset_to_original(self):
        """Reset spectrum to original state"""
        if self.original_wave is not None:
            self.current_wave = self.original_wave.copy()
            self.current_flux = self.original_flux.copy()
            self.preprocessing_steps = []
            self.step_history = []
            
            # Clear continuum information
            self.current_continuum = None
            self.continuum_method = None
            self.continuum_params = None
            
            if self.auto_update:
                self.update_plot()
    
    def apply_savgol_filter(self, filter_type: str = "fixed", value: float = 11.0, polyorder: int = 3) -> bool:
        """Apply Savitzky-Golay filtering"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for preprocessing")
            return False
            
        try:
            if filter_type == "fixed" and value >= 3:
                # Fixed-width Savitzky-Golay filter
                from snid_sage.snid.preprocessing import savgol_filter_fixed
                filtered_flux = savgol_filter_fixed(self.current_flux, int(value), polyorder)
                step_info = f"Savitzky-Golay filter (window={int(value)}, order={polyorder})"
            elif filter_type == "wavelength" and value > 0:
                # Wavelength-based Savitzky-Golay filter
                from snid_sage.snid.preprocessing import savgol_filter_wavelength
                filtered_flux = savgol_filter_wavelength(self.current_wave, self.current_flux, value, polyorder)
                step_info = f"Savitzky-Golay filter (FWHM={value:.1f}Å, order={polyorder})"
            else:
                return False
            
            self.current_flux = filtered_flux
            self.preprocessing_steps.append({
                'type': 'savgol_filter',
                'filter_type': filter_type,
                'value': value,
                'polyorder': polyorder,
                'description': step_info
            })
            self.step_history.append(step_info)
            
            if self.auto_update:
                self.update_plot()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply Savitzky-Golay filter: {str(e)}")
            return False
    
    # Legacy method for backward compatibility
    def apply_median_filter(self, filter_type: str = "fixed", value: float = 11.0) -> bool:
        """Legacy wrapper for apply_savgol_filter"""
        return self.apply_savgol_filter(filter_type, value, polyorder=3)
    
    def apply_clipping(self, clip_type: str, **kwargs) -> bool:
        """Apply various clipping operations"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for preprocessing")
            return False
            
        try:
            if clip_type == "aband":
                self.current_wave, self.current_flux = clip_aband(
                    self.current_wave, self.current_flux
                )
                step_info = "Removed telluric A-band (7575-7675Å)"
                
            elif clip_type == "sky":
                width = kwargs.get('width', 40.0)
                self.current_wave, self.current_flux = clip_sky_lines(
                    self.current_wave, self.current_flux, width
                )
                step_info = f"Removed sky lines (width={width:.1f}Å)"
                
            elif clip_type == "emission":
                z = kwargs.get('z', 0.0)
                width = kwargs.get('width', 40.0)
                if z >= 0:
                    self.current_wave, self.current_flux = clip_host_emission_lines(
                        self.current_wave, self.current_flux, z, width
                    )
                    step_info = f"Removed emission lines (z={z:.3f}, width={width:.1f}Å)"
                else:
                    return False
                    
            elif clip_type == "wavelength":
                ranges = kwargs.get('ranges', [])
                if ranges:
                    self.current_wave, self.current_flux = apply_wavelength_mask(
                        self.current_wave, self.current_flux, ranges
                    )
                    range_str = ", ".join([f"{r[0]:.1f}-{r[1]:.1f}Å" for r in ranges])
                    step_info = f"Masked wavelength ranges: {range_str}"
                else:
                    return False
            else:
                return False
            
            self.preprocessing_steps.append({
                'type': 'clipping',
                'clip_type': clip_type,
                'kwargs': kwargs,
                'description': step_info
            })
            self.step_history.append(step_info)
            
            if self.auto_update:
                self.update_plot()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply {clip_type} clipping: {str(e)}")
            return False
    
    def apply_log_rebinning(self) -> bool:
        """Apply log-wavelength rebinning"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for preprocessing")
            return False
            
        try:
            log_wave, log_flux = log_rebin(self.current_wave, self.current_flux)
            self.current_wave = log_wave
            self.current_flux = log_flux
            
            step_info = "Applied log-wavelength rebinning"
            self.preprocessing_steps.append({
                'type': 'log_rebin',
                'description': step_info
            })
            self.step_history.append(step_info)
            
            if self.auto_update:
                self.update_plot()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply log rebinning: {str(e)}")
            return False
    
    def apply_continuum_fitting(self, method: str = "spline", **kwargs) -> bool:
        """Apply continuum fitting and flattening"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for preprocessing")
            return False
            
        try:
            if method == "gaussian":
                sigma = kwargs.get('sigma', None)
                # Pass sigma to fit_continuum, which will auto-calculate if None
                flat_flux, continuum = fit_continuum(
                    self.current_flux, method="gaussian", sigma=sigma
                )
                if sigma is None:
                    from snid_sage.snid.preprocessing import calculate_auto_gaussian_sigma
                    calculated_sigma = calculate_auto_gaussian_sigma(self.current_flux)
                    step_info = f"Continuum fitted (Gaussian, σ={calculated_sigma:.1f} auto)"
                    self.continuum_params = {'sigma': calculated_sigma}
                else:
                    step_info = f"Continuum fitted (Gaussian, σ={sigma:.1f})"
                    self.continuum_params = {'sigma': sigma}
            elif method == "spline":
                knotnum = kwargs.get('knotnum', 13)
                izoff = kwargs.get('izoff', 0)
                flat_flux, continuum = fit_continuum(
                    self.current_flux, method="spline", knotnum=knotnum, izoff=izoff
                )
                step_info = f"Continuum fitted (Spline, knots={knotnum})"
                self.continuum_params = {'knotnum': knotnum, 'izoff': izoff}
            else:
                return False
            
            # Store continuum information
            self.current_continuum = continuum.copy()
            self.continuum_method = method
            
            # Store both flattened flux and continuum
            self.current_flux = flat_flux
            
            self.preprocessing_steps.append({
                'type': 'continuum_fit',
                'method': method,
                'kwargs': kwargs,
                'continuum': continuum,
                'description': step_info
            })
            self.step_history.append(step_info)
            
            if self.auto_update:
                self.update_plot()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply continuum fitting: {str(e)}")
            return False
    
    def open_interactive_continuum_editor(self, parent_dialog=None):
        """Open the interactive continuum editor"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for editing")
            return None
            
        if self.current_continuum is None:
            messagebox.showwarning("No Continuum", 
                                 "Please fit a continuum first before editing it.")
            return None
        
        # Import here to avoid circular imports
        from snid_sage.interfaces.gui.components.dialogs.continuum_editor_dialog import InteractiveContinuumEditor
        
        # Find the spectrum BEFORE continuum fitting by reconstructing from steps
        pre_continuum_flux = None
        pre_continuum_wave = None
        
        # Find the continuum fitting step
        continuum_step_index = None
        for i, step in enumerate(self.preprocessing_steps):
            if step['type'] == 'continuum_fit':
                continuum_step_index = i
                break
        
        if continuum_step_index is not None:
            # Reconstruct the spectrum state just before continuum fitting
            # Start from original and apply all steps up to (but not including) continuum fitting
            temp_wave = self.original_wave.copy()
            temp_flux = self.original_flux.copy()
            
            # Apply all preprocessing steps before continuum fitting
            for i in range(continuum_step_index):
                step = self.preprocessing_steps[i]
                
                if step['type'] == 'savgol_filter':
                    polyorder = step.get('polyorder', 3)
                    if step['filter_type'] == "fixed" and step['value'] >= 3:
                        from snid_sage.snid.preprocessing import savgol_filter_fixed
                        temp_flux = savgol_filter_fixed(temp_flux, int(step['value']), polyorder)
                    elif step['filter_type'] == "wavelength" and step['value'] > 0:
                        from snid_sage.snid.preprocessing import savgol_filter_wavelength
                        temp_flux = savgol_filter_wavelength(temp_wave, temp_flux, step['value'], polyorder)
                elif step['type'] == 'median_filter':  # Legacy support - convert to savgol
                    polyorder = 3  # Default polynomial order for legacy median filters
                    if step['filter_type'] == "fixed" and step['value'] > 1:
                        from snid_sage.snid.preprocessing import savgol_filter_fixed
                        temp_flux = savgol_filter_fixed(temp_flux, max(3, int(step['value'])), polyorder)
                    elif step['filter_type'] == "wavelength" and step['value'] > 0:
                        from snid_sage.snid.preprocessing import savgol_filter_wavelength
                        temp_flux = savgol_filter_wavelength(temp_wave, temp_flux, step['value'], polyorder)
                
                elif step['type'] == 'clipping':
                    if step['clip_type'] == "aband":
                        from snid_sage.snid.preprocessing import clip_aband
                        temp_wave, temp_flux = clip_aband(temp_wave, temp_flux)
                    elif step['clip_type'] == "sky":
                        from snid_sage.snid.preprocessing import clip_sky_lines
                        width = step['kwargs'].get('width', 40.0)
                        temp_wave, temp_flux = clip_sky_lines(temp_wave, temp_flux, width)
                    elif step['clip_type'] == "emission":
                        from snid_sage.snid.preprocessing import clip_host_emission_lines
                        z = step['kwargs'].get('z', 0.0)
                        width = step['kwargs'].get('width', 40.0)
                        temp_wave, temp_flux = clip_host_emission_lines(temp_wave, temp_flux, z, width)
                    elif step['clip_type'] == "wavelength":
                        from snid_sage.snid.preprocessing import apply_wavelength_mask
                        ranges = step['kwargs'].get('ranges', [])
                        temp_wave, temp_flux = apply_wavelength_mask(temp_wave, temp_flux, ranges)
                
                elif step['type'] == 'log_rebin':
                    from snid_sage.snid.preprocessing import log_rebin
                    temp_wave, temp_flux = log_rebin(temp_wave, temp_flux)
                
                elif step['type'] == 'flux_scaling':
                    if step['scale_to_mean']:
                        mask = temp_flux > 0
                        if np.any(mask):
                            mean_flux = np.mean(temp_flux[mask])
                            if mean_flux > 0:
                                temp_flux /= mean_flux
            
            pre_continuum_flux = temp_flux
            pre_continuum_wave = temp_wave
            
        else:
            # No continuum fitting step found, fallback to current state
            # Reconstruct by multiplying flattened spectrum by continuum
            pre_continuum_flux = self.current_flux * self.current_continuum
            pre_continuum_wave = self.current_wave.copy()
        
        # Ensure we have valid data
        if pre_continuum_flux is None:
            # Final fallback
            pre_continuum_flux = self.current_flux * self.current_continuum
            pre_continuum_wave = self.current_wave.copy()
        
        # Create and return the interactive editor with the correct data
        # Pass the spectrum BEFORE continuum fitting, not the flattened one
        editor = InteractiveContinuumEditor(
            pre_continuum_wave,  # Wavelength array (may be log-rebinned)
            pre_continuum_flux,  # Flux BEFORE continuum division (input + preprocessing)
            self.current_continuum,  # The continuum fit
            parent_dialog
        )
        return editor
    
    def apply_modified_continuum(self, new_continuum):
        """Apply a modified continuum from the interactive editor"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for continuum modification")
            return False
            
        try:
            # Store the new continuum
            self.current_continuum = new_continuum.copy()
            
            # Reconstruct the pre-continuum flux
            pre_continuum_flux = self.current_flux * self.current_continuum
            
            # Apply the new continuum
            self.current_flux = pre_continuum_flux / new_continuum
            
            # Update the last continuum fitting step
            for i, step in enumerate(self.preprocessing_steps):
                if step['type'] == 'continuum_fit':
                    step['continuum'] = new_continuum.copy()
                    step['description'] += " (manually edited)"
                    self.step_history[i] += " (manually edited)"
                    break
            
            if self.auto_update:
                self.update_plot()
                
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply modified continuum: {str(e)}")
            return False
    
    def apply_flux_scaling(self, scale_to_mean: bool = True) -> bool:
        """Apply flux scaling"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for preprocessing")
            return False
            
        try:
            if scale_to_mean:
                mask = self.current_flux > 0
                if np.any(mask):
                    mean_flux = np.mean(self.current_flux[mask])
                    if mean_flux > 0:
                        self.current_flux /= mean_flux
                        step_info = "Scaled flux to mean=1"
                    else:
                        return False
                else:
                    return False
            else:
                return False
            
            self.preprocessing_steps.append({
                'type': 'flux_scaling',
                'scale_to_mean': scale_to_mean,
                'description': step_info
            })
            self.step_history.append(step_info)
            
            if self.auto_update:
                self.update_plot()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply flux scaling: {str(e)}")
            return False
    
    def apply_apodization(self, percent: float = 10.0) -> bool:
        """Apply apodization to spectrum ends"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for preprocessing")
            return False
            
        try:
            # Find nonzero region
            nz = np.nonzero(self.current_flux)[0]
            if nz.size:
                l1, l2 = nz[0], nz[-1]
                apodized_flux = apodize(self.current_flux, l1, l2, percent=percent)
                self.current_flux = apodized_flux
                
                step_info = f"Applied apodization ({percent:.1f}%)"
                self.preprocessing_steps.append({
                    'type': 'apodization',
                    'percent': percent,
                    'description': step_info
                })
                self.step_history.append(step_info)
                
                if self.auto_update:
                    self.update_plot()
                return True
            else:
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply apodization: {str(e)}")
            return False
    
    def undo_last_step(self) -> bool:
        """Undo the last preprocessing step"""
        if not self.preprocessing_steps:
            return False
        
        try:
            # Remove last step
            last_step = self.preprocessing_steps.pop()
            self.step_history.pop()
            
            # Reapply all remaining steps from original spectrum
            self.current_wave = self.original_wave.copy()
            self.current_flux = self.original_flux.copy()
            
            steps_to_reapply = self.preprocessing_steps.copy()
            self.preprocessing_steps = []
            self.step_history = []
            
            # Temporarily disable auto-update to avoid multiple plot updates
            old_auto_update = self.auto_update
            self.auto_update = False
            
            # Reapply all steps
            for step in steps_to_reapply:
                if step['type'] == 'median_filter':  # Legacy support - convert to savgol
                    self.apply_savgol_filter(step['filter_type'], step['value'], polyorder=3)
                elif step['type'] == 'savgol_filter':
                    self.apply_savgol_filter(step['filter_type'], step['value'], step.get('polyorder', 3))
                elif step['type'] == 'clipping':
                    self.apply_clipping(step['clip_type'], **step['kwargs'])
                elif step['type'] == 'log_rebin':
                    self.apply_log_rebinning()
                elif step['type'] == 'continuum_fit':
                    self.apply_continuum_fitting(step['method'], **step['kwargs'])
                elif step['type'] == 'flux_scaling':
                    self.apply_flux_scaling(step['scale_to_mean'])
                elif step['type'] == 'apodization':
                    self.apply_apodization(step['percent'])
            
            # Restore auto-update and update plot
            self.auto_update = old_auto_update
            if self.auto_update:
                self.update_plot()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to undo step: {str(e)}")
            return False
    
    def get_preprocessed_spectrum(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get the current preprocessed spectrum"""
        if not self.has_spectrum_data():
            return np.array([]), np.array([])
        return self.current_wave.copy(), self.current_flux.copy()
    
    def get_preprocessing_summary(self) -> Dict[str, Any]:
        """Get a summary of all preprocessing steps applied"""
        return {
            'steps': self.preprocessing_steps.copy(),
            'step_history': self.step_history.copy(),
            'original_shape': self.original_wave.shape if self.original_wave is not None else None,
            'current_shape': self.current_wave.shape if self.current_wave is not None else None,
            'wavelength_range': {
                'original': (self.original_wave.min(), self.original_wave.max()) if self.original_wave is not None else None,
                'current': (self.current_wave.min(), self.current_wave.max()) if self.current_wave is not None else None
            }
        }
    
    def update_plot(self):
        """Update the GUI plot with current spectrum"""
        if self.gui and hasattr(self.gui, 'plot_preprocessed_spectrum'):
            self.gui.plot_preprocessed_spectrum(self.current_wave, self.current_flux)
    
    def export_preprocessed_spectrum(self, file_path: str) -> bool:
        """Export the preprocessed spectrum to a file"""
        if not self.has_spectrum_data():
            messagebox.showerror("Error", "No spectrum data available for export")
            return False
            
        try:
            # Create output in SNID format
            with open(file_path, 'w') as f:
                f.write("# Preprocessed spectrum from SNID SAGE GUI\n")
                f.write("# Preprocessing steps applied:\n")
                for step in self.step_history:
                    f.write(f"# - {step}\n")
                f.write("#\n")
                f.write("# Wavelength(Å)  Flux\n")
                for w, f_val in zip(self.current_wave, self.current_flux):
                    f.write(f"{w:.3f}  {f_val:.6e}\n")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export spectrum: {str(e)}")
            return False 
