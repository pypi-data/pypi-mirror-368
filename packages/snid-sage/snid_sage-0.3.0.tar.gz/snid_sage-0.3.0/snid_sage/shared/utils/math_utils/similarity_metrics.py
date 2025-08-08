"""
Spectral Similarity Metrics for SNID Analysis
=============================================

This module contains spectral similarity metrics used in SNID analysis,
particularly for enhancing GMM clustering with additional similarity measures.

The primary metric implemented here is cosine similarity, which is used to
create the RLAP-Cos composite metric for improved template discrimination.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def _common_checks(spec1: np.ndarray, spec2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Ensure equal length, finite values, remove padded zeros, and L2-normalise arrays."""
    n = min(len(spec1), len(spec2))
    if n == 0:
        return np.array([]), np.array([])
    s1, s2 = spec1[:n], spec2[:n]
    # Exclude padded / empty parts: assume padding is zero or very close to zero.
    non_zero_mask = np.abs(s1) > 1e-12  # tolerance for floating-point noise
    mask = np.isfinite(s1) & np.isfinite(s2) & non_zero_mask
    if not np.any(mask):
        return np.array([]), np.array([])
    a = s1[mask].astype(float)
    b = s2[mask].astype(float)
    # L2 normalisation — avoids scale bias for cosine, SID, etc.
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return np.array([]), np.array([])
    return a / a_norm, b / b_norm


