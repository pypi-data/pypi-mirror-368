"""
Simplified LLM Integration for SNID AI Assistant

This module provides a unified interface for LLM interactions with:
- OpenRouter-only backend support
- Single comprehensive summary generation
- Chat functionality with context awareness
- User metadata integration
- Enhanced SNID result formatting
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
import traceback

try:
    from snid_sage.interfaces.llm.openrouter.openrouter_llm import (
        call_openrouter_api,
        configure_openrouter_dialog,
        get_openrouter_config,
        get_openrouter_api_key,
        DEFAULT_MODEL,
    )
    from snid_sage.interfaces.llm.analysis.llm_utils import build_enhanced_context_with_metadata
    OPENROUTER_AVAILABLE = True
except ImportError as e:
    print(f"OpenRouter integration not available: {e}")
    OPENROUTER_AVAILABLE = False


class LLMIntegration:
    """
    Simplified LLM Integration class with OpenRouter-only support.
    
    Features:
    - Single comprehensive summary generation
    - Context-aware chat functionality
    - User metadata integration
    - Enhanced SNID result formatting
    """
    
    def __init__(self, gui_instance=None):
        """Initialize LLM integration."""
        self.gui = gui_instance
        self.llm_available = OPENROUTER_AVAILABLE
        self.current_model = None
        self.api_key = None
        
        # Initialize OpenRouter configuration
        if OPENROUTER_AVAILABLE:
            self._load_openrouter_config()
    
    def _load_openrouter_config(self):
        """Load OpenRouter configuration."""
        try:
            config = get_openrouter_config()
            # Prefer secure storage for API key
            try:
                self.api_key = get_openrouter_api_key()
            except Exception:
                self.api_key = None
            if not self.api_key:
                # Backward compatibility if key was stored previously
                self.api_key = config.get('api_key')

            # Use saved model or default to a known free variant
            self.current_model = config.get('model_id') or DEFAULT_MODEL
            
            # Check if configuration is valid
            if self.api_key and self.current_model:
                self.llm_available = True
            else:
                self.llm_available = False
                
        except Exception as e:
            print(f"Error loading OpenRouter config: {e}")
            self.llm_available = False
    
    def configure_openrouter(self):
        """Configure OpenRouter settings."""
        if not OPENROUTER_AVAILABLE:
            raise Exception("OpenRouter integration not available")
        
        # Reload configuration after setup
        self._load_openrouter_config()
    
    def _open_comprehensive_openrouter_config(self):
        """Open comprehensive OpenRouter configuration dialog."""
        if not OPENROUTER_AVAILABLE:
            raise Exception("OpenRouter integration not available")
        
        try:
            # Import and show configuration dialog
            configure_openrouter_dialog(parent=None)
            
            # Reload configuration
            self._load_openrouter_config()
            
        except Exception as e:
            raise Exception(f"Failed to open OpenRouter configuration: {str(e)}")
    
    def generate_summary(self, snid_results: Union[Dict[str, Any], Any], user_metadata: Dict[str, str] = None) -> str:
        """
        Generate a comprehensive AI summary of SNID results.
        
        Args:
            snid_results: SNID analysis results (can be Dict or SNIDResult object)
            user_metadata: User-provided observation metadata
            
        Returns:
            str: Generated summary text
        """
        if not self.llm_available:
            raise Exception("LLM backend not configured. Please configure OpenRouter in settings.")
        
        try:
            # Format SNID results for LLM
            formatted_data = self.format_snid_results_for_llm(snid_results)
            
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
                if user_metadata.get('additional_notes'):
                    metadata_parts.append(f"   Additional Notes: {user_metadata['additional_notes']}")
                
                formatted_data += "\n\n" + "\n".join(metadata_parts)
            
            # Create simple prompt
            system_prompt = """You are AstroSage, a world-renowned expert in supernova spectroscopy with decades of experience in stellar evolution, spectral analysis, and observational astronomy. You have published extensively on Type Ia, Type II, and exotic supernovae classifications.

