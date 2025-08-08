"""
Spectrum Reset Manager for SNID SAGE GUI
=========================================

This module manages the resetting of spectrum data and associated GUI state
when loading new spectra or clearing the analysis workspace.
"""

import tkinter as tk

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.reset')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.reset')

import numpy as np
from typing import Optional

# Import unified systems for consistent plot styling
try:
    from .no_title_plot_manager import apply_no_title_styling
    UNIFIED_SYSTEMS_AVAILABLE = True
except ImportError:
    UNIFIED_SYSTEMS_AVAILABLE = False


class SpectrumResetManager:
    """
    Manages comprehensive reset of spectrum-related state and plots
    
    This manager ensures that when a new spectrum is loaded, all previous
    state is completely cleared, including plots, analysis results,
    preprocessing state, and visualization components.
    """
    
    def __init__(self, gui_instance):
        """
        Initialize the spectrum reset manager
        
        Args:
            gui_instance: The main GUI instance to reset
        """
        self.gui = gui_instance
    
    def reset_for_new_spectrum(self, preserve_file_path: bool = False):
        """
        Perform comprehensive reset for a new spectrum load
        
        This method clears all spectrum-related state, plots, and analysis results
        to ensure the application starts fresh with the new spectrum.
        
        Args:
            preserve_file_path (bool): Whether to preserve the current file path
                                     (useful when the reset is called before the new file is loaded)
        """
        _LOGGER.info("🔄 Performing comprehensive spectrum reset...")
        
        # Reset core spectrum data
        self._reset_spectrum_data(preserve_file_path)
        
        # Reset analysis and processing state
        self._reset_analysis_state()
        
        # Reset all plots and visualization
        self._reset_plots_and_visualization()
        
        # Reset controllers and components
        self._reset_controllers_and_components()
        
        # Reset UI state
        self._reset_ui_state()
        
        # Update button states to reflect fresh state
        self._update_button_states_after_reset()
        
        _LOGGER.info("✅ Comprehensive spectrum reset completed")
    
    def _reset_spectrum_data(self, preserve_file_path: bool = False):
        """Reset all spectrum data variables"""
        if not preserve_file_path:
            self.gui.file_path = None
        
        # Reset original spectrum data
        self.gui.original_wave = None
        self.gui.original_flux = None
        
        # Reset preprocessed spectrum data
        self.gui.preprocessed_wave = None
        self.gui.preprocessed_flux = None
        self.gui.processed_spectrum = None
        
        # Reset any loaded spectrum data
        if hasattr(self.gui, 'loaded_spectrum'):
            self.gui.loaded_spectrum = None
        
        _LOGGER.info("  📊 Spectrum data variables reset")
    
    def _reset_analysis_state(self):
        """Reset all analysis results and processing state"""
        # Reset SNID results
        self.gui.snid_results = None
        self.gui.snid_trace = None
        
        # Reset template navigation
        if hasattr(self.gui, 'current_template'):
            self.gui.current_template = 0
        
        # Reset any cached analysis data
        if hasattr(self.gui, 'analysis_cache'):
            self.gui.analysis_cache = None
        
        # Reset line detection results
        if hasattr(self.gui, 'detected_lines'):
            self.gui.detected_lines = None
        
        # Reset any LLM analysis results
        if hasattr(self.gui, 'llm_analysis'):
            self.gui.llm_analysis = None
        
        _LOGGER.info("  🔬 Analysis state reset")
    
    def _reset_plots_and_visualization(self):
        """Reset all plots and visualization components"""
        # Clear main matplotlib plot
        if hasattr(self.gui, 'ax') and self.gui.ax:
            self.gui.ax.clear()
            if hasattr(self.gui, 'canvas') and self.gui.canvas:
                try:
                    self.gui.canvas.draw()
                except Exception as e:
                    _LOGGER.warning(f"  ⚠️ Warning clearing canvas: {e}")
        
        # Reset plot controller state
        if hasattr(self.gui, 'plot_controller') and self.gui.plot_controller:
            try:
                self.gui.plot_controller.reset_view_state()
            except Exception as e:
                _LOGGER.warning(f"  ⚠️ Warning resetting plot controller: {e}")
        
        # Reset view controller state
        if hasattr(self.gui, 'view_controller') and self.gui.view_controller:
            try:
                self.gui.view_controller.reset_to_initial_view()
            except Exception as e:
                _LOGGER.warning(f"  ⚠️ Warning resetting view controller: {e}")
        
        # Reset any cached plot data
        self._reset_plot_components()
        
        _LOGGER.info("  📈 Plots and visualization reset")
    
    def _reset_plot_components(self):
        """Reset individual plot components"""
        # Reset spectrum plotter
        if hasattr(self.gui, 'spectrum_plotter') and self.gui.spectrum_plotter:
            try:
                self.gui.spectrum_plotter.clear_all_plots()
            except (AttributeError, Exception):
                pass  # Component may not have this method
        
        # Reset analysis plotter
        if hasattr(self.gui, 'analysis_plotter') and self.gui.analysis_plotter:
            try:
                self.gui.analysis_plotter.clear_analysis_plots()
            except (AttributeError, Exception):
                pass  # Component may not have this method
        

        
        # Reset summary plotter
        if hasattr(self.gui, 'summary_plotter') and self.gui.summary_plotter:
            try:
                self.gui.summary_plotter.clear_summary_plots()
            except (AttributeError, Exception):
                pass  # Component may not have this method
    
    def _reset_controllers_and_components(self):
        """Reset controller and component state"""
        # Reset preprocessing controller
        if hasattr(self.gui, 'preprocessing_controller') and self.gui.preprocessing_controller:
            try:
                self.gui.preprocessing_controller.reset_preprocessing_state()
            except Exception as e:
                _LOGGER.warning(f"  ⚠️ Warning resetting preprocessing controller: {e}")
        
        # Reset analysis controller
        if hasattr(self.gui, 'analysis_controller') and self.gui.analysis_controller:
            try:
                self.gui.analysis_controller.reset_analysis_state()
            except Exception as e:
                _LOGGER.warning(f"  ⚠️ Warning resetting analysis controller: {e}")
        
        # Reset line detection controller
        if hasattr(self.gui, 'line_detection_controller') and self.gui.line_detection_controller:
            try:
                self.gui.line_detection_controller.reset_line_detection()
            except Exception as e:
                _LOGGER.warning(f"  ⚠️ Warning resetting line detection controller: {e}")
        
        # Reset results manager
        if hasattr(self.gui, 'results_manager') and self.gui.results_manager:
            try:
                self.gui.results_manager.clear_all_results()
            except Exception as e:
                _LOGGER.warning(f"  ⚠️ Warning resetting results manager: {e}")
        
        _LOGGER.info("  🎛️ Controllers and components reset")
    
    def _reset_ui_state(self):
        """Reset UI state and visual indicators"""
        # Reset header status to initial state
        try:
            self.gui.update_header_status("🚀 Ready - Load a spectrum to begin analysis")
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning updating header status: {e}")
        
        # Reset any progress indicators
        if hasattr(self.gui, 'progress_var'):
            try:
                self.gui.progress_var.set(0)
            except Exception:
                pass
        
        # Reset any status labels
        if hasattr(self.gui, 'status_label'):
            try:
                self.gui.status_label.config(text="No spectrum loaded")
            except Exception:
                pass
        
        # Clear any temporary UI elements
        self._clear_temporary_ui_elements()
        
        _LOGGER.info("  🖥️ UI state reset")
    
    def _clear_temporary_ui_elements(self):
        """Clear temporary UI elements like dialogs or overlays"""
        # Close any open preprocessing dialogs
        if hasattr(self.gui, 'preprocessing_dialog_open'):
            self.gui.preprocessing_dialog_open = False
        
        # Clear any overlay information
        if hasattr(self.gui, 'overlay_info'):
            self.gui.overlay_info = None
        
        # Reset any modal states
        if hasattr(self.gui, 'modal_active'):
            self.gui.modal_active = False
    
    def _update_button_states_after_reset(self):
        """Update button states to reflect the fresh state"""
        try:
            # Update button states through the workflow integrator system (PySide6 pattern)
            if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                self.gui.workflow_integrator._workflow_update_button_states()
            else:
                # Fallback for older pattern
                if hasattr(self.gui, 'app_controller') and hasattr(self.gui.app_controller, 'update_button_states'):
                    self.gui.app_controller.update_button_states()
                elif hasattr(self.gui, 'update_button_states'):
                    self.gui.update_button_states()
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning updating button states: {e}")
    
    def soft_reset(self):
        """
        Perform a soft reset that only clears plots and analysis results
        but preserves loaded spectrum data
        
        Useful for refreshing the view without completely starting over
        """
        _LOGGER.info("🔄 Performing soft reset...")
        
        # Reset only analysis state and plots
        self._reset_analysis_state()
        self._reset_plots_and_visualization()
        
        # Update UI to reflect reset
        try:
            self.gui.update_header_status("📊 Spectrum loaded - Ready for analysis")
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning updating header status: {e}")
        
        self._update_button_states_after_reset()
        
        _LOGGER.info("✅ Soft reset completed")
    
    def reset_specific_component(self, component_name: str):
        """
        Reset a specific component by name
        
        Args:
            component_name (str): Name of the component to reset
        """
        try:
            if component_name == "spectrum":
                self._reset_spectrum_data()
            elif component_name == "analysis":
                self._reset_analysis_state()
            elif component_name == "plots":
                self._reset_plots_and_visualization()
            elif component_name == "controllers":
                self._reset_controllers_and_components()
            elif component_name == "ui":
                self._reset_ui_state()
            else:
                _LOGGER.warning(f"⚠️ Unknown component for reset: {component_name}")
                
        except Exception as e:
            _LOGGER.error(f"❌ Error resetting component {component_name}: {e}")
    
    def reset_gui_to_initial_state(self):
        """
        Complete GUI reset to initial state (like when first opened)
        
        This performs the most comprehensive reset possible, bringing the GUI back
        to its initial state while preserving user settings like theme and fonts.
        """
        _LOGGER.info("🔄 Starting complete GUI reset to initial state...")
        
        try:
            # 1. Stop any blinking effects before other resets
            self._stop_all_blinking_effects()
            
            # 2. Clear all data and analysis results
            self.reset_for_new_spectrum(preserve_file_path=False)
            
            # 3. Clear plot display completely
            self._clear_all_plots_completely()
            
            # 4. Reset view controller to initial view
            self._reset_view_to_initial()
            
            # 5. Reset state manager to initial state
            self._reset_state_manager()
            
            # 6. Clear header status
            self._reset_header_status()
            
            # 7. Update GUI components to initial appearance
            self._reset_gui_appearance_to_initial()
            
            # 8. Force button state update to initial
            self._force_initial_button_states()
            
            # 9. Apply theme to ensure proper appearance
            self._apply_theme_after_reset()
            
            _LOGGER.info("✅ Complete GUI reset to initial state completed successfully")
            
            # Show confirmation to user
            self._show_reset_confirmation()
            
        except Exception as e:
            _LOGGER.error(f"❌ Error during complete GUI reset: {e}")
            import traceback
            traceback.print_exc()
    
    def _stop_all_blinking_effects(self):
        """Stop all blinking effects that might be active"""
        try:
            # Stop cluster summary blinking
            if hasattr(self.gui, 'stop_cluster_summary_blinking'):
                self.gui.stop_cluster_summary_blinking()
                _LOGGER.debug("  🔴 Stopped cluster summary blinking effect")
            
            # Reset cluster summary state variables explicitly
            if hasattr(self.gui, 'cluster_summary_blinking'):
                self.gui.cluster_summary_blinking = False
            if hasattr(self.gui, 'cluster_summary_clicked_once'):
                self.gui.cluster_summary_clicked_once = False
            if hasattr(self.gui, 'cluster_summary_blink_timer'):
                if self.gui.cluster_summary_blink_timer:
                    self.gui.cluster_summary_blink_timer.stop()
                    self.gui.cluster_summary_blink_timer = None
            if hasattr(self.gui, 'cluster_summary_original_style'):
                self.gui.cluster_summary_original_style = None
                
            _LOGGER.debug("  ✅ All blinking effects stopped and state variables reset")
            
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning stopping blinking effects: {e}")
    
    def _clear_all_plots_completely(self):
        """Clear all plots and restore initial empty state"""
        try:
            # Close any orphaned matplotlib figures first
            try:
                import matplotlib.pyplot as plt
                plt.close('all')
            except:
                pass
            
            # Get theme colors
            if hasattr(self.gui, 'theme_manager'):
                theme = self.gui.theme_manager.get_current_theme() if hasattr(self.gui.theme_manager, 'get_current_theme') else {}
                text_color = theme.get('text_color', 'black')
                plot_bg = theme.get('bg_color', 'white')
            else:
                text_color = 'black'
                plot_bg = 'white'
            
            # Clear the axis and restore initial state
            self.gui.ax.clear()
            
            # Set background color properly for the current theme
            self.gui.ax.set_facecolor(plot_bg)
            self.gui.fig.patch.set_facecolor(plot_bg)
            
            # Set initial plot appearance
            self.gui.ax.text(0.5, 0.5, 'SNID SAGE - Ready for Spectrum Analysis\n\nLoad a spectrum file to begin',
                           ha='center', va='center', transform=self.gui.ax.transAxes,
                           fontsize=14, color=text_color, weight='bold')
            
            # Apply proper theming immediately
            if hasattr(self.gui, 'plot_controller') and self.gui.plot_controller:
                self.gui.plot_controller._apply_plot_theme()
            
            # Apply no-title styling per user requirement
            if UNIFIED_SYSTEMS_AVAILABLE:
                apply_no_title_styling(self.gui.fig, self.gui.ax, "", "", 
                                     getattr(self.gui, 'theme_manager', None))
            
            if hasattr(self.gui, 'canvas') and self.gui.canvas:
                self.gui.canvas.draw()
            
            # Reset any cached plot data in components
            self._reset_plot_components()
            
            # Ensure matplotlib figure/canvas relationship is maintained
            # Re-establish the connection between figure, axis, and canvas
            self._restore_matplotlib_connection()
            
            _LOGGER.info("  📈 All plots cleared and reset to initial state")
            
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning clearing plots completely: {e}")
    
    def _restore_matplotlib_connection(self):
        """Restore proper matplotlib figure/canvas/axis connection after reset"""
        try:
            # Check if we have the essential matplotlib components
            if not (hasattr(self.gui, 'fig') and hasattr(self.gui, 'ax') and hasattr(self.gui, 'canvas')):
                _LOGGER.debug("  🔧 Some matplotlib components missing - attempting restoration")
                
                # If we have a plot controller, reinitialize through it
                if hasattr(self.gui, 'plot_controller') and self.gui.plot_controller:
                    # Force plot controller to reinitialize if needed
                    if not hasattr(self.gui, 'fig') or self.gui.fig is None:
                        self.gui.plot_controller.init_matplotlib_plot()
                    return
                
                # If no plot controller, try direct initialization
                if hasattr(self.gui, 'init_matplotlib_plot'):
                    self.gui.init_matplotlib_plot()
                return
            
            # Verify the figure-axis relationship
            if self.gui.fig and self.gui.ax:
                # Check if the axis belongs to the figure
                if self.gui.ax not in self.gui.fig.axes:
                    _LOGGER.debug("  🔧 Axis not properly connected to figure - recreating")
                    # Clear the figure and create new axis
                    self.gui.fig.clear()
                    self.gui.ax = self.gui.fig.add_subplot(111)
                    
                    # Set initial plot appearance again
                    # Get theme colors
                    if hasattr(self.gui, 'theme_manager'):
                        theme = self.gui.theme_manager.get_current_theme() if hasattr(self.gui.theme_manager, 'get_current_theme') else {}
                        text_color = theme.get('text_color', 'black')
                    else:
                        text_color = 'black'
                        
                    self.gui.ax.text(0.5, 0.5, 'SNID SAGE - Ready for Spectrum Analysis\n\nLoad a spectrum file to begin',
                                   ha='center', va='center', transform=self.gui.ax.transAxes,
                                   fontsize=14, color=text_color, weight='bold')
                    # Apply no-title styling per user requirement
                    if UNIFIED_SYSTEMS_AVAILABLE:
                        apply_no_title_styling(self.gui.fig, self.gui.ax, "", "", 
                                             getattr(self.gui, 'theme_manager', None))
            
            # Verify the canvas-figure relationship
            if self.gui.canvas and self.gui.fig:
                if self.gui.canvas.figure != self.gui.fig:
                    _LOGGER.debug("  🔧 Canvas not properly connected to figure - restoring connection")
                    self.gui.canvas.figure = self.gui.fig
            
            # Final validation using plot controller if available
            if hasattr(self.gui, 'plot_controller') and self.gui.plot_controller:
                if hasattr(self.gui.plot_controller, '_matplotlib_components_valid'):
                    if not self.gui.plot_controller._matplotlib_components_valid():
                        _LOGGER.debug("  🔧 Components still invalid after restoration - forcing reinit")
                        self.gui.plot_controller.init_matplotlib_plot()
                        return
            
            # Force a redraw to ensure everything is connected
            if hasattr(self.gui, 'canvas') and self.gui.canvas:
                self.gui.canvas.draw_idle()
            
            _LOGGER.info("  🔗 Matplotlib connections restored successfully")
            
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning restoring matplotlib connection: {e}")
            # If restore fails, try to force a complete reinit
            try:
                if hasattr(self.gui, 'plot_controller') and self.gui.plot_controller:
                    self.gui.plot_controller.init_matplotlib_plot()
            except Exception as reinit_error:
                _LOGGER.warning(f"  ⚠️ Matplotlib reinit also failed: {reinit_error}")
    
    def _reset_view_to_initial(self):
        """Reset view controller to initial view"""
        try:
            if hasattr(self.gui, 'view_controller') and self.gui.view_controller:
                self.gui.view_controller.reset_to_initial_view()
            
            # Reset view style variable: leave both options OFF
            if hasattr(self.gui, 'view_style'):
                self.gui.view_style.set("")
            
            _LOGGER.info("  👁️ View reset to initial state (no view selected)")
            
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning resetting view: {e}")
    
    def _reset_state_manager(self):
        """Reset state manager to initial state"""
        try:
            if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                self.gui.workflow_integrator.reset_workflow()
                _LOGGER.info("  🏠 Workflow integrator reset to initial state")
            else:
                _LOGGER.warning("  ⚠️ No workflow integrator available for reset")
        except Exception as e:
            _LOGGER.error(f"  ❌ Error resetting workflow integrator: {e}")
    
    def _reset_header_status(self):
        """Reset header status to initial message"""
        try:
            if hasattr(self.gui, 'update_header_status'):
                self.gui.update_header_status("🚀 Ready - Load a spectrum to begin analysis")
            elif hasattr(self.gui, 'header_status_label'):
                self.gui.header_status_label.config(text="🚀 Ready - Load a spectrum to begin analysis")
            
            # Also reset any file status labels to initial state
            if hasattr(self.gui, 'file_status_label'):
                if hasattr(self.gui, 'theme_manager'):
                    text_color = self.gui.theme_manager.get_color('text_secondary')
                else:
                    text_color = 'gray'
                self.gui.file_status_label.config(
                    text="No spectrum loaded",
                    fg=text_color
                )
            
            # Reset configuration status if it exists
            if hasattr(self.gui, 'config_status_label'):
                self.gui.config_status_label.config(text="📋 Default SNID parameters loaded")
            
            # Reset quick config label if it exists
            if hasattr(self.gui, 'quick_config_label'):
                self.gui.quick_config_label.config(text="z: -0.01 to 1.2 | Templates: 10")
            
            _LOGGER.info("  📋 Header and file status reset to initial message")
            
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning resetting header status: {e}")
    
    def _reset_gui_appearance_to_initial(self):
        """Reset GUI appearance elements to initial state"""
        try:
            # Clear any temporary overlays or highlights
            self._clear_temporary_ui_elements()

            # Theme helper – fallback to gray text if theme manager missing
            def _secondary_color():
                try:
                    return self.gui.theme_manager.get_color('text_secondary') if hasattr(self.gui, 'theme_manager') else 'gray'
                except Exception:
                    return 'gray'

            # 1. Configuration status (below Run Analysis)
            if hasattr(self.gui, 'config_status_label'):
                self.gui.config_status_label.config(text="📋 Default SNID parameters loaded", fg=_secondary_color())

            # 2. File / quick-config helpers (for forward-compatibility)
            if hasattr(self.gui, 'quick_config_label'):
                self.gui.quick_config_label.config(text="z: -0.01 to 1.2 | Templates: 10", fg=_secondary_color())

            # 3. Redshift status label (below Redshift Selection)
            if hasattr(self.gui, 'redshift_status_label'):
                self.gui.redshift_status_label.config(text="Optional: no redshift selected", fg=_secondary_color())

            # 4. Pre-processing status label (below Preprocess Spectrum)
            if hasattr(self.gui, 'preprocess_status_label'):
                self.gui.preprocess_status_label.config(text="Not preprocessed", fg=_secondary_color())

            # 5. Emission-line analysis status label
            if hasattr(self.gui, 'emission_status_label'):
                self.gui.emission_status_label.config(text="Not analyzed", fg=_secondary_color())

            
            if hasattr(self.gui, 'ai_status_label'):
                self.gui.ai_status_label.config(text="Configuration • Summary • Chat", fg=_secondary_color())

            _LOGGER.info("  🎨 GUI appearance reset to initial state – status labels restored")

        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning resetting GUI appearance: {e}")
    
    def _force_initial_button_states(self):
        """Force all buttons to initial state (only Browse enabled)"""
        try:
            _LOGGER.info("  🔘 Forcing button states to initial configuration")
            
            # Force workflow integrator to initial state if available
            if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                self.gui.workflow_integrator.reset_workflow()
                _LOGGER.info("  🏠 Workflow integrator forced to initial state")
            
            # Update button states through the workflow integrator system (PySide6 pattern)
            if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                self.gui.workflow_integrator._workflow_update_button_states()
                _LOGGER.info("  🔘 Button states updated via workflow integrator")
            else:
                # Fallback for older pattern
                if hasattr(self.gui, 'app_controller') and hasattr(self.gui.app_controller, 'update_button_states'):
                    self.gui.app_controller.update_button_states()
                elif hasattr(self.gui, 'update_button_states'):
                    self.gui.update_button_states()
                _LOGGER.info("  🔘 Button states updated via fallback method")
            
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning forcing button states: {e}")
    
    def _apply_theme_after_reset(self):
        """Theme is managed by the theme system"""
        try:
            if hasattr(self.gui, 'theme_manager'):
                _LOGGER.info("  🎨 Theme system is active")
            
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning in theme manager: {e}")
    
    def _show_reset_confirmation(self):
        """Show brief confirmation that reset was completed"""
        try:
            if hasattr(self.gui, 'update_header_status'):
                # Temporarily show reset confirmation
                self.gui.update_header_status("✅ GUI Reset Complete - Ready for new analysis")
                # Return to normal initial message after 3 seconds
                self.gui.master.after(3000, lambda: self.gui.update_header_status("🚀 Ready - Load a spectrum to begin analysis"))
            
        except Exception as e:
            _LOGGER.warning(f"  ⚠️ Warning showing reset confirmation: {e}") 
