"""
Results Manager for SNID GUI

This module handles results display, management, and export functionality.
Extracted from the main GUI to improve modularity and maintainability.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import json
import csv

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.results')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.results')


class ResultsManager:
    """Handles results display, management, and export"""
    
    def __init__(self, parent_gui):
        """Initialize the results manager
        
        Args:
            parent_gui: Reference to the main GUI instance
        """
        self.parent_gui = parent_gui
        self.theme_manager = parent_gui.theme_manager
        self.current_result = None
        self.results_history = []
        
    def show_results_summary(self, result):
        """Display a summary of SNID-SAGE analysis results
        
        Args:
            result: SNID-SAGE analysis result object
        """
        try:
            self.current_result = result
            self.results_history.append(result)
            
            # Update header status
            self.parent_gui.header_status_label.config(
                text="✅ Analysis complete - Results available"
            )
            
            # Update results display
            self.update_results_display(result)
            
            # Enable result-related buttons
            self._enable_result_buttons()
            

            
            _LOGGER.debug("✅ Results summary displayed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display results: {str(e)}")
            print(f"❌ Error displaying results: {str(e)}")
    
    def update_results_display(self, result):
        """Update the results display area with new results
        
        Args:
            result: SNID-SAGE analysis result object
        """
        try:
            if not hasattr(self.parent_gui, 'results_text'):
                return
            
            # Clear previous results
            self.parent_gui.results_text.delete(1.0, tk.END)
            
            # Format and display results
            results_text = self._format_results_text(result)
            self.parent_gui.results_text.insert(tk.END, results_text)
            
            # Update result statistics if available
            if hasattr(result, 'statistics'):
                self._update_statistics_display(result.statistics)
            
        except Exception as e:
            print(f"❌ Error updating results display: {str(e)}")
    
    def _format_results_text(self, result):
        """Format results for text display
        
        Args:
            result: SNID-SAGE analysis result object
            
        Returns:
            str: Formatted results text
        """
        try:
            text_lines = []
            text_lines.append("=" * 60)
            text_lines.append("SNID-SAGE ANALYSIS RESULTS")
            text_lines.append("=" * 60)
            text_lines.append("")
            
            # Basic information
            if hasattr(result, 'input_file'):
                text_lines.append(f"Input File: {result.input_file}")
            if hasattr(result, 'analysis_time'):
                text_lines.append(f"Analysis Time: {result.analysis_time}")
            text_lines.append("")
            
            # Best matches
            if hasattr(result, 'best_matches') and result.best_matches:
                text_lines.append("BEST MATCHES:")
                text_lines.append("-" * 40)
                for i, match in enumerate(result.best_matches[:10], 1):
                    if hasattr(match, 'template_name') and hasattr(match, 'rlap'):
                        text_lines.append(f"{i:2d}. {match.template_name:<25} (rlap: {match.rlap:.3f})")
                text_lines.append("")
            
            # Type classification
            if hasattr(result, 'type_classification'):
                text_lines.append("TYPE CLASSIFICATION:")
                text_lines.append("-" * 40)
                for type_name, confidence in result.type_classification.items():
                    text_lines.append(f"{type_name:<15}: {confidence:.1%}")
                text_lines.append("")
            
            # Redshift information
            if hasattr(result, 'redshift'):
                text_lines.append("REDSHIFT INFORMATION:")
                text_lines.append("-" * 40)
                text_lines.append(f"Best Redshift: {result.redshift:.6f}")
                if hasattr(result, 'redshift_error'):
                    text_lines.append(f"Redshift Error: ±{result.redshift_error:.6f}")
                text_lines.append("")
            
            # Age information
            if hasattr(result, 'age_days'):
                text_lines.append("AGE INFORMATION:")
                text_lines.append("-" * 40)
                text_lines.append(f"Age: {result.age_days:.1f} days")
                if hasattr(result, 'age_error'):
                    text_lines.append(f"Age Error: ±{result.age_error:.1f} days")
                text_lines.append("")
            
            # Quality metrics
            if hasattr(result, 'quality_metrics'):
                text_lines.append("QUALITY METRICS:")
                text_lines.append("-" * 40)
                for metric, value in result.quality_metrics.items():
                    text_lines.append(f"{metric:<20}: {value}")
                text_lines.append("")
            
            text_lines.append("=" * 60)
            
            return "\n".join(text_lines)
            
        except Exception as e:
            return f"Error formatting results: {str(e)}"
    
    def _update_statistics_display(self, statistics):
        """Update statistics display
        
        Args:
            statistics: Statistics object or dictionary
        """
        try:
            if hasattr(self.parent_gui, 'stats_labels'):
                for label_name, value in statistics.items():
                    if label_name in self.parent_gui.stats_labels:
                        self.parent_gui.stats_labels[label_name].config(text=str(value))
        except Exception as e:
            print(f"❌ Error updating statistics: {str(e)}")
    
    def _enable_result_buttons(self):
        """Enable buttons that require results to be available"""
        try:
            # Enable plot buttons
            plot_buttons = [
                'plot_correlation_btn', 'plot_gmm_btn',
                'plot_redshift_age_btn', 'plot_subtype_proportions_btn'
            ]
            
            for btn_name in plot_buttons:
                if hasattr(self.parent_gui, btn_name):
                    getattr(self.parent_gui, btn_name).config(state='normal')
            
            # Enable export buttons
            export_buttons = ['export_results_btn', 'save_report_btn']
            for btn_name in export_buttons:
                if hasattr(self.parent_gui, btn_name):
                    getattr(self.parent_gui, btn_name).config(state='normal')
            
            # Enable LLM buttons if available
            if hasattr(self.parent_gui, 'llm_integration'):
                self.parent_gui.update_llm_button_states()
            
        except Exception as e:
            print(f"❌ Error enabling result buttons: {str(e)}")
    
    def export_results(self, format_type='json'):
        """Export results to file
        
        Args:
            format_type (str): Export format ('json', 'csv', 'txt')
        """
        try:
            if not self.current_result:
                messagebox.showwarning("No Results", "No results available to export.")
                return
            
            # Get export filename with proper default names
            spectrum_name = getattr(self.current_result, 'spectrum_name', 'Unknown')
            file_extensions = {'json': '.json', 'csv': '.csv', 'txt': '.txt'}
            default_filename = f"{spectrum_name}_results{file_extensions.get(format_type, '.txt')}"
            
            if format_type == 'json':
                filename = filedialog.asksaveasfilename(
                    title="Export Results as JSON",
                    defaultextension=".json",
                    initialfile=default_filename,
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
                )
            elif format_type == 'csv':
                filename = filedialog.asksaveasfilename(
                    title="Export Results as CSV",
                    defaultextension=".csv",
                    initialfile=default_filename,
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
            else:  # txt
                filename = filedialog.asksaveasfilename(
                    title="Export Results as Text",
                    defaultextension=".txt",
                    initialfile=default_filename,
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
            
            if filename:
                self._export_to_file(filename, format_type)
                messagebox.showinfo("Export Complete", f"Results exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def _export_to_file(self, filename, format_type):
        """Export results to specific file format using unified formatter
        
        Args:
            filename (str): Output filename
            format_type (str): Export format
        """
        try:
            # Use the unified formatter for consistent output
            from snid_sage.shared.utils.results_formatter import create_unified_formatter
            spectrum_name = getattr(self.current_result, 'spectrum_name', 'Unknown')
            formatter = create_unified_formatter(self.current_result, spectrum_name)
            formatter.save_to_file(filename, format_type)
                
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")
    
    def _export_to_json(self, filename):
        """Export results to JSON format
        
        Args:
            filename (str): Output filename
        """
        result_dict = self._result_to_dict(self.current_result)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, default=str)
    
    def _export_to_csv(self, filename):
        """Export results to CSV format
        
        Args:
            filename (str): Output filename
        """
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Property', 'Value'])
            
            # Write basic information
            result_dict = self._result_to_dict(self.current_result)
            for key, value in result_dict.items():
                if not isinstance(value, (list, dict)):
                    writer.writerow([key, value])
            
            # Write best matches if available
            if hasattr(self.current_result, 'best_matches'):
                writer.writerow([])
                writer.writerow(['Best Matches'])
                writer.writerow(['Rank', 'Template', 'Rlap'])
                for i, match in enumerate(self.current_result.best_matches[:10], 1):
                    if hasattr(match, 'template_name') and hasattr(match, 'rlap'):
                        writer.writerow([i, match.template_name, match.rlap])
    
    def _export_to_txt(self, filename):
        """Export results to text format
        
        Args:
            filename (str): Output filename
        """
        results_text = self._format_results_text(self.current_result)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(results_text)
    
    def _result_to_dict(self, result):
        """Convert result object to dictionary
        
        Args:
            result: SNID result object
            
        Returns:
            dict: Result data as dictionary
        """
        result_dict = {}
        
        # Extract basic attributes
        for attr in ['input_file', 'analysis_time', 'redshift', 'redshift_error',
                    'age_days', 'age_error', 'best_template', 'best_rlap']:
            if hasattr(result, attr):
                result_dict[attr] = getattr(result, attr)
        
        # Extract type classification
        if hasattr(result, 'type_classification'):
            result_dict['type_classification'] = result.type_classification
        
        # Extract quality metrics
        if hasattr(result, 'quality_metrics'):
            result_dict['quality_metrics'] = result.quality_metrics
        
        # Extract best matches (limited to top 10)
        if hasattr(result, 'best_matches'):
            matches = []
            for match in result.best_matches[:10]:
                if hasattr(match, 'template_name') and hasattr(match, 'rlap'):
                    matches.append({
                        'template_name': match.template_name,
                        'rlap': match.rlap,
                        'redshift': getattr(match, 'redshift', None),
                        'age': getattr(match, 'age', None)
                    })
            result_dict['best_matches'] = matches
        
        return result_dict
    
    def save_analysis_report(self):
        """Save a comprehensive analysis report"""
        try:
            if not self.current_result:
                messagebox.showwarning("No Results", "No results available to save.")
                return
            
            filename = filedialog.asksaveasfilename(
                title="Save Analysis Report",
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                if filename.endswith('.html'):
                    self._save_html_report(filename)
                else:
                    self._save_text_report(filename)
                
                messagebox.showinfo("Report Saved", f"Analysis report saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save report: {str(e)}")
    
    def _save_html_report(self, filename):
        """Save HTML analysis report
        
        Args:
            filename (str): Output filename
        """
        html_content = self._generate_html_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _save_text_report(self, filename):
        """Save text analysis report
        
        Args:
            filename (str): Output filename
        """
        text_content = self._generate_text_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_content)
    
    def _generate_html_report(self):
        """Generate HTML report content
        
        Returns:
            str: HTML report content
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
                            <title>SNID-SAGE Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; border-bottom: 2px solid #ecf0f1; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .highlight {{ background-color: #fff3cd; }}
            </style>
        </head>
        <body>
                            <h1>SNID-SAGE Analysis Report</h1>
            {self._format_results_html(self.current_result)}
        </body>
        </html>
        """
        return html
    
    def _generate_text_report(self):
        """Generate text report content
        
        Returns:
            str: Text report content
        """
        return self._format_results_text(self.current_result)
    
    def _format_results_html(self, result):
        """Format results as HTML
        
        Args:
            result: SNID result object
            
        Returns:
            str: HTML formatted results
        """
        # This would be a more detailed HTML formatting
        # For now, return a simple conversion
        text_results = self._format_results_text(result)
        return f"<pre>{text_results}</pre>"
    
    def clear_results(self):
        """Clear current results and reset display"""
        try:
            self.current_result = None
            
            # Clear results display
            if hasattr(self.parent_gui, 'results_text'):
                self.parent_gui.results_text.delete(1.0, tk.END)
            
            # Reset header status
            self.parent_gui.header_status_label.config(
                text="Ready - Load a spectrum to begin analysis"
            )
            
            # Disable result-related buttons
            self._disable_result_buttons()
            
            _LOGGER.debug("✅ Results cleared")
            
        except Exception as e:
            print(f"❌ Error clearing results: {str(e)}")
    
    def _disable_result_buttons(self):
        """Disable buttons that require results"""
        try:
            # Disable plot buttons
            plot_buttons = [
                'plot_correlation_btn', 'plot_gmm_btn',
                'plot_redshift_age_btn', 'plot_subtype_proportions_btn'
            ]
            
            for btn_name in plot_buttons:
                if hasattr(self.parent_gui, btn_name):
                    getattr(self.parent_gui, btn_name).config(state='disabled')
            
            # Disable export buttons
            export_buttons = ['export_results_btn', 'save_report_btn']
            for btn_name in export_buttons:
                if hasattr(self.parent_gui, btn_name):
                    getattr(self.parent_gui, btn_name).config(state='disabled')
            
        except Exception as e:
            print(f"❌ Error disabling result buttons: {str(e)}")
    
    def get_results_summary(self):
        """Get a summary of current results
        
        Returns:
            dict: Results summary
        """
        if not self.current_result:
            return None
        
        summary = {
            'has_results': True,
            'best_template': getattr(self.current_result, 'best_template', 'Unknown'),
            'best_rlap': getattr(self.current_result, 'best_rlap', 0.0),
            'redshift': getattr(self.current_result, 'redshift', None),
            'age_days': getattr(self.current_result, 'age_days', None),
            'num_matches': len(getattr(self.current_result, 'best_matches', [])),
            'analysis_time': getattr(self.current_result, 'analysis_time', 'Unknown')
        }
        
        return summary
    
    def clear_all_results(self):
        """Clear all results and reset manager state"""
        try:
            _LOGGER.debug("🔄 Clearing all results manager state...")
            
            # Clear current result
            self.clear_results()
            
            # Reset any cached results
            if hasattr(self, 'cached_results'):
                self.cached_results = None
            
            # Clear any export history
            if hasattr(self, 'export_history'):
                self.export_history = []
            
            # Reset any analysis summaries
            if hasattr(self, 'analysis_summaries'):
                self.analysis_summaries = None
            
            # Clear any LLM analysis data
            if hasattr(self.parent_gui, 'llm_analysis'):
                self.parent_gui.llm_analysis = None
            
            _LOGGER.debug("✅ Results manager state cleared")
            
        except Exception as e:
            print(f"❌ Error clearing all results: {e}") 
