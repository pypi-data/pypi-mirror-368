"""
Application State Manager for SNID SAGE GUI
==========================================

Manages the application workflow state and tracks progression through
the analysis pipeline to provide appropriate button states and user guidance.
"""

import tkinter as tk
import os
from enum import Enum
from typing import Optional, Dict, Any, List

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.state')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.state')


class ApplicationState(Enum):
    """Progressive workflow states for button management"""
    INITIAL = "initial"           # Only input spectrum enabled
    SPECTRUM_LOADED = "loaded"    # Galaxy/preprocessing enabled
    PREPROCESSED = "preprocessed" # SNID configuration/analysis enabled  
    ANALYSIS_COMPLETE = "analyzed" # Navigation/plots/tools enabled
    AI_READY = "ai_ready"         # AI features enabled


class StateManager:
    """Manager for application state and variables"""
    
    def __init__(self, gui_instance):
        """Initialize state manager"""
        self.gui = gui_instance
        self.current_app_state = ApplicationState.INITIAL
    
    def track_application_state(self):
        """Determine current application state based on data availability"""
        try:
            # Check current data state
            file_path_exists = bool(self.gui.file_path)
            has_spectrum = self.gui.has_spectrum_loaded() if hasattr(self.gui, 'has_spectrum_loaded') else False
            has_processed = hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum is not None
            has_results = hasattr(self.gui, 'snid_results') and self.gui.snid_results is not None
            
            # Check if file is loaded - use has_spectrum_loaded() method instead of checking original_wave
            
            if not self.gui.file_path or not self.gui.has_spectrum_loaded():
                new_state = ApplicationState.INITIAL
            
            # Check if preprocessing is complete
            elif not (hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum is not None):
                new_state = ApplicationState.SPECTRUM_LOADED
            
            # Check if SNID analysis is complete
            elif not (hasattr(self.gui, 'snid_results') and self.gui.snid_results is not None):
                new_state = ApplicationState.PREPROCESSED
            
            # Check if AI is configured and available
            elif not self._is_ai_available():
                new_state = ApplicationState.ANALYSIS_COMPLETE
            
            # Everything is ready
            else:
                new_state = ApplicationState.AI_READY
            
            # Update state if changed
            if new_state != self.current_app_state:
                old_state = self.current_app_state
                self.current_app_state = new_state
                _LOGGER.info(f"🔄 Application state changed: {old_state.value} → {new_state.value}")
                _LOGGER.info(f"🔍 Data state: file={file_path_exists}, spectrum={has_spectrum}, processed={has_processed}, results={has_results}")
                
                # Update workflow status message
                self.update_workflow_status(new_state)
                
                # Trigger button state update
                if hasattr(self.gui, 'app_controller'):
                    self.gui.app_controller.update_button_states()
                else:
                    _LOGGER.warning(f"⚠️ No app_controller found for button state updates!")
            
            return self.current_app_state
            
        except Exception as e:
            _LOGGER.error(f"❌ Error tracking application state: {e}")
            import traceback
            _LOGGER.error(f"❌ Traceback: {traceback.format_exc()}")
            return ApplicationState.INITIAL
    
    def _is_ai_available(self):
        """Check if AI features are configured and available"""
        try:
            # Check if LLM integration exists and is configured
            if hasattr(self.gui, 'llm_integration') and self.gui.llm_integration:
                return self.gui.llm_integration.llm_available
            return False
        except Exception:
            return False
    
    def update_workflow_status(self, state):
        """Update header status with current workflow step"""
        try:
            status_messages = {
                ApplicationState.INITIAL: "Ready - Load a spectrum to begin analysis",
                ApplicationState.SPECTRUM_LOADED: "📊 Spectrum loaded - Configure galaxy properties and preprocessing",  
                ApplicationState.PREPROCESSED: "⚙️ Preprocessing complete - Configure SNID parameters and run analysis",
                ApplicationState.ANALYSIS_COMPLETE: "✅ Analysis complete - Explore results and run additional tools",
                ApplicationState.AI_READY: "🤖 AI features ready - Generate summaries and chat with AI"
            }
            
            message = status_messages.get(state, "🔧 Processing...")
            
            if hasattr(self.gui, 'header_status_label'):
                self.gui.header_status_label.config(text=message)
                
            _LOGGER.info(f"📋 Workflow status: {message}")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error updating workflow status: {e}")
    
    def get_state_button_groups(self):
        """Get button groups for different workflow states"""
        return {
            'always_enabled': [
                'load_btn',              # Always allow loading new files
                'configure_llm_btn',     # Always allow LLM configuration
                'reset_btn'              # Always allow GUI reset
            ],
            'spectrum_loaded': [
                'redshift_selection_btn', # Combined redshift selection
                'preprocess_btn'         # Preprocessing options
            ],
            'preprocessed': [
                            'analysis_btn'           # Combined SNID analysis (replaces options_btn and analyze_btn)
            ],
            'analysis_complete': [
                'prev_btn',              # Template navigation
                'next_btn',              # Template navigation
                'emission_line_overlay_btn'  # SN emission line overlay
        
                # as these buttons don't exist in the current GUI layout
            ],
            'ai_ready': [
                'summarize_llm_btn',     # AI summary generation
                'chat_llm_btn'           # AI chat interface
            ]
        }
    
    def force_state_transition(self, target_state):
        """Force transition to a specific state (for testing/debugging)"""
        try:
            old_state = self.current_app_state
            self.current_app_state = target_state
            _LOGGER.info(f"🔧 Forced state transition: {old_state.value} → {target_state.value}")
            
            self.update_workflow_status(target_state)
            
            if hasattr(self.gui, 'app_controller'):
                self.gui.app_controller.update_button_states()
                
        except Exception as e:
            _LOGGER.error(f"❌ Error forcing state transition: {e}")
    
    def init_variables(self):
        """Initialize application state variables"""
        try:
            # Core application state
            self.gui.file_path = ""
            self.gui.current_template = 0
            self.gui.current_view = ''  # No view selected initially
            self.gui.is_masking_active = False
            
            # Data storage
            self.gui.original_wave = None
            self.gui.original_flux = None
            self.gui.processed_spectrum = None
            self.gui.snid_results = None
            self.gui.galaxy_redshift_result = None
            
            # Mask management
            self.gui.mask_regions = []  # List of (start, end) wavelength tuples for masking
            
            # UI state variables
            self.gui.view_style = tk.StringVar(value="")
            
            # Analysis options and parameters
            self.gui.params = self._get_default_parameters()
            
            # Matplotlib components (will be initialized later)
            self.gui.fig = None
            self.gui.ax = None
            self.gui.canvas = None
            
            # Component references (will be initialized later)
            self.gui.preprocessor = None
            self.gui.mask_manager_dialog = None
            self.gui.interactive_tools = None  # Will be initialized when plot is ready
            
            # Track toggle states
            self.gui.toggle_states = {}
            
            # Line markers for plot
            self.gui.line_markers = []
            
            _LOGGER.info("✅ Application variables initialized")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error initializing variables: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_default_parameters(self):
        """Get default SNID analysis parameters"""
        return {
            # Basic analysis parameters
            'zmin': '-0.01',
            'zmax': '1.0',
            'rlapmin': '3.0',
            'lapmin': '0.5',
    
            'max_output_templates': '5',
            
            # Preprocessing parameters
            'median_fwmed': '',
            'medlen': '1',
            'aband_remove': '',
            'skyclip': '',
            'emclip_z': '-1.0',
            'emwidth': '40.0',
            'apodize_percent': '10.0',
            'wavelength_masks': '',
            
            # Advanced options
            'type_filter': '',
            'age_min': '',
            'age_max': '',
            'verbose': 'True',
            'show_plots': 'True',
            'save_plots': 'False',
        'save_summary': 'False',
            
            # LLM options
            'llm_provider': 'openrouter',
            'llm_model': 'anthropic/claude-3.5-sonnet',
            'llm_enabled': 'False'
        }
    
    def init_llm(self):
        """Initialize LLM settings"""
        try:
            # Initialize GUI-specific LLM integration
            from snid_sage.interfaces.gui.features.results.llm_integration import LLMIntegration
            
            self.gui.llm_integration = LLMIntegration(self.gui)
            
            # LLM configuration variables for compatibility
            self.gui.llm_enabled = tk.BooleanVar(value=self.gui.llm_integration.llm_available)
            self.gui.llm_provider = tk.StringVar(value="openrouter")
            # Get model from llm_config instead of current_model attribute
            current_model = self.gui.llm_integration.llm_config.get('model_id') if self.gui.llm_integration.llm_config else None
            # Default display model to a known free variant to avoid accidental paid fallbacks
            self.gui.llm_model = tk.StringVar(value=current_model or "deepseek/deepseek-chat-v3-0324:free")
            
            # Try to load optional LLM features
            optional_features = self._import_optional_features()
            self.gui.optional_features = optional_features
            
            _LOGGER.info("✅ LLM integration initialized")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error initializing LLM: {e}")
            # Create fallback LLM integration
            self.gui.llm_integration = None
    
    def _import_optional_features(self):
        """Import optional features that might not be available"""
        optional_features = {}
        
        try:
            from snid_sage.shared.utils.line_detection.spectrum_utils import plot_spectrum, apply_savgol_filter
            optional_features['spectrum_utils'] = True
        except ImportError:
            optional_features['spectrum_utils'] = False
        
        try:
            from snid_sage.interfaces.llm.openrouter.openrouter_llm import get_openrouter_config
            optional_features['openrouter'] = True
            optional_features['openrouter_config'] = get_openrouter_config()
        except ImportError:
            optional_features['openrouter'] = False
            optional_features['openrouter_config'] = {}
        
        # Local LLM support removed - using OpenRouter only
        optional_features['llama'] = False
        
        return optional_features
    
    def reset_state(self):
        """Reset application state to initial values"""
        try:
            # Reset core state
            self.gui.file_path = ""
            self.gui.current_template = 0
            self.gui.current_view = ''  # No view selected
            self.gui.is_masking_active = False
            
            # Clear data
            self.gui.original_wave = None
            self.gui.original_flux = None
            self.gui.processed_spectrum = None
            self.gui.snid_results = None
            self.gui.galaxy_redshift_result = None
            
            # Clear mask regions
            if hasattr(self.gui, 'mask_regions'):
                self.gui.mask_regions.clear()
            
            # Reset UI variables: no view selected
            self.gui.view_style.set("")
            
            # Clear line markers
            if hasattr(self.gui, 'line_markers'):
                self.gui.line_markers.clear()
            
            # Clear plot if exists
            if hasattr(self.gui, 'ax') and self.gui.ax:
                self.gui.ax.clear()
                if hasattr(self.gui, 'canvas') and self.gui.canvas:
                    self.gui.canvas.draw()
            
            # Reset to initial state and update buttons
            self.current_app_state = ApplicationState.INITIAL
            self.update_workflow_status(ApplicationState.INITIAL)
            
            if hasattr(self.gui, 'app_controller'):
                self.gui.app_controller.update_button_states()
            
            _LOGGER.info("✅ Application state reset to INITIAL")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error resetting state: {e}")
    
    def force_state_refresh(self):
        """Force a refresh of the current application state"""
        try:
            old_state = self.current_app_state
            self.current_app_state = ApplicationState.INITIAL  # Reset to initial
            new_state = self.track_application_state()  # Re-evaluate
            _LOGGER.info(f"🔄 Forced state refresh: {old_state.value} → {new_state.value}")
        except Exception as e:
            _LOGGER.error(f"❌ Error forcing state refresh: {e}")
    
    def reset_to_initial_state(self):
        """
        Reset state manager completely to initial state
        
        This method resets all variables and state to how they were when
        the application first started, effectively bringing the GUI back
        to its initial condition.
        """
        try:
            _LOGGER.info("🔄 Resetting state manager to initial state...")
            
            # Reset current state
            self.current_app_state = ApplicationState.INITIAL
            
            # Reinitialize all variables to initial state
            self.init_variables()
            
            # Update workflow status
            self.update_workflow_status(ApplicationState.INITIAL)
            
            _LOGGER.info("✅ State manager reset to initial state completed")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error resetting state manager to initial state: {e}")
    
    def save_state(self, filepath):
        """Save current application state to file"""
        try:
            import json
            
            state_data = {
                'file_path': self.gui.file_path,
                'current_template': self.gui.current_template,
                'current_view': self.gui.current_view,
                'view_style': self.gui.view_style.get(),
                'params': self.gui.params.copy(),
                'mask_regions': getattr(self.gui, 'mask_regions', []),  # Save mask regions
                'llm_enabled': self.gui.llm_enabled.get() if hasattr(self.gui, 'llm_enabled') else False,
                'llm_provider': self.gui.llm_provider.get() if hasattr(self.gui, 'llm_provider') else "openrouter",
                'llm_model': self.gui.llm_model.get() if hasattr(self.gui, 'llm_model') else "anthropic/claude-3.5-sonnet"
            }
            
            with open(filepath, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            _LOGGER.info(f"✅ State saved to {filepath}")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error saving state: {e}")
    
    def load_state(self, filepath):
        """Load application state from file"""
        try:
            import json
            
            if not os.path.exists(filepath):
                _LOGGER.warning(f"⚠️ State file not found: {filepath}")
                return False
            
            with open(filepath, 'r') as f:
                state_data = json.load(f)
            
            # Restore core state
            self.gui.file_path = state_data.get('file_path', "")
            self.gui.current_template = state_data.get('current_template', 0)
            self.gui.current_view = state_data.get('current_view', '')
            
            # Restore mask regions
            self.gui.mask_regions = state_data.get('mask_regions', [])
            
            # Restore UI state
            if hasattr(self.gui, 'view_style'):
                self.gui.view_style.set(state_data.get('view_style', "Flux"))
            
            # Restore parameters
            saved_params = state_data.get('params', {})
            self.gui.params.update(saved_params)
            
            # Restore LLM settings
            if hasattr(self.gui, 'llm_enabled'):
                self.gui.llm_enabled.set(state_data.get('llm_enabled', False))
            if hasattr(self.gui, 'llm_provider'):
                self.gui.llm_provider.set(state_data.get('llm_provider', "openrouter"))
            if hasattr(self.gui, 'llm_model'):
                self.gui.llm_model.set(state_data.get('llm_model', "anthropic/claude-3.5-sonnet"))
            
            _LOGGER.info(f"✅ State loaded from {filepath}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"❌ Error loading state: {e}")
            return False
    
    def get_current_state_summary(self):
        """Get a summary of current application state"""
        try:
            summary = {
                'file_loaded': bool(self.gui.file_path),
                'file_path': self.gui.file_path,
                'has_original_data': self.gui.original_wave is not None and self.gui.original_flux is not None,
                'has_processed_data': self.gui.processed_spectrum is not None,
                'has_snid_results': self.gui.snid_results is not None,
                'current_template': self.gui.current_template,
                'current_view': self.gui.current_view,
                'view_style': self.gui.view_style.get(),
                'num_line_markers': len(self.gui.line_markers) if hasattr(self.gui, 'line_markers') else 0
            }
            
            return summary
            
        except Exception as e:
            _LOGGER.error(f"❌ Error getting state summary: {e}")
            return {}
    
    def update_header_status(self, message):
        """Update header status message"""
        try:
            if hasattr(self.gui, 'header_status_label') and self.gui.header_status_label:
                self.gui.header_status_label.configure(text=message)
                self.gui.master.update_idletasks()
                _LOGGER.info(f"📢 Status: {message}")
        except Exception as e:
            _LOGGER.error(f"❌ Error updating header status: {e}")
    
    def cleanup(self):
        """Clean up state manager resources"""
        try:
            # Clear data references
            self.gui.original_wave = None
            self.gui.original_flux = None
            self.gui.processed_spectrum = None
            self.gui.snid_results = None
            self.gui.galaxy_redshift_result = None
            
            # Clear line markers
            if hasattr(self.gui, 'line_markers'):
                self.gui.line_markers.clear()
            
            _LOGGER.info("✅ State manager cleanup completed")
            
        except Exception as e:
            _LOGGER.warning(f"⚠️ Error during state manager cleanup: {e}") 
