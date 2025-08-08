"""
SNID Batch Command
=================

Simplified command for batch processing multiple spectra with SNID.
Two modes: Complete analysis or Minimal summary.

OPTIMIZED VERSION: Templates are loaded once and reused for all spectra.
"""

import argparse
import sys
import os
import glob
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import concurrent.futures
from datetime import datetime
import json
import time
import numpy as np

from snid_sage.snid.snid import preprocess_spectrum, run_snid_analysis, SNIDResult
from snid_sage.shared.utils.math_utils import (
    calculate_weighted_redshift_balanced,
    calculate_weighted_age_estimate,
    get_best_metric_value
)

# Import and apply centralized font configuration for consistent plotting
try:
    from snid_sage.shared.utils.plotting.font_sizes import apply_font_config
    apply_font_config()
except ImportError:
    # Fallback if font configuration is not available
    pass


class BatchTemplateManager:
    """
    Optimized template manager for batch processing.
    
    Loads templates once and reuses them for all spectrum analyses,
    providing 10-50x speedup for batch processing by avoiding repeated
    template loading and FFT computation.
    """
    
    def __init__(self, templates_dir: Optional[str], verbose: bool = False):
        # Validate and auto-correct templates directory
        self.templates_dir = self._validate_and_fix_templates_dir(templates_dir)
        self.verbose = verbose
        self._templates = None
        self._templates_metadata = None
        self._load_time = None
        
        # Initialize logging
        self._log = logging.getLogger('snid_sage.snid.batch.template_manager')
    
    def _validate_and_fix_templates_dir(self, templates_dir: Optional[str]) -> str:
        """
        Validate templates directory and auto-correct if needed.
        
        Args:
            templates_dir: Path to templates directory (None to auto-discover)
            
        Returns:
            Valid templates directory path
            
        Raises:
            FileNotFoundError: If no valid templates directory can be found
        """
        # If no templates directory provided, auto-discover
        if templates_dir is None:
            try:
                from snid_sage.shared.utils.simple_template_finder import find_templates_directory_or_raise
                auto_found_dir = find_templates_directory_or_raise()
                print(f"[SUCCESS] Auto-discovered templates at: {auto_found_dir}")
                return str(auto_found_dir)
            except (ImportError, FileNotFoundError):
                raise FileNotFoundError(
                    "Could not auto-discover templates directory. Please provide templates_dir explicitly."
                )
        
        # Check if provided directory exists and is valid
        if os.path.exists(templates_dir):
            return templates_dir
        
        # Try to auto-find templates directory
        try:
            from snid_sage.shared.utils.simple_template_finder import find_templates_directory_or_raise
            auto_found_dir = find_templates_directory_or_raise()
            print(f"⚠️  Templates directory '{templates_dir}' not found.")
            print(f"[SUCCESS] Auto-discovered templates at: {auto_found_dir}")
            return str(auto_found_dir)
        except (ImportError, FileNotFoundError):
            # Fallback failed
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
        
    def load_templates_once(self) -> bool:
        """
        Load templates once for the entire batch processing session.
        
        Returns
        -------
        bool
            True if templates were loaded successfully, False otherwise
        """
        if self._templates is not None:
            return True  # Already loaded
            
        start_time = time.time()
        
        try:
            # Use unified storage system (for HDF5 templates) - this is already optimized
            try:
                from snid_sage.snid.core.integration import load_templates_unified
                self._templates = load_templates_unified(self.templates_dir)
                self._templates_metadata = {}
                self._log.info(f"✅ Loaded {len(self._templates)} templates using UNIFIED STORAGE")
            except ImportError:
                # Fallback to standard loading (for .lnw files)
                from snid_sage.snid.io import load_templates
                self._templates, self._templates_metadata = load_templates(self.templates_dir, flatten=True)
                self._log.info(f"✅ Loaded {len(self._templates)} templates using STANDARD method")
            
            self._load_time = time.time() - start_time
            
            if not self._templates:
                self._log.error("❌ No templates loaded")
                self._log.error("   Check that templates directory exists and contains .hdf5 or .lnw files")
                self._log.error(f"   Templates directory: {self.templates_dir}")
                return False
                
            self._log.info(f"🚀 Template loading complete in {self._load_time:.2f}s")
            self._log.info(f"📊 Ready for batch processing with {len(self._templates)} templates")
            
            return True
            
        except Exception as e:
            self._log.error(f"❌ Failed to load templates: {e}")
            self._log.error(f"   Templates directory: {self.templates_dir}")
            self._log.error("   Ensure the directory exists and contains valid template files")
            if self.verbose:
                import traceback
                self._log.error(f"   Full traceback: {traceback.format_exc()}")
            return False
    
    def get_filtered_templates(self, 
                             type_filter: Optional[List[str]] = None,
                             template_filter: Optional[List[str]] = None,
                             age_range: Optional[Tuple[float, float]] = None) -> List[Dict[str, Any]]:
        """
        Get filtered templates without reloading from disk.
        
        Parameters
        ----------
        type_filter : list of str, optional
            Only include templates of these types
        template_filter : list of str, optional
            Only include templates with these names
        age_range : tuple of (float, float), optional
            Only include templates within this age range
            
        Returns
        -------
        List[Dict[str, Any]]
            Filtered templates ready for analysis
        """
        if self._templates is None:
            raise RuntimeError("Templates not loaded. Call load_templates_once() first.")
        
        templates = self._templates[:]  # Start with copy of all templates
        original_count = len(templates)
        
        # Apply age filtering
        if age_range is not None:
            age_min, age_max = age_range
            templates = [t for t in templates if age_min <= t.get('age', 0) <= age_max]
            self._log.info(f"🔍 Age filtering: {original_count} -> {len(templates)} templates")
        
        # Apply type filtering
        if type_filter is not None and len(type_filter) > 0:
            templates = [t for t in templates if t.get('type', '') in type_filter]
            self._log.info(f"🔍 Type filtering: {original_count} -> {len(templates)} templates")
        
        # Apply template name filtering
        if template_filter is not None and len(template_filter) > 0:
            pre_filter_count = len(templates)
            templates = [t for t in templates if t.get('name', '') in template_filter]
            self._log.info(f"🔍 Template name filtering: {pre_filter_count} -> {len(templates)} templates")
            
            if len(templates) == 0 and pre_filter_count > 0:
                self._log.warning(f"⚠️ All templates filtered out by name filter: {template_filter}")
        
        return templates
    
    @property
    def is_loaded(self) -> bool:
        """Check if templates are loaded."""
        return self._templates is not None
    
    @property
    def template_count(self) -> int:
        """Get total number of loaded templates."""
        return len(self._templates) if self._templates else 0
    
    @property
    def load_time(self) -> float:
        """Get time taken to load templates."""
        return self._load_time or 0.0


