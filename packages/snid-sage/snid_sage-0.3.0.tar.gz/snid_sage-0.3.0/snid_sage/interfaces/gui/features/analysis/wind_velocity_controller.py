"""
SNID SAGE - Wind Velocity Analysis Controller
============================================

Controller for managing wind velocity analysis functionality.
Handles integration with the emission line overlay system and provides 
coordination between the main GUI and wind velocity analysis dialogs.

Part of the SNID SAGE GUI system.
"""

from typing import Optional, Dict, Any, List

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.wind_velocity_controller')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.wind_velocity_controller')

# Wind velocity dialog functionality removed - module no longer exists
show_wind_velocity_dialog = None


class WindVelocityController:
    """
    Controller for wind velocity analysis functionality
    
    This controller manages wind velocity analysis, including:
    - Opening wind velocity analysis dialogs for specific lines
    - Managing spectrum data and redshift information
    - Coordinating with emission line overlay system
    - Handling results collection and export
    """
    
    def __init__(self, gui_instance):
        """
        Initialize the wind velocity controller
        
        Args:
            gui_instance: Main GUI instance
        """
        self.gui = gui_instance
        self.active_dialogs = {}  # line_name -> dialog_instance mapping
        self.analysis_results = {}  # line_name -> results mapping
        
        _LOGGER.debug("Wind velocity controller initialized")
    
    def analyze_wind_velocity(self, line_name, line_data, spectrum_data, current_redshift=0.0):
        """
        Open wind velocity analysis for a specific emission line
        
        Args:
            line_name: Name of the emission line
            line_data: Dictionary containing line information
            spectrum_data: Dictionary containing wavelength and flux data
            current_redshift: Current redshift for line positioning
        
        Returns:
            WindVelocityAnalysisDialog instance or None if failed
        """
        try:
            # Validate inputs
            if not line_name or not line_data:
                self._show_invalid_line_error()
                return None
            
            if not spectrum_data or not self._validate_spectrum_data(spectrum_data):
                self._show_invalid_spectrum_error()
                return None
            
            # Close existing dialog for this line if open
            if line_name in self.active_dialogs:
                try:
                    self.active_dialogs[line_name].dialog.destroy()
                except:
                    pass
                del self.active_dialogs[line_name]
            
            # Open new wind velocity analysis dialog
            if show_wind_velocity_dialog:
                dialog = show_wind_velocity_dialog(
                    parent=self.gui.master if hasattr(self.gui, 'master') else self.gui,
                    line_name=line_name,
                    line_data=line_data,
                    spectrum_data=spectrum_data,
                    theme_manager=self.gui.theme_manager,
                    current_redshift=current_redshift
                )
                
                # Store active dialog
                self.active_dialogs[line_name] = dialog
                
                _LOGGER.info(f"🌪️ Opened wind velocity analysis for line: {line_name}")
                return dialog
            else:
                self._show_import_error()
                return None
                
        except Exception as e:
            _LOGGER.error(f"❌ Error opening wind velocity analysis for {line_name}: {e}")
            self._show_generic_error(str(e))
            return None
    
    def _validate_spectrum_data(self, spectrum_data):
        """
        Validate spectrum data for wind velocity analysis
        
        Args:
            spectrum_data: Dictionary containing spectrum data
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(spectrum_data, dict):
            return False
        
        # Check for required keys
        wavelength = spectrum_data.get('wavelength', [])
        flux = spectrum_data.get('flux', [])
        
        # Check if arrays exist and have data
        try:
            if wavelength is None or flux is None:
                return False
            
            # Convert to lists if they're numpy arrays for length checking
            import numpy as np
            if isinstance(wavelength, np.ndarray):
                wavelength_len = wavelength.size
            else:
                wavelength_len = len(wavelength)
                
            if isinstance(flux, np.ndarray):
                flux_len = flux.size
            else:
                flux_len = len(flux)
            
            if wavelength_len == 0 or flux_len == 0:
                return False
                
        except Exception as e:
            _LOGGER.warning(f"Error validating spectrum data: {e}")
            return False
        
            # Check if arrays have same length
            if wavelength_len != flux_len:
                _LOGGER.warning(f"Wavelength and flux arrays have different lengths: {wavelength_len} vs {flux_len}")
                return False
        
        return True
    
    def get_analysis_results(self, line_name=None):
        """
        Get wind velocity analysis results
        
        Args:
            line_name: Specific line name, or None for all results
            
        Returns:
            Dictionary containing analysis results
        """
        if line_name:
            # Get results for specific line
            if line_name in self.active_dialogs:
                return self.active_dialogs[line_name].get_results()
            elif line_name in self.analysis_results:
                return self.analysis_results[line_name]
            else:
                return None
        else:
            # Get all results
            all_results = {}
            
            # Get results from active dialogs
            for name, dialog in self.active_dialogs.items():
                all_results[name] = dialog.get_results()
            
            # Add stored results
            for name, results in self.analysis_results.items():
                if name not in all_results:
                    all_results[name] = results
            
            return all_results
    
    def save_analysis_results(self, line_name=None):
        """
        Save analysis results from active dialogs
        
        Args:
            line_name: Specific line name, or None for all active dialogs
        """
        if line_name:
            # Save specific line results
            if line_name in self.active_dialogs:
                results = self.active_dialogs[line_name].get_results()
                self.analysis_results[line_name] = results
                _LOGGER.debug(f"Saved wind velocity results for {line_name}")
        else:
            # Save all active dialog results
            for name, dialog in self.active_dialogs.items():
                results = dialog.get_results()
                if results['total_measurements'] > 0:
                    self.analysis_results[name] = results
                    _LOGGER.debug(f"Saved wind velocity results for {name}")
    
    def close_analysis_dialog(self, line_name):
        """
        Close wind velocity analysis dialog for specific line
        
        Args:
            line_name: Name of the emission line
        """
        if line_name in self.active_dialogs:
            try:
                # Save results before closing
                self.save_analysis_results(line_name)
                
                # Close dialog
                self.active_dialogs[line_name].dialog.destroy()
                del self.active_dialogs[line_name]
                
                _LOGGER.info(f"Closed wind velocity analysis for {line_name}")
            except Exception as e:
                _LOGGER.error(f"Error closing wind velocity analysis for {line_name}: {e}")
    
    def close_all_dialogs(self):
        """Close all active wind velocity analysis dialogs"""
        try:
            # Save all results first
            self.save_analysis_results()
            
            # Close all dialogs
            for line_name in list(self.active_dialogs.keys()):
                try:
                    self.active_dialogs[line_name].dialog.destroy()
                except:
                    pass
            
            self.active_dialogs.clear()
            _LOGGER.info("Closed all wind velocity analysis dialogs")
            
        except Exception as e:
            _LOGGER.error(f"Error closing all wind velocity dialogs: {e}")
    
    def get_summary_statistics(self):
        """
        Get summary statistics of all wind velocity measurements
        
        Returns:
            Dictionary containing summary statistics
        """
        all_results = self.get_analysis_results()
        
        if not all_results:
            return {
                'total_lines_analyzed': 0,
                'total_measurements': 0,
                'average_velocity': 0,
                'velocity_range': (0, 0),
                'lines_analyzed': []
            }
        
        # Collect all measurements
        all_velocities = []
        total_measurements = 0
        lines_analyzed = []
        
        for line_name, results in all_results.items():
            measurements = results.get('measurements', [])
            if measurements:
                lines_analyzed.append(line_name)
                total_measurements += len(measurements)
                
                for measurement in measurements:
                    velocity = measurement.get('wind_velocity', 0)
                    if velocity > 0:
                        all_velocities.append(velocity)
        
        # Calculate statistics
        if all_velocities:
            avg_velocity = sum(all_velocities) / len(all_velocities)
            min_velocity = min(all_velocities)
            max_velocity = max(all_velocities)
        else:
            avg_velocity = 0
            min_velocity = 0
            max_velocity = 0
        
        return {
            'total_lines_analyzed': len(lines_analyzed),
            'total_measurements': total_measurements,
            'total_velocity_measurements': len(all_velocities),
            'average_velocity': avg_velocity,
            'velocity_range': (min_velocity, max_velocity),
            'lines_analyzed': lines_analyzed,
            'all_velocities': all_velocities
        }
    
    def export_all_results(self, filename=None):
        """
        Export all wind velocity analysis results to file
        
        Args:
            filename: Output filename, or None to show file dialog
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Get all results
            all_results = self.get_analysis_results()
            summary_stats = self.get_summary_statistics()
            
            if not all_results:
                _LOGGER.warning("No wind velocity results to export")
                return False
            
            # Show file dialog if no filename provided
            if not filename:
                from tkinter import filedialog
                filename = filedialog.asksaveasfilename(
                    title="Export All Wind Velocity Results",
                    defaultextension=".json",
                    filetypes=[
                        ("JSON files", "*.json"),
                        ("CSV files", "*.csv"),
                        ("All files", "*.*")
                    ]
                )
                
                if not filename:
                    return False
            
            # Export based on file extension
            if filename.lower().endswith('.csv'):
                self._export_all_to_csv(filename, all_results, summary_stats)
            else:
                self._export_all_to_json(filename, all_results, summary_stats)
            
            _LOGGER.info(f"Exported all wind velocity results to {filename}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error exporting all wind velocity results: {e}")
            return False
    
    def _export_all_to_json(self, filename, all_results, summary_stats):
        """Export all results to JSON format"""
        import json
        from datetime import datetime
        
        export_data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'export_type': 'wind_velocity_analysis_complete',
                'total_lines': len(all_results),
                'total_measurements': summary_stats['total_measurements']
            },
            'summary_statistics': summary_stats,
            'line_analyses': all_results
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def _export_all_to_csv(self, filename, all_results, summary_stats):
        """Export all results to CSV format"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header with summary
            writer.writerow(['# Wind Velocity Analysis Export'])
            writer.writerow([f'# Total Lines Analyzed: {summary_stats["total_lines_analyzed"]}'])
            writer.writerow([f'# Total Measurements: {summary_stats["total_measurements"]}'])
            writer.writerow([f'# Average Velocity: {summary_stats["average_velocity"]:.1f} km/s'])
            writer.writerow([f'# Velocity Range: {summary_stats["velocity_range"][0]:.1f} - {summary_stats["velocity_range"][1]:.1f} km/s'])
            writer.writerow([])
            
            # Data header
            writer.writerow([
                'Line_Name', 'Measurement_Number', 'Rest_Wavelength_A', 
                'Emission_Wavelength_A', 'Absorption_Wavelength_A', 
                'Wind_Velocity_km_s', 'Redshift', 'Timestamp'
            ])
            
            # Data rows
            for line_name, results in all_results.items():
                measurements = results.get('measurements', [])
                for i, measurement in enumerate(measurements, 1):
                    writer.writerow([
                        line_name, i, measurement['rest_wavelength'],
                        measurement['emission_wavelength'], measurement['absorption_wavelength'],
                        measurement['wind_velocity'], measurement['redshift'], 
                        measurement['timestamp']
                    ])
    
    def is_available(self):
        """Check if wind velocity analysis is available"""
        return show_wind_velocity_dialog is not None
    
    def get_active_dialog_count(self):
        """Get number of active wind velocity analysis dialogs"""
        return len(self.active_dialogs)
    
    def has_results(self):
        """Check if any wind velocity results are available"""
        return len(self.analysis_results) > 0 or len(self.active_dialogs) > 0
    
    def get_status_text(self):
        """Get status text for the wind velocity analysis system"""
        if not self.is_available():
            return "Wind velocity analysis not available"
        
        active_count = self.get_active_dialog_count()
        results_count = len(self.analysis_results)
        
        if active_count > 0:
            return f"Wind velocity analysis active ({active_count} dialogs open)"
        elif results_count > 0:
            return f"Wind velocity results available ({results_count} lines analyzed)"
        else:
            return "Wind velocity analysis ready"
    
    # Error handling methods
    def _show_invalid_line_error(self):
        """Show error for invalid line data"""
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Invalid Line Data",
                "Cannot analyze wind velocity: Invalid or missing line data.",
                parent=getattr(self.gui, 'master', None)
            )
        except:
            _LOGGER.error("Invalid line data for wind velocity analysis")
    
    def _show_invalid_spectrum_error(self):
        """Show error for invalid spectrum data"""
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Invalid Spectrum Data",
                "Cannot analyze wind velocity: Invalid or missing spectrum data.\n\n"
                "Please ensure a spectrum is loaded and processed.",
                parent=getattr(self.gui, 'master', None)
            )
        except:
            _LOGGER.error("Invalid spectrum data for wind velocity analysis")
    
    def _show_import_error(self):
        """Show error for missing wind velocity dialog"""
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Feature Not Available",
                "Wind velocity analysis is not available.\n\n"
                "This may be due to missing dependencies or import errors.",
                parent=getattr(self.gui, 'master', None)
            )
        except:
            _LOGGER.error("Wind velocity dialog not available")
    
    def _show_generic_error(self, error_message):
        """Show generic error message"""
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Wind Velocity Analysis Error",
                f"An error occurred during wind velocity analysis:\n\n{error_message}",
                parent=getattr(self.gui, 'master', None)
            )
        except:
            _LOGGER.error(f"Wind velocity analysis error: {error_message}")