You are analyzing results from SNID-SAGE, a spectral template matching pipeline that performs cross-correlation analysis between observed spectra and template libraries to identify supernova types and estimate redshifts.

Provide a concise, scientifically rigorous summary that includes the key classification results, confidence assessment, and main findings. Focus on the most important information for researchers and observers."""

            user_prompt = f"Analyze the following supernova data:\n\n{formatted_data}"
            
            full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
            
            # Generate summary using OpenRouter
            response = call_openrouter_api(
                prompt=full_prompt,
                max_tokens=2000
            )
            
            if response:
                return self._format_summary_response(response)
            else:
                raise Exception("No response received from AI model")
                
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")
    
    def chat_with_llm(self, message: str, conversation_history: List[Dict] = None, 
                     user_metadata: Dict[str, str] = None, max_tokens: int = 1500) -> str:
        """
        Chat with the LLM with context awareness.
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            user_metadata: User-provided observation metadata
            max_tokens: Maximum tokens for response (default: 1500)
            
        Returns:
            str: AI response
        """
        if not self.llm_available:
            raise Exception("LLM backend not configured. Please configure OpenRouter in settings.")
        
        try:
            # Build context-aware chat prompt
            chat_prompt = self._build_chat_prompt(message, conversation_history, user_metadata)
            
            # Get response from OpenRouter
            response = call_openrouter_api(
                prompt=chat_prompt,
                max_tokens=max_tokens
            )
            
            if response:
                return self._format_chat_response(response)
            else:
                raise Exception("No response received from AI model")
                
        except Exception as e:
            raise Exception(f"Chat failed: {str(e)}")
    
    def _build_chat_prompt(self, message: str, conversation_history: List[Dict] = None, 
                          user_metadata: Dict[str, str] = None) -> str:
        """Build context-aware chat prompt."""
        system_prompt = """You are AstroSage, an expert AI assistant specializing in supernova spectroscopy and the SNID (SuperNova IDentification) analysis pipeline.

You help researchers interpret spectral analysis results, understand classification confidence, discuss redshift measurements, and provide scientific context for observations.

