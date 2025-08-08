"""
Analysis Plotter Component

Handles all advanced analysis plotting functionality for the SNID GUI:
- GMM clustering visualization (2D and 3D)
- Redshift vs Age distribution plots  
- Subtype proportion analysis
- Results summary plots

Extracted from sage_gui.py to improve maintainability and modularity.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.text
import tkinter as tk

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.analysis_plotter')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.analysis_plotter')

# Import the new metric utility functions for RLAP-cos support
try:
    from snid_sage.shared.utils.math_utils import get_best_metric_value, get_metric_name_for_match
    METRIC_UTILS_AVAILABLE = True
except ImportError:
    # Fallback functions if utilities not available
    get_best_metric_value = lambda m: m.get('rlap', 0)
    get_metric_name_for_match = lambda m: 'RLAP'
    METRIC_UTILS_AVAILABLE = False
    _LOGGER.warning("Metric utilities not available - falling back to RLAP only")


class AnalysisPlotter:
    """
    Handles all analysis plotting operations for the SNID GUI.
    
    This class encapsulates advanced analysis plotting logic and provides a clean interface
    for the main GUI to display various analytical visualizations.
    """
    
    def __init__(self, gui_instance):
        """
        Initialize the analysis plotter.
        
        Args:
            gui_instance: Reference to the main GUI instance for accessing
                         matplotlib figures, theme manager, and SNID results
        """
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
    
    def plot_gmm_clustering(self):
        """Plot GMM clustering analysis with type-specific clustering and 3D visualization"""
        try:
            # Make sure Flux/Flat segmented control is cleared while an analysis plot is active
            self._deactivate_view_style()
            
            # Ensure matplotlib is initialized
            if self.fig is None:
                self.gui.init_matplotlib_plot()
            
            # Ensure we have a valid canvas
            if not hasattr(self.gui, 'canvas') or self.gui.canvas is None:
                self.gui.init_matplotlib_plot()
            
            # Ensure we have a valid axis before trying to clear it
            if self.ax is None:
                self.gui.init_matplotlib_plot()
            
            # Clear the plot only if we have a valid axis
            if self.ax is not None:
                self.ax.clear()
            
            if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results or not self.gui.snid_results.best_matches:
                # Ensure we have a valid axis for displaying the message
                if self.ax is None:
                    self.gui.init_matplotlib_plot()
                
                theme = self.theme_manager.get_current_theme()
                text_color = theme.get('text_color', 'black')
                self.ax.text(0.5, 0.5, 'No results available\nRun SNID analysis first', 
                           ha='center', va='center', transform=self.ax.transAxes,
                           fontsize=14, color=text_color)
                self.ax.set_title('No GMM Data', color=text_color)
                self.gui._finalize_plot()
                return

            # Check if we have cosmological clustering results  
            if (hasattr(self.gui.snid_results, 'clustering_results') and 
                self.gui.snid_results.clustering_results and
                self.gui.snid_results.clustering_results.get('success', False)):
                
                try:
                    # Always use 3D clustering visualization (2D functionality removed)
                    self._plot_integrated_3d_clustering(marginalize_over_type=False)
                    
                    _LOGGER.info(f"✅ Cosmological GMM clustering displayed")
                    
                except Exception as e:
                    _LOGGER.error(f"Error in integrated clustering plot: {e}")
                    # 2D fallback removed - show error message instead
                    theme = self.theme_manager.get_current_theme()
                    text_color = theme.get('text_color', 'black')
                    self.ax.text(0.5, 0.5, f'Error displaying clustering plot\n{str(e)}', 
                               ha='center', va='center', transform=self.ax.transAxes,
                               fontsize=12, color='red')
                    self.gui._finalize_plot()
            else:
                # No clustering results available
                # Ensure we have a valid axis for displaying the message
                if self.ax is None:
                    self.gui.init_matplotlib_plot()
                
                theme = self.theme_manager.get_current_theme()
                text_color = theme.get('text_color', 'black')
                warning_color = theme.get('warning_color', 'orange')
                
                self.ax.text(0.5, 0.5, 'No GMM clustering results available\nRun SNID analysis first', 
                           ha='center', va='center', transform=self.ax.transAxes,
                           fontsize=14, color=warning_color)
                self.ax.set_title('Cosmological GMM Clustering', color=text_color)
                self.gui._finalize_plot()
                
        except Exception as e:
            _LOGGER.error(f"Error plotting GMM clustering: {e}")
            import traceback
            traceback.print_exc()
            self.gui._plot_error(f"Error plotting GMM clustering: {str(e)}")
    
    def _toggle_clustering_view(self, event=None):
        """Toggle functionality removed - always use 3D view"""
        # This method is kept for compatibility but does nothing
        # 2D functionality has been completely removed
        pass
    
    def _disconnect_event_handlers(self):
        """Event handler disconnection removed - no longer needed for 2D/3D switching"""
        # This method is kept for compatibility but does nothing
        # 2D functionality has been completely removed
        pass
    
    def _recreate_figure_for_view_switch(self):
        """Figure recreation removed - no longer needed for 2D/3D switching"""
        # This method is kept for compatibility but does nothing
        # 2D functionality has been completely removed
        pass
    
    def _plot_integrated_3d_clustering(self, marginalize_over_type=False):
        """Plot 3D clustering visualization (2D marginalized view removed)"""
        clustering_results = self.gui.snid_results.clustering_results
        
        if not clustering_results or not clustering_results.get('success', False):
            # Ensure we have a basic axis for the error message
            if self.ax is None:
                ax = self.fig.add_subplot(111)
                self.gui.ax = ax
            
            self.ax.text(0.5, 0.5, 'No clustering results available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.gui._finalize_plot()
            return
        
        # Ensure we have a valid figure and clear it properly
        if self.fig is None:
            self.gui.init_matplotlib_plot()
        
        # Clear the current figure completely and maximize for full window usage
        self.fig.clear()
        
        try:
            # Extract data for visualization
            all_candidates = clustering_results.get('all_candidates', [])
            best_cluster = clustering_results.get('best_cluster')
            user_selected_cluster = clustering_results.get('user_selected_cluster')
            
            if not all_candidates:
                ax_3d = self.fig.add_subplot(111, projection='3d')
                ax_3d.text(0.5, 0.5, 0.5, 'No cluster candidates available', 
                          ha='center', va='center', transform=ax_3d.transAxes)
                return
            
            # Get theme colors
            theme = self.theme_manager.get_current_theme()
            
            # Define 10 DISTINCT PASTEL colors for the specified supernova types
            TYPE_COLORS = {
                'Ia': '#FFB3B3',      # Pastel Red
                'Ib': '#FFCC99',      # Pastel Orange  
                'Ic': '#99CCFF',      # Pastel Blue
                'II': '#9370DB',     # Medium slate blue
                'Galaxy': '#8A2BE2',  # Blue-violet for galaxies
                'Star': '#FFD700',    # Gold for stars  
                'AGN': '#FF6347',     # Tomato red for AGN/QSO
                'SLSN': '#20B2AA',    # Light sea green
                'LFBOT': '#FFFF99',   # Pastel Yellow
                'TDE': '#D8BFD8',     # Pastel Purple/Thistle
                'KN': '#B3FFFF',      # Pastel Cyan
                'GAP': '#FFCC80',     # Pastel Orange
                'Unknown': '#D3D3D3', # Light Gray
                'Other': '#C0C0C0',    # Silver
            }
            
            # 2D marginalized plotting removed - always use 3D view
            # 3D plot: redshift vs type vs RLAP (MUCH WIDER and TALLER)
            from mpl_toolkits.mplot3d import Axes3D
            
            # Create 3D subplot with MAXIMUM space usage
            ax_3d = self.fig.add_subplot(111, projection='3d')
            
            # MAXIMIZE the plot area - use consistent layout with 2D plots
            self.fig.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.12)
            
            # Create 3D scatter plot of redshift vs type vs RLAP
            types = sorted(list(set(candidate['type'] for candidate in all_candidates)))
            
            # Map types to numeric values for y-axis - consistent ordering
            type_mapping = {t: i for i, t in enumerate(types)}
            
            # Track which types we've already added to legend
            legend_added = set()
            
            for candidate in all_candidates:
                matches = candidate['matches']
                redshifts = [m['redshift'] for m in matches]
                metric_values = [get_best_metric_value(m) for m in matches]
                type_nums = [type_mapping[candidate['type']]] * len(matches)
                
                # Determine visual style based on selection status
                is_auto_best = (candidate == best_cluster)
                is_user_selected = (candidate == user_selected_cluster)
                is_highlighted = is_auto_best or is_user_selected
                
                # Use same large point size as cluster selection dialog for better visibility
                size = 80
                alpha = 1.0
                
                # Black edges for selected clusters, gray for others
                if is_user_selected:
                    edgecolor = 'black'
                    linewidth = 2.5
                elif is_auto_best:
                    edgecolor = 'black'
                    linewidth = 2.0
                else:
                    edgecolor = 'gray'
                    linewidth = 0.5
                
                # Use consistent type colors
                color = TYPE_COLORS.get(candidate['type'], TYPE_COLORS['Unknown'])
                
                # Create label only for the first occurrence of each type
                sn_type = candidate['type']
                if sn_type not in legend_added:
                    if is_user_selected:
                        label = f"{sn_type} (SELECTED)"
                    elif is_auto_best:
                        label = f"{sn_type} (AUTO)"
                    else:
                        label = sn_type
                    legend_added.add(sn_type)
                else:
                    label = None  # No label for subsequent occurrences
                
                ax_3d.scatter(redshifts, type_nums, metric_values, 
                            c=color, 
                            s=size, alpha=alpha,
                            edgecolors=edgecolor, linewidths=linewidth,
                            label=label)
            
            # Determine metric name for Z-axis label
            metric_name = 'RLAP'  # Default fallback
            if all_candidates and all_candidates[0].get('matches'):
                metric_name = get_metric_name_for_match(all_candidates[0]['matches'][0])
            
            # Set labels with larger fonts
            # Axes always show redshift values (clustering works directly with z values)
            ax_3d.set_xlabel('Redshift (z)', color=theme.get('text_color', 'black'), fontsize=14, labelpad=12)
            ax_3d.set_ylabel('SN Type', color=theme.get('text_color', 'black'), fontsize=14, labelpad=12)
            ax_3d.set_zlabel(metric_name, color=theme.get('text_color', 'black'), fontsize=14, labelpad=12)
            
            # Set y-axis labels to show actual type names
            ax_3d.set_yticks(list(type_mapping.values()))
            ax_3d.set_yticklabels(list(type_mapping.keys()), fontsize=10)
            
            # Optimize 3D plot dimensions for MUCH better space usage
            ax_3d.view_init(elev=25, azim=45)  # Slightly higher elevation for better view
            
            # Make the plot WIDER and fit the window better
            ax_3d.set_box_aspect([2.0, 1.0, 1.2])  # Much wider, normal height, good depth
            
            # CONSTRAIN rotation to horizontal (azimuth) only - with enhanced error protection
            def on_rotate(event):
                try:
                    # Check if all necessary objects are still valid
                    if (event and 
                        hasattr(event, 'inaxes') and event.inaxes and
                        event.inaxes == ax_3d and 
                        hasattr(self, 'fig') and self.fig and
                        hasattr(self.fig, 'canvas') and self.fig.canvas and
                        hasattr(ax_3d, 'figure') and ax_3d.figure is not None and
                        ax_3d.figure == self.fig):
                        
                        # LOCK elevation to 25 degrees, only allow azimuth changes
                        current_azim = getattr(ax_3d, 'azim', 45)  # Default to 45 if azim is None
                        ax_3d.view_init(elev=25, azim=current_azim)
                        
                        # Only draw if canvas is still valid
                        if hasattr(self.fig.canvas, 'draw_idle'):
                            self.fig.canvas.draw_idle()
                            
                except (AttributeError, RuntimeError, TypeError, ValueError):
                    # Silently ignore all errors during view transitions or figure cleanup
                    pass
            
            # Connect rotation constraint with enhanced error protection
            if (hasattr(self, 'fig') and self.fig and 
                hasattr(self.fig, 'canvas') and self.fig.canvas and
                hasattr(self.fig.canvas, 'mpl_connect')):
                try:
                    self.fig.canvas.mpl_connect('motion_notify_event', on_rotate)
                except (AttributeError, RuntimeError):
                    # Ignore connection errors
                    pass
            
            # Enhanced legend with clustering statistics
            n_types = clustering_results['n_types_clustered']
            n_candidates = clustering_results['total_candidates']
            best_type = best_cluster['type'] if best_cluster else 'None'
            user_type = user_selected_cluster['type'] if user_selected_cluster else None
            
            if user_type:
                legend_title = f"GMM Clustering | Types: {n_types} | Clusters: {n_candidates} | Selected: {user_type}"
            else:
                legend_title = f"GMM Clustering | Types: {n_types} | Clusters: {n_candidates} | Best: {best_type}"
            
            # Remove the legend title to give more space
            legend = ax_3d.legend(fontsize=10, loc='upper left', title=None, title_fontsize=11,
                                framealpha=0.95, edgecolor='black')
            if legend:
                legend.get_frame().set_facecolor(theme.get('bg_color', 'white'))
                # Remove legend title styling since there's no title now
                # legend.get_title().set_color(theme.get('text_color', 'black'))
                # legend.get_title().set_weight('bold')
            
            # Apply theme colors to the plot with larger tick labels
            ax_3d.xaxis.label.set_color(theme.get('text_color', 'black'))
            ax_3d.yaxis.label.set_color(theme.get('text_color', 'black'))
            ax_3d.zaxis.label.set_color(theme.get('text_color', 'black'))
            ax_3d.tick_params(colors=theme.get('text_color', 'black'), labelsize=10)
            
            # Enhanced grid appearance
            ax_3d.grid(True, alpha=0.4, color=theme.get('grid_color', 'gray'), linestyle='-', linewidth=0.5)
            
            # Set transparent panes for better visibility
            ax_3d.xaxis.pane.fill = False
            ax_3d.yaxis.pane.fill = False
            ax_3d.zaxis.pane.fill = False
            
            # Make pane edges more subtle
            ax_3d.xaxis.pane.set_edgecolor('gray')
            ax_3d.yaxis.pane.set_edgecolor('gray')
            ax_3d.zaxis.pane.set_edgecolor('gray')
            ax_3d.xaxis.pane.set_alpha(0.1)
            ax_3d.yaxis.pane.set_alpha(0.1)
            ax_3d.zaxis.pane.set_alpha(0.1)
            
            # Update GUI axis reference
            self.gui.ax = ax_3d
            
            # Set figure background
            self.fig.patch.set_facecolor(theme.get('bg_color', 'white'))
            
            # Ensure the canvas draws the plot properly
            if hasattr(self.gui, 'canvas') and self.gui.canvas:
                self.gui.canvas.draw()
            
            # Toggle button removed - always use 3D view
            
            # Bind click events for toggle button with enhanced error protection
            if (hasattr(self.gui, 'fig') and self.gui.fig and 
                hasattr(self.gui.fig, 'canvas') and self.gui.fig.canvas and
                hasattr(self.gui.fig.canvas, 'mpl_connect')):
                try:
                    # Check if there are any existing pick_event handlers and clear them to avoid duplicates
                    canvas = self.gui.fig.canvas
                    if hasattr(canvas, 'callbacks') and hasattr(canvas.callbacks, 'callbacks'):
                        if 'pick_event' in canvas.callbacks.callbacks:
                            # Clear existing pick event handlers to avoid accumulation
                            existing_handlers = canvas.callbacks.callbacks['pick_event'].copy()
                            canvas.callbacks.callbacks['pick_event'] = {}
                    
                    # Connect the new handler
                    # Toggle button event binding removed - always use 3D view
                    
                except (AttributeError, RuntimeError, KeyError):
                    # Ignore errors during setup
                    pass
            
            # Ensure the plot is finalized and displayed
            self.gui._finalize_plot()
                
        except ImportError:
            _LOGGER.error("3D plotting not available - mplot3d required")
            # Show error message instead of 2D fallback
            self.fig.clear()
            self.gui.ax = self.fig.add_subplot(111)
            self.gui.ax.text(0.5, 0.5, '3D plotting not available\nPlease install mplot3d', 
                           ha='center', va='center', transform=self.gui.ax.transAxes,
                           fontsize=14, color='red')
            self.gui._finalize_plot()
        except Exception as e:
            _LOGGER.error(f"Error creating clustering plot: {e}")
            # Show error message instead of 2D fallback
            self.fig.clear() 
            self.gui.ax = self.fig.add_subplot(111)
            self.gui.ax.text(0.5, 0.5, f'Error creating clustering plot\n{str(e)}', 
                           ha='center', va='center', transform=self.gui.ax.transAxes,
                           fontsize=12, color='red')
            self.gui._finalize_plot()
        
        # Finalize the plot with tight layout for maximum space usage
        try:
            if hasattr(self, 'fig') and self.fig:
                self.fig.tight_layout(pad=0.5)
        except Exception as e:
            _LOGGER.debug(f"Layout adjustment skipped: {e}")
        
        try:
            if hasattr(self.gui, '_finalize_plot'):
                self.gui._finalize_plot()
        except Exception as e:
            _LOGGER.debug(f"Plot finalization skipped: {e}")
    
    def _plot_clustering_summary_2d(self):
        """2D plotting functionality removed - always use 3D view"""
        # This method is kept for compatibility but does nothing
        # 2D functionality has been completely removed
        pass
    
    def plot_redshift_age(self):
        """Plot redshift vs age analysis using the analysis plotter"""
        try:
            # Clear Flux/Flat selection when displaying this analysis plot
            self._deactivate_view_style()
            
            # Ensure matplotlib is initialized
            if self.fig is None:
                self.gui.init_matplotlib_plot()
            
            # Clear the plot
            self.ax.clear()
            
            if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results or not self.gui.snid_results.best_matches:
                theme = self.theme_manager.get_current_theme()
                text_color = theme.get('text_color', 'black')
                self.ax.text(0.5, 0.5, 'No results available\nRun SNID analysis first', 
                           ha='center', va='center', transform=self.ax.transAxes,
                           fontsize=14, color=text_color)
                self.ax.set_title('No Redshift-Age Data', color=text_color)
                self.gui._finalize_plot()
                return
            
            # Import the plotting function from SNID
            try:
                from snid_sage.snid.plotting import plot_redshift_age
                
                # Use the SNID plotting function but capture the figure
                # Clear our current figure and use it for the SNID plot
                self.fig.clear()
                
                # Call the SNID plotting function with our figure
                plot_redshift_age(self.gui.snid_results, fig=self.fig)
                
                # Recreate our axis reference since we cleared the figure
                self.gui.ax = self.fig.gca()
                
                # Apply theme styling
                self.gui._finalize_plot()
                
                _LOGGER.info("✅ Redshift vs age plot generated")
                
            except ImportError as e:
                theme = self.theme_manager.get_current_theme()
                text_color = theme.get('text_color', 'black')
                danger_color = theme.get('danger_color', 'red')
                self.ax.text(0.5, 0.5, f'Redshift-age plotting not available\nImport error: {e}', 
                           ha='center', va='center', transform=self.ax.transAxes,
                           fontsize=12, color=danger_color)
                self.ax.set_title('Redshift-Age Plot Unavailable', color=text_color)
                self.gui._finalize_plot()
                
        except Exception as e:
            _LOGGER.error(f"Error plotting redshift vs age: {e}")
            import traceback
            traceback.print_exc()
            self.gui._plot_error(f"Error plotting redshift vs age: {str(e)}")
    
    def plot_subtype_proportions(self):
        """Plot subtype proportions within selected cluster using the analysis plotter"""
        try:
            # Clear Flux/Flat selection when displaying this analysis plot
            self._deactivate_view_style()
            
            # Ensure matplotlib is initialized
            if self.fig is None:
                self.gui.init_matplotlib_plot()
            
            # Clear the plot
            self.ax.clear()
            
            if not hasattr(self.gui, 'snid_results') or not self.gui.snid_results or not self.gui.snid_results.best_matches:
                theme = self.theme_manager.get_current_theme()
                text_color = theme.get('text_color', 'black')
                self.ax.text(0.5, 0.5, 'No results available\nRun SNID analysis first', 
                           ha='center', va='center', transform=self.ax.transAxes,
                           fontsize=14, color=text_color)
                self.ax.set_title('No Subtype Proportions Data', color=text_color)
                self.gui._finalize_plot()
                return
            
            # Import the plotting function from SNID
            try:
                from snid_sage.snid.plotting import plot_cluster_subtype_proportions
                
                # Get the selected cluster from clustering results
                selected_cluster = None
                if (hasattr(self.gui, 'snid_results') and 
                    hasattr(self.gui.snid_results, 'clustering_results') and 
                    self.gui.snid_results.clustering_results):
                    
                    clustering_results = self.gui.snid_results.clustering_results
                    
                    # Check for user-selected cluster first
                    if 'user_selected_cluster' in clustering_results:
                        selected_cluster = clustering_results['user_selected_cluster']
                    elif 'best_cluster' in clustering_results:
                        # Fall back to automatic best cluster
                        selected_cluster = clustering_results['best_cluster']
                
                # Use the SNID plotting function but capture the figure
                # Clear our current figure and use it for the SNID plot
                self.fig.clear()
                
                # Call the SNID plotting function with our figure
                plot_cluster_subtype_proportions(
                    self.gui.snid_results, 
                    selected_cluster=selected_cluster,
                    fig=self.fig,
                    theme_manager=self.theme_manager
                )
                
                # Recreate our axis reference since we cleared the figure
                # Subtype proportions may have multiple subplots, so get all axes
                axes = self.fig.get_axes()
                if axes:
                    self.gui.ax = axes[0]  # Use first axis as primary
                
                # Apply theme styling
                self.gui._finalize_plot()
                
                _LOGGER.info("✅ Subtype proportions plot generated")
                
            except ImportError as e:
                theme = self.theme_manager.get_current_theme()
                text_color = theme.get('text_color', 'black')
                danger_color = theme.get('danger_color', 'red')
                self.ax.text(0.5, 0.5, f'Subtype proportions plotting not available\nImport error: {e}', 
                           ha='center', va='center', transform=self.ax.transAxes,
                           fontsize=12, color=danger_color)
                self.ax.set_title('Subtype Proportions Plot Unavailable', color=text_color)
                self.gui._finalize_plot()
                
        except Exception as e:
            _LOGGER.error(f"Error plotting subtype proportions: {e}")
            import traceback
            traceback.print_exc()
            self.gui._plot_error(f"Error plotting subtype proportions: {str(e)}")
    
    def _on_toggle_button_click(self, event):
        """Toggle button functionality removed - always use 3D view"""
        # This method is kept for compatibility but does nothing
        # 2D functionality has been completely removed
        pass 

    def _deactivate_view_style(self):
        """Clear Flux/Flat segmented control so that no option appears active."""
        try:
            if hasattr(self.gui, 'view_style'):
                # Only update if currently set to one of the spectrum views
                if self.gui.view_style.get() in ("Flux", "Flat"):
                    self.gui.view_style.set("")  # Clear selection
                # Ensure the segmented control button colours reflect the new state
                if hasattr(self.gui, '_update_segmented_control_buttons'):
                    self.gui._update_segmented_control_buttons()
        except Exception as e:
            _LOGGER.debug(f"View style deactivation failed: {e}")
