"""
SNID SAGE - Manual Selection Controller
======================================

Controller for managing manual selections and interactive analysis
in the emission line dialog. Coordinates between UI, tools, and analysis.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

_LOGGER = logging.getLogger(__name__)

try:
    from snid_sage.shared.utils.line_detection.interactive_fwhm_analyzer import InteractiveFWHMAnalyzer
    from snid_sage.interfaces.gui.components.analysis.interactive_line_tools import InteractiveLineTools, LivePreviewManager
except ImportError as e:
    _LOGGER.error(f"Failed to import required modules: {e}")
    # Create placeholder classes if imports fail
    class InteractiveFWHMAnalyzer:
        def __init__(self):
            pass
        def measure_fwhm_interactive(self, *args, **kwargs):
            return {'error': 'InteractiveFWHMAnalyzer not available'}
        def set_manual_region(self, *args): pass
        def set_manual_points(self, *args): pass
        def clear_manual_selections(self, *args): pass
    
    class InteractiveLineTools:
        def __init__(self, *args):
            pass
        def set_analysis_callback(self, callback): pass
        def set_status_callback(self, callback): pass
        def set_analysis_mode(self, mode): pass
        def set_selected_line(self, line): pass
        def get_manual_selection(self, line): return {}
        def clear_selections(self, line=None): pass
    
    class LivePreviewManager:
        def __init__(self, *args):
            pass
        def update_preview(self, *args): pass
        def clear_preview(self): pass


class ManualSelectionController:
    """Controller for managing manual line analysis selections"""
    
    def __init__(self, parent_dialog):
        self.parent = parent_dialog
        
        # Core components
        self.analyzer = InteractiveFWHMAnalyzer()
        self.interactive_tools = None
        self.preview_manager = None
        
        # Current state
        self.current_analysis_mode = 'auto'
        self.selected_line_for_analysis = None
        
        # Analysis parameters
        self.analysis_parameters = {
            'method': 'gaussian',
            'baseline_method': 'edges',
            'min_points': 3,
            'fallback_methods': ['empirical', 'simple_width'],
            'adaptive_region': True
        }
        
        # Results storage
        self.interactive_results = {}
        
        _LOGGER.info("Manual selection controller initialized")
    
    def setup_interactive_tools(self, canvas, ax_main):
        """Set up interactive tools with the plot canvas"""
        self.interactive_tools = InteractiveLineTools(self.parent, canvas, ax_main)
        
        # Set up callbacks
        self.interactive_tools.set_analysis_callback(self._on_interactive_analysis_requested)
        self.interactive_tools.set_status_callback(self._on_status_update)
        
        _LOGGER.debug("Interactive tools configured")
    
    def setup_preview_manager(self, preview_figure, preview_ax):
        """Set up live preview manager"""
        self.preview_manager = LivePreviewManager(preview_figure, preview_ax)
        _LOGGER.debug("Preview manager configured")
    
    def set_analysis_mode(self, mode: str):
        """Set the current analysis mode"""
        valid_modes = ['auto', 'manual_region', 'manual_points', 'baseline_fit', 'peak_mark']
        
        if mode not in valid_modes:
            _LOGGER.warning(f"Invalid analysis mode: {mode}")
            return
        
        self.current_analysis_mode = mode
        
        # Update interactive tools
        if self.interactive_tools:
            if mode == 'manual_region':
                self.interactive_tools.set_analysis_mode('region')
            elif mode == 'manual_points':
                self.interactive_tools.set_analysis_mode('points')
            elif mode == 'baseline_fit':
                self.interactive_tools.set_analysis_mode('baseline')
            elif mode == 'peak_mark':
                self.interactive_tools.set_analysis_mode('peak')
            else:
                self.interactive_tools.set_analysis_mode('select')
        
        _LOGGER.info(f"Analysis mode set to: {mode}")
    
    def set_selected_line(self, line_name: str):
        """Set the currently selected line for analysis"""
        self.selected_line_for_analysis = line_name
        
        if self.interactive_tools:
            self.interactive_tools.set_selected_line(line_name)
        
        # Update preview if we have previous results
        if line_name in self.interactive_results:
            self._update_preview_for_line(line_name)
        else:
            if self.preview_manager:
                self.preview_manager.clear_preview()
        
        _LOGGER.debug(f"Selected line for interactive analysis: {line_name}")
    
    def update_analysis_parameters(self, parameters: Dict[str, Any]):
        """Update analysis parameters"""
        self.analysis_parameters.update(parameters)
        _LOGGER.debug(f"Updated analysis parameters: {parameters}")
    
    def analyze_selected_line(self, line_name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze the selected line with current settings"""
        
        if line_name is None:
            line_name = self.selected_line_for_analysis
        
        if line_name is None:
            _LOGGER.warning("No line selected for analysis")
            return {'error': 'No line selected'}
        
        # Get spectrum data
        spectrum_data = getattr(self.parent, 'spectrum_data', {})
        if not spectrum_data or 'wavelength' not in spectrum_data:
            return {'error': 'No spectrum data available'}
        
        wavelength = spectrum_data['wavelength']
        flux = spectrum_data['flux']
        
        # Get line information
        line_center = self._get_line_center_wavelength(line_name)
        if line_center is None:
            return {'error': f'Could not determine center wavelength for {line_name}'}
        
        # Build analysis configuration
        analysis_config = self._build_analysis_config(line_name)
        
        # Set up manual selections in analyzer
        self._configure_analyzer_selections(line_name)
        
        # Perform analysis
        result = self.analyzer.measure_fwhm_interactive(
            wavelength, flux, line_center, analysis_config)
        
        # Store result
        self.interactive_results[line_name] = result
        
        # Update preview
        self._update_preview_for_line(line_name)
        
        _LOGGER.info(f"Analyzed line {line_name}: {'Success' if 'error' not in result else result['error']}")
        
        return result
    
    def get_analysis_results(self) -> Dict[str, Any]:
        """Get all interactive analysis results"""
        return self.interactive_results.copy()
    
    def analyze_line(self, line_name: str, obs_wavelength: float, 
                    wavelength: np.ndarray, flux: np.ndarray, 
                    method: str = 'gaussian') -> Dict[str, Any]:
        """
        Analyze a single line using the enhanced FWHM analyzer
        
        Args:
            line_name: Name of the line
            obs_wavelength: Observed wavelength of the line
            wavelength: Full wavelength array
            flux: Full flux array
            method: Analysis method ('gaussian', 'empirical', etc.)
            
        Returns:
            Analysis results dictionary
        """
        # Update analysis parameters with the specified method
        self.analysis_parameters['method'] = method
        
        # Check if we have manual selections for this line
        manual_selection = {}
        if self.interactive_tools:
            manual_selection = self.interactive_tools.get_manual_selection(line_name)
        
        # Build analysis configuration
        analysis_config = {
            'method': method,
            'baseline_method': self.analysis_parameters.get('baseline_method', 'edges'),
            'min_points': self.analysis_parameters.get('min_points', 3),
            'fallback_methods': self.analysis_parameters.get('fallback_methods', ['empirical', 'simple_width']),
            'adaptive_region': self.analysis_parameters.get('adaptive_region', True),
            'manual_selection': manual_selection
        }
        
        # Configure analyzer if we have manual selections
        if manual_selection:
            if manual_selection.get('type') == 'manual_region':
                region = manual_selection.get('region', (obs_wavelength - 20, obs_wavelength + 20))
                self.analyzer.set_manual_region(obs_wavelength, region[0], region[1])
            elif manual_selection.get('type') == 'manual_points':
                points = manual_selection.get('points', [])
                if points:
                    self.analyzer.set_manual_points(obs_wavelength, points)
        
        # Run enhanced analysis
        result = self.analyzer.measure_fwhm_interactive(
            wavelength, flux, obs_wavelength, analysis_config)
        
        # Store result
        self.interactive_results[line_name] = result
        
        # Update preview if available
        if self.preview_manager:
            self.preview_manager.update_preview(line_name, wavelength, flux, result)
        
        return result
    
    def clear_selections_for_line(self, line_name: str):
        """Clear manual selections for a specific line"""
        if self.interactive_tools:
            self.interactive_tools.clear_selections(line_name)
        
        line_center = self._get_line_center_wavelength(line_name)
        if line_center:
            self.analyzer.clear_manual_selections(line_center)
        
        # Remove from results
        self.interactive_results.pop(line_name, None)
        
        _LOGGER.debug(f"Cleared selections for line: {line_name}")
    
    def clear_all_selections(self):
        """Clear all manual selections"""
        if self.interactive_tools:
            self.interactive_tools.clear_selections()
        
        self.analyzer.clear_manual_selections()
        self.interactive_results.clear()
        
        if self.preview_manager:
            self.preview_manager.clear_preview()
        
        _LOGGER.debug("Cleared all manual selections")
    
    def _on_interactive_analysis_requested(self, line_name: str):
        """Callback when interactive tools request analysis update"""
        result = self.analyze_selected_line(line_name)
        
        # Provide user feedback
        if hasattr(self.parent, '_update_status'):
            if 'error' in result:
                self.parent._update_status(f"Analysis failed for {line_name}: {result['error']}")
            else:
                fwhm_vel = result.get('fwhm_velocity', 0)
                method = result.get('fitting_method', 'unknown')
                self.parent._update_status(f"{line_name}: FWHM = {fwhm_vel:.1f} km/s ({method})")
    
    def _on_status_update(self, message: str):
        """Callback for status updates from interactive tools"""
        if hasattr(self.parent, '_update_status'):
            self.parent._update_status(message)
    
    def _get_line_center_wavelength(self, line_name: str) -> Optional[float]:
        """Get the observed center wavelength for a line"""
        
        # Check in SN lines
        if hasattr(self.parent, 'sn_lines') and line_name in self.parent.sn_lines:
            obs_wavelength, line_data = self.parent.sn_lines[line_name]
            return obs_wavelength
        
        # Check in galaxy lines
        if hasattr(self.parent, 'galaxy_lines') and line_name in self.parent.galaxy_lines:
            obs_wavelength, line_data = self.parent.galaxy_lines[line_name]
            return obs_wavelength
        
        _LOGGER.warning(f"Could not find center wavelength for line: {line_name}")
        return None
    
    def _build_analysis_config(self, line_name: str) -> Dict[str, Any]:
        """Build analysis configuration for a line"""
        
        config = self.analysis_parameters.copy()
        
        # Add mode-specific settings
        if self.current_analysis_mode == 'manual_region':
            config['use_manual_region'] = True
            config['adaptive_region'] = False
        elif self.current_analysis_mode == 'manual_points':
            config['use_manual_points'] = True
            config['min_points'] = 2
        elif self.current_analysis_mode == 'baseline_fit':
            config['use_manual_baseline'] = True
            config['baseline_method'] = 'manual'
        elif self.current_analysis_mode == 'peak_mark':
            config['use_manual_peak'] = True
        else:
            # Auto mode
            config['adaptive_region'] = True
            config['min_points'] = 3
        
        return config
    
    def _configure_analyzer_selections(self, line_name: str):
        """Configure the analyzer with manual selections"""
        
        if not self.interactive_tools:
            return
        
        line_center = self._get_line_center_wavelength(line_name)
        if line_center is None:
            return
        
        # Get manual selections from interactive tools
        selections = self.interactive_tools.get_manual_selection(line_name)
        
        if 'region' in selections:
            start_wave, end_wave = selections['region']
            self.analyzer.set_manual_region(line_center, start_wave, end_wave)
        
        if 'points' in selections:
            points = selections['points']
            wavelength_points = [point[0] for point in points]
            self.analyzer.set_manual_points(line_center, wavelength_points)
    
    def _update_preview_for_line(self, line_name: str):
        """Update the live preview for a specific line"""
        
        if not self.preview_manager:
            return
        
        if line_name not in self.interactive_results:
            return
        
        result = self.interactive_results[line_name]
        
        # Get the analysis region data for preview
        line_center = self._get_line_center_wavelength(line_name)
        if line_center is None:
            return
        
        spectrum_data = getattr(self.parent, 'spectrum_data', {})
        if not spectrum_data:
            return
        
        wavelength = spectrum_data['wavelength']
        flux = spectrum_data['flux']
        
        # Extract region around the line for preview
        if 'wavelength_range' in result:
            w_min, w_max = result['wavelength_range']
            mask = (wavelength >= w_min) & (wavelength <= w_max)
        else:
            # Default region
            mask = (wavelength >= line_center - 25) & (wavelength <= line_center + 25)
        
        if np.any(mask):
            preview_wavelength = wavelength[mask]
            preview_flux = flux[mask]
            
            self.preview_manager.update_preview(line_name, preview_wavelength, preview_flux, result)


