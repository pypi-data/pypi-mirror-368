"""
PySide6 Preview Calculator Module
================================

Mathematical preview calculations for PySide6 preprocessing dialogs without modifying actual data.
Handles real-time preview generation for the preprocessing pipeline.

Features:
- Step-by-step preview calculations
- Non-destructive preview generation  
- Support for all preprocessing operations (including Savitzky-Golay filtering)
- Maintains calculation history
- PyQtGraph integration for real-time updates

Supported Step Types:
- masking: Wavelength region masking
- savgol_filter: Savitzky-Golay smoothing
- clipping: Various spectrum clipping operations
- log_rebin: Log-wavelength rebinning
- log_rebin_with_scaling: Log rebinning with flux scaling
- continuum_fit: Continuum fitting and removal
- apodization: Spectrum edge tapering
"""

import numpy as np
import logging
from typing import Tuple, List, Dict, Any, Optional
from PySide6 import QtCore

# Import SNID preprocessing functions
try:
    from snid_sage.snid.preprocessing import (
        savgol_filter_fixed, savgol_filter_wavelength,
        clip_aband, clip_sky_lines, 
        log_rebin, fit_continuum, fit_continuum_spline, 
        apodize, calculate_auto_gaussian_sigma
    )
    # Import wavelength grid constants - use same source as dialog
    from snid_sage.snid.snid import NW, MINW, MAXW
    SNID_AVAILABLE = True
except ImportError:
    SNID_AVAILABLE = False
    # Fallback constants - FIXED to match actual SNID values
    NW, MINW, MAXW = 1024, 2500, 10000

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.pyside6_preview_calculator')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.pyside6_preview_calculator')