def process_single_spectrum_optimized(
    spectrum_path: str,
    template_manager: BatchTemplateManager,
    output_dir: str,
    args: argparse.Namespace
) -> Tuple[str, bool, str, Dict[str, Any]]:
    """
    Process a single spectrum using pre-loaded templates.
    
    This optimized version uses the BatchTemplateManager to avoid
    reloading templates for each spectrum.
    """
    spectrum_name = Path(spectrum_path).stem
    spectrum_output_dir = Path(output_dir) / spectrum_name
    
    # Determine output settings based on mode
    if args.minimal:
        # Minimal mode: basic output files only (no plots or extra data) - flat directory structure
        save_outputs = True
        create_dir = False  # Don't create individual spectrum directories
    elif args.complete:
        # Complete mode: all outputs including plots - organized in subdirectories
        save_outputs = True
        create_dir = True
        spectrum_output_dir.mkdir(parents=True, exist_ok=True)
    else:
        # Default mode: main outputs only - organized in subdirectories
        save_outputs = True
        create_dir = True
        spectrum_output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # STEP 1: Preprocess spectrum
        processed_spectrum, _ = preprocess_spectrum(
            spectrum_path=spectrum_path,
            savgol_window=getattr(args, 'savgol_window', 0),
            savgol_fwhm=getattr(args, 'savgol_fwhm', 0.0),
            savgol_order=getattr(args, 'savgol_order', 3),
            aband_remove=getattr(args, 'aband_remove', False),
            skyclip=getattr(args, 'skyclip', False),
            wavelength_masks=getattr(args, 'wavelength_masks', None),
            verbose=False  # Suppress preprocessing output in batch mode
        )
        
        # STEP 2: Get filtered templates (no reloading!)
        filtered_templates = template_manager.get_filtered_templates(
            type_filter=args.type_filter,
            template_filter=args.template_filter
        )
        
        if not filtered_templates:
            return spectrum_name, False, "No templates after filtering", {
                'spectrum': spectrum_name,
                'file_path': spectrum_path,
                'success': False,
                'error': 'No templates after filtering'
            }
        
        # STEP 3: Run SNID analysis with pre-loaded templates
        # Pass the templates directory to the analysis function
        _run_optimized_snid_analysis._templates_dir = template_manager.templates_dir
        
        result = _run_optimized_snid_analysis(
            processed_spectrum=processed_spectrum,
            templates=filtered_templates,
            zmin=args.zmin,
            zmax=args.zmax,
            forced_redshift=args.forced_redshift,
            verbose=False
        )
        
        # STEP 4: Generate outputs if requested
        if save_outputs and result.success:
            _save_spectrum_outputs(
                result=result,
                spectrum_path=spectrum_path,
                output_dir=spectrum_output_dir if create_dir else output_dir,
                args=args
            )
        
        if result.success:
            # Create GUI-style summary with cluster-aware analysis
            summary = _create_cluster_aware_summary(result, spectrum_name, spectrum_path)
            return spectrum_name, True, "Success", summary
        else:
            return spectrum_name, False, "No good matches found", {
                'spectrum': spectrum_name,
                'file_path': spectrum_path,
                'success': False
            }
            
    except Exception as e:
        return spectrum_name, False, str(e), {
            'spectrum': spectrum_name,
            'file_path': spectrum_path,
            'success': False,
            'error': str(e)
        }


def _run_optimized_snid_analysis(
    processed_spectrum: Dict[str, Any],
    templates: List[Dict[str, Any]],
    zmin: float = -0.01,
    zmax: float = 1.0,
    forced_redshift: Optional[float] = None,
    verbose: bool = False
) -> SNIDResult:
    """
    Run SNID analysis using pre-loaded templates.
    
    This bypasses the template loading in run_snid_analysis by monkey-patching
    the template loading functions to return our pre-loaded templates.
    """
    try:
        # Import required modules
        from snid_sage.snid.snid import SNIDResult
        
        # We need to pass a valid templates directory to avoid TemplateFFTStorage errors
        # Get the templates directory from the global template manager if possible
        templates_dir = getattr(_run_optimized_snid_analysis, '_templates_dir', None)
        if not templates_dir:
            # Fallback to a dummy directory - the monkey-patch will handle the actual loading
            templates_dir = "dummy_templates_dir"
        
        # Import the functions we need to patch
        import snid_sage.snid.core.integration
        import snid_sage.snid.io
        
        # Store original functions
        original_load_templates_unified = snid_sage.snid.core.integration.load_templates_unified
        original_load_templates = snid_sage.snid.io.load_templates
        
        # Create mock functions that return our pre-loaded templates
        def mock_load_templates_unified(template_dir, type_filter=None, template_names=None, exclude_templates=None):
            # Apply filtering to our pre-loaded templates
            filtered_templates = templates[:]
            
            if type_filter:
                filtered_templates = [t for t in filtered_templates if t.get('type', '') in type_filter]
            
            if template_names:
                filtered_templates = [t for t in filtered_templates if t.get('name', '') in template_names]
            
            if exclude_templates:
                filtered_templates = [t for t in filtered_templates if t.get('name', '') not in exclude_templates]
            
            return filtered_templates
        
        def mock_load_templates(template_dir, flatten=True):
            return templates, {}
        
        try:
            # Apply the monkey patches
            snid_sage.snid.core.integration.load_templates_unified = mock_load_templates_unified
            snid_sage.snid.io.load_templates = mock_load_templates
            
            # Temporarily suppress some logging during individual spectrum processing
            import logging
            snid_pipeline_logger = logging.getLogger('snid_sage.snid.pipeline')
            original_pipeline_level = snid_pipeline_logger.level
            
            # Set to ERROR level to suppress "No templates loaded" messages
            snid_pipeline_logger.setLevel(logging.ERROR)
            
            try:
                # Now call run_snid_analysis with the mocked functions
                result, _ = run_snid_analysis(
                    processed_spectrum=processed_spectrum,
                    templates_dir=templates_dir,
                    zmin=zmin,
                    zmax=zmax,
                    forced_redshift=forced_redshift,
                    verbose=verbose,
                    show_plots=False,
                    save_plots=False
                )
                
                return result
                
            finally:
                # Restore logging level
                snid_pipeline_logger.setLevel(original_pipeline_level)
                
        finally:
            # Restore original functions
            snid_sage.snid.core.integration.load_templates_unified = original_load_templates_unified
            snid_sage.snid.io.load_templates = original_load_templates
            
    except Exception as e:
        # Return failed result
        result = SNIDResult(success=False)
        result.error_message = str(e)
        return result