class InteractiveAnalysisUI:
    """UI components for interactive analysis controls"""
    
    def __init__(self, parent_frame, controller: ManualSelectionController, theme_colors: Dict[str, str]):
        self.parent_frame = parent_frame
        self.controller = controller
        self.colors = theme_colors
        
        # UI variables
        self.analysis_mode_var = tk.StringVar(value='auto')
        self.current_line_var = tk.StringVar(value="None selected")
        
        # Create UI components
        self._create_mode_controls()
        self._create_line_selection()
        self._create_parameter_controls()
        self._create_action_buttons()
    
    def _create_mode_controls(self):
        """Create analysis mode control buttons"""
        
        mode_frame = tk.LabelFrame(self.parent_frame, text="🛠️ Analysis Mode", 
                                  bg=self.colors.get('bg_step', 'white'), 
                                  fg=self.colors.get('text_primary', 'black'),
                                  font=('Segoe UI', 12, 'bold'))
        mode_frame.pack(fill='x', pady=(0, 10))
        
        # Mode buttons
        buttons_frame = tk.Frame(mode_frame, bg=self.colors.get('bg_step', 'white'))
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        modes = [
            ('auto', '🤖 Auto', 'Automatic analysis'),
            ('manual_region', '📏 Region', 'Manual region selection'),
            ('manual_points', '🎯 Points', 'Point-by-point selection')
        ]
        
        self.mode_buttons = {}
        for i, (mode, text, tooltip) in enumerate(modes):
            btn = tk.Radiobutton(buttons_frame, text=text, variable=self.analysis_mode_var, 
                               value=mode, command=self._on_mode_changed,
                               bg=self.colors.get('bg_step', 'white'),
                               fg=self.colors.get('text_primary', 'black'),
                               font=('Segoe UI', 10))
            btn.grid(row=i//3, column=i%3, sticky='w', padx=5, pady=2)
            self.mode_buttons[mode] = btn
    
    def _create_line_selection(self):
        """Create current line selection dropdown"""
        
        line_frame = tk.Frame(self.parent_frame, bg=self.colors.get('bg_step', 'white'))
        line_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(line_frame, text="Current Line:",
                bg=self.colors.get('bg_step', 'white'),
                fg=self.colors.get('text_primary', 'black'),
                font=('Segoe UI', 11, 'bold')).pack(side='left')
        

        self.line_dropdown = tk.OptionMenu(
            line_frame,
            self.current_line_var,
            "None selected",  # placeholder; real list set in update_line_list()
            command=lambda _sel: self._on_line_selection_changed())

        self.line_dropdown.config(
            font=('Segoe UI', 10),
            bg=self.colors.get('bg_main', 'white'),
            fg=self.colors.get('text_primary', 'black'),
            activebackground=self.colors.get('accent', '#0078d4'),
            activeforeground='white',
            relief='raised', bd=2, width=20, cursor='hand2')

        self.line_dropdown.pack(side='right')
    
    def _create_parameter_controls(self):
        """Create parameter adjustment controls"""
        
        params_frame = tk.LabelFrame(self.parent_frame, text="⚙️ Parameters", 
                                   bg=self.colors.get('bg_step', 'white'),
                                   fg=self.colors.get('text_primary', 'black'),
                                   font=('Segoe UI', 12, 'bold'))
        params_frame.pack(fill='x', pady=(0, 10))
        
        # Fitting method
        method_frame = tk.Frame(params_frame, bg=self.colors.get('bg_step', 'white'))
        method_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(method_frame, text="Method:",
                bg=self.colors.get('bg_step', 'white'),
                fg=self.colors.get('text_primary', 'black'),
                font=('Segoe UI', 10)).pack(side='left')
        
        self.method_var = tk.StringVar(value='gaussian')

        self.method_menu = tk.OptionMenu(
            method_frame,
            self.method_var,
            'gaussian', 'lorentzian', 'empirical',
            command=lambda _sel: self._on_parameter_changed())

        self.method_menu.config(
            width=12,
            font=('Segoe UI', 10),
            bg=self.colors.get('bg_main', 'white'),
            fg=self.colors.get('text_primary', 'black'),
            activebackground=self.colors.get('accent', '#0078d4'),
            activeforeground='white',
            relief='raised', bd=2, cursor='hand2')

        self.method_menu.pack(side='right')
    
    def _create_action_buttons(self):
        """Create action buttons"""
        
        actions_frame = tk.Frame(self.parent_frame, bg=self.colors.get('bg_step', 'white'))
        actions_frame.pack(fill='x', pady=(0, 10))
        
        # Analyze current line
        analyze_btn = tk.Button(actions_frame, text="🔄 Analyze Current",
                              command=self._analyze_current_line,
                              bg=self.colors.get('accent', 'blue'), fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='raised', bd=2, width=15)
        analyze_btn.pack(side='left', padx=(0, 10))
        
        # Clear selections
        clear_btn = tk.Button(actions_frame, text="🗑️ Clear",
                            command=self._clear_current_selections,
                            bg=self.colors.get('warning', 'orange'), fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='raised', bd=2, width=10)
        clear_btn.pack(side='right')
    
    def update_line_list(self, line_names: List[str]):
        """Update the list of available lines in the OptionMenu"""

        menu = self.line_dropdown['menu']
        menu.delete(0, 'end')

        for ln in line_names:
            menu.add_command(label=ln,
                             command=tk._setit(self.current_line_var, ln, lambda _sel=ln: self._on_line_selection_changed()))

        if line_names:
            self.current_line_var.set(line_names[0])
            self._on_line_selection_changed()
    
    def _on_mode_changed(self):
        """Handle analysis mode change"""
        mode = self.analysis_mode_var.get()
        self.controller.set_analysis_mode(mode)
    
    def _on_line_selection_changed(self, event=None):
        """Handle line selection change"""
        line_name = self.current_line_var.get()
        if line_name and line_name != "None selected":
            self.controller.set_selected_line(line_name)
    
    def _on_parameter_changed(self, event=None):
        """Handle parameter changes"""
        parameters = {
            'method': self.method_var.get()
        }
        self.controller.update_analysis_parameters(parameters)
    
    def _analyze_current_line(self):
        """Analyze the currently selected line"""
        line_name = self.current_line_var.get()
        if line_name and line_name != "None selected":
            self.controller.analyze_selected_line(line_name)
    
    def _clear_current_selections(self):
        """Clear selections for current line"""
        line_name = self.current_line_var.get()
        if line_name and line_name != "None selected":
            self.controller.clear_selections_for_line(line_name) 
