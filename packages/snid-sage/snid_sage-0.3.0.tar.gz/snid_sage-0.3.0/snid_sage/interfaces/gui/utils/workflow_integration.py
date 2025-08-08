"""
SNID SAGE - Workflow Integration
Script to integrate the improved button workflow system with the existing GUI.
"""

import tkinter as tk
from typing import TYPE_CHECKING
import logging

# Import the new workflow system
from .improved_button_workflow import ImprovedButtonWorkflow, WorkflowState

# Import centralized logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.workflow_integration')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.workflow_integration')

if TYPE_CHECKING:
    from snid_sage.interfaces.gui.sage_gui import SageGUI

class WorkflowIntegrator:
    """Integrates the improved workflow system with the existing GUI"""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.workflow = ImprovedButtonWorkflow(gui_instance)
        self._setup_integration()
        
        _LOGGER.info("🔄 Workflow integration initialized")
    
    def _setup_integration(self):
        """Set up the integration with existing GUI components"""
        # Replace the old update_button_states method
        self._replace_button_state_methods()
        
        # Register existing buttons
        self._register_existing_buttons()
        
        # Set up workflow state change handlers
        self._setup_state_handlers()
    
    def _replace_button_state_methods(self):
        """Replace old button state update methods with workflow calls"""
        # Store original methods for fallback
        if hasattr(self.gui, 'update_button_states'):
            self.gui._original_update_button_states = self.gui.update_button_states
        
        if hasattr(self.gui, 'app_controller') and hasattr(self.gui.app_controller, 'update_button_states'):
            self.gui.app_controller._original_update_button_states = self.gui.app_controller.update_button_states
        
        # Replace with workflow-based methods
        self.gui.update_button_states = self._workflow_update_button_states
        
        if hasattr(self.gui, 'app_controller'):
            self.gui.app_controller.update_button_states = self._workflow_update_button_states
    
    def _register_existing_buttons(self):
        """Register all existing buttons with the workflow system"""
        button_mappings = {
            'load_btn': 'load_btn',
            'preprocess_btn': 'preprocess_btn',
            'redshift_selection_btn': 'redshift_selection_btn',
            'analysis_btn': 'analysis_btn',
            'emission_line_overlay_btn': 'emission_line_overlay_btn',
            'configure_llm_btn': 'configure_llm_btn',
            'summarize_llm_btn': 'summarize_llm_btn',
            'chat_llm_btn': 'chat_llm_btn',
            'reset_btn': 'reset_btn',
            'settings_btn': 'settings_btn',
            # Additional analysis buttons
            'cluster_summary_btn': 'cluster_summary_btn',
            'gmm_btn': 'gmm_btn',
            'redshift_age_btn': 'redshift_age_btn',
            'subtype_proportions_btn': 'subtype_proportions_btn',
            
            'ai_assistant_btn': 'ai_assistant_btn'
        }
        
        registered_count = 0
        missing_count = 0
        
        for gui_attr, workflow_name in button_mappings.items():
            if hasattr(self.gui, gui_attr):
                button = getattr(self.gui, gui_attr)
                if button and isinstance(button, tk.Button):
                    # Ensure the button has the proper workflow attributes
                    button._workflow_managed = True
                    button._workflow_button_name = workflow_name
                    
                    # Register with workflow system
                    self.workflow.register_button(workflow_name, button)
                    registered_count += 1
                    _LOGGER.debug(f"✅ Registered existing button: {workflow_name}")
                else:
                    missing_count += 1
                    _LOGGER.debug(f"⏳ Button {workflow_name} not ready yet (will be registered when created)")
            else:
                missing_count += 1
                _LOGGER.debug(f"⏳ Button {workflow_name} not found yet (will be registered when created)")
        
        _LOGGER.info(f"✅ Registered {registered_count} existing buttons with workflow system")
        if missing_count > 0:
            _LOGGER.debug(f"⏳ {missing_count} buttons will be registered when they are created")
    
    def _setup_state_handlers(self):
        """Set up handlers for state changes"""
        # Add callback to update header status when workflow state changes
        self.workflow.add_state_change_callback(self._on_workflow_state_change)
        

    
    def _workflow_update_button_states(self):
        """New button state update method using workflow system with enhanced macOS handling"""
        try:
            # Only update workflow button states, not global theme/colors
            # This prevents the blue button color override issue
            
            # Determine current state based on GUI state
            gui_detected_state = self._determine_current_gui_state()
            current_workflow_state = self.workflow.get_current_state()
            
            # Only update state if GUI state indicates progression, not regression
            # This prevents overriding manually set states during transitions
            state_order = [
                WorkflowState.INITIAL,
                WorkflowState.FILE_LOADED,
                WorkflowState.PREPROCESSED,
                WorkflowState.REDSHIFT_SET,
                WorkflowState.ANALYSIS_COMPLETE,
                WorkflowState.AI_READY
            ]
            
            current_index = state_order.index(current_workflow_state)
            detected_index = state_order.index(gui_detected_state)
            
            # Store previous state for macOS color correction
            previous_state = current_workflow_state
            
            # Only update workflow state if detected state is higher than current state
            # This prevents regression during file loading process
            if detected_index > current_index:
                # Only update workflow-managed buttons, not all GUI elements
                self.workflow.update_workflow_state(gui_detected_state)
                _LOGGER.debug(f"🔄 Workflow state progressed: {current_workflow_state.value} → {gui_detected_state.value}")
                
                # Enhanced macOS handling: Ensure colors stick after state changes
                self._apply_macos_color_fixes_after_state_change(previous_state, gui_detected_state)
                
            elif detected_index < current_index:
                # Only allow regression if we've completely lost data (e.g., reset)
                if gui_detected_state == WorkflowState.INITIAL and not self._has_any_data():
                    self.workflow.update_workflow_state(gui_detected_state)
                    _LOGGER.debug(f"🔄 Workflow state reset: {current_workflow_state.value} → {gui_detected_state.value}")
                    
                    # Enhanced macOS handling for reset state
                    self._apply_macos_color_fixes_after_state_change(previous_state, gui_detected_state)
                    
                else:
                    _LOGGER.debug(f"🔒 Preventing workflow regression: {current_workflow_state.value} (keeping current state)")
            
            # Update AI configuration status
            ai_configured = self._is_ai_configured()
            if ai_configured != self.workflow.ai_configured:
                self.workflow.set_ai_configured(ai_configured)
            
            # Additional macOS-specific: Force color reapplication periodically
            self._schedule_macos_color_maintenance()
            
            _LOGGER.debug(f"🔄 Enhanced workflow-based button state update completed")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error in workflow button state update: {e}")
            # Fallback to original method if available
            if hasattr(self.gui, '_original_update_button_states'):
                try:
                    self.gui._original_update_button_states()
                except:
                    pass
    
    def _apply_macos_color_fixes_after_state_change(self, previous_state: WorkflowState, new_state: WorkflowState):
        """Apply macOS-specific color fixes after workflow state changes"""
        try:
            from snid_sage.shared.utils.config.platform_config import get_platform_config
            platform_config = get_platform_config()
            
            if not platform_config or not platform_config.is_macos:
                return  # Only apply on macOS
            
            _LOGGER.debug(f"🎨 Applying macOS color fixes for state change: {previous_state.value} → {new_state.value}")
            
            # Get all workflow-managed buttons
            workflow_buttons = getattr(self.workflow, 'button_widgets', {})
            
            for button_name, button_widget in workflow_buttons.items():
                try:
                    if button_widget and button_widget.winfo_exists():
                        # Force color reapplication with macOS-specific techniques
                        self._force_macos_button_color_reapplication(button_widget, button_name)
                        
                except Exception as button_error:
                    _LOGGER.debug(f"Color fix failed for button {button_name}: {button_error}")
                    
            # Schedule delayed color verification
            if hasattr(self.gui, 'master'):
                self.gui.master.after(100, lambda: self._verify_macos_button_colors())
                
        except Exception as e:
            _LOGGER.debug(f"macOS color fixes failed: {e}")
    
    def _force_macos_button_color_reapplication(self, button_widget, button_name: str):
        """Force color reapplication for a specific button on macOS"""
        try:
            # Get the expected color for this button based on its current state
            button_definitions = getattr(self.workflow, 'BUTTON_DEFINITIONS', {})
            if button_name not in button_definitions:
                return
                
            definition = button_definitions[button_name]
            should_be_enabled = self.workflow._should_button_be_enabled(definition)
            
            if should_be_enabled:
                expected_color = definition.enabled_color
            else:
                from snid_sage.interfaces.gui.utils.improved_button_workflow import ButtonColors
                expected_color = ButtonColors.LIGHT_GREY
            
            # Get current color to check if reapplication is needed
            try:
                current_bg = button_widget.cget('bg')
                if current_bg != expected_color:
                    _LOGGER.debug(f"🔧 macOS color mismatch detected for {button_name}: {current_bg} != {expected_color}")
                    
                    # Apply multiple macOS color setting techniques
                    button_widget.configure(bg=expected_color)
                    button_widget.configure(background=expected_color)
                    button_widget.configure(highlightbackground=expected_color)
                    
                    # Force update
                    button_widget.update_idletasks()
                    
                    # Schedule another verification
                    button_widget.after(50, lambda: self._verify_single_button_color(button_widget, button_name, expected_color))
                    
            except Exception as color_check_error:
                _LOGGER.debug(f"Color check failed for {button_name}: {color_check_error}")
                
        except Exception as e:
            _LOGGER.debug(f"Force color reapplication failed for {button_name}: {e}")
    
    def _verify_single_button_color(self, button_widget, button_name: str, expected_color: str):
        """Verify a single button has the correct color"""
        try:
            if button_widget and button_widget.winfo_exists():
                current_bg = button_widget.cget('bg')
                if current_bg != expected_color:
                    _LOGGER.debug(f"⚠️ macOS button {button_name} color still incorrect after fix: {current_bg} != {expected_color}")
                    # One more attempt
                    button_widget.configure(bg=expected_color, highlightbackground=expected_color)
                else:
                    _LOGGER.debug(f"✅ macOS button {button_name} color verified: {current_bg}")
        except:
            pass
    
    def _schedule_macos_color_maintenance(self):
        """Schedule periodic color maintenance for macOS"""
        try:
            from snid_sage.shared.utils.config.platform_config import get_platform_config
            platform_config = get_platform_config()
            
            if not platform_config or not platform_config.is_macos:
                return
            
            # Only schedule if not already scheduled
            if not hasattr(self, '_macos_maintenance_scheduled') or not self._macos_maintenance_scheduled:
                self._macos_maintenance_scheduled = True
                
                def periodic_color_check():
                    try:
                        self._verify_macos_button_colors()
                        # Reschedule for next check
                        if hasattr(self.gui, 'master'):
                            self.gui.master.after(5000, periodic_color_check)  # Every 5 seconds
                    except:
                        self._macos_maintenance_scheduled = False
                
                if hasattr(self.gui, 'master'):
                    self.gui.master.after(2000, periodic_color_check)  # First check after 2 seconds
                    
        except Exception as e:
            _LOGGER.debug(f"macOS color maintenance scheduling failed: {e}")
    
    def _verify_macos_button_colors(self):
        """Verify all button colors are correct on macOS"""
        try:
            from snid_sage.shared.utils.config.platform_config import get_platform_config
            platform_config = get_platform_config()
            
            if not platform_config or not platform_config.is_macos:
                return
            
            workflow_buttons = getattr(self.workflow, 'button_widgets', {})
            button_definitions = getattr(self.workflow, 'BUTTON_DEFINITIONS', {})
            
            incorrect_buttons = []
            
            for button_name, button_widget in workflow_buttons.items():
                try:
                    if button_widget and button_widget.winfo_exists() and button_name in button_definitions:
                        definition = button_definitions[button_name]
                        should_be_enabled = self.workflow._should_button_be_enabled(definition)
                        
                        if should_be_enabled:
                            expected_color = definition.enabled_color
                        else:
                            from snid_sage.interfaces.gui.utils.improved_button_workflow import ButtonColors
                            expected_color = ButtonColors.LIGHT_GREY
                        
                        current_bg = button_widget.cget('bg')
                        if current_bg != expected_color:
                            incorrect_buttons.append((button_name, current_bg, expected_color))
                            
                except Exception as button_check_error:
                    _LOGGER.debug(f"Button color verification failed for {button_name}: {button_check_error}")
            
            if incorrect_buttons:
                _LOGGER.debug(f"🔧 macOS button color corrections needed: {len(incorrect_buttons)} buttons")
                for button_name, current, expected in incorrect_buttons:
                    button_widget = workflow_buttons[button_name]
                    self._force_macos_button_color_reapplication(button_widget, button_name)
            else:
                _LOGGER.debug("✅ All macOS button colors verified correct")
                
        except Exception as e:
            _LOGGER.debug(f"macOS button color verification failed: {e}")
    
    def _determine_current_gui_state(self) -> WorkflowState:
        """Determine the current workflow state based on GUI state"""
        # Check if analysis is complete
        if hasattr(self.gui, 'snid_results') and self.gui.snid_results:
            return WorkflowState.ANALYSIS_COMPLETE
        
        # Check if redshift is set
        if hasattr(self.gui, 'galaxy_redshift_result') and self.gui.galaxy_redshift_result is not None:
            return WorkflowState.REDSHIFT_SET
        
        # Check if spectrum is preprocessed
        if hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum is not None:
            return WorkflowState.PREPROCESSED
        
        # Check if file is loaded - FIXED: Use file_path and has_spectrum_loaded instead of current_spectrum
        if (hasattr(self.gui, 'file_path') and self.gui.file_path and 
            hasattr(self.gui, 'has_spectrum_loaded') and self.gui.has_spectrum_loaded()):
            return WorkflowState.FILE_LOADED
        
        # Default to initial state
        return WorkflowState.INITIAL
    
    def _is_ai_configured(self) -> bool:
        """Check if AI is configured and available"""
        try:
            if hasattr(self.gui, 'llm_integration'):
                return (self.gui.llm_integration is not None and 
                       getattr(self.gui.llm_integration, 'llm_available', False))
            return False
        except:
            return False
    
    def _on_workflow_state_change(self, new_state: WorkflowState):
        """Handle workflow state changes"""
        try:
            # Update header status
            if hasattr(self.gui, 'update_header_status'):
                status_messages = {
                    WorkflowState.INITIAL: "Ready - Load a spectrum to begin analysis",
                    WorkflowState.FILE_LOADED: "📂 Spectrum loaded - Ready for preprocessing",
                    WorkflowState.PREPROCESSED: "🔧 Preprocessing complete - Determine redshift or continue with analysis",
                    WorkflowState.REDSHIFT_SET: "🌌 Redshift set - Ready for SNID analysis",
                    WorkflowState.ANALYSIS_COMPLETE: "✅ Analysis complete - Advanced features available",
                    WorkflowState.AI_READY: "🤖 AI ready - All features available"
                }
                
                if new_state in status_messages:
                    self.gui.update_header_status(status_messages[new_state])
            
            _LOGGER.info(f"📋 Workflow state changed to: {new_state.value}")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error handling workflow state change: {e}")
    
    # Public interface methods
    def set_file_loaded(self):
        """Manually trigger file loaded state"""
        self.workflow.update_workflow_state(WorkflowState.FILE_LOADED)
    
    def set_preprocessed(self):
        """Manually trigger preprocessed state"""
        self.workflow.update_workflow_state(WorkflowState.PREPROCESSED)
    
    def set_redshift_determined(self):
        """Manually trigger redshift determined state"""
        self.workflow.update_workflow_state(WorkflowState.REDSHIFT_SET)
    
    def set_analysis_complete(self):
        """Manually trigger analysis complete state"""
        self.workflow.update_workflow_state(WorkflowState.ANALYSIS_COMPLETE)
    
    def set_ai_configured(self, configured: bool):
        """Manually set AI configuration status"""
        self.workflow.set_ai_configured(configured)
    
    def reset_workflow(self):
        """Reset workflow to initial state"""
        self.workflow.reset_to_initial_state()
    
    def get_current_state(self) -> WorkflowState:
        """Get current workflow state"""
        return self.workflow.get_current_state()

    def _has_any_data(self) -> bool:
        """Check if GUI has any data loaded"""
        return (
            (hasattr(self.gui, 'file_path') and self.gui.file_path) or
            (hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum) or
            (hasattr(self.gui, 'snid_results') and self.gui.snid_results)
        )

    def register_button_if_needed(self, button_name: str, button_widget: tk.Button):
        """Register a button with the workflow system if it hasn't been registered yet"""
        try:
            # Check if button is already registered
            if button_name in self.workflow.button_widgets:
                return
            
            # Ensure the button has the proper workflow attributes
            button_widget._workflow_managed = True
            button_widget._workflow_button_name = button_name
            
            # Register with workflow system
            self.workflow.register_button(button_name, button_widget)
            _LOGGER.debug(f"✅ Late-registered button: {button_name}")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error registering button {button_name}: {e}")

def integrate_workflow_with_gui(gui_instance) -> WorkflowIntegrator:
    """
    Main integration function to set up the improved workflow system.
    Call this from the GUI initialization.
    """
    try:
        integrator = WorkflowIntegrator(gui_instance)
        
        # Store integrator in GUI for access
        gui_instance.workflow_integrator = integrator
        
        _LOGGER.info("🎯 Workflow integration complete - Enhanced button management active")
        return integrator
        
    except Exception as e:
        _LOGGER.error(f"❌ Failed to integrate workflow system: {e}")
        # Return None to indicate failure
        return None 