def _create_cluster_aware_summary(result: SNIDResult, spectrum_name: str, spectrum_path: str) -> Dict[str, Any]:
    """
    Create GUI-style cluster-aware summary with winning cluster analysis.
    
    This matches the GUI's approach of using the winning cluster for all analysis
    rather than mixing all matches above threshold.
    """
    # Get the winning cluster (user selected or automatic best)
    winning_cluster = None
    cluster_matches = []
    
    if (hasattr(result, 'clustering_results') and 
        result.clustering_results and 
        result.clustering_results.get('success')):
        
        clustering_results = result.clustering_results
        
        # Priority: user_selected_cluster > best_cluster  
        if 'user_selected_cluster' in clustering_results:
            winning_cluster = clustering_results['user_selected_cluster']
        elif 'best_cluster' in clustering_results:
            winning_cluster = clustering_results['best_cluster']
        
        if winning_cluster:
            cluster_matches = winning_cluster.get('matches', [])
            # Sort cluster matches by best available metric (RLAP-Cos if available, otherwise RLAP) descending
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            cluster_matches = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
    
    # If no clustering or cluster, fall back to filtered_matches, then best_matches
    if not cluster_matches:
        if hasattr(result, 'filtered_matches') and result.filtered_matches:
            cluster_matches = result.filtered_matches
            # Sort by best available metric (RLAP-Cos if available, otherwise RLAP) descending
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            cluster_matches = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
        elif hasattr(result, 'best_matches') and result.best_matches:
            cluster_matches = result.best_matches
            # Sort by best available metric (RLAP-Cos if available, otherwise RLAP) descending
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            cluster_matches = sorted(cluster_matches, key=get_best_metric_value, reverse=True)
    
    # Create the summary using winning cluster data
    summary = {
        'spectrum': spectrum_name,
        'file_path': spectrum_path,
        'success': True,
        'best_template': result.template_name,
        'best_template_type': result.template_type,
        'best_template_subtype': result.template_subtype,
        'consensus_type': result.consensus_type,
        'consensus_subtype': result.best_subtype,
        'redshift': result.redshift,
        'redshift_error': result.redshift_error,
        'rlap': result.rlap,


        'runtime': result.runtime_sec,
        'has_clustering': winning_cluster is not None,
        'cluster_size': len(cluster_matches) if cluster_matches else 0,
    }
    
    # Add cluster statistics if available
    if winning_cluster:
        summary['cluster_type'] = winning_cluster.get('type', 'Unknown')
        summary['cluster_score'] = winning_cluster.get('composite_score', 0.0)
        summary['cluster_method'] = 'Type-specific GMM'
        
        # Add new quality metrics
        if 'quality_assessment' in winning_cluster:
            qa = winning_cluster['quality_assessment']
            summary['cluster_quality_category'] = qa.get('quality_category', 'Unknown')
            summary['cluster_quality_description'] = qa.get('quality_description', '')
            summary['cluster_mean_top_5'] = qa.get('mean_top_5', 0.0)
            summary['cluster_penalized_score'] = qa.get('penalized_score', 0.0)
        
        if 'confidence_assessment' in winning_cluster:
            ca = winning_cluster['confidence_assessment']
            summary['cluster_confidence_level'] = ca.get('confidence_level', 'unknown')
            summary['cluster_confidence_description'] = ca.get('confidence_description', '')
            summary['cluster_statistical_significance'] = ca.get('statistical_significance', 'unknown')
            summary['cluster_second_best_type'] = ca.get('second_best_type', 'N/A')
        
        # Calculate enhanced cluster statistics using hybrid methods
        if cluster_matches:
            rlaps = np.array([m['rlap'] for m in cluster_matches])
            
            # Collect redshift data with uncertainties for balanced estimation
            redshifts_with_errors = []
            redshift_errors = []
            rlap_cos_values = []
            
            # Collect age data for separate age estimation
            ages_for_estimation = []
            age_rlap_cos_values = []
            
            for m in cluster_matches:
                template = m.get('template', {})
                
                # Always collect redshift data (uncertainties are always available)
                z = m.get('redshift')
                z_err = m.get('redshift_error', 0.0)
                rlap_cos = get_best_metric_value(m)
                
                if z is not None and np.isfinite(z) and z_err > 0:
                    redshifts_with_errors.append(z)
                    redshift_errors.append(z_err)
                    rlap_cos_values.append(rlap_cos)
                
                # Separately collect age data (no uncertainties available)
                age = template.get('age', 0.0) if template else 0.0
                if age is not None and np.isfinite(age):
                    ages_for_estimation.append(age)
                    age_rlap_cos_values.append(rlap_cos)
            
            # Balanced redshift estimation (always use this when data available)
            if redshifts_with_errors:
                z_final, z_final_err = calculate_weighted_redshift_balanced(
                    redshifts_with_errors, redshift_errors, rlap_cos_values
                )
                summary['cluster_redshift_weighted'] = z_final
                summary['cluster_redshift_weighted_uncertainty'] = z_final_err
                summary['cluster_redshift_scatter'] = 0.0  # Properly handled in balanced estimation
            else:
                # No valid redshift data
                summary['cluster_redshift_weighted'] = np.nan
                summary['cluster_redshift_weighted_uncertainty'] = np.nan
                summary['cluster_redshift_scatter'] = 0.0
            
            # Simple age estimation (no uncertainties)
            if ages_for_estimation:
                age_final = calculate_weighted_age_estimate(ages_for_estimation, age_rlap_cos_values)
                summary['cluster_age_weighted'] = age_final
                summary['cluster_age_uncertainty'] = 0.0  # No uncertainty available for ages
                summary['cluster_age_scatter'] = 0.0
                summary['redshift_age_covariance'] = 0.0  # Separate estimation, no covariance
            else:
                # No valid age data
                summary['cluster_age_weighted'] = np.nan
                summary['cluster_age_uncertainty'] = 0.0
                summary['cluster_age_scatter'] = 0.0
                summary['redshift_age_covariance'] = 0.0
            
            summary['cluster_rlap_mean'] = np.mean(rlaps)
            
            # Subtype composition within cluster (GUI-style)
            from collections import Counter
            subtypes = []
            for m in cluster_matches:
                template = m.get('template', {})
                subtype = template.get('subtype', 'Unknown') if template else 'Unknown'
                if not subtype or subtype.strip() == '':
                    subtype = 'Unknown'
                subtypes.append(subtype)
            
            subtype_counts = Counter(subtypes)
            subtype_fractions = {}
            for subtype, count in subtype_counts.items():
                subtype_fractions[subtype] = count / len(cluster_matches)
            
            # Sort subtypes by frequency
            sorted_subtypes = sorted(subtype_fractions.items(), key=lambda x: x[1], reverse=True)
            summary['cluster_subtypes'] = sorted_subtypes[:5]  # Top 5 subtypes
    
    # Fallback to old approach only if no clustering available
    else:
        summary['cluster_method'] = 'No clustering'
        # Use type/subtype fractions as fallback
        if hasattr(result, 'type_fractions') and result.type_fractions:
            sorted_types = sorted(result.type_fractions.items(), key=lambda x: x[1], reverse=True)
            summary['top_types'] = sorted_types[:3]
        else:
            summary['top_types'] = [(result.consensus_type, 1.0)]
        
        if (hasattr(result, 'subtype_fractions') and result.subtype_fractions and 
            result.consensus_type in result.subtype_fractions):
            subtype_data = result.subtype_fractions[result.consensus_type]
            sorted_subtypes = sorted(subtype_data.items(), key=lambda x: x[1], reverse=True)
            summary['cluster_subtypes'] = sorted_subtypes[:3]
        else:
            summary['cluster_subtypes'] = [(result.best_subtype or 'Unknown', 1.0)]
    
    return summary