class PySide6PreviewCalculator(QtCore.QObject):
    """
    Handles preview calculations for PySide6 preprocessing steps without modifying the actual preprocessor.
    
    This class maintains its own state for preview calculations, allowing users to see
    the effects of preprocessing steps before applying them permanently.
    
    Enhanced with comprehensive stage memory system for precise navigation.
    """
    
    # Signals for real-time updates
    preview_updated = QtCore.Signal(np.ndarray, np.ndarray)  # wave, flux
    continuum_updated = QtCore.Signal(np.ndarray, np.ndarray)  # wave, continuum
    stage_memory_updated = QtCore.Signal(int, list)  # current_step, available_stages
    
    def __init__(self, original_wave: np.ndarray, original_flux: np.ndarray):
        """
        Initialize preview calculator with original spectrum data
        
        Args:
            original_wave: Original wavelength array
            original_flux: Original flux array
        """
        super().__init__()
        
        self.original_wave = original_wave.copy()
        self.original_flux = original_flux.copy()
        self.stored_continuum = None  # Store continuum for proper reconstruction
        self.continuum_method = None  # Store the method used for continuum fitting
        self.continuum_kwargs = None  # Store the parameters used
        
        # Enhanced stage memory system
        self.stage_memory = {}  # Dict[step_index, StageMemory]
        self.current_stage_index = -1  # -1 means original spectrum
        
        # Track edge information properly through preprocessing steps
        self.current_left_edge = None
        self.current_right_edge = None
        
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
        
        # Reset stage memory
        self.stage_memory = {}
        self.current_stage_index = -1
        
        # Reset edge tracking
        self.current_left_edge = None
        self.current_right_edge = None
        
        # Store initial state (original spectrum)
        self._store_stage_memory(-1, "Original Spectrum", {
            'wave': self.original_wave.copy(),
            'flux': self.original_flux.copy()
        }, {
            'wave': self.original_wave.copy(),
            'flux': self.original_flux.copy()
        })
    
    def _store_stage_memory(self, stage_index: int, stage_name: str, 
                           current_state: Dict[str, np.ndarray], 
                           preview_state: Dict[str, np.ndarray],
                           processing_params: Optional[Dict[str, Any]] = None):
        """
        Store stage memory for precise navigation
        
        Args:
            stage_index: Unique index for this stage
            stage_name: Human-readable name for this stage
            current_state: Current spectrum state (wave, flux, continuum if applicable)
            preview_state: Preview spectrum state before this step was applied
            processing_params: Parameters used for this processing step
        """
        from dataclasses import dataclass
        from typing import Optional, Dict, Any
        
        @dataclass
        class StageMemory:
            stage_index: int
            stage_name: str
            current_wave: np.ndarray
            current_flux: np.ndarray
            current_continuum: Optional[np.ndarray]
            preview_wave: np.ndarray
            preview_flux: np.ndarray
            preview_continuum: Optional[np.ndarray]
            processing_params: Optional[Dict[str, Any]]
            applied_steps: List[Dict[str, Any]]
            timestamp: float
        
        import time
        
        # Extract continuum if available
        current_continuum = current_state.get('continuum', None)
        preview_continuum = preview_state.get('continuum', None)
        
        # Create stage memory
        stage_memory = StageMemory(
            stage_index=stage_index,
            stage_name=stage_name,
            current_wave=current_state['wave'].copy(),
            current_flux=current_state['flux'].copy(),
            current_continuum=current_continuum.copy() if current_continuum is not None else None,
            preview_wave=preview_state['wave'].copy(),
            preview_flux=preview_state['flux'].copy(),
            preview_continuum=preview_continuum.copy() if preview_continuum is not None else None,
            processing_params=processing_params.copy() if processing_params else None,
            applied_steps=self.applied_steps.copy(),
            timestamp=time.time()
        )
        
        self.stage_memory[stage_index] = stage_memory
        self.current_stage_index = stage_index
        
        # Emit signal for UI updates
        available_stages = list(self.stage_memory.keys())
        self.stage_memory_updated.emit(stage_index, available_stages)
        
        _LOGGER.debug(f"Stored stage memory for stage {stage_index}: {stage_name}")
    
    def get_available_stages(self) -> List[Tuple[int, str]]:
        """Get list of available stages for navigation"""
        stages = []
        for stage_index in sorted(self.stage_memory.keys()):
            stage_memory = self.stage_memory[stage_index]
            stages.append((stage_index, stage_memory.stage_name))
        return stages
    
    def navigate_to_stage(self, target_stage_index: int) -> bool:
        """
        Navigate to a specific stage by restoring its exact state
        
        Args:
            target_stage_index: Index of the stage to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        if target_stage_index not in self.stage_memory:
            _LOGGER.error(f"Stage {target_stage_index} not found in memory")
            return False
        
        try:
            stage_memory = self.stage_memory[target_stage_index]
            
            # Restore the exact current state from that stage
            self.current_wave = stage_memory.current_wave.copy()
            self.current_flux = stage_memory.current_flux.copy()
            
            # Restore continuum if available
            if stage_memory.current_continuum is not None:
                self.stored_continuum = stage_memory.current_continuum.copy()
            else:
                self.stored_continuum = None
            
            # Restore applied steps up to that stage
            self.applied_steps = stage_memory.applied_steps.copy()
            
            # Update current stage index
            self.current_stage_index = target_stage_index
            
            # Emit signals for UI updates
            self.preview_updated.emit(self.current_wave, self.current_flux)
            available_stages = list(self.stage_memory.keys())
            self.stage_memory_updated.emit(target_stage_index, available_stages)
            
            _LOGGER.info(f"Successfully navigated to stage {target_stage_index}: {stage_memory.stage_name}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Failed to navigate to stage {target_stage_index}: {e}")
            return False
    
    def get_stage_preview(self, stage_index: int) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Get the preview state for a specific stage without navigating to it
        
        Args:
            stage_index: Index of the stage to get preview for
            
        Returns:
            Tuple of (wave, flux) for the preview, or None if not found
        """
        if stage_index not in self.stage_memory:
            return None
        
        stage_memory = self.stage_memory[stage_index]
        return stage_memory.preview_wave.copy(), stage_memory.preview_flux.copy()
    
    def get_current_stage_info(self) -> Dict[str, Any]:
        """Get information about the current stage"""
        if self.current_stage_index not in self.stage_memory:
            return {
                'stage_index': self.current_stage_index,
                'stage_name': 'Unknown',
                'processing_params': None,
                'applied_steps_count': len(self.applied_steps)
            }
        
        stage_memory = self.stage_memory[self.current_stage_index]
        return {
            'stage_index': stage_memory.stage_index,
            'stage_name': stage_memory.stage_name,
            'processing_params': stage_memory.processing_params,
            'applied_steps_count': len(stage_memory.applied_steps),
            'timestamp': stage_memory.timestamp
        }
    
    def clear_stages_after(self, stage_index: int):
        """
        Clear all stages after the specified stage index
        
        Args:
            stage_index: Clear all stages with index > stage_index
        """
        stages_to_remove = [idx for idx in self.stage_memory.keys() if idx > stage_index]
        for idx in stages_to_remove:
            del self.stage_memory[idx]
        
        _LOGGER.debug(f"Cleared {len(stages_to_remove)} stages after stage {stage_index}")
        
        # Update current stage if necessary
        if self.current_stage_index > stage_index:
            available_stages = sorted(self.stage_memory.keys())
            if available_stages:
                self.current_stage_index = available_stages[-1]
            else:
                self.current_stage_index = -1
        
        # Emit signal for UI updates
        available_stages = list(self.stage_memory.keys())
        self.stage_memory_updated.emit(self.current_stage_index, available_stages)
    
    def get_current_state(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get current wavelength and flux arrays"""
        return self.current_wave.copy(), self.current_flux.copy()
    
    def _update_edge_info_after_step(self, step_type: str):
        """Update edge information after certain preprocessing steps"""
        if step_type in ["masking", "clipping"]:
            # Recalculate edges based on current data range after masking/clipping
            # For masking/clipping, we track the actual wavelength range, not flux-based edges
            if len(self.current_wave) > 0:
                # Find the mapping from current indices to original indices
                # This helps track which parts of the original spectrum are still valid
                orig_wave_min, orig_wave_max = self.current_wave[0], self.current_wave[-1]
                
                # Find corresponding indices in original wavelength array
                orig_left_idx = np.searchsorted(self.original_wave, orig_wave_min, side='left')
                orig_right_idx = np.searchsorted(self.original_wave, orig_wave_max, side='right') - 1
                
                self.current_left_edge = orig_left_idx
                self.current_right_edge = orig_right_idx
                
                _LOGGER.debug(f"Updated edges after {step_type}: left={self.current_left_edge}, right={self.current_right_edge}")
                _LOGGER.debug(f"Wavelength range: {orig_wave_min:.1f} - {orig_wave_max:.1f}")
        elif step_type in ["log_rebin", "log_rebin_with_scaling"]:
            # After log rebinning, calculate edges based on valid flux regions (including negative values)
            valid_mask = (self.current_flux != 0) & np.isfinite(self.current_flux)
            if np.any(valid_mask):
                self.current_left_edge = np.argmax(valid_mask)
                self.current_right_edge = len(self.current_flux) - 1 - np.argmax(valid_mask[::-1])
            else:
                self.current_left_edge = 0
                self.current_right_edge = len(self.current_flux) - 1
                
            _LOGGER.debug(f"Updated edges after {step_type}: left={self.current_left_edge}, right={self.current_right_edge}")
        # Note: For other steps like savgol_filter, continuum_fit, and apodization, 
        # we don't need to update edges as they preserve the data structure
    
    def get_current_edges(self) -> Tuple[int, int]:
        """Get current left and right edge indices"""
        return self.current_left_edge or 0, self.current_right_edge or (len(self.current_flux) - 1)
    
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
        # Store current state as preview state for stage memory
        preview_state = {
            'wave': self.current_wave.copy(),
            'flux': self.current_flux.copy()
        }
        if self.stored_continuum is not None:
            preview_state['continuum'] = self.stored_continuum.copy()
        
        # Apply the step
        preview_wave, preview_flux = self.preview_step(step_type, **kwargs)
        self.current_wave = preview_wave
        self.current_flux = preview_flux
        
        # Update edge information after applying the step
        self._update_edge_info_after_step(step_type)
        
        # Store step info with step_index if provided
        step_kwargs = kwargs.copy()
        step_index = step_kwargs.pop('step_index', None)  # Remove step_index from processing kwargs
        
        step_info = {'type': step_type, 'kwargs': step_kwargs}
        if step_index is not None:
            step_info['step_index'] = step_index
        
        self.applied_steps.append(step_info)
        
        # Store stage memory if step_index is provided
        if step_index is not None:
            # Define stage names
            stage_names = {
                0: "Masking & Clipping",
                1: "Savitzky-Golay Filtering", 
                2: "Log-wavelength Rebinning & Flux Scaling",
                3: "Continuum Fitting",
                4: "Apodization",
                5: "Final Review"
            }
            
            stage_name = stage_names.get(step_index, f"Step {step_index}")
            
            # Store current state after applying step
            current_state = {
                'wave': self.current_wave.copy(),
                'flux': self.current_flux.copy()
            }
            if self.stored_continuum is not None:
                current_state['continuum'] = self.stored_continuum.copy()
            
            # Clear any stages after this step (in case user is going backwards)
            self.clear_stages_after(step_index - 1)
            
            # Store stage memory
            self._store_stage_memory(
                stage_index=step_index,
                stage_name=stage_name,
                current_state=current_state,
                preview_state=preview_state,
                processing_params=step_kwargs
            )
        
        # Emit signal for real-time updates
        self.preview_updated.emit(self.current_wave, self.current_flux)
    
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
    
    def _preview_savgol_filter(self, filter_type: str = "none", value: float = 11.0, polyorder: int = 3, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview Savitzky-Golay filtering step"""
        if filter_type == "none" or not SNID_AVAILABLE:
            return self.current_wave.copy(), self.current_flux.copy()
        
        try:
            temp_wave = self.current_wave.copy()
            temp_flux = self.current_flux.copy()
            
            if filter_type == "fixed" and value >= 3:
                filtered_flux = savgol_filter_fixed(temp_flux, int(value), polyorder)
            elif filter_type == "wavelength" and value > 0:
                filtered_flux = savgol_filter_wavelength(temp_wave, temp_flux, value, polyorder)
            else:
                return temp_wave, temp_flux
            
            return temp_wave, filtered_flux
            
        except Exception as e:
            _LOGGER.error(f"Savitzky-Golay filter preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def _preview_clipping(self, clip_type: str = "aband", **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview clipping operations"""
        if not SNID_AVAILABLE:
            return self.current_wave.copy(), self.current_flux.copy()
        
        try:
            temp_wave = self.current_wave.copy()
            temp_flux = self.current_flux.copy()
            
            if clip_type == "aband":
                clipped_wave, clipped_flux = clip_aband(temp_wave, temp_flux)
            elif clip_type == "sky":
                width = kwargs.get('width', 40.0)
                clipped_wave, clipped_flux = clip_sky_lines(temp_wave, temp_flux, width)
            else:
                return temp_wave, temp_flux
            
            return clipped_wave, clipped_flux
            
        except Exception as e:
            _LOGGER.error(f"Clipping preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def _preview_log_rebin(self, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview log-wavelength rebinning"""
        if not SNID_AVAILABLE:
            return self.current_wave.copy(), self.current_flux.copy()
        
        try:
            temp_wave = self.current_wave.copy()
            temp_flux = self.current_flux.copy()
            
            # Ensure wavelength grid is initialized before rebinning
            from snid_sage.snid.preprocessing import init_wavelength_grid
            init_wavelength_grid(num_points=NW, min_wave=MINW, max_wave=MAXW)
            
            rebinned_wave, rebinned_flux = log_rebin(temp_wave, temp_flux)
            return rebinned_wave, rebinned_flux
            
        except Exception as e:
            _LOGGER.error(f"Log rebinning preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def _preview_log_rebin_with_scaling(self, scale_to_mean: bool = True, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview log rebinning with flux scaling"""
        if not SNID_AVAILABLE:
            return self.current_wave.copy(), self.current_flux.copy()
        
        try:
            temp_wave = self.current_wave.copy()
            temp_flux = self.current_flux.copy()
            
            # Ensure wavelength grid is initialized before rebinning
            from snid_sage.snid.preprocessing import init_wavelength_grid
            init_wavelength_grid(num_points=NW, min_wave=MINW, max_wave=MAXW)
            
            # Apply log rebinning first
            rebinned_wave, rebinned_flux = log_rebin(temp_wave, temp_flux)
            
            # Apply flux scaling if requested
            if scale_to_mean:
                mask = rebinned_flux > 0
                if np.any(mask):
                    mean_flux = np.mean(rebinned_flux[mask])
                    if mean_flux > 0:
                        rebinned_flux /= mean_flux
            
            return rebinned_wave, rebinned_flux
            
        except Exception as e:
            _LOGGER.error(f"Log rebinning with scaling preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def _preview_flux_scaling(self, scale_to_mean: bool = True, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview flux scaling"""
        try:
            temp_wave = self.current_wave.copy()
            temp_flux = self.current_flux.copy()
            
            if scale_to_mean:
                mask = temp_flux > 0
                if np.any(mask):
                    mean_flux = np.mean(temp_flux[mask])
                    if mean_flux > 0:
                        temp_flux /= mean_flux
            
            return temp_wave, temp_flux
            
        except Exception as e:
            _LOGGER.error(f"Flux scaling preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def _preview_continuum_fit(self, method: str = 'spline', **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Preview continuum fitting with proper continuum storage and calculation"""
        # Check if manual continuum is active
        if hasattr(self, 'manual_continuum_active') and self.manual_continuum_active:
            if hasattr(self, 'stored_continuum') and self.stored_continuum is not None:
                return self.current_wave.copy(), self.current_flux.copy()
        
        try:
            temp_wave = self.current_wave.copy()
            temp_flux = self.current_flux.copy()
            
            if method == "gaussian":
                sigma = kwargs.get('sigma', None)
                flat_flux, continuum = self._fit_continuum_improved(temp_flux, method="gaussian", sigma=sigma)
                # Store continuum and method for later reconstruction
                self.stored_continuum = continuum.copy()
                self.continuum_method = "gaussian"
                self.continuum_kwargs = {'sigma': sigma}
            elif method == "spline":
                knotnum = kwargs.get('knotnum', 13)
                flat_flux, continuum = self._fit_continuum_improved(temp_flux, method="spline", knotnum=knotnum)
                # Store continuum and method for later reconstruction
                self.stored_continuum = continuum.copy()
                self.continuum_method = "spline"
                self.continuum_kwargs = {'knotnum': knotnum}
            else:
                return temp_wave, temp_flux
            
            # CRITICAL: Always emit continuum signal for visualization even in preview mode
            self.continuum_updated.emit(temp_wave, continuum)
            
            return temp_wave, flat_flux
            
        except Exception as e:
            _LOGGER.error(f"Continuum fitting preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
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
        """Preview apodization (edge tapering)"""
        if not SNID_AVAILABLE:
            return self.current_wave.copy(), self.current_flux.copy()
        
        try:
            temp_wave = self.current_wave.copy()
            temp_flux = self.current_flux.copy()
            
            # Find the valid data range for apodization
            # For continuum-removed spectra, we need to find where we have significant data
            has_negative = np.any(temp_flux < 0)
            
            if has_negative:
                # For continuum-removed spectra, find the range where we have "significant" data
                abs_flux = np.abs(temp_flux)
                threshold = np.max(abs_flux) * 0.01 if np.max(abs_flux) > 0 else 0
                nz = np.nonzero(abs_flux > threshold)[0]
            else:
                # For non-continuum-removed spectra, use positive values only
                nz = np.nonzero(temp_flux > 0)[0]
            
            if nz.size > 0:
                n1, n2 = nz[0], nz[-1]
                # Ensure we have enough points for meaningful apodization
                if n2 - n1 >= 10:
                    apodized_flux = apodize(temp_flux, n1, n2, percent=percent)
                    return temp_wave, apodized_flux
            
            # If we can't find a valid range, return unchanged
            return temp_wave, temp_flux
            
        except Exception as e:
            _LOGGER.error(f"Apodization preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def _fit_continuum_improved(self, flux: np.ndarray, method: str = "spline", **kwargs):
        """Improved continuum fitting with better error handling - matches Tkinter version"""
        try:
            if not SNID_AVAILABLE:
                # Fallback: return flat spectrum and unity continuum
                return np.zeros_like(flux), np.ones_like(flux)
            
            if method == "gaussian":
                sigma = kwargs.get('sigma', None)
                if sigma is None:
                    sigma = calculate_auto_gaussian_sigma(flux)
                # Use the same fit_continuum function as the Tkinter version
                flat_flux, continuum = fit_continuum(flux, method="gaussian", sigma=sigma)
                return flat_flux, continuum
            elif method == "spline":
                knotnum = kwargs.get('knotnum', 13)
                # Use the same fit_continuum function as the Tkinter version
                flat_flux, continuum = fit_continuum(flux, method="spline", knotnum=knotnum)
                return flat_flux, continuum
            else:
                # Return flat spectrum if method not recognized
                return np.zeros_like(flux), np.ones_like(flux)
                
        except Exception as e:
            _LOGGER.error(f"Continuum fitting failed: {e}")
            # Return flat spectrum on error
            return np.zeros_like(flux), np.ones_like(flux)
    
    def _calculate_manual_continuum_preview(self, manual_continuum: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate preview with manual continuum array"""
        try:
            temp_wave = self.current_wave.copy()
            temp_flux = self.current_flux.copy()
            
            # Apply continuum division with proper handling
            positive_mask = temp_flux > 0
            continuum_mask = manual_continuum > 0
            valid_mask = positive_mask & continuum_mask
            
            flat_flux = np.zeros_like(temp_flux)
            flat_flux[valid_mask] = (temp_flux[valid_mask] / manual_continuum[valid_mask]) - 1.0
            
            # Emit continuum signal for visualization
            self.continuum_updated.emit(temp_wave, manual_continuum)
            
            return temp_wave, flat_flux
            
        except Exception as e:
            _LOGGER.error(f"Manual continuum preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def calculate_interactive_continuum_preview(self, continuum_points: List[Tuple[float, float]]) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate preview with interactive continuum points"""
        try:
            if len(continuum_points) < 2:
                return self.current_wave.copy(), self.current_flux.copy()
            
            # Extract wavelength and continuum values
            wave_points = np.array([point[0] for point in continuum_points])
            continuum_values = np.array([point[1] for point in continuum_points])
            
            # Interpolate continuum to full wavelength grid
            continuum = np.interp(self.current_wave, wave_points, continuum_values)
            
            # Apply continuum division
            temp_flux = self.current_flux.copy()
            positive_mask = temp_flux > 0
            continuum_mask = continuum > 0
            valid_mask = positive_mask & continuum_mask
            
            flat_flux = np.zeros_like(temp_flux)
            flat_flux[valid_mask] = (temp_flux[valid_mask] / continuum[valid_mask]) - 1.0
            
            # Emit continuum signal for visualization
            self.continuum_updated.emit(self.current_wave, continuum)
            
            return self.current_wave.copy(), flat_flux
            
        except Exception as e:
            _LOGGER.error(f"Interactive continuum preview failed: {e}")
            return self.current_wave.copy(), self.current_flux.copy()
    
    def get_continuum_from_fit(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get the stored continuum from the last fitting operation"""
        
        if self.stored_continuum is not None:
            return self.current_wave.copy(), self.stored_continuum.copy()
        else:
            # Return flat continuum if none stored
            return self.current_wave.copy(), np.ones_like(self.current_wave)
    
    def get_applied_steps(self) -> List[Dict[str, Any]]:
        """Get list of applied preprocessing steps"""
        return self.applied_steps.copy() 