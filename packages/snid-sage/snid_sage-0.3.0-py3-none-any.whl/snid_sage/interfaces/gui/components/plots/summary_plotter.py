"""
Summary Plotter Component

This module handles summary plotting functionality including:
- Combined view plotting (flux + flattened)
- Results summary plots
- GMM clustering visualization
- Redshift vs age plots  
- Type fractions analysis

Extracted from sage_gui.py to improve maintainability and modularity.
"""

import matplotlib.pyplot as plt
import numpy as np

# Import unified systems for consistent plot styling
try:
    from snid_sage.interfaces.gui.utils.no_title_plot_manager import apply_no_title_styling
    UNIFIED_SYSTEMS_AVAILABLE = True
except ImportError:
    UNIFIED_SYSTEMS_AVAILABLE = False

# Import template name cleaning utility
from snid_sage.shared.utils import clean_template_name


class SummaryPlotter:
    """Handles results summary plotting operations"""
    
    def __init__(self, gui_instance):
        """Initialize with reference to main GUI"""
        self.gui = gui_instance
    
    @property
    def theme_manager(self):
        """Access to the theme manager from the GUI"""
        return self.gui.theme_manager
    
    @property
    def fig(self):
        """Access to the matplotlib figure from the GUI"""
        return self.gui.fig
    
    @property
    def ax(self):
        """Access to the matplotlib axis from the GUI"""
        return self.gui.ax
    
    def plot_both_views(self):
        """Plot both flux and flattened views side by side or overlaid"""
        try:
            # Ensure matplotlib is initialized
            if self.fig is None:
                self.gui.init_matplotlib_plot()
            
            # Clear the plot
            self.ax.clear()
            
            if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results or not self.gui.snid_results.best_matches:
                theme = self.theme_manager.get_current_theme()
                text_color = theme.get('text_color', 'black')
                self.ax.text(0.5, 0.5, 'No SNID results available\nRun analysis first', 
                           ha='center', va='center', transform=self.ax.transAxes,
                           fontsize=14, color=text_color)
                # Apply no-title styling per user requirement
                # self.ax.set_title('No Data for Combined View', color=text_color)
                self.gui._finalize_plot()
                return
            
            # Ensure current template index is valid
            self.gui.current_template = max(0, min(self.gui.current_template, len(self.gui.snid_results.best_matches) - 1))
            current_match = self.gui.snid_results.best_matches[self.gui.current_template]
            
            # Get both flux and flattened spectra
            obs_wave = self.gui.snid_results.processed_spectrum['log_wave']
            obs_flux = self.gui.snid_results.processed_spectrum['log_flux']
            obs_flat = self.gui.snid_results.processed_spectrum['flat_flux']  # This is already apodized from SNID results
            
            # Filter out zero-padded regions from observed spectra
            obs_wave, obs_flux = self.gui._filter_nonzero_spectrum(obs_wave, obs_flux, self.gui.snid_results.processed_spectrum)
            obs_wave_flat, obs_flat = self.gui._filter_nonzero_spectrum(obs_wave, obs_flat, self.gui.snid_results.processed_spectrum)
            
            template_wave_flux = current_match['spectra']['flux']['wave']
            template_flux_flux = current_match['spectra']['flux']['flux']
            template_wave_flat = current_match['spectra']['flat']['wave']
            template_flux_flat = current_match['spectra']['flat']['flux']
            
            # DON'T filter templates - they are already properly trimmed by SNID analysis
            # snid_sage.snid.py
            # Filtering them again with input spectrum edges cuts them incorrectly
            # template_wave_flux, template_flux_flux = self.gui._filter_nonzero_spectrum(
            #     template_wave_flux, template_flux_flux, self.gui.snid_results.processed_spectrum
            # )
            # template_wave_flat, template_flux_flat = self.gui._filter_nonzero_spectrum(
            #     template_wave_flat, template_flux_flat, self.gui.snid_results.processed_spectrum
            # )
            
            # Plot both views overlaid with different colors
            # Flux view
            self.ax.plot(obs_wave, obs_flux, 'b-', linewidth=2, alpha=0.7)
            self.ax.plot(template_wave_flux, template_flux_flux, 'r-', linewidth=1.5, alpha=0.7)
            
            # Flattened view (normalized and offset)
            flat_offset = np.max(obs_flux) * 0.1  # Small offset
            self.ax.plot(obs_wave_flat, obs_flat + flat_offset, 'c--', linewidth=2, alpha=0.7)
            self.ax.plot(template_wave_flat, template_flux_flat + flat_offset, 'm--', linewidth=1.5, alpha=0.7)
            
            # Add template info (using subtype from template object)
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
            theme = self.theme_manager.get_current_theme()
            text_color = theme.get('text_color', 'black')
            info_bg_color = theme.get('bg_tertiary', 'lightcyan')
            
            theme_colors = {
                'text_primary': text_color,
                'bg_tertiary': info_bg_color
            }
            add_adaptive_template_info(self.ax, info_text, position='upper right', 
                                     theme_colors=theme_colors, fontsize=10)
            
            # Apply no-title styling per user requirement
            # self.ax.set_title(f'Combined View - {current_match["name"]} (z={current_match["redshift"]:.4f})', color=text_color)
            self.ax.set_ylabel('Flux / Flattened Flux', color=text_color)
            self.ax.set_xlabel('Wavelength (Å)', color=text_color)
            
            self.gui._finalize_plot()
            print(f"Plotted combined view for template {self.gui.current_template + 1}: {current_match['name']}")
            
        except Exception as e:
            print(f"Error plotting both views: {e}")
            import traceback
            traceback.print_exc()
            self.gui._plot_error(f"Error plotting combined view: {str(e)}")


    
    def plot_gmm_clustering(self):
        """Plot GMM clustering results"""
        try:
            if hasattr(self.gui, 'last_result') and self.gui.last_result:
                result = self.gui.last_result
                
                # Check if we have clustering data
                if hasattr(result, 'gmm_data') and result.gmm_data:
                    self._plot_gmm_data(result.gmm_data)
                else:
                    self._plot_no_clustering_data()
            else:
                self._plot_no_data()
                
        except Exception as e:
            self._handle_plot_error(f"Error plotting GMM clustering: {str(e)}")
    
    def plot_redshift_age(self):
        """Plot redshift vs age analysis"""
        try:
            if hasattr(self.gui, 'last_result') and self.gui.last_result:
                result = self.gui.last_result
                
                # Check if we have redshift/age data
                if hasattr(result, 'redshift_age_data') and result.redshift_age_data:
                    self._plot_redshift_age_data(result.redshift_age_data)
                else:
                    self._plot_no_redshift_age_data()
            else:
                self._plot_no_data()
                
        except Exception as e:
            self._handle_plot_error(f"Error plotting redshift vs age: {str(e)}")
    
    def plot_subtype_proportions(self):
        """Plot subtype proportions within selected cluster"""
        try:
            if hasattr(self.gui, 'last_result') and self.gui.last_result:
                result = self.gui.last_result
                
                # Check if we have clustering results with subtype data
                if (hasattr(result, 'clustering_results') and result.clustering_results and
                    hasattr(result, 'filtered_matches') and result.filtered_matches):
                    self._plot_subtype_proportions_data(result)
                else:
                    self._plot_no_subtype_proportions_data()
            else:
                self._plot_no_data()
                
        except Exception as e:
            self._handle_plot_error(f"Error plotting subtype proportions: {str(e)}")
    
    def _plot_summary_data(self, result):
        """Plot summary data from result"""
        self.gui._clear_plot_with_theme()
        
        # Get theme colors
        theme = self.theme_manager.get_current_theme()
        
        # Extract summary metrics
        summary_data = self._extract_summary_data(result)
        
        if summary_data:
            # Create bar chart of key metrics
            metrics = list(summary_data.keys())
            values = list(summary_data.values())
            
            bars = self.ax.bar(metrics, values, color=theme['accent_color'], alpha=0.7)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{value:.3f}', ha='center', va='bottom',
                            color=theme['text_color'])
            
            # Apply no-title styling per user requirement
            # self.ax.set_title('Analysis Summary', color=theme['text_color'])
            self.ax.tick_params(colors=theme['text_color'])
        else:
            self._plot_message("No summary data available")
        
        self._finalize_summary_plot()
    
    def _plot_gmm_data(self, gmm_data):
        """Plot GMM clustering data"""
        self.gui._clear_plot_with_theme()
        
        # Get theme colors
        theme = self.theme_manager.get_current_theme()
        
        # Set up the plot styling
        self.gui._standardize_plot_styling(
            title="GMM Clustering Analysis",
            xlabel="Component",
            ylabel="Weight",
            clear_plot=False
        )
        
        # Extract clustering information
        if 'weights' in gmm_data and 'components' in gmm_data:
            weights = gmm_data['weights']
            components = [f"Cluster {i+1}" for i in range(len(weights))]
            
            bars = self.ax.bar(components, weights, color=theme['accent_color'], alpha=0.7)
            
            # Add percentage labels
            for bar, weight in zip(bars, weights):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{weight*100:.1f}%', ha='center', va='bottom',
                            color=theme['text_color'])
        
        self._finalize_summary_plot()
    
    def _plot_redshift_age_data(self, redshift_age_data):
        """Plot redshift vs age data"""
        self.gui._clear_plot_with_theme()
        
        # Get theme colors
        theme = self.theme_manager.get_current_theme()
        
        # Set up the plot styling
        self.gui._standardize_plot_styling(
            title="Redshift vs Age Distribution",
            xlabel="Redshift",
            ylabel="Age (days)",
            clear_plot=False
        )
        
        # Create scatter plot
        if 'redshifts' in redshift_age_data and 'ages' in redshift_age_data:
            redshifts = redshift_age_data['redshifts']
            ages = redshift_age_data['ages']
            
            scatter = self.ax.scatter(redshifts, ages, c=theme['accent_color'], 
                                    alpha=0.7, s=60)
            
            # Add trend line if enough points
            if len(redshifts) > 2:
                z = np.polyfit(redshifts, ages, 1)
                p = np.poly1d(z)
                self.ax.plot(redshifts, p(redshifts), color=theme['secondary_color'], 
                           linestyle='--', alpha=0.8, label='Trend')
                self.ax.legend()
        
        self._finalize_summary_plot()
    
    def _plot_type_fractions_data(self, type_fractions):
        """Plot type fractions data"""
        self.gui._clear_plot_with_theme()
        
        # Get theme colors
        theme = self.theme_manager.get_current_theme()
        
        # Set up the plot styling
        self.gui._standardize_plot_styling(
            title="SN Type Fractions",
            xlabel="",
            ylabel="",
            clear_plot=False
        )
        
        # Create pie chart
        if 'labels' in type_fractions and 'fractions' in type_fractions:
            labels = type_fractions['labels']
            fractions = type_fractions['fractions']
            
            # Create pie chart
            colors = [theme['accent_color'], theme['secondary_color'], 
                     theme['tertiary_color'], theme['quaternary_color']][:len(labels)]
            
            wedges, texts, autotexts = self.ax.pie(fractions, labels=labels, 
                                                  colors=colors, autopct='%1.1f%%',
                                                  startangle=90)
            
            # Style the text
            for text in texts:
                text.set_color(theme['text_color'])
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
        
        self._finalize_summary_plot()
    
    def _plot_no_clustering_data(self):
        """Plot message when no clustering data is available"""
        self._plot_message("GMM clustering data not available\nRun analysis with clustering enabled")
    
    def _plot_no_redshift_age_data(self):
        """Plot message when no redshift/age data is available"""
        self._plot_message("Redshift vs Age data not available\nRun analysis with redshift/age analysis enabled")
    
    def _plot_subtype_proportions_data(self, result):
        """Plot subtype proportions data for the selected cluster"""
        try:
            from snid_sage.snid.plotting import plot_cluster_subtype_proportions
            
            # Get the selected cluster from clustering results
            selected_cluster = None
            if hasattr(result, 'clustering_results') and result.clustering_results:
                clustering_results = result.clustering_results
                
                # Check for user-selected cluster first
                if 'user_selected_cluster' in clustering_results:
                    selected_cluster = clustering_results['user_selected_cluster']
                elif 'best_cluster' in clustering_results:
                    # Fall back to automatic best cluster
                    selected_cluster = clustering_results['best_cluster']
            
            # Clear existing plot
            self.gui._clear_plot_with_theme()
            
            # Create the subtype proportions plot using the existing figure
            plot_cluster_subtype_proportions(
                result,
                selected_cluster=selected_cluster,
                fig=self.gui.fig,
                theme_manager=self.theme_manager
            )
            
            # Update axes reference
            axes = self.gui.fig.get_axes()
            if axes:
                self.gui.ax = axes[0]
            
            self._finalize_summary_plot()
            
        except Exception as e:
            self._plot_message(f"Error plotting subtype proportions: {str(e)}")
    
    def _plot_no_subtype_proportions_data(self):
        """Plot message when no subtype proportions data is available"""
        self._plot_message("Subtype proportions data not available\nRun analysis with GMM clustering to generate cluster-based subtype analysis")
    
    def _plot_no_data(self):
        """Plot message when no data is available"""
        self._plot_message("No analysis results available\nRun SNID analysis first")
    
    def _plot_message(self, message):
        """Plot a message on the canvas"""
        self.gui._clear_plot_with_theme()
        
        theme = self.theme_manager.get_current_theme()
        text_color = theme['text_color']
        
        self.ax.text(0.5, 0.5, message,
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, fontsize=12, color=text_color,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=theme['accent_color'], alpha=0.3))
        
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        self._finalize_summary_plot()
    
    def _extract_summary_data(self, result):
        """Extract summary data from SNID result"""
        summary = {}
        
        # Extract key metrics from the result
        if hasattr(result, 'best_template'):
            summary['Best Match'] = getattr(result, 'correlation_value', 0.0)
        
        if hasattr(result, 'redshift'):
            summary['Redshift'] = getattr(result, 'redshift', 0.0)
        
        if hasattr(result, 'age'):
            summary['Age (days)'] = getattr(result, 'age', 0.0)
        
        if hasattr(result, 'template_count'):
            summary['Templates'] = getattr(result, 'template_count', 0)
        
        return summary
    
    def _finalize_summary_plot(self):
        """Apply final styling and redraw the plot"""
        try:
            # Apply theme colors to the plot
            self.gui._apply_plot_theme()
            
            # Redraw the canvas
            if hasattr(self.gui, 'canvas') and self.gui.canvas:
                self.gui.canvas.draw()
        except Exception as e:
            print(f"Error finalizing summary plot: {e}")
    
    def _handle_plot_error(self, error_message):
        """Handle plot errors"""
        print(f"Summary plotting error: {error_message}")
        import traceback
        traceback.print_exc()
        self.gui._plot_error(error_message) 