def _get_winning_cluster(result: SNIDResult) -> Optional[Dict[str, Any]]:
    """
    Get the winning cluster from SNID results (user selected or automatic best).
    
    This matches the GUI's cluster selection logic.
    """
    if not (hasattr(result, 'clustering_results') and 
            result.clustering_results and 
            result.clustering_results.get('success')):
        return None
    
    clustering_results = result.clustering_results
    
    # Priority: user_selected_cluster > best_cluster
    if 'user_selected_cluster' in clustering_results:
        return clustering_results['user_selected_cluster']
    elif 'best_cluster' in clustering_results:
        return clustering_results['best_cluster']
    
    return None


def _save_spectrum_outputs(
    result: SNIDResult,
    spectrum_path: str,
    output_dir: Path,
    args: argparse.Namespace
) -> None:
    """
    Save spectrum outputs based on the analysis mode using GUI-style cluster-aware approach.
    """
    try:
        # Extract spectrum name from path
        spectrum_name = Path(spectrum_path).stem
        
        if args.minimal:
            # Minimal mode: save main result file only
            from snid_sage.snid.io import write_result
            output_file = output_dir / f"{spectrum_name}.output"
            write_result(result, str(output_file))
            
        elif args.complete:
            # Complete mode: save all outputs including comprehensive plots and data files
            from snid_sage.snid.io import (
                write_result, write_fluxed_spectrum, write_flattened_spectrum,
                write_correlation, write_template_correlation_data, write_template_spectra_data
            )
            from snid_sage.snid.plotting import (
                plot_redshift_age, plot_cluster_subtype_proportions,
                plot_flux_comparison, plot_flat_comparison, plot_correlation_view
            )
            
            # Save main result file
            output_file = output_dir / f"{spectrum_name}.output"
            write_result(result, str(output_file))
            
            # Save additional spectrum files
            if hasattr(result, 'processed_spectrum'):
                # Save fluxed spectrum
                if 'log_wave' in result.processed_spectrum and 'log_flux' in result.processed_spectrum:
                    fluxed_file = output_dir / f"{spectrum_name}.fluxed"
                    write_fluxed_spectrum(
                        result.processed_spectrum['log_wave'], 
                        result.processed_spectrum['log_flux'], 
                        str(fluxed_file)
                    )
                
                # Save flattened spectrum
                if 'log_wave' in result.processed_spectrum and 'flat_flux' in result.processed_spectrum:
                    flat_file = output_dir / f"{spectrum_name}.flattened"
                    write_flattened_spectrum(
                        result.processed_spectrum['log_wave'], 
                        result.processed_spectrum['flat_flux'], 
                        str(flat_file)
                    )
            
            if result.success:
                # Get winning cluster for GUI-style plotting
                winning_cluster = _get_winning_cluster(result)
                cluster_matches = winning_cluster.get('matches', []) if winning_cluster else []
                
                # Use cluster matches for plotting, fallback to filtered/best matches
                plot_matches = cluster_matches
                if not plot_matches:
                    if hasattr(result, 'filtered_matches') and result.filtered_matches:
                        plot_matches = result.filtered_matches
                    elif hasattr(result, 'best_matches') and result.best_matches:
                        plot_matches = result.best_matches
                
                # CRITICAL: Sort all plot matches by best available metric (RLAP-Cos if available, otherwise RLAP) descending
                if plot_matches:
                    from snid_sage.shared.utils.math_utils import get_best_metric_value
                    plot_matches = sorted(plot_matches, key=get_best_metric_value, reverse=True)
                
                # 1. 3D GMM Clustering Visualization (GUI-style)
                if (hasattr(result, 'clustering_results') and 
                    result.clustering_results and 
                    result.clustering_results.get('success')):
                    try:
                        # Use correct 3D GMM clustering plot like GUI does
                        from snid_sage.snid.plotting_3d import plot_3d_type_clustering
                        import matplotlib.pyplot as plt
                        
                        gmm_file = output_dir / f"{spectrum_name}_3d_gmm_clustering.png"
                        fig = plot_3d_type_clustering(result.clustering_results, save_path=str(gmm_file))
                        plt.close(fig)  # Prevent memory leak
                        
                    except Exception as e:
                        logging.getLogger('snid_sage.snid.batch').debug(f"3D GMM clustering plot failed: {e}")
                
                # 2. Redshift vs Age plot (cluster-aware)
                try:
                    import matplotlib.pyplot as plt
                    redshift_age_file = output_dir / f"{spectrum_name}_redshift_age.png"
                    fig = plot_redshift_age(result, save_path=str(redshift_age_file))
                    plt.close(fig)  # Prevent memory leak
                except Exception as e:
                    logging.getLogger('snid_sage.snid.batch').debug(f"Redshift-age plot failed: {e}")
                
                # 3. Cluster-aware subtype proportions (GUI-style)
                try:
                    import matplotlib.pyplot as plt
                    subtype_file = output_dir / f"{spectrum_name}_cluster_subtypes.png"
                    fig = plot_cluster_subtype_proportions(
                        result, 
                        selected_cluster=winning_cluster,
                        save_path=str(subtype_file)
                    )
                    plt.close(fig)  # Prevent memory leak
                except Exception as e:
                    logging.getLogger('snid_sage.snid.batch').debug(f"Cluster subtype plot failed: {e}")
                
                # 5. Flux spectrum plot (best match) - same as GUI
                if plot_matches:
                    try:
                        import matplotlib.pyplot as plt
                        flux_file = output_dir / f"{spectrum_name}_flux_spectrum.png"
                        fig = plot_flux_comparison(plot_matches[0], result, save_path=str(flux_file))
                        plt.close(fig)  # Prevent memory leak
                    except Exception as e:
                        logging.getLogger('snid_sage.snid.batch').debug(f"Flux spectrum plot failed: {e}")
                    
                    # 6. Flattened spectrum plot (best match) - same as GUI
                    try:
                        import matplotlib.pyplot as plt
                        flat_file = output_dir / f"{spectrum_name}_flattened_spectrum.png"
                        fig = plot_flat_comparison(plot_matches[0], result, save_path=str(flat_file))
                        plt.close(fig)  # Prevent memory leak
                    except Exception as e:
                        logging.getLogger('snid_sage.snid.batch').debug(f"Flattened spectrum plot failed: {e}")
                
                # Save correlation function data files
                if hasattr(result, 'best_matches') and result.best_matches:
                    # Main correlation function
                    best_match = result.best_matches[0]
                    if 'correlation' in best_match:
                        corr_data = best_match['correlation']
                        if 'z_axis_full' in corr_data and 'correlation_full' in corr_data:
                            corr_data_file = output_dir / f"{spectrum_name}_correlation.dat"
                            write_correlation(
                                corr_data['z_axis_full'], 
                                corr_data['correlation_full'],
                                str(corr_data_file),
                                header=f"Cross-correlation function for {spectrum_name}"
                            )
                    
                    # Template-specific correlation and spectra data (top 5)
                    for i, match in enumerate(result.best_matches[:5], 1):
                        try:
                            # Template correlation data
                            write_template_correlation_data(match, i, str(output_dir), spectrum_name)
                            
                            # Template spectra data
                            write_template_spectra_data(match, i, str(output_dir), spectrum_name)
                        except Exception as e:
                            logging.getLogger('snid_sage.snid.batch').warning(f"Failed to save template {i} data: {e}")
                
        elif not args.minimal:
            # Default mode: save main outputs only
            from snid_sage.snid.io import write_result
            output_file = output_dir / f"{spectrum_name}.output"
            write_result(result, str(output_file))
            
    except Exception as e:
        logging.getLogger('snid_sage.snid.batch').warning(f"Failed to save outputs: {e}")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the batch command."""
    # Set epilog with examples
    parser.epilog = """