Provide clear, scientifically accurate responses that are helpful for both students and professional astronomers. When discussing technical concepts, explain them clearly while maintaining scientific rigor."""

        # Build conversation context
        context_parts = []
        
        # Add user metadata if available
        if user_metadata and any(user_metadata.values()):
            context_parts.append("Current observation context:")
            for key, value in user_metadata.items():
                if value:
                    context_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        # Add conversation history
        if conversation_history:
            context_parts.append("\nRecent conversation:")
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                if role == 'user':
                    context_parts.append(f"User: {content}")
                elif role == 'assistant':
                    context_parts.append(f"Assistant: {content}")
        
        # Combine everything
        if context_parts:
            context_str = "\n".join(context_parts)
            full_prompt = f"{system_prompt}\n\n{context_str}\n\nUser: {message}\n\nAssistant:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
        
        return full_prompt
    
    def _format_summary_response(self, response: str) -> str:
        """Format and clean up summary response."""
        # Remove any system artifacts
        cleaned = response.strip()
        
        # Ensure proper formatting
        if not cleaned.startswith("🔬"):
            cleaned = "🔬 SNID CLASSIFICATION RESULTS\n\n" + cleaned
        
        return cleaned
    
    def _format_chat_response(self, response: str) -> str:
        """Format and clean up chat response."""
        # Remove any system artifacts and clean up
        cleaned = response.strip()
        
        # Remove common AI prefixes if present
        prefixes_to_remove = [
            "Assistant:",
            "AI Assistant:",
            "AstroSage:",
            "Response:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        return cleaned
    
    def format_snid_results_for_llm(self, snid_results: Union[Dict[str, Any], Any]) -> str:
        """
        Format SNID results for LLM consumption using unified formatter.
        
        Args:
            snid_results: SNID analysis results (can be Dict or SNIDResult object)
            
        Returns:
            str: Formatted results string
        """
        if not snid_results:
            return "No SNID results available."
        
        try:
            # Handle both dictionary and SNIDResult object inputs
            if hasattr(snid_results, 'consensus_type'):
                # snid_results is a SNIDResult object
                result = snid_results
            else:
                # snid_results is a dictionary
                result = snid_results.get('result')
            
            if not result:
                return "No SNID result object found."
            
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
                
                # Ensure we only show top 5 templates by truncating if needed
                lines = summary_text.split('\n')
                template_section_started = False
                template_count = 0
                filtered_lines = []
                
                for line in lines:
                    if '🏆 TEMPLATE MATCHES' in line:
                        template_section_started = True
                        filtered_lines.append(line)
                    elif template_section_started and line.strip() and not line.startswith('#') and not line.startswith('-'):
                        # This is a template match line
                        if template_count < 5:
                            filtered_lines.append(line)
                            template_count += 1
                        # Skip remaining template lines after 5
                    elif template_section_started and (line.startswith('#') or line.startswith('-')):
                        # Header lines in template section
                        filtered_lines.append(line)
                    elif not template_section_started:
                        # Lines before template section
                        filtered_lines.append(line)
                    elif template_section_started and not line.strip():
                        # Empty line after template section - end of templates
                        filtered_lines.append(line)
                        template_section_started = False
                    else:
                        # Lines after template section
                        filtered_lines.append(line)
                
                # Add emission lines context if available (if we have access to GUI instance)
                if hasattr(self, 'gui_instance') and self.gui_instance:
                    emission_lines_text = self._format_emission_lines_for_llm()
                    if emission_lines_text:
                        filtered_lines.extend(['', emission_lines_text])
                
                return '\n'.join(filtered_lines)
                
            except ImportError:
                # Fallback if unified formatter not available
                return f"SNID analysis completed for {getattr(result, 'spectrum_name', 'Unknown')}\n" \
                       f"Type: {result.consensus_type}\n" \
                       f"Redshift: {result.redshift:.6f}\n" \
                       f"Quality: {result.rlap:.2f} RLAP"
            
        except Exception as e:
            return f"Error formatting SNID results: {str(e)}"
    
    def _format_emission_lines_for_llm(self):
        """Format detected emission lines for LLM context
        
        Returns:
            str: Formatted emission lines text or empty string if none detected
        """
        try:
            # This method requires access to GUI instance for spectrum data
            if not hasattr(self, 'gui_instance') or not self.gui_instance:
                return ""
            
            gui = self.gui_instance
            
            # Try to get spectrum data from SNID results
            spectrum_data = None
            if hasattr(gui, 'snid_results') and gui.snid_results:
                if hasattr(gui.snid_results, 'processed_spectrum') and gui.snid_results.processed_spectrum:
                    processed = gui.snid_results.processed_spectrum
                    if 'log_wave' in processed and 'flat_flux' in processed:
                        # Convert log wavelength to linear
                        import numpy as np
                        wavelength = np.power(10, processed['log_wave'])
                        flux = processed['flat_flux']
                        spectrum_data = {'wavelength': wavelength, 'flux': flux}
            
            # Fallback to GUI processed spectrum
            if spectrum_data is None and hasattr(gui, 'processed_spectrum') and gui.processed_spectrum:
                if 'log_wave' in gui.processed_spectrum and 'flat_flux' in gui.processed_spectrum:
                    import numpy as np
                    wavelength = np.power(10, gui.processed_spectrum['log_wave'])
                    flux = gui.processed_spectrum['flat_flux']
                    spectrum_data = {'wavelength': wavelength, 'flux': flux}
            
            if spectrum_data is None:
                return ""
            
            # Detect emission lines using Tk-free detection utilities
            try:
                from snid_sage.shared.utils.line_detection.detection import detect_and_fit_lines
                
                wavelength = spectrum_data['wavelength']
                flux = spectrum_data['flux']
                
                # Filter out zero/invalid regions
                import numpy as np
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
                # Log debug message but don't fail
                return ""
                
        except Exception as e:
            # Log debug message but don't fail
            return ""


# Backward compatibility
def create_llm_integration(gui_instance=None):
    """Create and return LLM integration instance."""
    return LLMIntegration(gui_instance) 