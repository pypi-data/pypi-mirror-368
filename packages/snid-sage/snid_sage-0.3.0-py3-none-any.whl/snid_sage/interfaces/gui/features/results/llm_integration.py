"""
LLM Integration Feature

Handles LLM-related functionality including:
- OpenRouter backend configuration
- AI summarization of SNID results
- Chat interface with LLM
- Results formatting for LLM processing
- AI summary window display

Simplified version with only OpenRouter support and single summary type.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import json
import os
from datetime import datetime

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.llm')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.llm')


class LLMIntegration:
    """Handles LLM integration for AI-powered analysis features"""
    
    def __init__(self, gui_instance):
        """Initialize LLM integration with reference to main GUI"""
        self.gui = gui_instance
        self.llm_available = False
        self.llm_config = {}
        
        # Initialize LLM on startup
        self.init_llm()
    
    def init_llm(self):
        """Initialize OpenRouter LLM backend"""
        try:
            # Try to import and initialize OpenRouter backend
            self._check_openrouter_availability()
            
            if self.llm_available:
                self._update_llm_status("OpenRouter backend configured and ready")
            else:
                self._update_llm_status("Configure OpenRouter to enable AI features")
                
        except Exception as e:
            _LOGGER.error(f"⚠️ Error initializing LLM: {e}")
            self.llm_available = False
            self._update_llm_status("Configure OpenRouter to enable AI features")
        
        return self.llm_available
    
    def _check_openrouter_availability(self):
        """Check if OpenRouter LLM is available"""
        try:
            from snid_sage.interfaces.llm.openrouter.openrouter_llm import get_openrouter_config
            config = get_openrouter_config()
            if config and config.get('api_key'):
                self.llm_config = config
                self.llm_available = True
                _LOGGER.info("✅ OpenRouter LLM backend available")
            else:
                _LOGGER.info("💡 OpenRouter API not configured - AI features will be disabled until configured")
        except ImportError:
            _LOGGER.info("💡 OpenRouter LLM module not available - AI features disabled")
        except Exception as e:
            _LOGGER.warning(f"⚠️ Error checking OpenRouter: {e}")
    
    def _update_llm_status(self, status_text):
        """Update LLM status label"""
        if hasattr(self.gui, 'llm_status_label'):
            self.gui.llm_status_label.config(text=status_text)
    
    def update_llm_button_states(self):
        """Update workflow button states after LLM configuration change"""
        try:
            # Inform the workflow integrator so it can transition to AI_READY
            if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                self.gui.workflow_integrator._workflow_update_button_states()
            
            _LOGGER.debug(
                "🤖 Workflow refresh requested after LLM configuration change "
                f"(available={self.llm_available})"
            )
        except Exception as e:
            _LOGGER.error(f"Error updating workflow after LLM state change: {e}")
    
    def generate_summary(self, user_metadata=None, *, max_tokens: int = 3000, temperature: float = 0.7):
        """Generate AI summary with user metadata"""
        if not self.llm_available:
            raise Exception("OpenRouter backend is not configured")
        
        if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results:
            raise Exception("No SNID analysis results available")
        
        # Format results for LLM with enhanced context including user metadata
        formatted_results = self.format_snid_results_for_llm(user_metadata)
        
        # Pass the token / temperature settings forward
        return self._generate_openrouter_summary(
            formatted_results,
            user_metadata,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def _generate_openrouter_summary(self, formatted_results, user_metadata, *, max_tokens: int = 3000, temperature: float = 0.7):
        """Generate summary using OpenRouter"""
        try:
            from snid_sage.interfaces.llm.openrouter.openrouter_summary import EnhancedOpenRouterSummary
            
            # Use configured model or fallback to default
            model_id = self.llm_config.get('model_id') or 'openai/gpt-3.5-turbo'

            openrouter_summary = EnhancedOpenRouterSummary(
                api_key=self.llm_config.get('api_key'),
                model_id=model_id
            )
            
            # Extract specific request from user metadata as custom instructions
            custom_instructions = ""
            if user_metadata and user_metadata.get('specific_request'):
                custom_instructions = user_metadata['specific_request']
            
            # Add mandatory guidelines if not already present
            guidance_lines = [
                "Please respond in English.",
                "Do NOT introduce information that is not explicitly present in the provided context.",
                "Avoid converting or inferring new physical quantities (e.g., distances in Mpc) unless that exact number and unit are present in the input." 
            ]

            for line in guidance_lines:
                if line.lower() not in custom_instructions.lower():
                    custom_instructions += ("\n" if custom_instructions else "") + line
            
            # Generate summary with custom instructions
            summary_text, error_message, metadata = openrouter_summary.generate_summary(
                formatted_results,
                custom_instructions=custom_instructions,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if error_message:
                raise Exception(error_message)
            
            return summary_text, metadata
            
        except Exception as e:
            raise Exception(f"OpenRouter summary generation failed: {str(e)}")
    
    def chat_with_llm(self, message, context="", user_metadata=None, max_tokens=1500):
        """Chat with OpenRouter LLM with enhanced context including user metadata"""
        try:
            from snid_sage.interfaces.llm.openrouter.openrouter_llm import call_openrouter_api
            
            # Build enhanced context similar to summary generation
            enhanced_context = self._build_enhanced_chat_context(context, user_metadata)
            
            # Build the prompt with enhanced context
            if enhanced_context:
                prompt = f"Context from SNID analysis:\n{enhanced_context}\n\nUser question: {message}\n\nPlease provide a helpful response based on the analysis results."
            else:
                prompt = f"User question: {message}\n\nPlease provide a helpful response about supernova spectrum analysis."
            
            return call_openrouter_api(prompt, max_tokens=max_tokens)
        except Exception as e:
            return f"Error communicating with OpenRouter: {str(e)}"
    
    def _build_enhanced_chat_context(self, base_context="", user_metadata=None):
        """Build enhanced context for chat including user metadata and emission lines"""
        context_parts = []
        
        # Add base SNID results context
        if base_context:
            context_parts.append(base_context)
        
        # Add user metadata if available
        if user_metadata and any(user_metadata.values()):
            metadata_parts = []
            metadata_parts.append("📋 OBSERVATION DETAILS:")
            
            if user_metadata.get('object_name'):
                metadata_parts.append(f"   Object Name: {user_metadata['object_name']}")
            if user_metadata.get('telescope_instrument'):
                metadata_parts.append(f"   Telescope/Instrument: {user_metadata['telescope_instrument']}")
            if user_metadata.get('observation_date'):
                metadata_parts.append(f"   Observation Date: {user_metadata['observation_date']}")
            if user_metadata.get('observer'):
                metadata_parts.append(f"   Observer: {user_metadata['observer']}")
            if user_metadata.get('specific_request'):
                metadata_parts.append(f"   Specific Request: {user_metadata['specific_request']}")
            
            context_parts.extend(metadata_parts)
        
        # Add emission lines context if not already in base context
        if base_context and "🌟 DETECTED SPECTRAL LINES:" not in base_context:
            emission_lines_text = self._format_emission_lines_for_llm()
            if emission_lines_text:
                context_parts.extend(['', emission_lines_text])
        
        return '\n'.join(context_parts)
    
    def configure_openrouter(self):
        """Open OpenRouter configuration dialog"""
        try:
            from snid_sage.interfaces.llm.openrouter.openrouter_llm import configure_openrouter_dialog
            
            # Open the comprehensive OpenRouter dialog
            dialog = configure_openrouter_dialog(self.gui.master)
            
            # Check if configuration was successful when dialog closes
            def check_config_on_close():
                """Check configuration when dialog is closed"""
                try:
                    # Add a small delay to ensure config file is written
                    self.gui.master.after(500, lambda: self._check_configuration_success())
                except Exception as e:
                    _LOGGER.warning(f"⚠️ Error checking configuration: {e}")
            
            # Bind to dialog close event
            if dialog:
                dialog.protocol("WM_DELETE_WINDOW", lambda: (dialog.destroy(), check_config_on_close()))
            
        except ImportError as e:
            messagebox.showerror("Configuration Error", 
                               f"OpenRouter configuration module not available: {str(e)}")
        except Exception as e:
            messagebox.showerror("Configuration Error", 
                               f"Error opening OpenRouter configuration: {str(e)}")
    
    def _check_configuration_success(self):
        """Check if OpenRouter configuration was successful"""
        try:
            from snid_sage.interfaces.llm.openrouter.openrouter_llm import get_openrouter_config
            config = get_openrouter_config()
            
            if config and config.get('api_key') and config.get('model_id'):
                # Configuration was successful
                self.llm_config = config
                self.llm_available = True
                
                self._update_llm_status(f"OpenRouter configured: {config.get('model_id', 'Unknown model')}")
                
                # Trigger state transition when LLM is configured
                if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                    self.gui.workflow_integrator._workflow_update_button_states()
                else:
                    self.update_llm_button_states()
                
                _LOGGER.info(f"✅ OpenRouter configured with model: {config.get('model_id')}")
                messagebox.showinfo("Configuration Complete", 
                                  "OpenRouter backend configured successfully!\n\n"
                                  "You can now use AI Summary and AI Chat features.")
            else:
                _LOGGER.warning("⚠️ OpenRouter configuration incomplete")
                
        except Exception as e:
            _LOGGER.warning(f"⚠️ Error checking configuration success: {e}")

    def format_snid_results_for_llm(self, user_metadata=None):
        """Format SNID results for LLM processing using unified formatter
        
        Args:
            user_metadata: Optional user-provided observation metadata
            
        Returns:
            str: Formatted SNID results text suitable for LLM analysis
        """
        try:
            if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results:
                return "No SNID analysis results available."
            
            result = self.gui.snid_results
            
            # Check if it's a successful result
            if not hasattr(result, 'success') or not result.success:
                return "SNID analysis was not successful or incomplete."
            
            # Use the unified formatter to get the display summary
            # This ensures consistency with what the user sees in the GUI
            try:
                from snid_sage.shared.utils.results_formatter import create_unified_formatter
                spectrum_name = getattr(result, 'spectrum_name', 'Unknown')
                formatter = create_unified_formatter(result, spectrum_name)
                summary_text = formatter.get_display_summary()
                
                # Process the summary to ensure only top 5 templates and clean formatting
                lines = summary_text.split('\n')
                template_section_started = False
                template_count = 0
                total_templates = 0
                filtered_lines = []
                
                for line in lines:
                    if '🏆 TEMPLATE MATCHES' in line:
                        template_section_started = True
                        filtered_lines.append(line)
                    elif template_section_started and line.strip() and line.startswith('-'):
                        # Separator line in template section
                        filtered_lines.append(line)
                    elif template_section_started and line.strip() and not line.startswith('-') and not line.startswith('#'):
                        # Check if this is a template match line (starts with a number)
                        if line.strip() and line.strip()[0].isdigit():
                            # This is a template match line
                            total_templates += 1
                            if template_count < 5:
                                filtered_lines.append(line)
                                template_count += 1
                            # Skip remaining template lines after 5
                        else:
                            # This is a header line or other content in template section
                            filtered_lines.append(line)
                    elif not template_section_started:
                        # Lines before template section
                        filtered_lines.append(line)
                    elif template_section_started and not line.strip():
                        # Empty line after template section - end of templates
                        if total_templates > 5:
                            filtered_lines.append(f"   ... and {total_templates - 5} more templates (showing top 5)")
                        filtered_lines.append(line)
                        template_section_started = False
                    else:
                        # Lines after template section
                        filtered_lines.append(line)
                
                # Add a note at the end to clarify this is a summary
                if total_templates > 5:
                    filtered_lines.append("")
                    filtered_lines.append("📝 NOTE: This summary shows only the top 5 template matches for brevity.")
                    filtered_lines.append("   Full analysis includes all template matches and detailed statistics.")
                
                # Build the final result - ensure no duplication
                final_result_parts = []
                
                # Add the main SNID results
                main_results = '\n'.join(filtered_lines)
                final_result_parts.append(main_results)
                
                # Add user metadata if available
                if user_metadata and any(user_metadata.values()):
                    metadata_parts = []
                    metadata_parts.append("📋 OBSERVATION DETAILS:")
                    
                    if user_metadata.get('object_name'):
                        metadata_parts.append(f"   Object Name: {user_metadata['object_name']}")
                    if user_metadata.get('telescope_instrument'):
                        metadata_parts.append(f"   Telescope/Instrument: {user_metadata['telescope_instrument']}")
                    if user_metadata.get('observation_date'):
                        metadata_parts.append(f"   Observation Date: {user_metadata['observation_date']}")
                    if user_metadata.get('observer'):
                        metadata_parts.append(f"   Observer: {user_metadata['observer']}")
                    if user_metadata.get('specific_request'):
                        metadata_parts.append(f"   Specific Request: {user_metadata['specific_request']}")
                    
                    final_result_parts.append('\n'.join(metadata_parts))
                
                # Add emission lines context if available
                emission_lines_text = self._format_emission_lines_for_llm()
                if emission_lines_text:
                    final_result_parts.append(emission_lines_text)
                
                # Join all parts with proper spacing and return
                return '\n\n'.join(final_result_parts)
                
            except ImportError:
                # Fallback if unified formatter not available
                return f"SNID analysis completed for {getattr(result, 'spectrum_name', 'Unknown')}\n" \
                       f"Type: {result.consensus_type}\n" \
                       f"Redshift: {result.redshift:.6f}\n" \
                       f"Quality: {result.rlap:.2f} RLAP"
                
        except Exception as e:
            _LOGGER.error(f"Error formatting SNID results for LLM: {e}")
            return f"Error formatting SNID results: {str(e)}"
    
    def _format_emission_lines_for_llm(self):
        """Format detected emission lines for LLM context
        
        Returns:
            str: Formatted emission lines text or empty string if none detected
        """
        try:
            # Try to get spectrum data from SNID results
            spectrum_data = None
            if hasattr(self.gui, 'snid_results') and self.gui.snid_results:
                if hasattr(self.gui.snid_results, 'processed_spectrum') and self.gui.snid_results.processed_spectrum:
                    processed = self.gui.snid_results.processed_spectrum
                    if 'log_wave' in processed and 'flat_flux' in processed:
                        # Convert log wavelength to linear
                        import numpy as np
                        wavelength = np.power(10, processed['log_wave'])
                        flux = processed['flat_flux']
                        spectrum_data = {'wavelength': wavelength, 'flux': flux}
            
            # Fallback to GUI processed spectrum
            if spectrum_data is None and hasattr(self.gui, 'processed_spectrum') and self.gui.processed_spectrum:
                if 'log_wave' in self.gui.processed_spectrum and 'flat_flux' in self.gui.processed_spectrum:
                    import numpy as np
                    wavelength = np.power(10, self.gui.processed_spectrum['log_wave'])
                    flux = self.gui.processed_spectrum['flat_flux']
                    spectrum_data = {'wavelength': wavelength, 'flux': flux}
            
            if spectrum_data is None:
                return ""
            
            # Detect emission lines using available detection utilities
            try:
                from snid_sage.shared.utils.line_detection.line_detection_utils import detect_and_fit_lines
                
                wavelength = spectrum_data['wavelength']
                flux = spectrum_data['flux']
                
                # Filter out zero/invalid regions
                valid_mask = (flux != 0) & np.isfinite(flux) & np.isfinite(wavelength)
                if not np.any(valid_mask):
                    return ""
                
                wavelength = wavelength[valid_mask]
                flux = flux[valid_mask]
                
                # Detect lines with conservative parameters
                detected_lines = detect_and_fit_lines(
                    wavelength, flux, 
                    min_width=2, max_width=15, min_snr=3.0,
                    max_fit_window=30, smoothing_window=5, use_smoothing=True
                )
                
                if not detected_lines:
                    return ""
                
                # Format detected lines for LLM
                emission_lines = [line for line in detected_lines if line.get('type') == 'emission']
                absorption_lines = [line for line in detected_lines if line.get('type') == 'absorption']
                
                if not emission_lines and not absorption_lines:
                    return ""
                
                lines_text = ["🌟 DETECTED SPECTRAL LINES:"]
                
                if emission_lines:
                    lines_text.append("   Emission Lines:")
                    # Sort by SNR (strongest first) and limit to top 10
                    emission_lines.sort(key=lambda x: x.get('snr', 0), reverse=True)
                    for i, line in enumerate(emission_lines[:10], 1):
                        wavelength_val = line.get('wavelength', 0)
                        snr = line.get('snr', 0)
                        lines_text.append(f"   {i:2d}. {wavelength_val:7.1f} Å  (S/N: {snr:.1f})")
                
                if absorption_lines:
                    lines_text.append("   Absorption Lines:")
                    # Sort by SNR (strongest first) and limit to top 5
                    absorption_lines.sort(key=lambda x: x.get('snr', 0), reverse=True)
                    for i, line in enumerate(absorption_lines[:5], 1):
                        wavelength_val = line.get('wavelength', 0)
                        snr = line.get('snr', 0)
                        lines_text.append(f"   {i:2d}. {wavelength_val:7.1f} Å  (S/N: {snr:.1f})")
                
                return '\n'.join(lines_text)
                
            except ImportError:
                # Line detection utilities not available
                return ""
            except Exception as e:
                _LOGGER.debug(f"Error detecting emission lines: {e}")
                return ""
                
        except Exception as e:
            _LOGGER.debug(f"Error formatting emission lines for LLM: {e}")
            return "" 
