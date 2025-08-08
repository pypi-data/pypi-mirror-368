"""
Preview Calculator Module
========================

Mathematical preview calculations for preprocessing steps without modifying actual data.
Handles real-time preview generation for the preprocessing pipeline.

Features:
- Step-by-step preview calculations
- Non-destructive preview generation
- Support for all preprocessing operations (including Savitzky-Golay filtering)
- Maintains calculation history

Supported Step Types:
- masking: Wavelength region masking
- savgol_filter: Savitzky-Golay smoothing (replaces old median filtering)
- clipping: Various spectrum clipping operations
- log_rebin: Log-wavelength rebinning
- log_rebin_with_scaling: Log rebinning with flux scaling
- continuum_fit: Continuum fitting and removal
- apodization: Spectrum edge tapering
"""

import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from snid_sage.snid.preprocessing import (
    savgol_filter_fixed, savgol_filter_wavelength,
    clip_aband, clip_sky_lines, 
    log_rebin, fit_continuum, fit_continuum_spline, 
    apodize, calculate_auto_gaussian_sigma
)

# Use centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.preprocessing.preview')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.preprocessing.preview')

# Print function redirection removed - using standard print for cleaner output

class PreviewCalculator:
    """
    Handles preview calculations for preprocessing steps without modifying the actual preprocessor.
    
    This class maintains its own state for preview calculations, allowing users to see
    the effects of preprocessing steps before applying them permanently.
    """
    
    def __init__(self, original_wave: np.ndarray, original_flux: np.ndarray):
        """
        Initialize preview calculator with original spectrum data
        
        Args:
            original_wave: Original wavelength array
            original_flux: Original flux array
        """
        self.original_wave = original_wave.copy()
        self.original_flux = original_flux.copy()
        self.stored_continuum = None  # Store continuum for proper reconstruction
        self.continuum_method = None  # Store the method used for continuum fitting
        self.continuum_kwargs = None  # Store the parameters used
        self.reset()
    
    def reset(self):
        """Reset calculator to original spectrum state"""
        self.current_wave = self.original_wave.copy()
        self.current_flux = self.original_flux.copy()
        self.applied_steps = []
        self.stored_continuum = None  # Reset stored continuum
        self.continuum_method = None
        self.continuum_kwargs = None
        self.manual_continuum_active = False  # Reset manual continuum flag
    
    def get_current_state(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get current wavelength and flux arrays"""
        return self.current_wave.copy(), self.current_flux.copy()
    
    def preview_step(self, step_type: str, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate preview for a step without applying it permanently
        
        Args:
            step_type: Type of preprocessing step
            **kwargs: Step-specific parameters
            
        Returns:
            Tuple of (preview_wave, preview_flux)
        """
        try:
            # Remove step_index from kwargs if present (it's only used for tracking)
            preview_kwargs = kwargs.copy()
            preview_kwargs.pop('step_index', None)
            
            if step_type == "masking":
                return self._preview_masking(**preview_kwargs)
            elif step_type == "savgol_filter":
                return self._preview_savgol_filter(**preview_kwargs)
            elif step_type == "clipping":
                return self._preview_clipping(**preview_kwargs)
            elif step_type == "log_rebin":
                return self._preview_log_rebin(**preview_kwargs)
            elif step_type == "log_rebin_with_scaling":
                return self._preview_log_rebin_with_scaling(**preview_kwargs)
            elif step_type == "flux_scaling":
                return self._preview_flux_scaling(**preview_kwargs)
            elif step_type == "continuum_fit":
                return self._preview_continuum_fit(**preview_kwargs)
            elif step_type == "interactive_continuum":
                return self._preview_interactive_continuum(**preview_kwargs)
            elif step_type == "apodization":
                return self._preview_apodization(**preview_kwargs)
            else:
                _LOGGER.warning(f"Warning: Unknown step type '{step_type}'")
                return self.current_wave.copy(), self.current_flux.copy()
                
        except Exception as e:
            _LOGGER.error(f"Preview calculation error for {step_type}: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def apply_step(self, step_type: str, **kwargs):
        """
        Apply a step permanently to the preview calculator state
        
        Args:
            step_type: Type of preprocessing step
            **kwargs: Step-specific parameters (including optional step_index)
        """
        preview_wave, preview_flux = self.preview_step(step_type, **kwargs)
        self.current_wave = preview_wave
        self.current_flux = preview_flux
        
        # Store step info with step_index if provided
        step_kwargs = kwargs.copy()
        step_index = step_kwargs.pop('step_index', None)  # Remove step_index from processing kwargs
        
        step_info = {'type': step_type, 'kwargs': step_kwargs}
        if step_index is not None:
            step_info['step_index'] = step_index
        
        self.applied_steps.append(step_info)
    
    def _preview_masking(self, mask_regions: List[Tuple[float, float]] = None, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview masking step - removes data points in masked regions"""
        if not mask_regions:
            return self.current_wave.copy(), self.current_flux.copy()
        
        temp_wave = self.current_wave.copy()
        temp_flux = self.current_flux.copy()
        
        # Create a mask for all regions to keep (inverse of mask regions)
        keep_mask = np.ones(len(temp_wave), dtype=bool)
        
        # Apply wavelength masks by marking regions to remove
        for start, end in mask_regions:
            mask_region = (temp_wave >= start) & (temp_wave <= end)
            keep_mask &= ~mask_region  # Remove these points
        
        # Return only the points outside the masked regions
        return temp_wave[keep_mask], temp_flux[keep_mask]
    
    def _preview_savgol_filter(self, filter_type: str = 'none', value: float = 11.0, polyorder: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """Preview Savitzky-Golay filtering step"""
        if filter_type == "fixed" and value >= 3:
            preview_flux = savgol_filter_fixed(self.current_flux, int(value), polyorder)
        elif filter_type == "wavelength" and value > 0:
            preview_flux = savgol_filter_wavelength(self.current_wave, self.current_flux, value, polyorder)
        else:
            preview_flux = self.current_flux.copy()
        
        return self.current_wave.copy(), preview_flux
    
    def _preview_clipping(self, clip_type: str, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview clipping operations"""
        temp_wave = self.current_wave.copy()
        temp_flux = self.current_flux.copy()
        
        if clip_type == "aband":
            temp_wave, temp_flux = clip_aband(temp_wave, temp_flux)
        elif clip_type == "sky":
            width = kwargs.get('width', 40.0)
            temp_wave, temp_flux = clip_sky_lines(temp_wave, temp_flux, width)
        
        return temp_wave, temp_flux
    
    def _preview_log_rebin(self, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview log-wavelength rebinning"""
        temp_wave, temp_flux = log_rebin(self.current_wave, self.current_flux)
        return temp_wave, temp_flux
    
    def _preview_log_rebin_with_scaling(self, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview log-wavelength rebinning combined with flux scaling"""
        # First apply log rebinning
        temp_wave, temp_flux = log_rebin(self.current_wave, self.current_flux)
        
        # Then apply flux scaling
        mask = temp_flux > 0
        if np.any(mask):
            mean_flux = np.mean(temp_flux[mask])
            if mean_flux > 0:
                temp_flux /= mean_flux
        
        return temp_wave, temp_flux
    
    def _preview_flux_scaling(self, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview flux scaling to mean = 1"""
        temp_flux = self.current_flux.copy()
        mask = temp_flux > 0
        if np.any(mask):
            mean_flux = np.mean(temp_flux[mask])
            if mean_flux > 0:
                temp_flux /= mean_flux
        return self.current_wave.copy(), temp_flux
    
    def _preview_continuum_fit(self, method: str = 'spline', **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview continuum fitting and removal with improved edge handling"""
        
        # CRITICAL FIX: Check if manual continuum is active - if so, don't recalculate
        if hasattr(self, 'manual_continuum_active') and self.manual_continuum_active:
            if hasattr(self, 'stored_continuum') and self.stored_continuum is not None:
                return self.current_wave.copy(), self.current_flux.copy()
        
        # Check if we already have a stored continuum to detect double-calculation
        if hasattr(self, 'stored_continuum') and self.stored_continuum is not None:
            pass  # Warning: overwriting existing stored continuum
        
        if method == "gaussian":
            sigma = kwargs.get('sigma', None)
            flat_flux, continuum = self._fit_continuum_improved(self.current_flux, method="gaussian", sigma=sigma)
            # Store continuum and method for later reconstruction
            self.stored_continuum = continuum.copy()
            self.continuum_method = "gaussian"
            self.continuum_kwargs = {'sigma': sigma}
        elif method == "spline":
            knotnum = kwargs.get('knotnum', 13)
            flat_flux, continuum = self._fit_continuum_improved(self.current_flux, method="spline", knotnum=knotnum)
            # Store continuum and method for later reconstruction
            self.stored_continuum = continuum.copy()
            self.continuum_method = "spline"
            self.continuum_kwargs = {'knotnum': knotnum}
        else:
            return self.current_wave.copy(), self.current_flux.copy()
        
        return self.current_wave.copy(), flat_flux
    
    def _preview_interactive_continuum(self, continuum_points: List[Tuple[float, float]] = None, manual_continuum: np.ndarray = None, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview interactive continuum fitting and removal"""
        # Handle new manual continuum approach (full array)
        if manual_continuum is not None and len(manual_continuum) == len(self.current_wave):
            return self._calculate_manual_continuum_preview(manual_continuum)
        
        # Handle legacy continuum points approach for compatibility
        if not continuum_points or len(continuum_points) < 2:
            return self.current_wave.copy(), self.current_flux.copy()
        
        return self.calculate_interactive_continuum_preview(continuum_points)
    
    def _preview_apodization(self, percent: float = 10.0, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview apodization (tapering spectrum ends)"""
        # For continuum-removed spectra, we need to find the valid data range differently
        # Check if this appears to be continuum-removed (has negative values)
        has_negative = np.any(self.current_flux < 0)
        
        if has_negative:
            # For continuum-removed spectra, find the range where we have "significant" data
            # Use absolute value and find where it's above a small threshold
            abs_flux = np.abs(self.current_flux)
            threshold = np.max(abs_flux) * 0.01 if np.max(abs_flux) > 0 else 0  # 1% of max absolute value
            nz = np.nonzero(abs_flux > threshold)[0]
        else:
            # For non-continuum-removed spectra, use positive values only
            nz = np.nonzero(self.current_flux > 0)[0]
        
        if nz.size > 0:
            n1, n2 = nz[0], nz[-1]
            # Ensure we have at least a few points to taper
            if n2 - n1 >= 10:  # Need at least 10 points for meaningful apodization
                temp_flux = apodize(self.current_flux, n1, n2, percent=percent)
                return self.current_wave.copy(), temp_flux
        
        # If we can't find a valid range, return unchanged
        return self.current_wave.copy(), self.current_flux.copy()
    
    def _fit_continuum_improved(self, flux, method="spline", **kwargs):
        """
        Improved continuum fitting that excludes problematic edge bins from log rebinning
        
        This method identifies the valid data range (excluding low-value edge bins from log rebinning)
        and estimates the continuum only on this range, then extends it to the full array.
        """
        from scipy.ndimage import gaussian_filter1d
        
        # Find valid data range, excluding problematic edge bins
        # Use a more sophisticated approach than just flux > 0
        positive_mask = flux > 0
        if not np.any(positive_mask):
            # No positive flux - return zeros and ones
            return np.zeros_like(flux), np.ones_like(flux)
        
        positive_indices = np.where(positive_mask)[0]
        
        # Find the "core" data range by excluding edge bins that are significantly lower
        # than the local average (these are likely log rebinning artifacts)
        median_flux = np.median(flux[positive_mask])
        threshold = median_flux * 0.1  # 10% of median flux
        
        # Find first and last indices where flux is above threshold
        above_threshold = positive_mask & (flux > threshold)
        if np.any(above_threshold):
            valid_indices = np.where(above_threshold)[0]
            i0, i1 = valid_indices[0], valid_indices[-1]
        else:
            # Fallback to simple positive flux range
            i0, i1 = positive_indices[0], positive_indices[-1]
        
        # Ensure we have a reasonable range
        if i1 - i0 < 10:
            # Too narrow - use the simple approach
            return fit_continuum(flux, method=method, **kwargs)
        
        # Extract the valid flux range for continuum estimation
        valid_flux = flux[i0:i1+1]
        valid_range = i1 - i0 + 1
        
        if method == "gaussian":
            # Estimate continuum on valid range only
            sigma = kwargs.get('sigma', None)
            if sigma is None:
                # Auto-calculate sigma based on valid range
                sigma = calculate_auto_gaussian_sigma(valid_flux, valid_range)
            
            # Apply Gaussian filter only to valid range
            valid_continuum = gaussian_filter1d(valid_flux, sigma=sigma, mode="mirror")
            
            # Create full continuum array
            continuum = np.ones_like(flux)
            continuum[i0:i1+1] = valid_continuum
            
            # Extend continuum to edges using edge values
            if i0 > 0:
                continuum[:i0] = valid_continuum[0]
            if i1 < len(flux) - 1:
                continuum[i1+1:] = valid_continuum[-1]
                
        elif method == "spline":
            # For spline, use the original implementation but only on valid range
            knotnum = kwargs.get('knotnum', 13)
            izoff = kwargs.get('izoff', 0)
            
            # Apply spline fitting to the full array (it has its own edge handling)
            flat_temp, continuum = fit_continuum_spline(flux, knotnum=knotnum, izoff=izoff)
        else:
            # Fallback
            return fit_continuum(flux, method=method, **kwargs)
        
        # Calculate flattened flux
        flat_flux = np.zeros_like(flux)
        good_mask = (flux > 0) & (continuum > 0)
        flat_flux[good_mask] = flux[good_mask] / continuum[good_mask] - 1.0
        
        # Zero out regions outside valid data range
        flat_flux[:i0] = 0.0
        flat_flux[i1+1:] = 0.0
        continuum[:i0] = 0.0
        continuum[i1+1:] = 0.0
        
        return flat_flux, continuum
    
    def get_filter_value(self, filter_type: str, fixed_value: str = "3", wave_value: str = "5.0") -> float:
        """
        Get filter value based on filter type and string inputs
        
        Args:
            filter_type: "fixed" or "wavelength" 
            fixed_value: String value for fixed filter
            wave_value: String value for wavelength filter
            
        Returns:
            Numeric filter value
        """
        try:
            if filter_type == "fixed":
                return float(fixed_value)
            elif filter_type == "wavelength":
                return float(wave_value)
        except (ValueError, TypeError):
            pass
        return 1.0
    
    def calculate_interactive_continuum_preview(self, continuum_points: List[Tuple[float, float]]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate preview using interactive continuum points
        
        Args:
            continuum_points: List of (wavelength, flux) continuum points
            
        Returns:
            Tuple of (wave, flattened_flux)
        """
        if len(continuum_points) < 2:
            return self.current_wave.copy(), self.current_flux.copy()
        
        try:
            from scipy.interpolate import interp1d
            
            x_points = [p[0] for p in continuum_points]
            y_points = [p[1] for p in continuum_points]
            
            # Create interpolation function
            f = interp1d(x_points, y_points, kind='linear', 
                        bounds_error=False, fill_value='extrapolate')
            
            # Interpolate continuum to current wavelength grid
            interpolated_continuum = f(self.current_wave)
            
            # Store the interactive continuum for later reconstruction
            self.stored_continuum = interpolated_continuum.copy()
            self.continuum_method = "interactive"
            self.continuum_kwargs = {'continuum_points': continuum_points}
            
            # CRITICAL FIX: Find the valid data range just like the standard continuum fitting does
            # This ensures proper edge handling for subsequent apodization
            
            # Find where we have actual data in the original flux (before continuum removal)
            positive_mask = self.current_flux > 0
            if not np.any(positive_mask):
                # No positive flux - return zeros
                return self.current_wave.copy(), np.zeros_like(self.current_flux)
            
            positive_indices = np.where(positive_mask)[0]
            i0, i1 = positive_indices[0], positive_indices[-1]
            
            # Apply continuum division with proper centering around 0 (matching fit_continuum behavior)
            flat_flux = np.zeros_like(self.current_flux)  # Initialize with zeros
            
            # Only apply continuum division where we have valid data and positive continuum
            valid_mask = positive_mask & (interpolated_continuum > 0)
            flat_flux[valid_mask] = (self.current_flux[valid_mask] / interpolated_continuum[valid_mask]) - 1.0
            
            # CRITICAL: Zero out regions outside the valid data range (same as standard continuum fitting)
            # This ensures apodization can correctly identify the data boundaries
            flat_flux[:i0] = 0.0
            flat_flux[i1+1:] = 0.0
            
            return self.current_wave.copy(), flat_flux
            
        except Exception as e:
            _LOGGER.error(f"Interactive continuum preview error: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def _calculate_manual_continuum_preview(self, manual_continuum: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate preview using manual continuum array (new approach)
        
        Args:
            manual_continuum: Full continuum array matching current wavelength grid
            
        Returns:
            Tuple of (wave, flattened_flux)
        """
        try:
            # Store the manual continuum for later reconstruction
            self.stored_continuum = manual_continuum.copy()
            self.continuum_method = "interactive"
            self.continuum_kwargs = {'manual_continuum': manual_continuum}
            
            # Find the valid data range just like the standard continuum fitting does
            # This ensures proper edge handling for subsequent apodization
            
            # Find where we have actual data in the original flux (before continuum removal)
            positive_mask = self.current_flux > 0
            if not np.any(positive_mask):
                # No positive flux - return zeros
                return self.current_wave.copy(), np.zeros_like(self.current_flux)
            
            positive_indices = np.where(positive_mask)[0]
            i0, i1 = positive_indices[0], positive_indices[-1]
            
            # Apply continuum division with proper centering around 0 (matching fit_continuum behavior)
            flat_flux = np.zeros_like(self.current_flux)  # Initialize with zeros
            
            # Only apply continuum division where we have valid data and positive continuum
            valid_mask = positive_mask & (manual_continuum > 0)
            flat_flux[valid_mask] = (self.current_flux[valid_mask] / manual_continuum[valid_mask]) - 1.0
            
            # Zero out regions outside the valid data range (same as standard continuum fitting)
            # This ensures apodization can correctly identify the data boundaries
            flat_flux[:i0] = 0.0
            flat_flux[i1+1:] = 0.0
            
            return self.current_wave.copy(), flat_flux
            
        except Exception as e:
            _LOGGER.error(f"Manual continuum preview error: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def get_continuum_from_fit(self, method: str = 'spline', **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the stored continuum that was used for flattening
        
        Args:
            method: Continuum fitting method ('gaussian' or 'spline') - for compatibility
            **kwargs: Method-specific parameters - for compatibility
            
        Returns:
            Tuple of (wave, continuum) for the continuum that was actually used for flattening
        """
        try:
            # Return the stored continuum if available (this is the one actually used for flattening)
            if self.stored_continuum is not None:
                return self.current_wave.copy(), self.stored_continuum.copy()
            
            # Fallback: if no stored continuum, create a unity continuum
            _LOGGER.warning("No stored continuum found, returning unity continuum")
            return self.current_wave.copy(), np.ones_like(self.current_wave)
            
        except Exception as e:
            _LOGGER.error(f"Error retrieving stored continuum: {e}")
            return self.current_wave.copy(), np.ones_like(self.current_wave)
    
    def get_applied_steps(self) -> List[Dict[str, Any]]:
        """Get list of applied preprocessing steps"""
        return self.applied_steps.copy()
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of current processing state"""
        return {
            'original_points': len(self.original_wave),
            'current_points': len(self.current_wave),
            'applied_steps': len(self.applied_steps),
            'wave_range': (float(np.min(self.current_wave)), float(np.max(self.current_wave))),
            'flux_range': (float(np.min(self.current_flux)), float(np.max(self.current_flux))),
            'steps': [step['type'] for step in self.applied_steps]
        } 
