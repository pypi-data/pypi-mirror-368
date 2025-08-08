"""Analysis Results Summary Module"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.cluster_summary')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.cluster_summary')

# Import all needed math utility functions
try:
    from snid_sage.shared.utils.math_utils import (
        calculate_weighted_redshift_balanced,
        calculate_weighted_age_estimate,
        calculate_weighted_median,
        get_best_metric_value,
        get_metric_name_for_match
    )
    _MATH_UTILS_AVAILABLE = True
except ImportError as e:
    _LOGGER.error(f"Failed to import math utilities: {e}")
    _MATH_UTILS_AVAILABLE = False
    # Create dummy functions to prevent crashes
    def calculate_joint_weighted_estimates(*args, **kwargs):
        return 0.0, 0.0, 0.01, 1.0, 0.0
    def calculate_weighted_redshift(*args, **kwargs):
        return 0.0, 0.01
    def calculate_weighted_age(*args, **kwargs):
        return 0.0, 1.0
    def calculate_weighted_median(values, weights):
        return np.median(values) if len(values) > 0 else 0.0
    def get_best_metric_value(match):
        return match.get('rlap', 0.0)
    def get_metric_name_for_match(match):
        return "RLAP"


def is_valid_age(age):
    """
    Check if an age value is valid and available.
    
    Returns True if age is a finite number (including negative values for pre-maximum times).
    Returns False if age is NaN, -999 (not available marker), or non-finite.
    """
    if age is None:
        return False
    
    try:
        age_float = float(age)
        # Check for common "not available" markers and invalid values
        # FIXED: Removed age_float <= 0 check since negative ages are valid (pre-maximum light)
        if not np.isfinite(age_float) or age_float == -999:
            return False
        return True
    except (ValueError, TypeError):
        return False


def extract_age(match, template=None):
    """
    Extract age from match or template, checking multiple possible fields.
    
    Parameters:
    -----------
    match : dict
        Match dictionary (may contain 'age' field)
    template : dict, optional
        Template dictionary (may contain 'age', 'epoch_age', 'phase' fields)
        
    Returns:
    --------
    float or None
        Valid age value, or None if no valid age found
    """
    # First try match-level age (epoch-specific)
    if match and 'age' in match:
        age = match.get('age')
        if is_valid_age(age):
            return float(age)
    
    # Then try template-level ages
    if template:
        # Try standard age field
        age = template.get('age')
        if is_valid_age(age):
            return float(age)
            
        # Try other age-related fields
        for field in ['epoch_age', 'phase', 'days_from_max']:
            age = template.get(field)
            if is_valid_age(age):
                return float(age)
    
    return None


def format_age_display(age_value):
    """
    Format age value for display.
    
    Parameters:
    -----------
    age_value : float or None
        Age value to format
        
    Returns:
    --------
    str
        Formatted age string ("N/A" if invalid/None, otherwise formatted number)
    """
    if age_value is None or not is_valid_age(age_value):
        return "N/A"
    return f"{age_value:.1f}"


def weighted_median(values, weights):
    """Calculate weighted median of a dataset."""
    if len(values) == 0:
        return 0.0
    
    values = np.array(values, dtype=float)
    weights = np.array(weights, dtype=float)
    
    # Filter out NaN values and their corresponding weights
    # Weights should be > 0 (RLAP, cosine similarity, or RLAP-cos are all positive metrics)
    valid_mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not np.any(valid_mask):
        return 0.0
    
    values = values[valid_mask]
    weights = weights[valid_mask]
    
    if len(values) == 1:
        return float(values[0])
        
    # Sort values and weights together
    idx = np.argsort(values)
    sorted_values = values[idx]
    sorted_weights = weights[idx]
    
    # Calculate cumulative weight
    cumw = np.cumsum(sorted_weights)
    
    # Find median at half of total weight
    half = cumw[-1] / 2.0
    idx = np.searchsorted(cumw, half)
    
    if idx >= len(values):  # Safety check
        return float(sorted_values[-1])
    
    return float(sorted_values[idx])


def weighted_mean_with_uncertainty(values, weights):
    """
    Calculate weighted mean and uncertainty using the new weighted statistics.
    
    This function provides backwards compatibility with updated implementation.
    """
    import numpy as np
    if _MATH_UTILS_AVAILABLE:
        # Use new weighted redshift calculation for single-variable estimation
        weighted_mean, uncertainty = calculate_weighted_redshift(values, weights)
        return weighted_mean, uncertainty
    else:
        # Fallback calculation
        values = np.asarray(values)
        weights = np.asarray(weights)
        if len(values) == 0 or np.sum(weights) == 0:
            return 0.0, 0.0
        weighted_mean = np.sum(values * weights) / np.sum(weights)
        # Simple uncertainty estimate
        variance = np.sum(weights * (values - weighted_mean)**2) / np.sum(weights)
        uncertainty = np.sqrt(variance / len(values))
        return float(weighted_mean), float(uncertainty)


class AnalysisResultsAnalyzer:
    def __init__(self, selected_cluster, all_candidates):
        self.selected_cluster = selected_cluster
        self.all_candidates = all_candidates
        raw_matches = selected_cluster.get('matches', [])
        
        # CRITICAL: Apply RLAP threshold filtering (should be done everywhere in SNID)
        # Get the RLAP threshold that was used in the analysis
        rlapmin = 5.0  # Default threshold - in production this should come from analysis parameters
        
        # Apply the same RLAP filtering that should be applied everywhere
        self.matches = [m for m in raw_matches if m.get('rlap', 0) >= rlapmin]
        self.rlapmin = rlapmin
        
        self.summary_stats = self._generate_summary_statistics()
        
    def _generate_summary_statistics(self):
        if not self.matches:
            return {}
        
        redshifts = np.array([m['redshift'] for m in self.matches])
        rlaps = np.array([m['rlap'] for m in self.matches])
        
        # Collect redshift data with uncertainties for balanced estimation
        redshifts_with_errors = []
        redshift_errors = []
        rlap_cos_for_redshift = []
        
        # Collect age data for separate age estimation  
        ages_for_estimation = []
        rlap_cos_for_age = []
        
        for m in self.matches:
            template = m.get('template', {})
            rlap_cos = get_best_metric_value(m)
            
            # Collect redshift data (uncertainties always available)
            z = m.get('redshift')
            z_err = m.get('redshift_error', 0.0)
            if z is not None and np.isfinite(z) and z_err > 0:
                redshifts_with_errors.append(z)
                redshift_errors.append(z_err)
                rlap_cos_for_redshift.append(rlap_cos)
            
            # Separately collect age data (no uncertainties available)
            age = extract_age(m, template)
            if age is not None and np.isfinite(age):
                ages_for_estimation.append(age)
                rlap_cos_for_age.append(rlap_cos)
        
        # Balanced redshift estimation
        if len(redshifts_with_errors) > 0 and _MATH_UTILS_AVAILABLE:
            z_weighted_mean, z_weighted_uncertainty = calculate_weighted_redshift_balanced(
                redshifts_with_errors, redshift_errors, rlap_cos_for_redshift
            )
            cluster_scatter = 0.0  # Properly handled in balanced estimation
        else:
            # Fallback if no valid data or math utils not available
            if len(redshifts) > 0:
                z_weighted_mean = np.average(redshifts, weights=rlaps)
                z_weighted_uncertainty = 0.01
            else:
                z_weighted_mean = np.nan
                z_weighted_uncertainty = np.nan
            cluster_scatter = 0.0
        
        # Simple age estimation
        if len(ages_for_estimation) > 0 and _MATH_UTILS_AVAILABLE:
            age_weighted_mean = calculate_weighted_age_estimate(ages_for_estimation, rlap_cos_for_age)
            age_weighted_uncertainty = 0.0  # No uncertainty available for ages
            age_stat_error = 0.0
            age_total_error = 0.0
            age_scatter = 0.0
        else:
            # No valid age data or math utils not available
            age_weighted_mean = 0.0
            age_weighted_uncertainty = 0.0
            age_stat_error = 0.0
            age_total_error = 0.0
            age_scatter = 0.0
        
        rlap_weighted_mean = np.mean(rlaps)  # For RLAP, just use mean since weighting by itself doesn't add value
        rlap_weighted_median = calculate_weighted_median(rlaps, rlaps)
        
        # Calculate subtype statistics
        subtype_stats = self._calculate_subtype_statistics()
        
        # Age statistics (using joint estimation results or separate calculation for all ages)
        ages = []
        age_weights = []
        for m in self.matches:
            template = m.get('template', {})
            age = extract_age(m, template)
            if age is not None:
                ages.append(age)
                age_weights.append(get_best_metric_value(m))
        
        age_stats = {}
        if len(ages_for_estimation) > 0:
            # Use separate estimation results
            age_stats = {
                'min': np.min(ages) if ages else 0.0,
                'max': np.max(ages) if ages else 0.0,
                'weighted_mean': age_weighted_mean,
                'weighted_uncertainty': age_total_error,
                'statistical_uncertainty': age_stat_error,
                'total_uncertainty': age_total_error,
                'cluster_scatter': age_scatter,
                'count': len(ages) if ages else 0,
                'redshift_age_covariance': 0.0  # No covariance since we estimate separately
            }
        elif ages:
            # Fallback for age-only calculation when no joint data available
            if _MATH_UTILS_AVAILABLE:
                # This is old fallback code - should not be reached with new implementation
                age_weighted_mean_fallback = np.average(ages, weights=age_weights)
                age_weighted_uncertainty_fallback = 0.0
            else:
                age_weighted_mean_fallback = np.average(ages, weights=age_weights)
                age_weighted_uncertainty_fallback = 1.0
            
            age_stats = {
                'min': np.min(ages),
                'max': np.max(ages),
                'weighted_mean': age_weighted_mean_fallback,
                'weighted_uncertainty': age_weighted_uncertainty_fallback,
                'statistical_uncertainty': age_weighted_uncertainty_fallback,
                'total_uncertainty': age_weighted_uncertainty_fallback,
                'cluster_scatter': 0.0,
                'count': len(ages),
                'redshift_age_covariance': 0.0
            }
        
        return {
            'cluster_size': len(self.matches),
            'supernova_type': self.selected_cluster.get('type', 'Unknown'),
            'subtype_stats': subtype_stats,
            'redshift': {
                'min': np.min(redshifts),
                'max': np.max(redshifts),
                'weighted_mean': z_weighted_mean,
                'weighted_uncertainty': z_weighted_uncertainty,
                'cluster_scatter': cluster_scatter
            },
            'rlap': {
                'mean': np.mean(rlaps),
                'min': np.min(rlaps),
                'max': np.max(rlaps),
                'weighted_mean': rlap_weighted_mean,
                'weighted_median': rlap_weighted_median
            },
            'age': age_stats,
            'quality_score': self.selected_cluster.get('quality_score', 0)
        }
    
    def _calculate_subtype_statistics(self):
        """Calculate detailed subtype statistics within the cluster"""
        from collections import defaultdict
        
        subtype_data = defaultdict(lambda: {
            'count': 0,
            'rlaps': [],
            'redshifts': [],
            'ages': [],
            'redshift_errors': [],
            'r_values': [],
            'laps': []
        })
        
        for match in self.matches:
            template = match.get('template', {})
            subtype = template.get('subtype', 'Unknown') if template else 'Unknown'
            if not subtype or subtype.strip() == '':
                subtype = 'Unknown'
            
            subtype_data[subtype]['count'] += 1
            subtype_data[subtype]['rlaps'].append(match.get('rlap', 0))
            subtype_data[subtype]['redshifts'].append(match.get('redshift', 0))
            subtype_data[subtype]['redshift_errors'].append(match.get('redshift_error', 0))
            subtype_data[subtype]['r_values'].append(match.get('r', 0))
            subtype_data[subtype]['laps'].append(match.get('lap', 0))
            
            # FIXED: Improved age extraction using new helper function
            age = extract_age(match, template)
            
            # Only add valid ages to the statistics
            if age is not None:
                subtype_data[subtype]['ages'].append(age)
        
        # Calculate statistics for each subtype
        subtype_stats = {}
        total_matches = len(self.matches)
        
        for subtype, data in subtype_data.items():
            count = data['count']
            rlaps = np.array(data['rlaps'])
            redshifts = np.array(data['redshifts'])
            redshift_errors = np.array(data['redshift_errors'])
            r_values = np.array(data['r_values'])
            laps = np.array(data['laps'])
            ages = np.array(data['ages']) if data['ages'] else np.array([])
            
            # Weighted redshift statistics
            # Get quality weights for this specific subtype
            subtype_rlap_weights = []
            for match in self.matches:
                template = match.get('template', {})
                match_subtype = template.get('subtype', 'Unknown')
                if match_subtype == subtype:
                    subtype_rlap_weights.append(get_best_metric_value(match))
            
            subtype_rlap_weights = np.array(subtype_rlap_weights[:len(redshifts)])  # Ensure matching length
            
            from snid_sage.shared.utils.math_utils import calculate_weighted_redshift
            z_weighted_mean, z_weighted_uncertainty = calculate_weighted_redshift(
                redshifts, subtype_rlap_weights
            )
            
            # Weighted age statistics (only for templates with valid ages)
            if len(ages) > 0:
                # Get quality values for templates that have valid ages in this subtype
                age_rlaps = []
                for match in self.matches:
                    template = match.get('template', {})
                    match_subtype = template.get('subtype', 'Unknown')
                    if match_subtype == subtype:
                        age = extract_age(match, template)
                        if age is not None and np.isfinite(age):
                            age_rlaps.append(get_best_metric_value(match))
                
                if len(age_rlaps) == len(ages) and len(ages) > 0:
                    # Use new age estimation function
                    age_weighted_mean = calculate_weighted_age_estimate(ages, age_rlaps)
                    age_weighted_uncertainty = 0.0  # No uncertainty available for ages
                else:
                    age_weighted_mean, age_weighted_uncertainty = 0.0, 0.0
            else:
                age_weighted_mean = age_weighted_uncertainty = 0
            
            subtype_stats[subtype] = {
                'count': count,
                'proportion': count / total_matches if total_matches > 0 else 0,
                'rlap_mean': np.mean(rlaps) if len(rlaps) > 0 else 0,
                'rlap_weighted_mean': np.mean(rlaps) if len(rlaps) > 0 else 0,  # Self-weighted
                'redshift_weighted_mean': z_weighted_mean,
                'redshift_weighted_uncertainty': z_weighted_uncertainty,
                'z_weighted_mean': z_weighted_mean,
                'z_weighted_uncertainty': z_weighted_uncertainty,
                'redshift_error_reference': np.median(redshift_errors) if len(redshift_errors) > 0 else 0,
                'r_value_mean': np.mean(r_values) if len(r_values) > 0 else 0,
                'lap_mean': np.mean(laps) if len(laps) > 0 else 0,
                # Enhanced age statistics only
                'age_weighted_mean': age_weighted_mean,
                'age_weighted_uncertainty': age_weighted_uncertainty,
                'age_count': len(ages)
            }
        
        return subtype_stats
    
    def generate_summary_report(self):
        """Generate a clean, simplified analysis results report"""
        if not self.summary_stats:
            return "No cluster data available for summary."
        
        stats = self.summary_stats
        
        # Clean, simplified header
        lines = [
            "🔬 SNID CLASSIFICATION SUMMARY",
            "=" * 50,
            "",
            f"🎯 CLASSIFICATION:",
            f"   Type: {stats['supernova_type']}",
        ]
        
        # Simple subtype display
        sorted_subtypes = []
        if stats.get('subtype_stats'):
            subtype_data = stats['subtype_stats']
            sorted_subtypes = sorted(subtype_data.items(), key=lambda x: x[1]['proportion'], reverse=True)
            
            if sorted_subtypes:
                primary_subtype, primary_data = sorted_subtypes[0]
                primary_proportion = primary_data['proportion']
                
                lines.extend([
                    f"   Subtype: {primary_subtype} ({primary_proportion*100:.0f}% of templates)",
                    ""
                ])
        
        # Essential measurements only
        z_stats = stats.get('redshift', {})
        if z_stats:
            weighted_mean = z_stats.get('weighted_mean', 0.0)
            weighted_uncertainty = z_stats.get('weighted_uncertainty', 0.0)
            lines.extend([
                f"📏 MEASUREMENTS:",
                f"   Redshift: {weighted_mean:.4f} ± {weighted_uncertainty:.4f}",
            ])
        else:
            lines.extend([
                f"📏 MEASUREMENTS:",
                f"   Redshift: Not available",
            ])
        
        # Age if available
        if stats.get('age') and stats['age'].get('count', 0) > 0:
            age_stats = stats['age']
            age_mean = age_stats.get('weighted_mean', 0.0)
            age_uncertainty = age_stats.get('weighted_uncertainty', 0.0)
            lines.append(f"   Age: {age_mean:.0f} ± {age_uncertainty:.0f} days")
        
        lines.extend([
            "",
            f"📊 ANALYSIS:",
            f"   Templates used: {stats['cluster_size']}",
            f"   Mean RLAP: {stats['rlap']['mean']:.1f}",
        ])
        
        # Add new quality metrics if available
        if hasattr(self, 'selected_cluster') and self.selected_cluster:
            if 'quality_assessment' in self.selected_cluster:
                qa = self.selected_cluster['quality_assessment']
                lines.append(f"   Quality Category: {qa.get('quality_category', 'Unknown')}")
                lines.append(f"   Quality Score: {qa.get('penalized_score', 0):.1f} (penalized top-5)")
            
            if 'confidence_assessment' in self.selected_cluster:
                ca = self.selected_cluster['confidence_assessment']
                lines.append(f"   Confidence Level: {ca.get('confidence_level', 'unknown').upper()}")
                if ca.get('second_best_type', 'N/A') != 'N/A':
                    lines.append(f"   vs {ca.get('second_best_type', 'N/A')}: {ca.get('confidence_description', '')}")
        
        lines.append("")
        
        # Sort matches by RLAP descending
        sorted_matches = sorted(self.matches, key=get_best_metric_value, reverse=True)
        
        # Get metric name from first match
        metric_name = "RLAP"
        if sorted_matches:
            metric_name = get_metric_name_for_match(sorted_matches[0])
        
        # Table header
        lines.extend([
            f"{'Rank':<4} {'Template':<20} {'Type':<8} {'Subtype':<12} {metric_name:<6} {'Redshift':<10} {'z_err':<8} {'Age':<8}",
            f"{'-'*4} {'-'*20} {'-'*8} {'-'*12} {'-'*6} {'-'*10} {'-'*8} {'-'*8}"
        ])
        
        # Show top matches
        for i, match in enumerate(sorted_matches[:10], 1):
            template = match.get('template', {})
            template_name = template.get('name', 'Unknown')[:18]  # Truncate long names
            template_type = template.get('type', 'Unknown')[:6]
            template_subtype = template.get('subtype', 'Unknown')[:10]
            metric_value = get_best_metric_value(match)
            redshift = match.get('redshift', 0)
            redshift_error = match.get('redshift_error', 0)
            
            # Extract epoch-specific age from match first, then template as fallback
            # For display purposes, show raw age values including -999 (not available marker)
            age = match.get('age')
            if age is None:
                age = template.get('age', 0) if template else 0
            
            # Format age for display - show raw values including -999
            if age is not None and np.isfinite(age):
                age_str = f"{age:.1f}"
            else:
                age_str = "N/A"
            
            z_err_str = f"{redshift_error:.5f}" if redshift_error > 0 else "N/A"
            
            # FIXED: Better formatting with proper spacing
            lines.append(f"{i:<4} {template_name:<20} {template_type:<8} {template_subtype:<12} "
                        f"{metric_value:<6.1f} {redshift:<10.5f} {z_err_str:<8} {age_str:<8}")
        
        if len(sorted_matches) > 10:
            lines.append(f"   ... and {len(sorted_matches) - 10} more templates in cluster")
        
        lines.extend([
            "",
            "=" * 80
        ])
        
        return "\n".join(lines)


class AnalysisResultsDialog:
    def __init__(self, parent, selected_cluster, all_candidates, theme_manager, cluster_index=-1):
        self.parent = parent
        self.selected_cluster = selected_cluster
        self.all_candidates = all_candidates
        self.theme_manager = theme_manager
        self.cluster_index = cluster_index
        
        self.analyzer = AnalysisResultsAnalyzer(selected_cluster, all_candidates)
        
        self.window = None
        self._create_dialog()
        
    def _create_dialog(self):
        self.window = tk.Toplevel(self.parent)
        cluster_type = self.selected_cluster.get('type', 'Unknown')
        cluster_num = self.cluster_index + 1 if self.cluster_index >= 0 else '?'
        self.window.title(f"📊 Analysis Results - {cluster_type} (Top Cluster #{cluster_num})")
        self.window.geometry("900x700")
        self.window.transient(self.parent)
        
        # Apply theme
        if self.theme_manager:
            self.window.configure(bg=self.theme_manager.get_color('bg_secondary'))
        
        # Header
        header_frame = tk.Frame(self.window)
        if self.theme_manager:
            header_frame.configure(bg=self.theme_manager.get_color('bg_secondary'))
        header_frame.pack(pady=15)
        
        header = tk.Label(header_frame, 
                         text=f"📊 Analysis Results\n{cluster_type} (Top Cluster #{cluster_num})", 
                         font=('Arial', 16, 'bold'),
                         justify='center')
        if self.theme_manager:
            header.configure(bg=self.theme_manager.get_color('bg_secondary'),
                           fg=self.theme_manager.get_color('text_primary'))
        header.pack()
        
        # Summary text
        text_frame = tk.Frame(self.window)
        if self.theme_manager:
            text_frame.configure(bg=self.theme_manager.get_color('bg_secondary'))
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 12))
        if self.theme_manager:
            config = {
                'bg': self.theme_manager.get_color('bg_tertiary'),
                'fg': self.theme_manager.get_color('text_primary'),
                'insertbackground': self.theme_manager.get_color('text_primary'),
                'selectbackground': self.theme_manager.get_color('accent'),
                'selectforeground': self.theme_manager.get_color('bg_primary')
            }
            # Apply configuration safely
            try:
                text_widget.configure(**config)
            except tk.TclError:
                # If selectforeground fails, apply without it
                safe_config = {k: v for k, v in config.items() if k != 'selectforeground'}
                text_widget.configure(**safe_config)
        
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        if self.theme_manager:
            scrollbar.configure(
                bg=self.theme_manager.get_color('bg_secondary'),
                troughcolor=self.theme_manager.get_color('bg_tertiary'),
                activebackground=self.theme_manager.get_color('accent')
            )
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Insert summary
        summary_text = self.analyzer.generate_summary_report()
        text_widget.insert('1.0', summary_text)
        text_widget.configure(state='disabled')
        
        # Button frame
        button_frame = tk.Frame(self.window)
        if self.theme_manager:
            button_frame.configure(bg=self.theme_manager.get_color('bg_secondary'))
        button_frame.pack(pady=15)
        
        # Close button
        close_btn = tk.Button(button_frame, text="✅ Close", 
                             font=('Arial', 12, 'bold'),
                             command=self.window.destroy)
        if self.theme_manager:
            close_btn.configure(
                bg=self.theme_manager.get_color('btn_secondary'),
                fg=self.theme_manager.get_color('text_on_accent'),
                activebackground=self.theme_manager.get_color('btn_secondary_hover'),
                relief='raised',
                bd=2,
                padx=20,
                pady=8
            )
        close_btn.pack()
        
        # Center the window
        self._center_window()
    
    def _center_window(self):
        """Center the dialog window on screen"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"900x700+{x}+{y}")


def show_analysis_results_dialog(parent, selected_cluster, all_candidates, theme_manager, cluster_index=-1):
    return AnalysisResultsDialog(parent, selected_cluster, all_candidates, theme_manager, cluster_index)


