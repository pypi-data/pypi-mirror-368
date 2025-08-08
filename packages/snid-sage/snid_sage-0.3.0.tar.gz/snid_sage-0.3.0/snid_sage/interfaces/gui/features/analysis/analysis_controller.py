"""
Analysis Controller Feature

Handles all SNID analysis workflow management including:
- SNID analysis execution
- Progress tracking and UI updates
- Results handling
- Threading management
- Error handling

Extracted from sage_gui.py to improve maintainability and modularity.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import numpy as np
import logging
import platform

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.analysis')
except ImportError:
    _LOGGER = logging.getLogger('gui.analysis')


class AnalysisController:
    """Handles SNID analysis workflow and management"""
    
    def __init__(self, gui_instance):
        """Initialize the analysis controller with reference to main GUI"""
        self.gui = gui_instance
        self.analysis_thread = None
        self.analysis_running = False
        self.progress_window = None
        self.progress_text = None
        self.cancel_button = None
        self.hide_button = None
        
        # Initialize analysis plotter component
        try:
            from snid_sage.interfaces.gui.components.analysis.analysis_plotter import AnalysisPlotter
            self.analysis_plotter = AnalysisPlotter(gui_instance)
            if self.gui.logger:
                self.gui.logger.debug("Analysis plotter initialized")
        except Exception as e:
            if self.gui.logger:
                self.gui.logger.warning(f"Analysis plotter not available: {e}")
            self.analysis_plotter = None
        
        # Cluster selection state
        self.selected_cluster = None
        self.selected_cluster_index = -1
        self.cluster_selection_made = False
        
        # Analysis state variables
        self._analysis_cancelled = False
        self._analysis_result = None
        self._analysis_trace = None
        self._analysis_error = None
        self.analysis_start_time = None
        
        # Redshift configuration
        self.redshift_config = {
            'mode': 'automatic',  # 'automatic', 'forced', 'constrained'
            'forced_redshift': None,
            'zmin': -0.01,
            'zmax': 1.0,
            'use_galaxy_constraint': False,
            'galaxy_redshift_range': 0.05
        }
    

    
    def run_snid_analysis_only(self):
        """Run SNID analysis only"""
        if not hasattr(self.gui, 'processed_spectrum') or self.gui.processed_spectrum is None:
            messagebox.showwarning("No Preprocessed Data", 
                                 "Please run preprocessing first.\n\n"
                                 "Choose either:\n"
                                 "• Quick Preprocessing (default settings)\n"
                                 "• Advanced Preprocessing (custom steps)")
            return None
        
        # Start threaded analysis
        self._start_threaded_analysis()
    
    def _start_threaded_analysis(self):
        """Start SNID analysis in a background thread"""
        try:
            # Update button states  
            self.gui.analysis_btn.configure(text="⏳ Analyzing...", state='disabled')
            
            # Disable other controls during analysis
            if hasattr(self.gui, 'load_btn'):
                self.gui.load_btn.configure(state='disabled')
            if hasattr(self.gui, 'preprocess_btn'):
                self.gui.preprocess_btn.configure(state='disabled')
            
            # Create progress tracking
            self._analysis_cancelled = False
            self._create_progress_window()
            
            # Offer games while analysis is running
            if hasattr(self.gui, 'games_integration'):
                self.gui.games_integration._offer_games_during_analysis()
            
            # Start analysis in background thread
            self.analysis_thread = threading.Thread(
                target=self._run_analysis_thread,
                daemon=True
            )
            self.analysis_thread.start()
            
            # Start progress monitoring
            self._monitor_analysis_progress()
            
        except Exception as e:
            self._handle_analysis_error(f"Failed to start analysis: {str(e)}")
    
    def _offer_games_during_analysis(self):
        """Games are now integrated into the progress window - no separate offering needed"""
        # Games are automatically shown in the progress window's right panel
        # Don't show the games message to keep progress window focused on analysis
        pass
    
    def _create_progress_window(self):
        """Create progress window with integrated game area"""
        self.progress_window = tk.Toplevel(self.gui.master)
        self.progress_window.title("SNID-SAGE Analysis Progress 🎮")
        self.progress_window.geometry("900x700")  # Slightly taller window for more space
        self.progress_window.resizable(True, True)
        
        # Configure window
        self.progress_window.configure(bg='#2c3e50')
        self.progress_window.transient(self.gui.master)
        
        # Center the window
        self.progress_window.update_idletasks()
        x = (self.progress_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.progress_window.winfo_screenheight() // 2) - (700 // 2)
        self.progress_window.geometry(f"900x700+{x}+{y}")
        
        # Create main container with split layout
        main_container = tk.Frame(self.progress_window, bg='#2c3e50')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel for SNID progress (expanded width)
        progress_panel = tk.Frame(main_container, bg='#34495e', relief='raised', bd=2)
        # Make the progress panel take most of the window width
        progress_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        progress_panel.configure(width=650)  # Wider fixed width for clearer summary
        progress_panel.pack_propagate(False)  # Maintain fixed width
        
        # Progress panel header
        progress_header = tk.Label(progress_panel, text="📊 SNID-SAGE Analysis Status",
                                 font=('Arial', 16, 'bold'),
                                 bg='#34495e', fg='#ecf0f1')
        progress_header.pack(pady=(10, 5))
        
        # Template progress section
        template_frame = tk.Frame(progress_panel, bg='#34495e')
        template_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        # ------------------------------------------------------------------
        # Replace ttk.Progressbar with a pure-Tk CanvasProgressBar to prevent
        
        # ------------------------------------------------------------------

        class CanvasProgressBar(tk.Canvas):
            def __init__(self, parent, width=300, height=18, bg='#2c3e50', fg='#1abc9c', **kwargs):
                super().__init__(parent, width=width, height=height, highlightthickness=0, bg=bg, **kwargs)
                self._width = width
                self._height = height
                self._fg = fg
                self._bg = bg
                self._value = 0
                self._maximum = 100
                self._bar = self.create_rectangle(0, 0, 0, height, fill=fg, width=0)
                # Bind to configure event to handle resizing
                self.bind('<Configure>', self._on_resize)

            def __setitem__(self, key, value):
                if key == 'value':
                    self._value = float(value)
                    self._redraw()
                elif key == 'maximum':
                    self._maximum = float(value)
                    self._redraw()
                else:
                    super().__setitem__(key, value)

            def _on_resize(self, event):
                """Update width when canvas is resized"""
                self._width = event.width
                self._redraw()

            def _redraw(self):
                frac = max(0.0, min(1.0, self._value / max(1.0, self._maximum)))
                # Use actual canvas width to ensure bar fills properly
                actual_width = self.winfo_width()
                if actual_width > 1:  # Canvas has been rendered
                    new_width = frac * actual_width
                else:
                    new_width = frac * self._width
                # Ensure bar is visible (minimum 1 pixel if > 0%)
                if frac > 0 and new_width < 1:
                    new_width = 1
                self.coords(self._bar, 0, 0, new_width, self._height)



        self.template_progress_bar = CanvasProgressBar(template_frame, width=300, height=18,
                                                       bg='#2c3e50', fg='#1abc9c')
        self.template_progress_bar.pack(fill='x', pady=(0, 5))
        
        # Force initial redraw to ensure bar is visible
        self.template_progress_bar.update_idletasks()
        self.template_progress_bar['value'] = 0  # Initialize to 0%


        
        # Current template label
        self.current_template_label = tk.Label(template_frame,
                                             text="Initializing...",
                                             font=('Arial', 14),
                                             bg='#34495e', fg='#bdc3c7',
                                             wraplength=600)
        self.current_template_label.pack(pady=(0, 10))
        
        # Progress text area
        progress_frame = tk.Frame(progress_panel, bg='#34495e')
        progress_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.progress_text = tk.Text(progress_frame,
                                   wrap=tk.WORD,
                                   bg='#2c3e50',
                                   fg='#ecf0f1',
                                   font=('Consolas', 16, 'bold'),
                                   relief='flat',
                                   bd=0,
                                   state='disabled')
        
        progress_scrollbar = tk.Scrollbar(progress_frame, command=self.progress_text.yview,
                                        bg='#34495e', troughcolor='#2c3e50')
        self.progress_text.configure(yscrollcommand=progress_scrollbar.set)
        
        self.progress_text.pack(side='left', fill='both', expand=True)
        progress_scrollbar.pack(side='right', fill='y')
        
        # Progress control buttons
        button_frame = tk.Frame(progress_panel, bg='#34495e')
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        btn_common_opts = dict(font=('Arial', 16, 'bold'), relief='raised', bd=2, padx=20, pady=10)

        self.cancel_button = tk.Button(button_frame, text="❌ Cancel Analysis",
                                     command=self._cancel_analysis,
                                     bg='#e74c3c', fg='white',
                                     **btn_common_opts)
        self.cancel_button.pack(side='left', padx=(0, 5))
        
        self.hide_button = tk.Button(button_frame, text="👁️ Hide Window",
                                   command=lambda: self.progress_window.withdraw(),
                                   bg='#95a5a6', fg='white',
                                   **btn_common_opts)
        self.hide_button.pack(side='left')
        
        # Add "Play Game" button next to control buttons
        if hasattr(self.gui, 'games_integration'):
            play_game_btn = tk.Button(
                button_frame,
                text="🛰️ PLAY SPACE DEBRIS GAME",
                bg='#27ae60', fg='white',
                cursor='hand2',
                command=lambda: self.gui.games_integration._start_debris(),
                **btn_common_opts
            )
            play_game_btn.pack(side='right', padx=(5, 0))
        
        # Handle window closing
        self.progress_window.protocol("WM_DELETE_WINDOW", self._on_progress_window_close)
        
        # Don't show any initial messages - keep it clean until analysis starts
        # Force update to show initial state
        self.progress_window.update_idletasks()
    
    def _on_progress_window_close(self):
        """Handle progress window closing"""
        if hasattr(self, 'analysis_thread') and self.analysis_thread and self.analysis_thread.is_alive():
            # Ask for confirmation if analysis is running
            response = messagebox.askyesno(
                "Analysis Running",
                "SNID analysis is still running. Do you want to cancel it?",
                parent=self.progress_window
            )
            if response:
                self._cancel_analysis()
            else:
                return  # Don't close the window
        
        # Close the progress window
        self.progress_window.destroy()
        self.progress_window = None
    
    def _run_analysis_thread(self):
        """Run SNID analysis in background thread"""
        self.analysis_start_time = time.time()
        
        try:
            # Get templates directory
            templates_dir = self.gui.get_templates_dir()
            if not templates_dir or not os.path.exists(templates_dir):
                self._analysis_error = "Templates directory not found"
                return
            
            # Better handling of Advanced Preprocessing results
            current_masks = self.gui._parse_wavelength_masks(self.gui.params.get('wavelength_masks', ''))
            last_preprocessing_masks = getattr(self.gui, '_last_preprocessing_masks', None)
            
            # Check if we have a custom Advanced Preprocessing result that shouldn't be overridden
            has_advanced_preprocessing = (
                hasattr(self.gui, 'processed_spectrum') and 
                self.gui.processed_spectrum is not None and
                # Check if this came from Advanced Preprocessing by looking for specific markers
                (self.gui.processed_spectrum.get('advanced_preprocessing', False) or
                 self.gui.processed_spectrum.get('preprocessing_type') == 'advanced' or
                 ('original_wave' in self.gui.processed_spectrum and 
                  'input_spectrum' in self.gui.processed_spectrum))
            )
            
            # Only force re-preprocessing if truly necessary
            needs_reprocessing = (
                not hasattr(self.gui, 'processed_spectrum') or 
                self.gui.processed_spectrum is None or
                # If masks changed AND we don't have Advanced Preprocessing results
                (current_masks != last_preprocessing_masks and not has_advanced_preprocessing)
            )
            
            if needs_reprocessing:
                if current_masks != last_preprocessing_masks and not has_advanced_preprocessing:
                    self._update_progress("🔄 Reprocessing with new wavelength masks...")
                else:
                    self._update_progress("🔄 Running preprocessing...")
                
                # Re-run preprocessing with current parameters including masks
                try:
                    # Import preprocessing function
                    from snid_sage.snid.snid import preprocess_spectrum
                    
                    processed_spectrum, trace = preprocess_spectrum(
                        spectrum_path=self.gui.file_path,
                        # Get parameters from GUI with safe parsing
                        # Using Savitzky-Golay parameters
                        savgol_window=self.gui._safe_int(self.gui.params.get('savgol_window', ''), 0),
                        savgol_fwhm=self.gui._safe_float(self.gui.params.get('savgol_fwhm', ''), 0.0),
                        savgol_order=self.gui._safe_int(self.gui.params.get('savgol_order', ''), 3),
                        aband_remove=self.gui._safe_bool(self.gui.params.get('aband_remove', '')),
                        skyclip=self.gui._safe_bool(self.gui.params.get('skyclip', '')),
                        emclip_z=self.gui._safe_float(self.gui.params.get('emclip_z', ''), -1.0),
                        emwidth=self.gui._safe_float(self.gui.params.get('emwidth', ''), 40.0),
                        wavelength_masks=current_masks,  # Use current masks
                        apodize_percent=self.gui._safe_float(self.gui.params.get('apodize_percent', ''), 10.0),
                        skip_steps=[],  # Don't skip any steps during analysis
                        verbose=self.gui._safe_bool(self.gui.params.get('verbose', ''))
                    )
                    
                    # Store the processed spectrum and remember the masks used
                    self.gui.processed_spectrum = processed_spectrum
                    self.gui.preprocessing_trace = trace
                    self.gui._last_preprocessing_masks = current_masks
                    
                    # Add marker to identify this as standard preprocessing from analysis controller
                    if self.gui.processed_spectrum is not None:
                        self.gui.processed_spectrum['preprocessing_type'] = 'standard'
                        self.gui.processed_spectrum['advanced_preprocessing'] = False
                    
                    if current_masks:
                        self._update_progress(f"✅ Applied {len(current_masks)} wavelength mask(s)")
                    
                except Exception as e:
                    self._analysis_error = f"Preprocessing failed: {str(e)}"
                    return
            
            # Debug logging to verify the fix
            _LOGGER.info(f"🔧 Analysis: Using preprocessed spectrum with {len(current_masks)} mask(s)")
            if hasattr(self.gui, '_last_preprocessing_masks'):
                _LOGGER.info(f"📍 Last preprocessing masks: {self.gui._last_preprocessing_masks}")
            _LOGGER.info(f"📍 Current SNID parameter masks: {current_masks}")
            if has_advanced_preprocessing:
                _LOGGER.info("🎯 Advanced Preprocessing result detected - preserving custom processing")
            
            # Get effective redshift range (may be constrained by manual redshift)
            zmin_effective, zmax_effective, is_manual_constrained = self.gui.get_effective_redshift_range()
            
            if is_manual_constrained:
                self._update_progress(f"🎯 Using manual redshift: z = {zmin_effective:.4f} to {zmax_effective:.4f}")
            else:
                self._update_progress(f"🔍 Redshift range: z = {zmin_effective:.4f} to {zmax_effective:.4f}")
            
            self._update_progress("🚀 Starting SNID analysis...")
            
            # Use the modular analysis function with safe parameter parsing
            from snid_sage.snid.snid import run_snid_analysis
            
            # DEBUG: Check what filters are being passed
            template_filter = self.gui._parse_template_filter()
            type_filter = self.gui._parse_type_filter()
            age_range = self.gui._parse_age_range()
            
            _LOGGER.info(f"DEBUG: Analysis starting with filters:")
            _LOGGER.info(f"  - template_filter: {template_filter}")
            _LOGGER.info(f"  - type_filter: {type_filter}")
            _LOGGER.info(f"  - age_range: {age_range}")
            
            # Determine forced redshift parameter based on configuration
            forced_redshift = None
            if self.redshift_config['mode'] == 'forced' and self.redshift_config['forced_redshift'] is not None:
                forced_redshift = self.redshift_config['forced_redshift']
                self._update_progress(f"🎯 Using FORCED REDSHIFT: z = {forced_redshift:.5f}")
            
            result, trace = run_snid_analysis(
                processed_spectrum=self.gui.processed_spectrum,
                templates_dir=templates_dir,
                zmin=zmin_effective,  # Use effective range instead of raw parameters
                zmax=zmax_effective,  # Use effective range instead of raw parameters
                age_range=age_range,
                type_filter=type_filter,
                template_filter=template_filter,
                peak_window_size=self.gui._safe_int(self.gui.params.get('peak_window_size', ''), 10),
                lapmin=self.gui._safe_float(self.gui.params.get('lapmin', ''), 0.3),
                rlapmin=self.gui._safe_float(self.gui.params.get('rlapmin', ''), 5.0),

                forced_redshift=forced_redshift,  # NEW: Pass forced redshift
                max_output_templates=self.gui._safe_int(self.gui.params.get('max_output_templates', ''), 10),
                verbose=self.gui._safe_bool(self.gui.params.get('verbose', '')),
                show_plots=False,  # We'll handle plotting in the GUI
                save_plots=False,
                progress_callback=self._analysis_progress_callback
            )
            
            # Final progress update
            self._update_progress("✅ Step 2 Complete: Template matching finished!")
            self._update_progress("📊 Step 3: Processing results and clustering...")
            
            # Store results for main thread
            self._analysis_result = result
            self._analysis_trace = trace
            self._analysis_error = None
            
            self._update_progress("✅ Analysis completed successfully!")
            
        except InterruptedError as e:
            # Handle cancellation specifically
            self._update_progress("🔴 Analysis cancelled by user")
            self._analysis_result = None
            self._analysis_trace = None
            self._analysis_error = None
            _LOGGER.debug(f"Analysis interrupted: {str(e)}")
        except Exception as e:
            import traceback
            error_details = f"Analysis failed: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self._analysis_error = error_details
            self._update_progress(f"❌ Analysis failed: {str(e)}")
            self._analysis_result = None
            self._analysis_trace = None
    
    def _analysis_progress_callback(self, message, progress=None):
        """Callback for analysis progress updates with enhanced template tracking"""
        # Check for cancellation at the start of each callback
        if self._analysis_cancelled:
            # Raise an exception to interrupt the SNID analysis
            raise InterruptedError("Analysis cancelled by user")
        
        # Debug logging
        _LOGGER.debug(f"Progress callback: message='{message}', progress={progress}")
        
        # Check if we have a progress percentage
        if progress is not None:
            # Update the progress bar based on the percentage
            try:
                # Get total templates from the message if available
                total_templates = 100  # Default
                if "Processing" in message and "templates" in message:
                    # Try to extract template count from messages like "Type Ia: Processing 500 templates"
                    import re
                    match = re.search(r'Processing (\d+) templates', message)
                    if match:
                        total_templates = int(match.group(1))
                
                # Calculate current based on progress percentage
                current = int((progress / 100.0) * total_templates)
                
                # Update progress bar
                self._update_template_progress(current, total_templates, template_name="")
                
            except Exception as e:
                _LOGGER.error(f"Error parsing progress: {e}")
        
        # Update progress text only if message has visible content
        if message and message.strip():
            self._update_progress(message)
    
    def _update_template_progress(self, current, total, template_name):
        """Update template progress bar and counter (thread-safe)"""
        def update_gui():
            if hasattr(self, 'template_progress_bar') and self.template_progress_bar and self.template_progress_bar.winfo_exists():
                try:
                    # Update progress bar
                    progress_percent = (current / total) * 100
                    # CanvasProgressBar uses dict-like assignment for value
                    self.template_progress_bar['value'] = progress_percent
                    
                    # Update current template label - show progress info instead of template name
                    if hasattr(self, 'current_template_label') and self.current_template_label:
                        if template_name:
                            self.current_template_label.config(
                                text=f"Processing: {template_name}"
                            )
                        else:
                            # Show progress percentage when no template name
                            self.current_template_label.config(
                                text=f"Progress: {progress_percent:.1f}% complete"
                            )
                    
                    # Force update
                    if hasattr(self, 'progress_window') and self.progress_window:
                        self.progress_window.update_idletasks()
                        
                except Exception as e:
                    _LOGGER.error(f"Error updating template progress: {e}")
        
        # Schedule the GUI update on the main thread
        if hasattr(self.gui, 'master') and self.gui.master:
            try:
                self.gui.master.after(0, update_gui)
            except:
                pass
    
    def _update_progress(self, message):
        """Update progress text in the progress window (thread-safe)"""
        def update_gui():
            if hasattr(self, 'progress_text') and self.progress_text and self.progress_text.winfo_exists():
                try:
                    timestamp = time.strftime("%H:%M:%S")
                    formatted_message = f"[{timestamp}] {message}\n"
                    
                    # Enable text widget temporarily to insert text
                    self.progress_text.config(state='normal')
                    self.progress_text.insert(tk.END, formatted_message)
                    self.progress_text.config(state='disabled')
                    
                    # Auto-scroll to bottom
                    self.progress_text.see(tk.END)
                    
                    # Update the display
                    self.progress_text.update_idletasks()
                    
                    # Also print to console for debugging
                    _LOGGER.debug(f"[PROGRESS] {message}")
                    
                except Exception as e:
                    _LOGGER.error(f"Error updating progress display: {e}")
                    # Fallback to console
                    _LOGGER.debug(f"[PROGRESS] {message}")
            else:
                # Fallback to console if window doesn't exist
                _LOGGER.debug(f"[PROGRESS] {message}")
        
        # Schedule the GUI update on the main thread
        if hasattr(self.gui, 'master') and self.gui.master:
            try:
                self.gui.master.after(0, update_gui)
            except:
                # If master is not available, just print to console
                _LOGGER.debug(f"[PROGRESS] {message}")
        else:
            # Fallback if no master window
            update_gui()
    
    def _monitor_analysis_progress(self):
        """Monitor analysis thread and update GUI"""
        if hasattr(self, 'analysis_thread') and self.analysis_thread.is_alive():
            # Check if analysis is still running
            self.gui.master.after(500, self._monitor_analysis_progress)
        else:
            # Analysis completed or failed
            self._handle_analysis_completion()
    
    def _handle_analysis_completion(self):
        """Handle analysis completion on main thread"""
        try:
            # Close progress window
            if hasattr(self, 'progress_window') and self.progress_window and self.progress_window.winfo_exists():
                self.progress_window.destroy()
            
            # Clean up game thread if it exists (games will continue independently)
            if hasattr(self, 'game_thread'):
                # Allow users to finish their games
                _LOGGER.debug("🎮 Game is still running - you can continue playing!")
            
            # Check for cancellation
            if self._analysis_cancelled:
                self.gui.update_header_status("🔴 Analysis cancelled")
                self._reset_analysis_ui()
                _LOGGER.debug("🔴 Analysis successfully cancelled")
                return
            
            # Check for errors
            if hasattr(self, '_analysis_error') and self._analysis_error:
                self._handle_analysis_error(self._analysis_error)
                return
            
            # Process successful results
            if hasattr(self, '_analysis_result') and self._analysis_result:
                result = self._analysis_result
                trace = self._analysis_trace
                
                # Store results
                self.gui.snid_results = result
                self.gui.analysis_trace = trace
                
                # Check if we have GMM clustering results that need user selection
                if self._is_clustering_available(result):
                    # Show cluster selection dialog
                    self._show_cluster_selection_dialog(result)
                    return  # Don't continue until user makes selection
                
                # Update GUI with results
                if result and result.success:
                    self.gui.update_results_display(result)
                    self.gui.enable_plot_navigation()
                    self.gui.show_results_summary(result)
                    
                    # Update status
                    if hasattr(self.gui, 'update_header_status'):
                        self.gui.update_header_status(f"✅ Best: {result.template_name} ({result.consensus_type})")
                    
                    # Update button states and navigation
                    if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                        # Analysis is complete - set workflow state
                        self.gui.workflow_integrator.set_analysis_complete()
                        _LOGGER.info("🔄 Analysis complete: Workflow state set to ANALYSIS_COMPLETE")

                        # Update status label with chosen type
                        if hasattr(self.gui, 'config_status_label'):
                            chosen_type = result.consensus_type if getattr(result, 'success', False) else None
                            if chosen_type and chosen_type.lower() not in ['unknown', '']:
                                self.gui.config_status_label.configure(
                                    text=f"✅ Analysis finished – {chosen_type} selected",
                                    fg=self.gui.theme_manager.get_color('text_primary') if hasattr(self.gui, 'theme_manager') else 'black'
                                )
                            else:
                                self.gui.config_status_label.configure(
                                    text="⚠️ Analysis finished – No good match",
                                    fg=self.gui.theme_manager.get_color('text_secondary') if hasattr(self.gui, 'theme_manager') else 'grey'
                                )
                    else:
                        _LOGGER.error("❌ No workflow integrator available - buttons will not update correctly!")

                        # Still update label even without workflow integrator
                        if hasattr(self.gui, 'config_status_label'):
                            chosen_type = result.consensus_type if getattr(result, 'success', False) else None
                            if chosen_type and chosen_type.lower() not in ['unknown', '']:
                                self.gui.config_status_label.configure(
                                    text=f"✅ Analysis finished – {chosen_type} selected",
                                    fg=self.gui.theme_manager.get_color('text_primary') if hasattr(self.gui, 'theme_manager') else 'black'
                                )
                            else:
                                self.gui.config_status_label.configure(
                                    text="⚠️ Analysis finished – No good match",
                                    fg=self.gui.theme_manager.get_color('text_secondary') if hasattr(self.gui, 'theme_manager') else 'grey'
                                )
                    
                    # Update GUI to ensure changes are visible
                    self.gui.master.update_idletasks()
                    
                    _LOGGER.debug(f"🔄 Button states updated - Analysis plots and tools enabled")
                    
                    # Show completion message
                    completion_msg = (f"SNID analysis completed successfully!\n\n"
                                    f"Best match: {result.template_name}\n"
                                    f"Type: {result.consensus_type}\n"
                                    f"Redshift: {result.redshift:.4f}\n"
                                    f"RLAP: {result.rlap:.2f}")
                    
                    # Check if games are running - notify in-game instead of showing popup
                    if hasattr(self, 'game_thread'):
                        try:
                            from snid_sage.snid.games import set_analysis_complete
                            result_summary = f"Type: {result.consensus_type}, z={result.redshift:.4f}, RLAP={result.rlap:.2f}"
                            set_analysis_complete(result_summary)
                            _LOGGER.debug("🎮 Notified game of analysis completion")
                        except Exception as e:
                            _LOGGER.error(f"Failed to notify game: {e}")
                            # Fallback to regular popup if game notification fails
                            messagebox.showinfo("Analysis Complete", completion_msg)
                    else:
                        # No game running - show regular popup
                        messagebox.showinfo("Analysis Complete", completion_msg)
                    
                else:
                    self.gui.update_header_status("⚠️ Analysis finished – No good match")
                    # Update status label to reflect no good match
                    if hasattr(self.gui, 'config_status_label'):
                        self.gui.config_status_label.configure(
                            text="⚠️ Analysis finished – No good match",
                            fg=self.gui.theme_manager.get_color('text_secondary') if hasattr(self.gui, 'theme_manager') else 'grey'
                        )
                    # Check if games are running - notify in-game instead of showing popup
                    if hasattr(self, 'game_thread'):
                        try:
                            from snid_sage.snid.games import notify_analysis_complete, notify_analysis_result
                            notify_analysis_complete("⚠️ SNID Analysis Complete")
                            notify_analysis_result("No good matches found")
                            notify_analysis_result("Try adjusting parameters or preprocessing")
                            _LOGGER.debug("🎮 Notified game of analysis completion (no matches)")
                        except Exception as e:
                            _LOGGER.error(f"Failed to notify game: {e}")
                            # Fallback to regular popup if game notification fails
                            messagebox.showwarning("Analysis Results", 
                                                 "No good matches found.\n"
                                                 "Try adjusting parameters or preprocessing steps.")
                    else:
                        # No game running - show regular popup
                        messagebox.showwarning("Analysis Results", 
                                             "No good matches found.\n"
                                             "Try adjusting parameters or preprocessing steps.")
                
                _LOGGER.debug("✅ SNID analysis completed successfully!")
            else:
                self._handle_analysis_error("No results returned from analysis")
            
        except Exception as e:
            self._handle_analysis_error(f"Error processing results: {str(e)}")
        finally:
            self._reset_analysis_ui()
    
    def _handle_analysis_error(self, error_msg):
        """Handle analysis errors"""
        _LOGGER.error(f"❌ {error_msg}")
        self.gui.update_header_status("❌ Analysis failed")
        
        # Check if games are running - notify in-game instead of showing popup
        if hasattr(self, 'game_thread'):
            try:
                from snid_sage.snid.games import notify_analysis_complete, notify_analysis_result
                notify_analysis_complete("❌ Analysis Failed")
                notify_analysis_result(f"Error: {error_msg}")
                notify_analysis_result("Check console for details")
                _LOGGER.debug("🎮 Notified game of analysis error")
            except Exception as e:
                _LOGGER.error(f"Failed to notify game of error: {e}")
                # Fallback to regular popup if game notification fails
                messagebox.showerror("Analysis Error", error_msg)
        else:
            # No game running - show regular popup
            messagebox.showerror("Analysis Error", error_msg)
        
        self._reset_analysis_ui()
    
    def _cancel_analysis(self):
        """Cancel running analysis"""
        self._analysis_cancelled = True
        
        # Update progress window to show cancellation is in progress
        if hasattr(self, 'progress_window') and self.progress_window and self.progress_window.winfo_exists():
            self._update_progress("🔴 Cancelling analysis... Please wait for current template to finish.")
            
            # Disable the cancel button to prevent multiple clicks
            if hasattr(self, 'cancel_button') and self.cancel_button:
                self.cancel_button.configure(state='disabled', text="⏳ Cancelling...")
        
        # Update status
        self.gui.update_header_status("🔴 Cancelling analysis...")
        
        _LOGGER.debug("🔴 Analysis cancellation requested by user")
    
    def _handle_automatic_saving(self, result):
        """Handle automatic saving of plots and summary files if enabled"""
        try:
            import os
            from datetime import datetime
            
            # Check if any save options are enabled
            save_plots = self.gui._safe_bool(self.gui.params.get('save_plots', ''))
            save_summary = self.gui._safe_bool(self.gui.params.get('save_summary', ''))
            
            if not (save_plots or save_summary):
                return  # No saving options enabled
            
            # Get the input file name for the results folder
            if hasattr(self.gui, 'input_file_path') and self.gui.input_file_path:
                input_filename = os.path.splitext(os.path.basename(self.gui.input_file_path))[0]
            elif hasattr(result, 'spectrum_name') and result.spectrum_name:
                input_filename = result.spectrum_name
            else:
                input_filename = "analysis_results"
            
            # Create unique timestamp for the folder name to prevent overwriting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_folder_name = f"{input_filename}_{timestamp}"
            
            # Create results directory structure
            results_dir = os.path.join(os.getcwd(), "results", unique_folder_name)
            os.makedirs(results_dir, exist_ok=True)
            
            _LOGGER.info(f"💾 Saving results to: {results_dir}")
            
            # Save plots if enabled (the same plots shown in the GUI)
            if save_plots:
                self._save_gui_plots(result, results_dir)
            
            # Save summary if enabled
            if save_summary:
                self._save_analysis_summary(result, results_dir)
            
            _LOGGER.info(f"✅ Results saved successfully to: {results_dir}")
            
        except Exception as e:
            _LOGGER.error(f"Error saving analysis results: {e}")
            # Don't update progress here since we're not in the analysis thread anymore
    
    def _save_gui_plots(self, result, results_dir):
        """Save the same plots that are shown in the GUI (flux, flattened, subtypes, GMM clustering)"""
        try:
            import matplotlib.pyplot as plt
            from snid_sage.snid.plotting import plot_cluster_subtype_proportions
            
            # Create plots subdirectory
            plots_dir = os.path.join(results_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            
            plot_count = 0
            
            # 1. Flux spectrum plot (what's shown in the main GUI)
            try:
                fig_flux = self._create_flux_plot(result)
                if fig_flux:
                    flux_path = os.path.join(plots_dir, "flux_spectrum.png")
                    fig_flux.savefig(flux_path, dpi=150, bbox_inches='tight')
                    plt.close(fig_flux)
                    plot_count += 1
                    _LOGGER.debug(f"Saved flux spectrum plot")
            except Exception as e:
                _LOGGER.warning(f"Failed to save flux spectrum plot: {e}")
            
            # 2. Flattened spectrum plot
            try:
                fig_flat = self._create_flattened_plot(result)
                if fig_flat:
                    flat_path = os.path.join(plots_dir, "flattened_spectrum.png")
                    fig_flat.savefig(flat_path, dpi=150, bbox_inches='tight')
                    plt.close(fig_flat)
                    plot_count += 1
                    _LOGGER.debug(f"Saved flattened spectrum plot")
            except Exception as e:
                _LOGGER.warning(f"Failed to save flattened spectrum plot: {e}")
            
            # 3. Subtype proportions plot (cluster-aware, same as GUI)
            try:
                # Get the selected cluster (user-selected or best cluster)
                selected_cluster = None
                if hasattr(result, 'clustering_results') and result.clustering_results:
                    clustering_results = result.clustering_results
                    if 'user_selected_cluster' in clustering_results:
                        selected_cluster = clustering_results['user_selected_cluster']
                    elif 'best_cluster' in clustering_results:
                        selected_cluster = clustering_results['best_cluster']
                
                fig_subtypes = plot_cluster_subtype_proportions(result, selected_cluster=selected_cluster)
                subtypes_path = os.path.join(plots_dir, "subtype_proportions.png")
                fig_subtypes.savefig(subtypes_path, dpi=150, bbox_inches='tight')
                plt.close(fig_subtypes)
                plot_count += 1
                _LOGGER.debug(f"Saved subtype proportions plot")
            except Exception as e:
                _LOGGER.warning(f"Failed to save subtype proportions plot: {e}")
            
            # 4. 3D GMM clustering plot (if available)
            if hasattr(result, 'clustering_results') and result.clustering_results:
                try:
                    from snid_sage.snid.plotting_3d import plot_3d_type_clustering
                    fig_3d = plot_3d_type_clustering(result.clustering_results)
                    clustering_path = os.path.join(plots_dir, "gmm_clustering.png")
                    fig_3d.savefig(clustering_path, dpi=150, bbox_inches='tight')
                    plt.close(fig_3d)
                    plot_count += 1
                    _LOGGER.debug(f"Saved GMM clustering plot")
                except Exception as e:
                    _LOGGER.warning(f"Failed to save GMM clustering plot: {e}")
            
            # 5. Redshift vs Age plot (cluster-aware, same as GUI)
            try:
                from snid_sage.snid.plotting import plot_redshift_age
                fig_redshift_age = plot_redshift_age(result)
                redshift_age_path = os.path.join(plots_dir, "redshift_age.png")
                fig_redshift_age.savefig(redshift_age_path, dpi=150, bbox_inches='tight')
                plt.close(fig_redshift_age)
                plot_count += 1
                _LOGGER.debug(f"Saved redshift vs age plot")
            except Exception as e:
                _LOGGER.warning(f"Failed to save redshift vs age plot: {e}")
            
            _LOGGER.info(f"📈 Saved {plot_count} plots to {plots_dir}")
            
        except Exception as e:
            _LOGGER.error(f"Error saving GUI plots: {e}")
    
    def _create_flux_plot(self, result):
        """Create flux spectrum plot similar to GUI display"""
        try:
            import matplotlib.pyplot as plt
            
            if not result.best_matches:
                return None
                
            # Get the best match
            best_match = result.best_matches[0]
            
            # Create figure
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111)
            
            # Get observed spectrum
            obs_wave = result.processed_spectrum['log_wave']
            obs_flux = result.processed_spectrum.get('display_flux', result.processed_spectrum['log_flux'])
            
            # Get template spectrum
            template_wave = best_match['spectra']['flux']['wave']
            template_flux = best_match['spectra']['flux']['flux']
            
            # Plot spectra
            ax.plot(obs_wave, obs_flux, color='#0078d4', linewidth=2, alpha=0.9, label='Input Spectrum')
            from snid_sage.shared.utils import clean_template_name
            clean_name = clean_template_name(best_match['name'])
            
            # Get redshift uncertainty if available
            redshift_error = best_match.get('redshift_error', 0)
            if redshift_error > 0:
                redshift_text = f"z={best_match['redshift']:.5f}±{redshift_error:.5f}"
            else:
                redshift_text = f"z={best_match['redshift']:.5f}"
            
            ax.plot(template_wave, template_flux, color='#E74C3C', linewidth=2.5, alpha=0.8, 
                   label=f"{clean_name} ({redshift_text})")
            
            # Add labels and styling
            ax.set_xlabel('Wavelength (Å)', fontsize=12)
            ax.set_ylabel('Flux', fontsize=12)
            ax.set_title(f"Flux View - Best Match: {clean_name}", fontsize=14)
            ax.legend(loc='upper right', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Add info text
            template = best_match.get('template', {})
            subtype = template.get('subtype', best_match.get('type', 'Unknown'))
            
            # Use RLAP-cos if available, otherwise RLAP
            rlap_cos = best_match.get('rlap_cos')
            if rlap_cos is not None:
                metric_text = f"RLAP-cos = {rlap_cos:.2f}"
            else:
                metric_text = f"RLAP = {best_match['rlap']:.2f}"
            
            info_text = (f"Type: {subtype}, Age: {best_match['age']:.1f}d\n"
                        f"z = {best_match['redshift']:.5f}\n"
                        f"{metric_text}")
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            _LOGGER.error(f"Error creating flux plot: {e}")
            return None
    
    def _create_flattened_plot(self, result):
        """Create flattened spectrum plot similar to GUI display"""
        try:
            import matplotlib.pyplot as plt
            
            if not result.best_matches:
                return None
                
            # Get the best match
            best_match = result.best_matches[0]
            
            # Create figure
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111)
            
            # Get observed spectrum (flattened)
            obs_wave = result.processed_spectrum['log_wave']
            obs_flux = result.processed_spectrum.get('display_flat', result.processed_spectrum['flat_flux'])
            
            # Get template spectrum (flattened)
            template_wave = best_match['spectra']['flat']['wave']
            template_flux = best_match['spectra']['flat']['flux']
            
            # Plot spectra
            ax.plot(obs_wave, obs_flux, color='#0078d4', linewidth=2, alpha=0.9, label='Input Spectrum')
            from snid_sage.shared.utils import clean_template_name
            clean_name = clean_template_name(best_match['name'])
            
            # Get redshift uncertainty if available
            redshift_error = best_match.get('redshift_error', 0)
            if redshift_error > 0:
                redshift_text = f"z={best_match['redshift']:.5f}±{redshift_error:.5f}"
            else:
                redshift_text = f"z={best_match['redshift']:.5f}"
            
            ax.plot(template_wave, template_flux, color='#E74C3C', linewidth=2.5, alpha=0.8, 
                   label=f"{clean_name} ({redshift_text})")
            
            # Add labels and styling
            ax.set_xlabel('Wavelength (Å)', fontsize=12)
            ax.set_ylabel('Flattened Flux', fontsize=12)
            ax.set_title(f"Flattened View - Best Match: {clean_name}", fontsize=14)
            ax.legend(loc='upper right', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Add info text
            template = best_match.get('template', {})
            subtype = template.get('subtype', best_match.get('type', 'Unknown'))
            
            # Use RLAP-cos if available, otherwise RLAP
            rlap_cos = best_match.get('rlap_cos')
            if rlap_cos is not None:
                metric_text = f"RLAP-cos = {rlap_cos:.2f}"
            else:
                metric_text = f"RLAP = {best_match['rlap']:.2f}"
            
            info_text = (f"Type: {subtype}, Age: {best_match['age']:.1f}d\n"
                        f"z = {best_match['redshift']:.5f}\n"
                        f"{metric_text}")
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            _LOGGER.error(f"Error creating flattened plot: {e}")
            return None
    
    def _save_analysis_summary(self, result, results_dir):
        """Save analysis summary text file"""
        try:
            import os
            from snid_sage.shared.utils.results_formatter import create_unified_formatter
            
            # Get spectrum name
            spectrum_name = "Unknown"
            if hasattr(self.gui, 'input_file_path') and self.gui.input_file_path:
                spectrum_name = os.path.splitext(os.path.basename(self.gui.input_file_path))[0]
            elif hasattr(result, 'spectrum_name') and result.spectrum_name:
                spectrum_name = result.spectrum_name
            
            _LOGGER.debug(f"📄 Creating summary for spectrum: {spectrum_name}")
            _LOGGER.debug(f"📄 Results directory: {results_dir}")
            
            # Create formatter and get summary
            formatter = create_unified_formatter(result, spectrum_name)
            summary_text = formatter.get_display_summary()
            
            _LOGGER.debug(f"📄 Summary text length: {len(summary_text)} characters")
            _LOGGER.debug(f"📄 Summary preview: {summary_text[:200]}...")
            
            # Save summary file
            summary_path = os.path.join(results_dir, "analysis_summary.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            
            _LOGGER.info(f"📄 Saved analysis summary to {summary_path}")
            
            # Verify file was created and has content
            if os.path.exists(summary_path):
                file_size = os.path.getsize(summary_path)
                _LOGGER.info(f"📄 Summary file created successfully, size: {file_size} bytes")
            else:
                _LOGGER.error(f"📄 Summary file was not created at {summary_path}")
            
        except Exception as e:
            _LOGGER.error(f"Failed to save analysis summary: {e}")
            import traceback
            _LOGGER.error(f"Traceback: {traceback.format_exc()}")
    
    def _reset_analysis_ui(self):
        """Reset UI after analysis completion/cancellation/error"""
        # Reset analysis button
        if hasattr(self.gui, 'analysis_btn'):
            self.gui.analysis_btn.configure(text="🚀 Analysis", state='normal')
        
        # Re-enable other controls
        if hasattr(self.gui, 'load_btn'):
            self.gui.load_btn.configure(state='normal')
        if hasattr(self.gui, 'preprocess_btn'):
            self.gui.preprocess_btn.configure(state='normal')
        
        # Clean up thread references
        if hasattr(self, 'analysis_thread'):
            del self.analysis_thread
    
    def enable_plot_navigation(self):
        """Enable plot navigation buttons after successful analysis"""
        try:
            # Enable navigation buttons (now in plot selector panel)
            if hasattr(self.gui, 'nav_buttons'):
                for btn in self.gui.nav_buttons:
                    btn.config(state='normal')
            
            # Enable plot buttons in plot selector panel
            if hasattr(self.gui, 'plot_buttons'):
                for btn in self.gui.plot_buttons:
                    btn.config(state='normal')
                    
            _LOGGER.debug("✅ Plot navigation and controls enabled")
            
        except Exception as e:
            _LOGGER.error(f"Error enabling plot navigation: {e}")
    
    def show_results_summary(self, result):
        """Show results summary using unified formatter for consistency with CLI"""
        if not result.success:
            return
            
        summary_window = tk.Toplevel(self.gui.master)
        summary_window.title("📊 SNID-SAGE Analysis Results")
        summary_window.geometry("900x700")
        summary_window.configure(bg=self.gui.theme_manager.get_color('bg_secondary'))
        
        # Make window OS-compatible with proper window controls
        summary_window.transient(self.gui.master)
        summary_window.resizable(True, True)  # Allow resize
        summary_window.minsize(700, 500)  # Set minimum size
        
        # Set window attributes for cross-platform OS compatibility
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows: Enable minimize/maximize buttons and proper window controls
                summary_window.wm_attributes('-toolwindow', False)
                # Ensure normal window decorations on Windows
                summary_window.wm_state('normal')
            elif system == "Darwin":  # macOS
                # macOS: Enable full window controls (close, minimize, maximize)
                summary_window.wm_attributes('-modified', False)
                summary_window.wm_attributes('-titlepath', '')
            elif system == "Linux":
                # Linux: Standard window manager integration
                summary_window.wm_state('normal')
                # Most Linux WMs will handle window controls automatically
        except Exception as e:
            # Fallback: just ensure basic window functionality
            summary_window.wm_state('normal')
            pass
        
        # Main container
        main_frame = tk.Frame(summary_window, bg=self.gui.theme_manager.get_color('bg_secondary'))
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Text frame with scrollbar
        text_frame = tk.Frame(main_frame, bg=self.gui.theme_manager.get_color('bg_secondary'))
        text_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        text_widget_config = {
            'wrap': 'word', 
            'font': ('Consolas', 14),  # Increased font size
            'bg': self.gui.theme_manager.get_color('bg_tertiary'), 
            'fg': self.gui.theme_manager.get_color('text_primary'),
            'padx': 15, 
            'pady': 15,  # Added padding for better readability
            'selectbackground': self.gui.theme_manager.get_color('accent'),
            'selectforeground': self.gui.theme_manager.get_color('bg_primary')
        }
        # Create text widget and apply safe configuration
        text_widget = tk.Text(text_frame)
        # Apply configuration safely
        try:
            text_widget.configure(**text_widget_config)
        except tk.TclError:
            # If selectforeground fails, apply without it
            safe_config = {k: v for k, v in text_widget_config.items() if k != 'selectforeground'}
            text_widget.configure(**safe_config)
        
        text_widget.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview,
                               bg=self.gui.theme_manager.get_color('bg_secondary'),
                               troughcolor=self.gui.theme_manager.get_color('bg_tertiary'),
                               activebackground=self.gui.theme_manager.get_color('accent'))
        scrollbar.pack(side='right', fill='y')
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Use unified formatter for consistent output with CLI
        try:
            from snid_sage.shared.utils.results_formatter import create_unified_formatter
            spectrum_name = getattr(result, 'spectrum_name', 'Unknown')
            formatter = create_unified_formatter(result, spectrum_name)
            summary_text = formatter.get_display_summary()
        except ImportError:
            # Fallback if formatter not available
            summary_text = f"Analysis Results for {getattr(result, 'spectrum_name', 'Unknown')}\n"
            summary_text += f"Type: {result.consensus_type}\n"
            summary_text += f"Redshift: {result.redshift:.5f}\n"
            summary_text += f"RLAP: {result.rlap:.2f}\n"
        
        text_widget.insert('1.0', summary_text)
        text_widget.config(state='disabled')  # Make read-only
        
        # Button frame for export options (same as CLI can save)
        button_frame = tk.Frame(main_frame, bg=self.gui.theme_manager.get_color('bg_secondary'))
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Export buttons - increased font size
        export_txt_btn = tk.Button(button_frame, text="💾 Export Text", 
                                   font=('Arial', 12),
                                   bg=self.gui.theme_manager.get_color('btn_primary'),
                                   fg=self.gui.theme_manager.get_color('text_on_accent'),
                                   activebackground=self.gui.theme_manager.get_color('btn_primary_hover'),
                                   relief='raised', bd=2, padx=15, pady=8,
                                   command=lambda: self._export_results(result, 'txt'))
        
        export_json_btn = tk.Button(button_frame, text="📄 Export JSON", 
                                    font=('Arial', 12),
                                    bg=self.gui.theme_manager.get_color('btn_primary'),
                                    fg=self.gui.theme_manager.get_color('text_on_accent'),
                                    activebackground=self.gui.theme_manager.get_color('btn_primary_hover'),
                                    relief='raised', bd=2, padx=15, pady=8,
                                    command=lambda: self._export_results(result, 'json'))
        
        export_csv_btn = tk.Button(button_frame, text="📊 Export CSV", 
                                   font=('Arial', 12),
                                   bg=self.gui.theme_manager.get_color('btn_primary'),
                                   fg=self.gui.theme_manager.get_color('text_on_accent'),
                                   activebackground=self.gui.theme_manager.get_color('btn_primary_hover'),
                                   relief='raised', bd=2, padx=15, pady=8,
                                   command=lambda: self._export_results(result, 'csv'))
        
        close_btn = tk.Button(button_frame, text="✅ Close", 
                              font=('Arial', 12, 'bold'),
                              bg=self.gui.theme_manager.get_color('btn_success'),
                              fg=self.gui.theme_manager.get_color('text_on_accent'),
                              activebackground=self.gui.theme_manager.get_color('btn_success_hover'),
                              relief='raised', bd=2, padx=25, pady=8,
                              command=summary_window.destroy)
        
        # Pack buttons
        export_txt_btn.pack(side='left', padx=(0, 5))
        export_json_btn.pack(side='left', padx=5)
        export_csv_btn.pack(side='left', padx=5)
        close_btn.pack(side='right')
        
        # Center the window and ensure proper display
        summary_window.update_idletasks()
        x = (summary_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (summary_window.winfo_screenheight() // 2) - (700 // 2)
        summary_window.geometry(f"900x700+{x}+{y}")
        
        # Bring window to front and give it focus
        summary_window.lift()
        summary_window.focus_force()
    
    def _export_results(self, result, format_type):
        """Export results using unified formatter (same format as CLI)"""
        try:
            from tkinter import filedialog, messagebox
            from snid_sage.shared.utils.results_formatter import create_unified_formatter
            
            # File dialog
            file_extensions = {'txt': '.txt', 'json': '.json', 'csv': '.csv'}
            file_types = {
                'txt': [("Text files", "*.txt")],
                'json': [("JSON files", "*.json")],
                'csv': [("CSV files", "*.csv")]
            }
            
            # Try to get spectrum name from result or gui state
            spectrum_name = getattr(result, 'spectrum_name', None)
            if not spectrum_name and hasattr(self.gui, 'input_file_path'):
                import os
                spectrum_name = os.path.splitext(os.path.basename(self.gui.input_file_path))[0]
            if not spectrum_name:
                spectrum_name = 'Unknown'
            
            default_filename = f"{spectrum_name}_results{file_extensions[format_type]}"
            
            filename = filedialog.asksaveasfilename(
                title=f"Export Results as {format_type.upper()}",
                defaultextension=file_extensions[format_type],
                initialfile=default_filename,  # Fixed: use initialfile instead of initialvalue
                filetypes=file_types[format_type] + [("All files", "*.*")]
            )
            
            if filename:
                formatter = create_unified_formatter(result, spectrum_name)
                formatter.save_to_file(filename, format_type)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
    
    def update_results_display(self, result):
        """Update the main GUI with analysis results"""
        if not result.success:
            _LOGGER.warning("⚠️ Analysis did not succeed - no results to display")
            return
            
        try:
            # Reset template navigation
            self.gui.current_template = 0
            self.gui.current_view = 'flux'
            
            # Ensure view_style is set to "Flux" for initial display
            if hasattr(self.gui, 'view_style') and self.gui.view_style:
                self.gui.view_style.set("Flux")
                _LOGGER.info("🔄 View style explicitly set to Flux after analysis")
            
            # Store results for plotting functions
            self.gui.snid_results = result
            
            # Plot the initial view (flux view with best match)
            self.gui.plot_original_spectra()
            
            # Update segmented control button states after setting view
            if hasattr(self.gui, '_update_segmented_control_buttons'):
                self.gui._update_segmented_control_buttons()
            
            # Enable navigation
            self.enable_plot_navigation()
            
            # Update status labels
            if hasattr(self.gui, 'update_header_status'):
                self.gui.update_header_status(f"✅ Best: {result.template_name} ({result.consensus_type})")
            
            _LOGGER.debug(f"✅ Results display updated - best match: {result.template_name}")
            
        except Exception as e:
            _LOGGER.error(f"Error updating results display: {e}")
            import traceback
            traceback.print_exc() 
    
    def reset_analysis_state(self):
        """Reset analysis controller state to initial values"""
        try:
            _LOGGER.debug("🔄 Resetting analysis controller state...")
            
            # Cancel any running analysis
            if hasattr(self, 'analysis_thread') and self.analysis_thread and self.analysis_thread.is_alive():
                self._analysis_cancelled = True
                
            # Reset analysis state variables
            self._analysis_cancelled = False
            self._analysis_result = None
            self._analysis_trace = None
            self._analysis_error = None
            self.analysis_start_time = None
            self.analysis_running = False
            
            # Close any open progress windows
            if hasattr(self, 'progress_window') and self.progress_window:
                try:
                    if self.progress_window.winfo_exists():
                        self.progress_window.destroy()
                except:
                    pass
                self.progress_window = None
            
            # Clear analysis plotter state if available
            if hasattr(self, 'analysis_plotter') and self.analysis_plotter:
                try:
                    if hasattr(self.analysis_plotter, 'clear_analysis_plots'):
                        self.analysis_plotter.clear_analysis_plots()
                except:
                    pass  # Method may not exist
            
            # Reset UI to initial state
            self._reset_analysis_ui()
            
            _LOGGER.debug("✅ Analysis controller state reset")
            
        except Exception as e:
            _LOGGER.error(f"❌ Error resetting analysis controller: {e}")
    
    def _show_cluster_selection_dialog(self, result):
        """Show the cluster selection dialog for user to choose best cluster"""
        try:
            from snid_sage.interfaces.gui.components.dialogs.cluster_selection_dialog import show_cluster_selection_dialog
            
            clustering_results = result.clustering_results
            
            # Validate clustering results before showing dialog
            if not self._is_clustering_available(result):
                _LOGGER.warning("Clustering results not valid - falling back to automatic selection")
                self._complete_analysis_workflow(result)
                return
            
            # Show cluster selection dialog
            dialog = show_cluster_selection_dialog(
                parent=self.gui.master,
                clustering_results=clustering_results,
                theme_manager=self.gui.theme_manager,
                snid_result=result,
                callback=lambda cluster, index: self._on_cluster_selected(cluster, index, result)
            )
            
            _LOGGER.info(f"🎯 Showing cluster selection dialog with {len(clustering_results.get('all_candidates', []))} candidates")
            
        except Exception as e:
            _LOGGER.error(f"Error showing cluster selection dialog: {e}")
            # Fallback to automatic selection
            self._complete_analysis_workflow(result)
    
    def _on_cluster_selected(self, selected_cluster, cluster_index, result):
        """Handle user's cluster selection"""
        try:
            self.selected_cluster = selected_cluster
            self.selected_cluster_index = cluster_index
            self.cluster_selection_made = True
            
            # Update the clustering results with user's selection
            if hasattr(result, 'clustering_results'):
                result.clustering_results['user_selected_cluster'] = selected_cluster
                result.clustering_results['user_selected_index'] = cluster_index
                
                # DO NOT overwrite best_cluster - keep the original automatic best
                # This allows the formatter to distinguish between automatic and manual selection
            
            # CRITICAL: Filter best_matches to only show templates from selected cluster
            if hasattr(result, 'best_matches') and selected_cluster.get('matches'):
                cluster_matches = selected_cluster.get('matches', [])
                
                # Sort cluster matches by best available metric (RLAP-Cos if available, otherwise RLAP) descending
                from snid_sage.shared.utils.math_utils import get_best_metric_value
                cluster_matches_sorted = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
                
                # Update best_matches to only contain cluster templates using user-configured limit
                max_templates = self.gui._safe_int(self.gui.params.get('max_output_templates', ''), 10)
                result.best_matches = cluster_matches_sorted[:max_templates]
                
                # Also update top_matches for consistency
                result.top_matches = cluster_matches_sorted[:max_templates]
                
                # CRITICAL: Update top-level result properties to reflect the best match from the selected cluster
                if cluster_matches_sorted:
                    best_cluster_match = cluster_matches_sorted[0]
                    template = best_cluster_match.get('template', {})
                    
                    # Update primary match properties
                    from snid_sage.shared.utils import clean_template_name
                    result.template_name = clean_template_name(best_cluster_match.get('name', 'Unknown'))
                    result.redshift = best_cluster_match.get('redshift', 0.0)
                    result.redshift_error = best_cluster_match.get('redshift_error', 0.0)
                    result.rlap = best_cluster_match.get('rlap', 0.0)
                    result.r = best_cluster_match.get('r', 0.0)
                    result.lap = best_cluster_match.get('lap', 0.0)
                    
                    # Update template properties
                    result.template_type = template.get('type', selected_cluster.get('type', 'Unknown'))
                    result.template_subtype = template.get('subtype', '')
                    result.template_age = template.get('age', 0.0)
                    
                    # Update consensus type to match cluster type
                    result.consensus_type = selected_cluster.get('type', 'Unknown')
                    if result.template_subtype and result.template_subtype != 'Unknown':
                        result.best_subtype = result.template_subtype
                    
                    _LOGGER.info(f"🎯 Updated result properties to cluster best match: {result.template_name} "
                                f"(Type: {result.consensus_type}, RLAP: {result.rlap:.2f}, z: {result.redshift:.4f})")
                
                # Reset template navigation to start from the best template in cluster
                if hasattr(self.gui, 'current_template'):
                    self.gui.current_template = 0
                
                _LOGGER.info(f"🎯 Filtered templates: {len(cluster_matches)} cluster matches -> "
                            f"{len(result.best_matches)} displayed templates")
                clean_top_name = clean_template_name(result.best_matches[0].get('name', 'Unknown'))
                _LOGGER.debug(f"   Top template from cluster: {clean_top_name} "
                             f"(RLAP: {result.best_matches[0].get('rlap', 0):.2f})")
                
                # Show template names for better debugging
                if _LOGGER.isEnabledFor(logging.DEBUG) and len(result.best_matches) > 1:
                    from snid_sage.shared.utils import clean_template_name
                    template_names = [f"{clean_template_name(match.get('name', 'Unknown'))} (RLAP: {match.get('rlap', 0):.2f})" 
                                    for match in result.best_matches[:5]]  # Show first 5
                    _LOGGER.debug(f"   Displayed templates: {', '.join(template_names)}")
                    if len(result.best_matches) > 5:
                        _LOGGER.debug(f"   ... and {len(result.best_matches) - 5} more templates")
            
            _LOGGER.info(f"✅ User selected cluster {cluster_index + 1}: {selected_cluster.get('type')} "
                        f"(Size: {selected_cluster.get('size')}, RLAP: {selected_cluster.get('mean_rlap', 0):.2f})")
            
            # Continue with analysis workflow
            self._complete_analysis_workflow(result)
            
        except Exception as e:
            _LOGGER.error(f"Error handling cluster selection: {e}")
            # Fallback to automatic selection
            self._complete_analysis_workflow(result)
    
    def _complete_analysis_workflow(self, result):
        """Complete the analysis workflow after cluster selection (if needed)"""
        try:
            # Update GUI with results
            if result and result.success:
                self.gui.update_results_display(result)
                self.gui.enable_plot_navigation()
                
                # Show unified analysis summary (combines results + cluster info)
                self.show_results_summary(result)
                
                # Update status
                if hasattr(self.gui, 'update_header_status'):
                    status_msg = f"✅ Best: {result.template_name} ({result.consensus_type})"
                    if self.cluster_selection_made:
                        status_msg += f" [Cluster #{self.selected_cluster_index + 1}]"
                    self.gui.update_header_status(status_msg)
                
                # Update button states and navigation
                if hasattr(self.gui, 'workflow_integrator') and self.gui.workflow_integrator:
                    # Analysis is complete - set workflow state
                    self.gui.workflow_integrator.set_analysis_complete()
                    _LOGGER.info("🔄 Analysis complete: Workflow state set to ANALYSIS_COMPLETE")

                    # Update status label with chosen type
                    if hasattr(self.gui, 'config_status_label'):
                        chosen_type = result.consensus_type if getattr(result, 'success', False) else None
                        if chosen_type and chosen_type.lower() not in ['unknown', '']:
                            self.gui.config_status_label.configure(
                                text=f"✅ Analysis finished – {chosen_type} selected",
                                fg=self.gui.theme_manager.get_color('text_primary') if hasattr(self.gui, 'theme_manager') else 'black'
                            )
                        else:
                            self.gui.config_status_label.configure(
                                text="⚠️ Analysis finished – No good match",
                                fg=self.gui.theme_manager.get_color('text_secondary') if hasattr(self.gui, 'theme_manager') else 'grey'
                            )
                else:
                    _LOGGER.error("❌ No workflow integrator available - buttons will not update correctly!")

                    # Still update label even without workflow integrator
                    if hasattr(self.gui, 'config_status_label'):
                        chosen_type = result.consensus_type if getattr(result, 'success', False) else None
                        if chosen_type and chosen_type.lower() not in ['unknown', '']:
                            self.gui.config_status_label.configure(
                                text=f"✅ Analysis finished – {chosen_type} selected",
                                fg=self.gui.theme_manager.get_color('text_primary') if hasattr(self.gui, 'theme_manager') else 'black'
                            )
                        else:
                            self.gui.config_status_label.configure(
                                text="⚠️ Analysis finished – No good match",
                                fg=self.gui.theme_manager.get_color('text_secondary') if hasattr(self.gui, 'theme_manager') else 'grey'
                            )
                
                self.gui.master.update_idletasks()
                
                # Only show completion message if games are running (no popup otherwise)
                if hasattr(self, 'game_thread'):
                    try:
                        from snid_sage.snid.games import set_analysis_complete
                        result_summary = f"Type: {result.consensus_type}, z={result.redshift:.4f}, RLAP={result.rlap:.2f}"
                        if self.cluster_selection_made:
                            result_summary += f", Cluster #{self.selected_cluster_index + 1}"
                        set_analysis_complete(result_summary)
                        _LOGGER.debug("🎮 Notified game of analysis completion")
                    except Exception as e:
                        _LOGGER.error(f"Failed to notify game: {e}")
                
                # Handle automatic saving if enabled (after cluster selection)
                self._handle_automatic_saving(result)
                
                _LOGGER.info(f"✅ Analysis complete: {result.consensus_type} at z={result.redshift:.4f}")
            
            else:
                self.gui.update_header_status("⚠️ Analysis finished – No good match")
                # Update status label to reflect no good match
                if hasattr(self.gui, 'config_status_label'):
                    self.gui.config_status_label.configure(
                        text="⚠️ Analysis finished – No good match",
                        fg=self.gui.theme_manager.get_color('text_secondary') if hasattr(self.gui, 'theme_manager') else 'grey'
                    )
                # Handle no matches case...
                
        except Exception as e:
            _LOGGER.error(f"Error completing analysis workflow: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._reset_analysis_ui()
    
    def _is_clustering_available(self, result):
        """Check if clustering results are available and valid"""
        try:
            if not hasattr(result, 'clustering_results') or not result.clustering_results:
                return False
                
            clustering_results = result.clustering_results
            
            # Check if clustering was successful
            if not clustering_results.get('success', False):
                return False
                
            # Check if we have multiple clusters to choose from
            all_candidates = clustering_results.get('all_candidates', [])
            if len(all_candidates) <= 1:
                return False
                
            # Verify clusters have required data
            for cluster in all_candidates:
                if not isinstance(cluster, dict) or not cluster.get('matches'):
                    return False
                    
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error checking clustering availability: {e}")
            return False
    

    
    def _handle_analysis_success(self, result, trace):
        # Implementation of _handle_analysis_success method
        pass 