def cosine_similarity(spec1: np.ndarray, spec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two spectra.
    
    Parameters
    ----------
    spec1, spec2 : np.ndarray
        Input spectra arrays
        
    Returns
    -------
    float
        Cosine similarity (-1 to 1, where 1 is identical spectra)
    """
    a, b = _common_checks(spec1, spec2)
    if a.size == 0:
        return 0.0
    dot = float(np.dot(a, b))
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.clip(dot / denom, -1.0, 1.0)) if denom else 0.0


def _extract_template_flux(match: Dict[str, Any]) -> np.ndarray:
    """Extract the best available template flux from a match dict."""
    tpl_flux: Optional[np.ndarray] = None
    
    # 1. Best: template flattened flux (continuum removed)
    if "spectra" in match:
        spectra_dict = match["spectra"]
        tpl_flux = np.asarray(
            spectra_dict.get("flat", {}).get("flux", []), dtype=float
        )
    
    # 2. Fallback: processed_flux already shifted & flattened in some SNID modes
    if (tpl_flux is None or tpl_flux.size == 0) and "processed_flux" in match:
        tpl_flux = np.asarray(match["processed_flux"], dtype=float)
    
    # 3. Last resort: raw template flux (may include continuum)
    if (tpl_flux is None or tpl_flux.size == 0) and "template" in match and isinstance(match["template"], dict):
        tpl_flux = np.asarray(match["template"].get("flux", []), dtype=float)
    
    if tpl_flux is None or tpl_flux.size == 0:
        return np.zeros(1)
    
    return tpl_flux


def compute_rlap_cos_metric(
    matches: List[Dict[str, Any]], 
    processed_spectrum: Dict[str, Any],
    verbose: bool = False
) -> List[Dict[str, Any]]:
    """
    Compute RLAP-Cos metric (RLAP * capped_cosine_similarity) for template matches.
    
    Uses the exact same spectrum preparation as snid_enhanced_metrics.py:
    - Prefers tapered_flux (apodized flattened spectrum) for consistency with SNID analysis
    - Trims to valid data range (left_edge:right_edge)
    - Template flux extraction follows the same priority order
    
    Parameters
    ----------
    matches : List[Dict[str, Any]]
        List of template matches from SNID analysis
    processed_spectrum : Dict[str, Any]
        Processed spectrum data from SNID preprocessing 
    verbose : bool, optional
        Enable detailed logging
        
    Returns
    -------
    List[Dict[str, Any]]
        Enhanced matches with cosine_similarity, cosine_similarity_capped, and rlap_cos fields
    """
    if not matches:
        return matches
    
    # Check if RLAP-cos is already computed for all matches
    already_computed = all('rlap_cos' in match for match in matches)
    if already_computed:
        if verbose:
            logger.info(f"🔄 RLAP-Cos already computed for all {len(matches)} matches - skipping computation")
        return matches
    
    # Check if partially computed - count how many need computation
    needs_computation = [match for match in matches if 'rlap_cos' not in match]
    if len(needs_computation) < len(matches):
        if verbose:
            logger.info(f"🔄 RLAP-Cos partially computed - computing for {len(needs_computation)}/{len(matches)} matches")
    else:
        logger.info(f"🔄 Computing RLAP-Cos metric for {len(matches)} matches")
    
    # ============================================================================
    
    # ============================================================================
    
    # 1a) Choose the best version of the flattened input flux
    
    # snid_sage.snid.py:1145
    if "tapered_flux" in processed_spectrum and processed_spectrum["tapered_flux"] is not None:
        base_flux = processed_spectrum["tapered_flux"]  # Apodized flattened spectrum (what SNID uses)
        if verbose:
            logger.info("Using tapered_flux (apodized flattened spectrum) for RLAP-Cos metrics")
    elif "display_flat" in processed_spectrum and processed_spectrum["display_flat"] is not None:
        base_flux = processed_spectrum["display_flat"]  # GUI's apodized version
        if verbose:
            logger.info("Using display_flat (GUI apodized flattened spectrum) for RLAP-Cos metrics")
    elif "flat_flux" in processed_spectrum and processed_spectrum["flat_flux"] is not None:
        base_flux = processed_spectrum["flat_flux"]  # Non-apodized flattened spectrum
        if verbose:
            logger.warning("Using flat_flux (non-apodized flattened spectrum) - may not match SNID analysis")
    else:
        # Fall back to tapered_flux (continuum-removed but not flattened)
        base_flux = processed_spectrum["tapered_flux"]
        if verbose:
            logger.warning("Using tapered_flux fallback (continuum-removed but not flattened)")
    
    if base_flux is None:
        logger.error("No suitable input flux found for RLAP-Cos computation")
        return matches
        
    base_flux = np.asarray(base_flux, dtype=float)
    
    # 1b) Always trim to the valid data range used in plotting – unless it is
    #     *already* trimmed (e.g., when display_flat is pre-cropped by GUI preprocessing).
    left_edge = int(processed_spectrum.get("left_edge", 0))
    right_edge = int(processed_spectrum.get("right_edge", len(base_flux) - 1))
    expected_len = right_edge - left_edge + 1
    
    if len(base_flux) == expected_len:
        input_flux = base_flux  # already trimmed
    else:
        input_flux = base_flux[left_edge : right_edge + 1]
    
    if verbose:
        logger.info(f"Input spectrum: length={len(input_flux)}, range=[{left_edge}:{right_edge}]")
    
    # ============================================================================
    # Compute enhanced metrics for each match
    # ============================================================================
    
    enhanced_matches = []
    successful_computations = 0
    
    for i, match in enumerate(matches):
        # Skip if already computed
        if 'rlap_cos' in match:
            enhanced_matches.append(match)
            successful_computations += 1
            continue
        
        # Extract template flux using the exact same logic as snid_enhanced_metrics.py
        tpl_flux = _extract_template_flux_exact(match)
        
        if tpl_flux is None or tpl_flux.size == 0:
            if verbose:
                logger.debug(f"Template flux missing for match {i} – skipping RLAP-Cos calculation")
            # Keep original match without enhancement
            enhanced_matches.append(match.copy())
            continue
        
        # Compute cosine similarity
        cos_sim = cosine_similarity(input_flux, tpl_flux)
        
        # Cap cosine similarity to [0, 1] (negative similarities are bad)
        cos_sim_capped = max(0.0, cos_sim)
        
        # Compute RLAP-Cos = RLAP * capped_cosine_similarity
        rlap = match.get('rlap', 0.0)
        rlap_cos = rlap * cos_sim_capped
        
        # Create enhanced match
        enhanced_match = match.copy()
        enhanced_match.update({
            'cosine_similarity': cos_sim,
            'cosine_similarity_capped': cos_sim_capped,
            'rlap_cos': rlap_cos
        })
        
        enhanced_matches.append(enhanced_match)
        successful_computations += 1
        
        if verbose and i < 5:  # Log first few for debugging
            template_name = match.get('template', {}).get('name', 'Unknown') if isinstance(match.get('template'), dict) else match.get('name', 'Unknown')
            logger.debug(f"  Match {i}: {template_name} - RLAP={rlap:.2f}, cos_sim={cos_sim:.3f}, capped={cos_sim_capped:.3f}, RLAP-Cos={rlap_cos:.3f}")
    
    if len(needs_computation) > 0:
        logger.info(f"✅ RLAP-Cos computation complete: {successful_computations}/{len(matches)} matches enhanced")
    
    return enhanced_matches


def _extract_template_flux_exact(match: Dict[str, Any]) -> Optional[np.ndarray]:
    """
    Extract template flux using the exact same logic as snid_enhanced_metrics.py.
    
    Priority order:
    1. Best: template flattened flux (continuum removed) - spectra.flat.flux
    2. Fallback: processed_flux already shifted & flattened in some SNID modes  
    3. Last resort: raw template flux (may include continuum) - template.flux
    """
    tpl_flux: Optional[np.ndarray] = None
    
    # 1. Best: template flattened flux (continuum removed)
    if "spectra" in match:
        spectra_dict = match["spectra"]
        tpl_flux = np.asarray(
            spectra_dict.get("flat", {}).get("flux", []), dtype=float
        )
        if tpl_flux.size > 0:
            return tpl_flux
    
    # 2. Fallback: processed_flux already shifted & flattened in some SNID modes
    if "processed_flux" in match:
        tpl_flux = np.asarray(match["processed_flux"], dtype=float)
        if tpl_flux.size > 0:
            return tpl_flux
    
    # 3. Last resort: raw template flux (may include continuum)
    if "template" in match and isinstance(match["template"], dict):
        tpl_flux = np.asarray(match["template"].get("flux", []), dtype=float)
        if tpl_flux.size > 0:
            return tpl_flux
    
    return None


def get_best_metric_value(match: Dict[str, Any]) -> float:
    """
    Get the best available metric value for sorting/display.
    
    Returns RLAP-Cos if available, otherwise falls back to RLAP.
    This ensures consistent behavior across the codebase when RLAP-Cos
    is available from the enhanced clustering.
    
    Parameters
    ----------
    match : Dict[str, Any]
        Template match dictionary
        
    Returns
    -------
    float
        Best available metric value
    """
    return match.get('rlap_cos', match.get('rlap', 0.0))


def get_metric_name_for_match(match: Dict[str, Any]) -> str:
    """
    Get the name of the metric being used for a match.
    
    Returns 'RLAP-Cos' if available, otherwise 'RLAP'.
    
    Parameters
    ----------
    match : Dict[str, Any]
        Template match dictionary
        
    Returns
    -------
    str
        Name of the metric
    """
    return 'RLAP-Cos' if 'rlap_cos' in match else 'RLAP'


def get_best_metric_name(match: Dict[str, Any]) -> str:
    """
    Get the name of the best available metric for a match.
    
    Returns 'RLAP-Cos' if available, otherwise 'RLAP'.
    This is a convenience function for summary reports.
    
    Parameters
    ----------
    match : Dict[str, Any]
        Template match dictionary or summary dictionary
        
    Returns
    -------
    str
        Name of the best available metric
    """
    # Check if this is a summary dict with rlap_cos or a match dict
    if 'rlap_cos' in match or (isinstance(match, dict) and any('rlap_cos' in str(k) for k in match.keys())):
        return 'RLAP-Cos'
    else:
        return 'RLAP'


def get_metric_display_values(match: Dict[str, Any]) -> Dict[str, float]:
    """
    Get all available metric values for display purposes.
    
    Returns a dictionary with all available metric values including
    original RLAP, RLAP-Cos, and cosine similarity when available.
    
    Parameters
    ----------
    match : Dict[str, Any]
        Template match dictionary
        
    Returns
    -------
    Dict[str, float]
        Dictionary containing available metric values
    """
    values = {
        'rlap': match.get('rlap', 0.0),
        'primary_metric': get_best_metric_value(match),
        'metric_name': get_metric_name_for_match(match)
    }
    
    if 'rlap_cos' in match:
        values['rlap_cos'] = match['rlap_cos']
        values['cosine_similarity'] = match.get('cosine_similarity', 0.0)
        values['cosine_similarity_capped'] = match.get('cosine_similarity_capped', 0.0)
    
    return values 