Examples:
  # Auto-discover templates - minimal mode (only summary report)
  snid batch "spectra/*" --output-dir results/ --minimal
  
  # Auto-discover templates - complete mode (all outputs + 3D plots)
  snid batch "spectra/*" --output-dir results/ --complete
  
  # Auto-discover templates - default mode (main outputs + summary)
  snid batch "spectra/*" --output-dir results/
  
  # Explicit templates directory
  snid batch "spectra/*" templates/ --output-dir results/
  
  # Custom redshift range with auto-discovery
  snid batch "*.dat" --zmin 0.0 --zmax 0.5 --output-dir results/
  
  # With forced redshift and explicit templates
  snid batch "*.dat" templates/ --forced-redshift 0.1 --output-dir results/
    """
    
    # Required arguments
    parser.add_argument(
        "input_pattern", 
        help="Pattern for input spectrum files (e.g., 'spectra/*' for all files in folder)"
    )
    parser.add_argument(
        "templates_dir", 
        nargs="?",  # Make optional
        help="Path to directory containing template spectra (optional - auto-discovers if not provided)"
    )
    parser.add_argument(
        "--output-dir", "-o", 
        required=True,
        help="Directory for output files"
    )
    
    # Processing modes (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--minimal", 
        action="store_true",
        help="Minimal mode: Main result files + comprehensive summary report (no plots/extras)"
    )
    mode_group.add_argument(
        "--complete", 
        action="store_true",
        help="Complete mode: Save all outputs including 3D plots for each spectrum"
    )
    
    # Analysis parameters
    analysis_group = parser.add_argument_group("Analysis Parameters")
    analysis_group.add_argument(
        "--zmin", 
        type=float, 
        default=-0.01,
        help="Minimum redshift to consider"
    )
    analysis_group.add_argument(
        "--zmax", 
        type=float, 
        default=1,
        help="Maximum redshift to consider"
    )
    analysis_group.add_argument(
        "--forced-redshift", 
        type=float, 
        help="Force analysis to this specific redshift for all spectra"
    )
    analysis_group.add_argument(
        "--type-filter", 
        nargs="+", 
        help="Only use templates of these types"
    )
    analysis_group.add_argument(
        "--template-filter", 
        nargs="+", 
        help="Only use specific templates (by name)"
    )
    
    # Processing options
    parser.add_argument(
        "--max-workers", 
        type=int, 
        default=1,
        help="Number of parallel workers"
    )
    parser.add_argument(
        "--stop-on-error", 
        action="store_true",
        help="Stop processing if any spectrum fails"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Print detailed processing information"
    )



def generate_summary_report(results: List[Tuple], args: argparse.Namespace) -> str:
    """Generate a clean, comprehensive summary report focused on batch processing success."""
    successful_results = [r for r in results if r[1] and r[3]]
    failed_results = [r for r in results if not r[1]]
    
    total_count = len(results)
    success_count = len(successful_results)
    failure_count = len(failed_results)
    
    # Generate report
    report = []
    report.append("="*80)
    report.append("🔬 SNID SAGE BATCH ANALYSIS REPORT")
    report.append("="*80)
    report.append("")
    
    # Summary
    report.append("📊 BATCH PROCESSING SUMMARY")
    report.append("-"*50)
    report.append(f"Input Pattern: {args.input_pattern}")
    report.append(f"Templates Directory: {args.templates_dir}")
    report.append(f"Analysis Mode: {'Minimal (summary only)' if args.minimal else 'Complete (all outputs + plots)' if args.complete else 'Standard (main outputs)'}")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append(f"📈 PROCESSING RESULTS:")
    report.append(f"   Total Spectra Processed: {total_count}")
    report.append(f"   Successful Analyses: {success_count} ({success_count/total_count*100:.1f}%)")
    report.append(f"   Failed Analyses: {failure_count} ({failure_count/total_count*100:.1f}%)")
    report.append("")
    
    report.append(f"⚙️ ANALYSIS PARAMETERS:")
    report.append(f"   Redshift Search Range: {args.zmin:.3f} ≤ z ≤ {args.zmax:.3f}")
    if args.forced_redshift is not None:
        report.append(f"   Forced Redshift: z = {args.forced_redshift:.6f}")
    if args.type_filter:
        report.append(f"   Type Filter: {', '.join(args.type_filter)}")
    if args.template_filter:
        report.append(f"   Template Filter: {', '.join(args.template_filter)}")
    
    report.append("")
    
    if successful_results:
        # Results table - focus on individual objects, not aggregated science
        report.append("📋 INDIVIDUAL SPECTRUM RESULTS")
        report.append("-"*50)
        report.append("Each spectrum represents a different astronomical object.")
        report.append("Results are sorted by analysis quality (RLAP-Cos) - highest quality first.")
        report.append("")
        
        # Header
        header = f"{'Spectrum':<25} {'Type':<8} {'Subtype':<10} {'Template':<18} {'z':<8} {'RLAP-Cos':<8} {'C':<1}"
        report.append(header)
        report.append("-" * len(header))
        report.append("Legend: 🎯 = Cluster-based analysis, z = redshift")
        
        # Sort results by RLAP-Cos descending (highest quality first)
        from snid_sage.shared.utils.math_utils import get_best_metric_value
        successful_results_sorted = sorted(successful_results, 
                                         key=lambda x: get_best_metric_value(x[3]), reverse=True)
        
        # Results
        for _, _, _, summary in successful_results_sorted:
            spectrum = summary['spectrum'][:24]
            cons_type = summary.get('consensus_type', 'Unknown')[:7]
            cons_subtype = summary.get('consensus_subtype', 'Unknown')[:9]
            template = summary.get('best_template', 'Unknown')[:17]
            
            # Use cluster-weighted redshift if available, otherwise regular redshift
            if summary.get('has_clustering') and 'cluster_redshift_weighted' in summary:
                redshift = f"{summary['cluster_redshift_weighted']:.6f}"
            else:
                redshift = f"{summary.get('redshift', 0):.6f}"
            
            # Use RLAP-Cos if available, otherwise RLAP
            from snid_sage.shared.utils.math_utils import get_best_metric_value
            rlap_cos = f"{get_best_metric_value(summary):.1f}"
            cluster_marker = "🎯" if summary.get('has_clustering', False) else " "
            
            row = f"{spectrum:<25} {cons_type:<8} {cons_subtype:<10} {template:<18} {redshift:<8} {rlap_cos:<8} {cluster_marker}"
            report.append(row)
        
        report.append("")
        
        # Detailed analysis (sorted by RLAP-Cos - highest quality first)
        report.append("🎯 DETAILED INDIVIDUAL ANALYSIS")
        report.append("-"*50)
        report.append("Detailed results for each spectrum (sorted by analysis quality):")
        
        for _, _, _, summary in successful_results_sorted:
            report.append(f"\n📄 {summary['spectrum']}")
            report.append(f"   Best Template: {summary.get('best_template', 'Unknown')}")
            report.append(f"   Classification: {summary.get('consensus_type', 'Unknown')} {summary.get('consensus_subtype', '')}")
            
            # Show cluster information if available
            if summary.get('has_clustering'):
                report.append(f"   🎯 CLUSTER ANALYSIS ({summary.get('cluster_method', 'Unknown')}):")
                report.append(f"      Cluster Type: {summary.get('cluster_type', 'Unknown')}")
                report.append(f"      Cluster Size: {summary.get('cluster_size', 0)} template matches")
                
                # Show new quality metrics
                if 'cluster_quality_category' in summary:
                    report.append(f"      Quality Category: {summary['cluster_quality_category']}")
                    report.append(f"      Quality Description: {summary['cluster_quality_description']}")
                
                if 'cluster_confidence_level' in summary:
                    report.append(f"      Confidence Level: {summary['cluster_confidence_level'].upper()}")
                    report.append(f"      Confidence vs Alternatives: {summary['cluster_confidence_description']}")
                    if summary.get('cluster_second_best_type', 'N/A') != 'N/A':
                        report.append(f"      Second Best Cluster Type: {summary['cluster_second_best_type']}")
                
                if 'cluster_redshift_weighted' in summary:
                    report.append(f"      RLAP-Weighted Redshift: {summary['cluster_redshift_weighted']:.6f} ± {summary.get('cluster_redshift_weighted_uncertainty', 0):.6f}")
                    report.append(f"      Cluster RLAP: {summary.get('cluster_rlap_mean', 0):.2f}")
                
                report.append(f"   Best Match Redshift: {summary.get('redshift', 0):.6f} ± {summary.get('redshift_error', 0):.6f}")
            else:
                report.append(f"   Redshift: {summary.get('redshift', 0):.6f} ± {summary.get('redshift_error', 0):.6f}")
            
            # Use RLAP-Cos if available, otherwise RLAP
            from snid_sage.shared.utils.math_utils import get_best_metric_value, get_best_metric_name
            metric_value = get_best_metric_value(summary)
            metric_name = get_best_metric_name(summary)
            report.append(f"   {metric_name} (analysis quality): {metric_value:.2f}")
            report.append(f"   Runtime: {summary.get('runtime', 0):.1f} seconds")
            
            # Show subtype composition within this spectrum's analysis
            if summary.get('cluster_subtypes'):
                if summary.get('has_clustering'):
                    report.append(f"   Cluster Subtype Composition:")
                else:
                    report.append(f"   Template Subtype Distribution:")
                for i, (subtype_name, fraction) in enumerate(summary['cluster_subtypes'][:3], 1):  # Top 3
                    report.append(f"      {i}. {subtype_name}: {fraction*100:.1f}%")
        
        # Analysis quality statistics (these ARE meaningful to aggregate)  
        report.append(f"\n\n📊 BATCH PROCESSING QUALITY STATISTICS")
        report.append("-"*50)
        report.append("These statistics describe the quality of the batch processing, not the science.")
        report.append("")
        
        # RLAP-Cos distribution (analysis quality)
        from snid_sage.shared.utils.math_utils import get_best_metric_value
        all_metrics = [get_best_metric_value(summary) for _, _, _, summary in successful_results]
        avg_metric = sum(all_metrics) / len(all_metrics) if all_metrics else 0
        high_quality = sum(1 for metric in all_metrics if metric >= 10.0)
        medium_quality = sum(1 for metric in all_metrics if 5.0 <= metric < 10.0)
        low_quality = sum(1 for metric in all_metrics if metric < 5.0)
        
        # Determine metric name (RLAP-Cos if available, otherwise RLAP)
        metric_name = "RLAP-Cos" if any('rlap_cos' in summary for _, _, _, summary in successful_results) else "RLAP"
        
        report.append(f"🎯 ANALYSIS QUALITY ({metric_name} Distribution):")
        report.append(f"   Average {metric_name}: {avg_metric:.2f}")
        report.append(f"   High Quality ({metric_name} ≥ 10): {high_quality}/{success_count} ({high_quality/success_count*100:.1f}%)")
        report.append(f"   Medium Quality (5 ≤ {metric_name} < 10): {medium_quality}/{success_count} ({medium_quality/success_count*100:.1f}%)")
        report.append(f"   Low Quality ({metric_name} < 5): {low_quality}/{success_count} ({low_quality/success_count*100:.1f}%)")
        
        # Classification confidence (using cluster-based metrics)
        cluster_count = sum(1 for _, _, _, s in successful_results if s.get('has_clustering', False))
        high_confidence = sum(1 for _, _, _, s in successful_results 
                             if s.get('cluster_confidence_level') == 'High')
        medium_confidence = sum(1 for _, _, _, s in successful_results 
                               if s.get('cluster_confidence_level') == 'Medium')
        low_confidence = sum(1 for _, _, _, s in successful_results 
                            if s.get('cluster_confidence_level') == 'Low')
        
        report.append(f"\n🔒 CLASSIFICATION CONFIDENCE:")
        if cluster_count > 0:
            report.append(f"   High Confidence: {high_confidence}/{success_count} ({high_confidence/success_count*100:.1f}%)")
            report.append(f"   Medium Confidence: {medium_confidence}/{success_count} ({medium_confidence/success_count*100:.1f}%)")
            report.append(f"   Low Confidence: {low_confidence}/{success_count} ({low_confidence/success_count*100:.1f}%)")
        else:
            report.append(f"   Note: Using legacy analysis method (no cluster-based confidence available)")
        
        # Clustering effectiveness
        cluster_count = sum(1 for _, _, _, s in successful_results if s.get('has_clustering', False))
        total_cluster_size = sum(s.get('cluster_size', 0) for _, _, _, s in successful_results if s.get('has_clustering', False))
        
        report.append(f"\n🎯 CLUSTERING EFFECTIVENESS:")
        report.append(f"   Spectra with GMM clustering: {cluster_count}/{success_count} ({cluster_count/success_count*100:.1f}%)")
        report.append(f"   Spectra with basic analysis: {success_count-cluster_count}/{success_count} ({(success_count-cluster_count)/success_count*100:.1f}%)")
        if cluster_count > 0:
            avg_cluster_size = total_cluster_size / cluster_count
            report.append(f"   Average cluster size: {avg_cluster_size:.1f} template matches")
        
        # Runtime statistics
        all_runtimes = [summary.get('runtime', 0) for _, _, _, summary in successful_results if summary.get('runtime', 0) > 0]
        if all_runtimes:
            avg_runtime = sum(all_runtimes) / len(all_runtimes)
            total_runtime = sum(all_runtimes)
            report.append(f"\n⏱️ PERFORMANCE STATISTICS:")
            report.append(f"   Average analysis time: {avg_runtime:.1f} seconds per spectrum")
            report.append(f"   Total analysis time: {total_runtime:.1f} seconds")
            report.append(f"   Throughput: {success_count/total_runtime*60:.1f} spectra per minute")
        
        # Type distribution (for reference only - not scientifically aggregated)
        type_counts = {}
        for _, _, _, summary in successful_results:
            cons_type = summary.get('consensus_type', 'Unknown')
            type_counts[cons_type] = type_counts.get(cons_type, 0) + 1
        
        if len(type_counts) > 1:  # Only show if there's variety
            report.append(f"\n📋 TYPE DISTRIBUTION (For Reference Only):")
            report.append("Note: Each spectrum is a different object - this is just a summary of what was found.")
            sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
            for type_name, count in sorted_types:
                percentage = count / success_count * 100
                report.append(f"   {type_name}: {count} spectra ({percentage:.1f}%)")
    
    # Separate no-matches from actual failures
    no_match_results = []
    actual_failed_results = []
    
    for spectrum_name, _, error_message, _ in failed_results:
        if "No good matches" in error_message or "No templates after filtering" in error_message:
            no_match_results.append((spectrum_name, error_message))
        else:
            actual_failed_results.append((spectrum_name, error_message))
    
    # No matches section (normal outcome)
    if no_match_results:
        report.append(f"\n\n📝 NO MATCHES FOUND ({len(no_match_results)} spectra)")
        report.append("-"*50)
        report.append("These spectra had no good template matches - this is a normal analysis outcome.")
        for spectrum_name, error_message in no_match_results:
            reason = "no templates available" if "No templates after filtering" in error_message else "no good matches"
            report.append(f"   {spectrum_name}: {reason}")
    
    # Actual failures section (real errors)
    if actual_failed_results:
        report.append(f"\n\n❌ ACTUAL FAILURES ({len(actual_failed_results)} spectra)")
        report.append("-"*50)
        report.append("These spectra failed due to processing errors:")
        for spectrum_name, error_message in actual_failed_results:
            report.append(f"   {spectrum_name}: {error_message}")
    
    report.append("\n" + "="*80)
    
    return "\n".join(report)


def main(args: argparse.Namespace) -> int:
    """Main function for the simplified batch command."""
    try:
        # Use centralized logging system instead of manual configuration
        from snid_sage.shared.utils.logging import configure_logging, VerbosityLevel
        
        # Configure logging based on verbosity
        # For CLI mode, default to QUIET (warnings/errors only) unless verbose is requested
        if args.verbose:
            verbosity = VerbosityLevel.VERBOSE
        else:
            verbosity = VerbosityLevel.QUIET  # Only show warnings and errors, not INFO messages
            
        configure_logging(verbosity=verbosity, gui_mode=False)
        
        # Additional suppression for CLI mode - silence specific noisy loggers
        if not args.verbose:
            # Suppress the most verbose loggers that users don't need to see
            logging.getLogger('snid_sage.snid.pipeline').setLevel(logging.WARNING)
            logging.getLogger('snid_sage.snid.pipeline').setLevel(logging.WARNING)
        
        # Suppress matplotlib warnings (tight layout warnings)
        import warnings
        warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
        
        # Suppress "No good matches found" as ERROR - it's a normal outcome
        pipeline_logger = logging.getLogger('snid_sage.snid.pipeline')
        pipeline_logger.setLevel(logging.CRITICAL)  # Only critical errors, not "no matches"
        
        # Find input files
        input_files = glob.glob(args.input_pattern)
        if not input_files:
            print(f"[ERROR] No files found matching pattern: {args.input_pattern}", file=sys.stderr)
            return 1
        
        # Determine mode
        if args.minimal:
            mode = "Minimal (summary only)"
        elif args.complete:
            mode = "Complete (all outputs + plots)"
        else:
            mode = "Standard (main outputs)"
        
        # Simple startup message
        print(f"🔬 SNID Batch Analysis - CLUSTER-AWARE & OPTIMIZED")
        print(f"   Files: {len(input_files)} spectra")
        print(f"   Mode: {mode}")
        print(f"   Analysis: GUI-style cluster-aware (winning cluster)")
        print(f"   Sorting: All results/plots sorted by RLAP-Cos (highest quality first)")
        print(f"   Output: {args.output_dir}")
        print(f"   Redshift Range: {args.zmin:.3f} ≤ z ≤ {args.zmax:.3f}")
        if args.forced_redshift:
            print(f"   Forced Redshift: {args.forced_redshift:.6f}")
        print(f"   Error Handling: {'Stop on first failure' if args.stop_on_error else 'Continue on failures (default)'}")
        print("")
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # ============================================================================
        # OPTIMIZATION: Load templates ONCE for the entire batch
        # ============================================================================
        print("📚 Loading templates once for entire batch...")
        template_manager = BatchTemplateManager(args.templates_dir, verbose=args.verbose)
        
        if not template_manager.load_templates_once():
            print("[ERROR] Failed to load templates", file=sys.stderr)
            return 1
        
        print(f"[SUCCESS] Templates loaded in {template_manager.load_time:.2f}s")
        print(f"📊 Ready to process {len(input_files)} spectra with {template_manager.template_count} templates")
        print("")
        
        # Process spectra
        results = []
        failed_count = 0
        
        if args.max_workers == 1:
            # Sequential processing with optimized template loading
            print("[INFO] Starting optimized sequential processing...")
            
            for i, spectrum_path in enumerate(input_files, 1):
                if args.verbose:
                    print(f"[{i:3d}/{len(input_files):3d}] {Path(spectrum_path).name}")
                else:
                    # Enhanced progress indicator
                    if i % 10 == 0 or i == len(input_files):
                        print(f"   Progress: {i}/{len(input_files)} ({i/len(input_files)*100:.0f}%)")
                
                name, success, message, summary = process_single_spectrum_optimized(
                    spectrum_path, template_manager, args.output_dir, args
                )
                
                results.append((name, success, message, summary))
                
                if not success:
                    failed_count += 1
                    if "No good matches" in message or "No templates after filtering" in message:
                        # Normal outcome - no match found
                        print(f"      {name}: No good matches found")
                    else:
                        # Actual error
                        if args.verbose:
                            print(f"      [ERROR] {name}: {message}")
                        else:
                            print(f"      [ERROR] {name}: error")
                    if args.stop_on_error:
                        print("🛑 Stopping due to error.")
                        break
                else:
                    # Success - show one-line summary
                    if summary and isinstance(summary, dict):
                        consensus_type = summary.get('consensus_type', 'Unknown')
                        consensus_subtype = summary.get('consensus_subtype', '')
                        
                        # Use cluster-weighted redshift if available, otherwise regular redshift
                        if summary.get('has_clustering') and 'cluster_redshift_weighted' in summary:
                            redshift = summary['cluster_redshift_weighted']
                            z_marker = "🎯"  # Cluster analysis marker
                        else:
                            redshift = summary.get('redshift', 0)
                            z_marker = ""
                        
                        # Use RLAP-Cos if available, otherwise RLAP
                        from snid_sage.shared.utils.math_utils import get_best_metric_value
                        rlap_cos = get_best_metric_value(summary)
                        
                        # Format subtype display
                        type_display = f"{consensus_type} {consensus_subtype}".strip()
                        
                        print(f"      {name}: {type_display} z={redshift:.6f} RLAP-Cos={rlap_cos:.1f} {z_marker}")
                    else:
                        print(f"      {name}: success")
        else:
            # Parallel processing is more complex with shared template manager
            # For now, we'll fall back to sequential processing with a warning
            print(f"⚠️  Parallel processing not yet supported with template optimization.")
            print(f"    Using sequential processing for maximum efficiency.")
            print(f"[INFO] Starting optimized sequential processing...")
            
            for i, spectrum_path in enumerate(input_files, 1):
                if args.verbose:
                    print(f"[{i:3d}/{len(input_files):3d}] {Path(spectrum_path).name}")
                else:
                    # Enhanced progress indicator
                    if i % 10 == 0 or i == len(input_files):
                        print(f"   Progress: {i}/{len(input_files)} ({i/len(input_files)*100:.0f}%)")
                
                name, success, message, summary = process_single_spectrum_optimized(
                    spectrum_path, template_manager, args.output_dir, args
                )
                
                results.append((name, success, message, summary))
                
                if not success:
                    failed_count += 1
                    if "No good matches" in message or "No templates after filtering" in message:
                        # Normal outcome - no match found
                        print(f"      {name}: No good matches found")
                    else:
                        # Actual error
                        if args.verbose:
                            print(f"      [ERROR] {name}: {message}")
                        else:
                            print(f"      [ERROR] {name}: error")
                    if args.stop_on_error:
                        print("🛑 Stopping due to error.")
                        break
                else:
                    # Success - show one-line summary
                    if summary and isinstance(summary, dict):
                        consensus_type = summary.get('consensus_type', 'Unknown')
                        consensus_subtype = summary.get('consensus_subtype', '')
                        
                        # Use cluster-weighted redshift if available, otherwise regular redshift
                        if summary.get('has_clustering') and 'cluster_redshift_weighted' in summary:
                            redshift = summary['cluster_redshift_weighted']
                            z_marker = "🎯"  # Cluster analysis marker
                        else:
                            redshift = summary.get('redshift', 0)
                            z_marker = ""
                        
                        # Use RLAP-Cos if available, otherwise RLAP
                        from snid_sage.shared.utils.math_utils import get_best_metric_value
                        rlap_cos = get_best_metric_value(summary)
                        
                        # Format subtype display
                        type_display = f"{consensus_type} {consensus_subtype}".strip()
                        
                        print(f"      {name}: {type_display} z={redshift:.6f} RLAP-Cos={rlap_cos:.1f} {z_marker}")
                    else:
                        print(f"      {name}: success")
        
        # Results summary
        successful_count = len(results) - failed_count
        success_rate = successful_count / len(results) * 100 if results else 0
        
        print(f"\n📊 Completed: {success_rate:.1f}% success ({successful_count}/{len(results)})")
        
        # Generate summary report
        summary_path = output_dir / "batch_analysis_report.txt"
        print(f"📄 Generating summary report...")
        
        summary_report = generate_summary_report(results, args)
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_report)
        
        print(f"[SUCCESS] Summary report: {summary_path}")
        
                # Show what was created
        if not args.minimal and successful_count > 0:
            print(f"📁 Individual results in: {output_dir}/")
            if args.complete:
                print(f"   📊 3D Plots: Static PNG files with optimized viewing angle")
                print(f"   📈 Top 5 templates: Sorted by RLAP-Cos (highest quality first)")
            
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1 