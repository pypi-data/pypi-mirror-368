"""
Spectrum Plotter Component

This module handles all spectrum plotting functionality including:
- Original spectrum plotting (flux view)
- Flattened spectrum plotting
- Template comparison plotting
- Spectrum preprocessing visualization

Extracted from sage_gui.py to improve maintainability and modularity.
"""

import numpy as np

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.spectrum_plotter')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.spectrum_plotter')

# Import template name cleaning utility
from snid_sage.shared.utils import clean_template_name


class SpectrumPlotter:
    """
    Handles all spectrum plotting operations for the SNID GUI.
    
    This class encapsulates spectrum plotting logic and provides a clean interface
    for the main GUI to display spectra without cluttering the main class.
    """
    
    def __init__(self, gui_instance):
        """
        Initialize the spectrum plotter.
        
        Args:
            gui_instance: Reference to the main GUI instance for accessing
                         matplotlib components, theme manager, and data
        """
        self.gui = gui_instance
        
    @property
    def ax(self):
        """Access to the matplotlib axes from the GUI"""
        return self.gui.ax
        
    @property
    def fig(self):
        """Access to the matplotlib figure from the GUI"""
        return self.gui.fig
        
    @property
    def canvas(self):
        """Access to the matplotlib canvas from the GUI"""
        return self.gui.canvas
        
    @property
    def theme_manager(self):
        """Access to the theme manager from the GUI"""
        return self.gui.theme_manager
    
    def plot_original_spectra(self, _retry_count=0):
        """Plot original spectrum view with best template match using standardized styling"""
        try:
            if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results:
                self._plot_spectrum_only()
                return
            
            # Get current template index
            if not self.gui.snid_results.best_matches:
                self._plot_no_matches()
                return
            
            # Ensure current template index is valid
            self.gui.current_template = max(0, min(self.gui.current_template, len(self.gui.snid_results.best_matches) - 1))
            current_match = self.gui.snid_results.best_matches[self.gui.current_template]
            
            # Use standardized styling
            title = f'Flux View - {current_match["name"]} (z={current_match["redshift"]:.5f})'
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title=title,
                ylabel='Flux'
            )
            
            # Get the observed spectrum data - prioritize original preprocessing over SNID processing
            if hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum and 'log_wave' in self.gui.processed_spectrum:
                # Use the original preprocessed data to preserve custom preprocessing
                obs_wave = self.gui.processed_spectrum['log_wave']
                # FIXED: Use display_flux (apodized) if available, otherwise log_flux (non-apodized)
                obs_flux = self.gui.processed_spectrum.get('display_flux', self.gui.processed_spectrum['log_flux'])
                filter_source = self.gui.processed_spectrum
            else:
                # Fallback to SNID processed data if no original preprocessing
                obs_wave = self.gui.snid_results.processed_spectrum['log_wave']
                obs_flux = self.gui.snid_results.processed_spectrum['log_flux']  # This is flux view
                filter_source = self.gui.snid_results.processed_spectrum
            
            # Filter out zero-padded regions from observed spectrum
            obs_wave, obs_flux = self.gui._filter_nonzero_spectrum(obs_wave, obs_flux, filter_source)
            
            # Get template spectrum (shift to observed redshift)
            template_wave = current_match['spectra']['flux']['wave']
            template_flux = current_match['spectra']['flux']['flux']
            
            # DON'T filter templates - they are already properly trimmed by SNID analysis
            # snid_sage.snid.py
            # Filtering them again with input spectrum edges cuts them incorrectly
            # template_wave, template_flux = self.gui._filter_nonzero_spectrum(
            #     template_wave, template_flux, filter_source
            # )
            
            # Plot observed spectrum with consistent colors
            spectrum_color = '#3b82f6'  # Same blue as Flux/Flat buttons
            template_color = '#E74C3C'  # Nice red that complements blue
            
            self.ax.plot(obs_wave, obs_flux, color=spectrum_color, linewidth=2, alpha=0.9)
            
            # Plot template spectrum
            self.ax.plot(template_wave, template_flux, color=template_color, linewidth=2.5, alpha=0.8)
            
            # Add template info text (using subtype from template object)
            template = current_match.get('template', {})
            subtype = template.get('subtype', current_match.get('type', 'Unknown'))
            
            # Get redshift uncertainty if available
            redshift_error = current_match.get('redshift_error', 0)
            if redshift_error > 0:
                redshift_text = f"z = {current_match['redshift']:.5f} ±{redshift_error:.5f}"
            else:
                redshift_text = f"z = {current_match['redshift']:.5f}"
            
            # Use RLAP-cos if available, otherwise RLAP
            rlap_cos = current_match.get('rlap_cos')
            if rlap_cos is not None:
                metric_text = f"RLAP-cos = {rlap_cos:.2f}"
            else:
                metric_text = f"RLAP = {current_match['rlap']:.2f}"
            
            info_text = (f"Template {self.gui.current_template + 1}/{len(self.gui.snid_results.best_matches)}: "
                        f"{clean_template_name(current_match['name'])}\n"
                        f"Subtype: {subtype}, Age: {current_match['age']:.1f}d\n"
                        f"{redshift_text}\n"
                        f"{metric_text}")
            
            # Use adaptive positioning for template info
            from ...utils.plot_legend_utils import add_adaptive_template_info
            theme_colors = {
                'text_primary': text_color,
                'bg_tertiary': self.theme_manager.get_color('bg_tertiary')
            }
            add_adaptive_template_info(self.ax, info_text, position='upper right', 
                                     theme_colors=theme_colors, fontsize=12)
            
            self.gui._finalize_plot_standard()
            
            _LOGGER.debug(f"Plotted flux view for template {self.gui.current_template + 1}: {current_match['name']}")
            
        except Exception as e:
            # NEW: Check if this is an axis type error and force reinit if needed
            if ("Axes3D" in str(e) or "missing 1 required positional argument" in str(e)) and _retry_count == 0:
                _LOGGER.warning("⚠️ Detected 3D/incompatible axis error - forcing plot reinitialization")
                self._force_plot_reinit()
                # Retry the plot after reinit (only once to prevent infinite loops)
                try:
                    self.plot_original_spectra(_retry_count=1)
                    return
                except Exception as retry_e:
                    _LOGGER.error(f"Error after plot reinitialization: {retry_e}")
            
            _LOGGER.error(f"Error plotting original spectra: {e}")
            import traceback
            traceback.print_exc()
            self._handle_plot_error(f"Error plotting flux view: {str(e)}")
    
    def plot_flattened_spectra(self, _retry_count=0):
        """Plot flattened spectrum view with best template match using standardized styling"""
        try:
            if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results:
                self._plot_flattened_spectrum_only()
                return
            
            # Get current template index
            if not self.gui.snid_results.best_matches:
                self._plot_no_matches()
                return
            
            # Ensure current template index is valid
            self.gui.current_template = max(0, min(self.gui.current_template, len(self.gui.snid_results.best_matches) - 1))
            current_match = self.gui.snid_results.best_matches[self.gui.current_template]
            
            # Use standardized styling
            title = f'Flattened View - {current_match["name"]} (z={current_match["redshift"]:.5f})'
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title=title,
                ylabel='Flattened Flux'
            )
            
            # Get the observed spectrum data (flattened version)
            if hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum and 'flat_flux' in self.gui.processed_spectrum:
                obs_wave = self.gui.processed_spectrum['log_wave']
                # FIXED: Use display_flat (apodized) if available, otherwise flat_flux (non-apodized)
                obs_flux = self.gui.processed_spectrum.get('display_flat', self.gui.processed_spectrum['flat_flux'])
                filter_source = self.gui.processed_spectrum
            else:
                obs_wave = self.gui.snid_results.processed_spectrum['log_wave']
                obs_flux = self.gui.snid_results.processed_spectrum['flat_flux']
                filter_source = self.gui.snid_results.processed_spectrum
            
            # Filter out zero-padded regions from observed spectrum
            obs_wave, obs_flux = self.gui._filter_nonzero_spectrum(obs_wave, obs_flux, filter_source)
            
            # Get template spectrum (flattened)
            template_wave = current_match['spectra']['flat']['wave']
            template_flux = current_match['spectra']['flat']['flux']
            
            # DON'T filter templates - they are already properly trimmed by SNID analysis
            # snid_sage.snid.py
            # Filtering them again with input spectrum edges cuts them incorrectly
            # template_wave, template_flux = self.gui._filter_nonzero_spectrum(
            #     template_wave, template_flux, filter_source
            # )
            
            # Plot observed spectrum with consistent colors
            spectrum_color = '#3b82f6'  # Same blue as Flux/Flat buttons
            template_color = '#E74C3C'  # Nice red that complements blue
            
            self.ax.plot(obs_wave, obs_flux, color=spectrum_color, linewidth=2, alpha=0.9)
            
            # Plot template spectrum
            self.ax.plot(template_wave, template_flux, color=template_color, linewidth=2.5, alpha=0.8)
            
            # Add template info text (using subtype from template object)
            template = current_match.get('template', {})
            subtype = template.get('subtype', current_match.get('type', 'Unknown'))
            
            # Get redshift uncertainty if available
            redshift_error = current_match.get('redshift_error', 0)
            if redshift_error > 0:
                redshift_text = f"z = {current_match['redshift']:.5f} ±{redshift_error:.5f}"
            else:
                redshift_text = f"z = {current_match['redshift']:.5f}"
            
            # Use RLAP-cos if available, otherwise RLAP
            rlap_cos = current_match.get('rlap_cos')
            if rlap_cos is not None:
                metric_text = f"RLAP-cos = {rlap_cos:.2f}"
            else:
                metric_text = f"RLAP = {current_match['rlap']:.2f}"
            
            info_text = (f"Template {self.gui.current_template + 1}/{len(self.gui.snid_results.best_matches)}: "
                        f"{clean_template_name(current_match['name'])}\n"
                        f"Subtype: {subtype}, Age: {current_match['age']:.1f}d\n"
                        f"{redshift_text}\n"
                        f"{metric_text}")
            
            # Use adaptive positioning for template info
            from ...utils.plot_legend_utils import add_adaptive_template_info
            theme_colors = {
                'text_primary': text_color,
                'bg_tertiary': self.theme_manager.get_color('bg_tertiary')
            }
            add_adaptive_template_info(self.ax, info_text, position='upper right', 
                                     theme_colors=theme_colors, fontsize=12)
            
            self.gui._finalize_plot_standard()
            
            _LOGGER.debug(f"Plotted flattened view for template {self.gui.current_template + 1}: {current_match['name']}")
            
        except Exception as e:
            # NEW: Check if this is an axis type error and force reinit if needed
            if ("Axes3D" in str(e) or "missing 1 required positional argument" in str(e)) and _retry_count == 0:
                _LOGGER.warning("⚠️ Detected 3D/incompatible axis error - forcing plot reinitialization")
                self._force_plot_reinit()
                # Retry the plot after reinit (only once to prevent infinite loops)
                try:
                    self.plot_flattened_spectra(_retry_count=1)
                    return
                except Exception as retry_e:
                    _LOGGER.error(f"Error after plot reinitialization: {retry_e}")
            
            _LOGGER.error(f"Error plotting flattened spectra: {e}")
            import traceback
            traceback.print_exc()
            self._handle_plot_error(f"Error plotting flattened view: {str(e)}")
    
    def plot_preprocessed_spectrum(self, wave, flux):
        """Plot a preprocessed spectrum"""
        try:
            # Filter out zero-padded regions before plotting
            wave, flux = self.gui._filter_nonzero_spectrum(wave, flux)
            
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title='Preprocessed Spectrum',
                ylabel='Flux'
            )
            
            spectrum_color = '#3b82f6'  # Same blue as Flux/Flat buttons
            self.ax.plot(wave, flux, color=spectrum_color, linewidth=2, alpha=0.8)
            
            self.gui._finalize_plot_standard()
            
            _LOGGER.debug("Plotted preprocessed spectrum")
            
        except Exception as e:
            _LOGGER.error(f"Error plotting preprocessed spectrum: {e}")
            self._handle_plot_error(f"Error plotting preprocessed spectrum: {str(e)}")
    
    def _plot_spectrum_only(self):
        """Plot just the processed spectrum if no SNID results"""
        if hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum:
            wave = self.gui.processed_spectrum['log_wave']
            flux = self.gui.processed_spectrum['log_flux']
            # Filter out zero-padded regions
            wave, flux = self.gui._filter_nonzero_spectrum(wave, flux, self.gui.processed_spectrum)
            
            # Use standardized styling
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title='Processed Spectrum - Flux View',
                ylabel='Flux'
            )
            
            spectrum_color = '#3b82f6'  # Same blue as Flux/Flat buttons
            self.ax.plot(wave, flux, color=spectrum_color, linewidth=2, alpha=0.8)
                    
        elif hasattr(self.gui, 'original_wave') and hasattr(self.gui, 'original_flux'):
            # Fallback to original spectrum if no preprocessing done yet
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title='Original Spectrum'
            )
            
            spectrum_color = '#3b82f6'  # Same blue as Flux/Flat buttons
            self.ax.plot(self.gui.original_wave, self.gui.original_flux, color=spectrum_color, 
                       linewidth=2, alpha=0.8)
        else:
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title='No Data'
            )
            self.ax.text(0.5, 0.5, 'No spectrum data available\nLoad a spectrum first', 
                       ha='center', va='center', transform=self.ax.transAxes,
                       fontsize=14, color=text_color)
        
        self.gui._finalize_plot_standard()
    
    def _plot_flattened_spectrum_only(self):
        """Plot just the flattened spectrum if no SNID results"""
        if hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum:
            wave = self.gui.processed_spectrum['log_wave']
            # FIXED: Use display_flat (apodized) if available, otherwise flat_flux (non-apodized)
            flux = self.gui.processed_spectrum.get('display_flat', self.gui.processed_spectrum['flat_flux'])
            # Filter out zero-padded regions
            wave, flux = self.gui._filter_nonzero_spectrum(wave, flux, self.gui.processed_spectrum)
            
            # Use standardized styling
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title='Processed Spectrum - Flattened View',
                ylabel='Flattened Flux'
            )
            
            spectrum_color = '#3b82f6'  # Same blue as Flux/Flat buttons
            self.ax.plot(wave, flux, color=spectrum_color, linewidth=2, alpha=0.8)
                    
        elif hasattr(self.gui, 'original_wave') and hasattr(self.gui, 'original_flux'):
            # If no preprocessing, show message about needing preprocessing for flattened view
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title='Preprocessing Required'
            )
            self.ax.text(0.5, 0.5, 'Flattened view requires preprocessing\nRun preprocessing first', 
                       ha='center', va='center', transform=self.ax.transAxes,
                       fontsize=14, color=self.theme_manager.get_color('warning'))
        else:
            bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
                title='No Data'
            )
            self.ax.text(0.5, 0.5, 'No spectrum data available\nLoad a spectrum first', 
                       ha='center', va='center', transform=self.ax.transAxes,
                       fontsize=14, color=text_color)
        
        self.gui._finalize_plot_standard()
    
    def _plot_no_matches(self):
        """Plot message when no template matches are found"""
        bg_color, text_color, grid_color = self.gui._standardize_plot_styling(
            title='No Matches Found'
        )
        self.ax.text(0.5, 0.5, 'No template matches found', 
                   ha='center', va='center', transform=self.ax.transAxes,
                   fontsize=14, color=text_color)
        self.gui._finalize_plot_standard()
    
    def _handle_plot_error(self, error_message):
        """Handle plot errors by showing error message"""
        try:
            if hasattr(self.gui, '_plot_error'):
                self.gui._plot_error(error_message)
            else:
                _LOGGER.error(f"Plot error handler not available: {error_message}")
        except Exception as e:
            _LOGGER.error(f"Error in plot error handler: {e}")
    
    def _is_valid_2d_axis(self):
        """Check if the current axis is a valid 2D axis for spectrum plotting"""
        try:
            if not hasattr(self, 'ax') or not self.ax:
                return False
                
            # Check if it's a 3D axis
            axis_type = str(type(self.ax))
            if 'Axes3D' in axis_type or '3d' in axis_type.lower():
                return False
                
            # Check if it's part of a multi-subplot figure
            if hasattr(self.gui, 'fig') and self.gui.fig:
                num_axes = len(self.gui.fig.axes)
                if num_axes > 1:
                    return False
                    
            return True
            
        except Exception as e:
            _LOGGER.debug(f"Error checking axis validity: {e}")
            return False
    
    def _force_plot_reinit(self):
        """Force plot reinitialization when axis type is incompatible"""
        try:
            _LOGGER.debug("🔧 Forcing plot reinitialization due to axis incompatibility")
            
            # Use plot controller's force reinit if available
            if hasattr(self.gui, 'plot_controller') and hasattr(self.gui.plot_controller, '_force_matplotlib_reinit'):
                self.gui.plot_controller._force_matplotlib_reinit()
            else:
                # Fallback reinit
                if hasattr(self.gui, 'init_matplotlib_plot'):
                    self.gui.init_matplotlib_plot()
                    
        except Exception as e:
            _LOGGER.error(f"Error forcing plot reinitialization: {e}") 
