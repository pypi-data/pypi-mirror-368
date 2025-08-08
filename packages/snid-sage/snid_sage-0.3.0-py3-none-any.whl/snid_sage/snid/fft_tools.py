"""
fft_tools.py – *all* low-level correlation & FFT helpers used by snid.py
========================================================================

Exports
-------
apply_filter             cosine-bell band-pass (k1–k4) on an FFT array
cross_correlate          FFT cross-correlation with band-pass + apodisation
overlap                  SNID's trimming / lap calculation
compute_redshift_from_lag  lag → z  (moved here from utils.py)
calculate_rms           calculate RMS of a bandpassed FFT spectrum
aspart                   calculate symmetric/antisymmetric components of a spectrum
shiftit                  shift a time-domain signal by a fractional amount

The implementation matches the original Fortran SNID code exactly.
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple
import math
import matplotlib.pyplot as plt
# ----------------------------------------------------
# ------------------
# Utility functions
# ----------------------------------------------------------------------

def compute_redshift_from_lag(lag: float, dlog: float) -> float:
    """z = exp(lag·dlog) – 1   (natural-log base, like the Fortran code)."""
    try:
        z = np.exp(lag * dlog) - 1.0
        return 0.0 if z < -0.95 or z > 10.0 else z
    except (OverflowError, ValueError):
        return 0.0


def _calculate_cosine_bell_factor(k_idx: int, k1: int, k2: int, k3: int, k4: int) -> float:
    """
    Calculate the cosine-bell taper factor for a frequency bin k_idx.
    This encapsulates the common logic used in several functions.
    
    Args:
        k_idx: Frequency bin index
        k1, k2, k3, k4: Bandpass filter parameters
        
    Returns:
        Filter factor in range [0.0, 1.0]
    """
    if k_idx < k1 or k_idx > k4:
        return 0.0
    
    if k_idx < k2:
        delta_k = (k2 - k1)
        if delta_k == 0:  # Avoid division by zero
            return 1.0 if k_idx >= k1 else 0.0
        arg = math.pi * (k_idx - k1) / delta_k
        return 0.5 * (1 - math.cos(arg))
    
    if k_idx > k3:
        delta_k = (k4 - k3)
        if delta_k == 0:  # Avoid division by zero
            return 1.0 if k_idx <= k4 else 0.0
        arg = math.pi * (k_idx - k3) / delta_k
        return 0.5 * (1 + math.cos(arg))
    
    # k2 <= k_idx <= k3
    return 1.0



# ----------------------------------------------------------------------
# 1) band-pass filtering and RMS calculations
# ----------------------------------------------------------------------

def apply_filter(ft: np.ndarray, k1: int, k2: int, k3: int, k4: int) -> np.ndarray:
    """
    Apply a cosine-bell band-pass filter to an FFT spectrum.
    
    Args:
        ft: FFT spectrum to filter (full complex FFT, not RFFT)
        k1, k2, k3, k4: Filter parameters
    """
    n = len(ft)
    filtered = ft.copy()
    
    # Process positive and negative frequencies
    for i in range(n):
        # Convert to frequency index
        if i < n//2:
            freq_idx = i
        else:
            freq_idx = i - n
            
        abs_freq = abs(freq_idx)
        factor = _calculate_cosine_bell_factor(abs_freq, k1, k2, k3, k4)
        filtered[i] *= factor
    
    return filtered


def calculate_rms(ft: np.ndarray, k1: int, k2: int, k3: int, k4: int) -> float:
    """
    Calculate the RMS of a signal after bandpass filtering its FFT.
    
    Args:
        ft: FFT spectrum (full complex FFT, not RFFT)
        k1, k2, k3, k4: Filter parameters
    """
    n = len(ft)
    power_sum = 0.0
    
    # Sum over frequency components from k1 to k4
    for k in range(k1, k4 + 1):
        # Parseval weight: 1.0 for DC and Nyquist, 2.0 for others
        weight = 1.0 if (k == 0 or k == n//2) else 2.0
        
        # Get cosine bell factor
        factor = _calculate_cosine_bell_factor(k, k1, k2, k3, k4)
            
        # Add power contribution
        power_sum += weight * factor * (ft[k].real**2 + ft[k].imag**2)
    
    return np.sqrt(power_sum) / float(n)


# ------------------------------------------------------------------
#  Symmetric / antisymmetric RMS within a cosine‑bell window
# ------------------------------------------------------------------

def aspart(x: np.ndarray, k1: int, k2: int, k3: int, k4: int, shift: float) -> Tuple[float, float]:
    """
    Calculate antisymmetric/symmetric parts of a spectrum.
    
    Args:
        x: Full complex FFT (not RFFT)
        k1, k2, k3, k4: Filter parameters
        shift: Time domain shift
    """
    n = len(x)
    arms_sum = 0.0
    srms_sum = 0.0
    
    # Process frequency components from k1 to k4
    for k in range(k1, k4 + 1):
        # Calculate phase shift
        angle = -2.0 * np.pi * k * shift / n
        phase = np.exp(1j * angle)  # Use numpy's complex exponential
        
        # Parseval weight
        weight = 1.0 if (k == 0 or k == n//2) else 2.0
        
        # Get cosine bell factor squared
        factor = _calculate_cosine_bell_factor(k, k1, k2, k3, k4)
        factor = factor * factor  # Square it
        
        # Apply phase shift and calculate symmetric/antisymmetric components
        val_shifted = phase * x[k]
        arms_sum += weight * factor * (val_shifted.imag**2)
        srms_sum += weight * factor * (val_shifted.real**2)
    
    return np.sqrt(arms_sum) / n, np.sqrt(srms_sum) / n


# ------------------------------------------------------------------
#  Shift a signal in the time domain by a fractional amount
# ------------------------------------------------------------------

def shiftit(x: np.ndarray, shift: float, tol: float = 1e-8) -> np.ndarray:
    """
    Shift a time-domain signal by a fractional amount.
    
    Args:
        x: Time domain signal
        shift: Shift amount in samples
        tol: Tolerance for identifying non-zero samples
    """
    n = len(x)
    if n == 0:
        return np.array([])
    
    # Find original non-zero region
    nz = np.flatnonzero(np.abs(x) > tol)
    if not nz.size:  # All zeros
        return np.zeros_like(x)
    
    # Use full FFT
    ft = np.fft.fft(x)
    
    # Apply phase shifts
    for i in range(n):
        freq_idx = i if i <= n//2 else i - n
        angle = -2.0 * np.pi * freq_idx * shift / n
        phase = np.exp(1j * angle)  # Use numpy's complex exponential
        ft[i] *= phase
    
    result = np.real(np.fft.ifft(ft))
    
    # Zero out everything outside the original non-zero region
    o0, o1 = int(nz[0]), int(nz[-1])
    n0 = int(np.floor(o0 + shift))
    n1 = int(np.ceil(o1 + shift))
    
    if n0 > 0:
        result[:n0] = 0.0
    if n1 < n - 1:
        result[n1+1:] = 0.0
    
    # Kill any tiny remaining ringing
    result[np.abs(result) < tol] = 0.0
    
    return result



# ----------------------------------------------------------------------
# 3) lap-trim overlap (apodised)
# ----------------------------------------------------------------------

def overlap(
    spec_t: np.ndarray,
    spec_d: np.ndarray,
    wave:   np.ndarray,
) -> Tuple[
    Tuple[int,int],    # (lt1, lt2): template non-zero start/end bins
    Tuple[int,int],    # (ld1, ld2): data     non-zero start/end bins
    Tuple[float,float],# (ov_start, ov_end): overlap wavelengths
    float              # lap: fractional overlap length
]:
    """
    Find the overlapping region between two spectra on the same wavelength grid.
    
    Args:
        spec_t, spec_d: Template and data spectra
        wave: Wavelength grid for both spectra
        
    Returns:
        Tuple of:
        - (lt1, lt2): Non-zero bin range in template
        - (ld1, ld2): Non-zero bin range in data
        - (ov_start, ov_end): Overlap wavelength range
        - lap: Fractional overlap length
    """
    n = len(spec_t)
    if n == 0 or n != len(spec_d) or n != len(wave):
        return (0, -1), (0, -1), (np.nan, np.nan), 0.0
    
    tol = 1e-3
    
    # Find non-zero regions in each spectrum
    nz_t = np.where(np.abs(spec_t) > tol)[0]
    lt1, lt2 = (int(nz_t[0]), int(nz_t[-1])) if nz_t.size else (0, n-1)
    
    nz_d = np.where(np.abs(spec_d) > tol)[0]
    ld1, ld2 = (int(nz_d[0]), int(nz_d[-1])) if nz_d.size else (0, n-1)
    
    # Calculate overlap
    ov1 = max(lt1, ld1)
    ov2 = min(lt2, ld2)
    
    # Fractional overlap
    lap = (ov2 - ov1 + 1) / n if ov2 >= ov1 else 0.0
    
    # Convert to wavelengths
    ov_start = wave[ov1] if ov2 >= ov1 and ov1 < len(wave) else np.nan
    ov_end = wave[ov2] if ov2 >= ov1 and ov2 < len(wave) else np.nan
    
    return (lt1, lt2), (ld1, ld2), (ov_start, ov_end), lap



def weighted_median_from_rlap(
    rpeaks: List[float],
    lpeaks: List[float],
    zpeaks: List[float]
) -> float:
    """
    Compute weighted median redshift from R-values and lap fractions.
    
    Args:
        rpeaks: R-values for each peak
        lpeaks: Lap fractions for each peak
        zpeaks: Redshift estimates for each peak
        
    Returns:
        Weighted median redshift
    """
    if not rpeaks or not lpeaks or not zpeaks:
        return 0.0
    
    buf = []
    for r, l, z in zip(rpeaks, lpeaks, zpeaks):
        rl = r * l
        
        # Add entries to buffer based on r*l thresholds
        nadd = 0
        if rl > 4.0:
            nadd += 1
        if rl > 5.0:
            nadd += 2
        if rl > 6.0:
            nadd += 2
        
        buf.extend([z] * nadd)
    
    # DEPRECATED: Simple median calculation - use enhanced methods instead
    return float(np.median(buf)) if buf else 0.0



# ----------------------------------------------------------------------
#  Calculate FFT and RMS for a spectrum slice (dtft_drms function)
# ------------------------------------------------------------------

def dtft_drms(flux: np.ndarray, start_zero: float, left_edge: int, right_edge: int, k1: int, k2: int, k3: int, k4: int) -> Tuple[np.ndarray, float]:
    """
    Calculate discrete Fourier transform and RMS for a spectrum slice.
    
    This function computes the FFT of a flux array and calculates the RMS
    using the provided SNID bandpass filter parameters. It's used in the
    main correlation analysis.
    
    Args:
        flux: Input flux array
        start_zero: Starting value (typically 0.0, kept for compatibility)
        left_edge: Left edge of valid data region
        right_edge: Right edge of valid data region
        k1, k2, k3, k4: Bandpass filter parameters
        
    Returns:
        Tuple of (fft_array, rms_value)
    """
    # Compute FFT
    fft_result = np.fft.fft(flux)
    
    # Calculate RMS using bandpass filter with provided parameters
    rms_value = calculate_rms(fft_result, k1, k2, k3, k4)
    
    return fft_result, rms_value



# ----------------------------------------------------------------------
__all__ = [
    "apply_filter", 
    "calculate_rms",
    "rms_filter",  # Legacy alias
    "cross_correlate", 
    "overlap", 
    "aspart", 
    "shiftit",
    "allpeaks", 
    "compute_redshift_from_lag", 
    "weighted_median_from_rlap",
    "dtft_drms"  # Add the missing function
]



def test_functions():
    """Test all the core functions in fft_tools.py with cases matching Fortran behavior."""
    print("Testing FFT tools functions...\n")
    
    # Create test signals
    n = 1024  # Must be even for FFT
    t = np.arange(n)
    
    # Signal 1: Clean sine wave with known frequency
    # Using period = 32 to get exact k index in FFT
    signal1 = np.sin(2*np.pi * t/32)  # period = 32 samples, k=32 in FFT
    
    # Signal 2: Shifted version of signal1
    shift_amount = 8  # Quarter period shift (32/4 = 8)
    signal2 = np.roll(signal1, shift_amount)
    
    # Test 1: calculate_rms (matching rmsfilter.f behavior)
    print("Test 1: calculate_rms (matching rmsfilter.f)")
    
    # Create FFT of signal (not scaled by n)
    ft1 = np.fft.fft(signal1)
    
    # Test with different filter ranges
    k1, k2, k3, k4 = 20, 30, 40, 50  # Filter around our signal's k=32
    
    # Calculate RMS with our function
    rms_filtered = calculate_rms(ft1, k1, k2, k3, k4)
    
    # Expected RMS for sine wave through bandpass:
    # - Sine amplitude = 1, so RMS = 1/√2 ≈ 0.707 before filter
    # - Our k=32 falls in passband (k2-k3), so should be close to this
    print(f"  Filtered RMS: {rms_filtered:.6f} (should be ≈ 0.707 in passband)")
    
    # Test with signal frequency outside filter
    k1, k2, k3, k4 = 60, 70, 80, 90  # Filter away from signal k=32
    rms_out_of_band = calculate_rms(ft1, k1, k2, k3, k4)
    print(f"  Out-of-band RMS: {rms_out_of_band:.6f} (should be ≈ 0)")
    
    # Verify filter shape matches Fortran's cosine bell
    k1, k2, k3, k4 = 20, 30, 40, 50
    ft_white = np.ones_like(ft1)  # White noise spectrum
    rms_white = calculate_rms(ft_white, k1, k2, k3, k4)
    print(f"  White noise RMS through filter: {rms_white:.6f}")
    print(f"  Result: {'PASS' if (0.69 < rms_filtered < 0.72 and rms_out_of_band < 0.1) else 'FAIL'}")
    
    # Test 2: aspart (matching aspart.f behavior)
    print("\nTest 2: aspart")
    
    # For pure sine wave with zero shift:
    # - Should be mostly antisymmetric (high ARMS, low SRMS)
    arms_zero, srms_zero = aspart(ft1, k1, k2, k3, k4, shift=0.0)
    
    # For quarter-period shift (8 samples):
    # - Should be mostly symmetric (low ARMS, high SRMS)
    arms_quarter, srms_quarter = aspart(ft1, k1, k2, k3, k4, shift=shift_amount)
    
    print(f"  Arms (zero shift): {arms_zero:.6f} (should be high)")
    print(f"  Srms (zero shift): {srms_zero:.6f} (should be near 0)")
    print(f"  Arms (quarter shift): {arms_quarter:.6f} (should be near 0)")
    print(f"  Srms (quarter shift): {srms_quarter:.6f} (should be high)")
    
    # Test conditions matching Fortran behavior:
    # 1. Zero shift: sine wave is antisymmetric
    # 2. Quarter shift: sine wave becomes symmetric
    aspart_test_passed = (arms_zero > 0.5 and srms_zero < 0.1 and 
                         arms_quarter < 0.1 and srms_quarter > 0.5)
    print(f"  Result: {'PASS' if aspart_test_passed else 'FAIL'}")
    
    # Test 3: shiftit
    print("\nTest 3: shiftit")
    # Test with fractional shift
    frac_shift = 5.5  # 5.5 samples
    shifted_signal = shiftit(signal1, frac_shift)
    
    # Cross-correlate original with shifted to verify shift amount
    xcorr = np.correlate(signal1, shifted_signal, mode='full')
    actual_shift = (len(xcorr)//2 - np.argmax(xcorr))
    
    print(f"  Requested shift: {frac_shift} samples")
    print(f"  Measured shift: {actual_shift:.2f} samples")
    print(f"  Result: {'PASS' if abs(actual_shift - frac_shift) < 0.6 else 'FAIL'}")
    
    # Test 4: overlap
    print("\nTest 4: overlap")
    # Create test signals with known non-zero regions
    wave = np.linspace(3000, 6000, n)  # wavelength grid
    signal_a = np.zeros(n)
    signal_b = np.zeros(n)
    
    # Signal A has data from index 200-700
    signal_a[200:701] = 1.0
    # Signal B has data from index 400-900
    signal_b[400:901] = 1.0
    
    # Expected overlap is from 400-700
    (t0, t1), (d0, d1), (ov_start, ov_end), lap = overlap(signal_a, signal_b, wave)
    
    expected_t0, expected_t1 = 200, 700
    expected_d0, expected_d1 = 400, 900
    expected_lap = (700-400+1)/n
    
    print(f"  Template range: [{t0}, {t1}] (expected: [{expected_t0}, {expected_t1}])")
    print(f"  Data range: [{d0}, {d1}] (expected: [{expected_d0}, {expected_d1}])")
    print(f"  Overlap wavelengths: [{ov_start:.1f}, {ov_end:.1f}]")
    print(f"  Overlap fraction: {lap:.4f} (expected: {expected_lap:.4f})")
    
    overlap_correct = (abs(t0-expected_t0) <= 1 and abs(t1-expected_t1) <= 1 and 
                      abs(d0-expected_d0) <= 1 and abs(d1-expected_d1) <= 1 and
                      abs(lap-expected_lap) < 0.01)
    
    print(f"  Result: {'PASS' if overlap_correct else 'FAIL'}")
    
    # Visual verification
    plt.figure(figsize=(12, 8))
    
    # Plot 1: Original signal and its RMS through different filter bands
    plt.subplot(221)
    # Ensure we don't exceed FFT size
    max_k = min(n//2 - 30, 400)  # Leave room for filter width
    k_positions = range(0, max_k, 20)
    rms_values = [calculate_rms(ft1, k1, k2, k3, k4) 
                 for k1, k2, k3, k4 in [(i, i+10, i+20, i+30) for i in k_positions]]
    plt.plot(k_positions, rms_values, 'o-', label='RMS vs filter position')
    plt.axhline(1/np.sqrt(2), color='r', linestyle='--', label='Expected RMS')
    plt.title('RMS vs Filter Position')
    plt.legend()
    
    # Plot 2: ARMS/SRMS behavior with shift
    plt.subplot(222)
    shifts = np.linspace(0, 32, 33)  # One period of our test signal
    arms_vals = []
    srms_vals = []
    for s in shifts:
        a, sr = aspart(ft1, k1, k2, k3, k4, s)
        arms_vals.append(a)
        srms_vals.append(sr)
    plt.plot(shifts, arms_vals, label='ARMS')
    plt.plot(shifts, srms_vals, label='SRMS')
    plt.title('ARMS/SRMS vs Shift')
    plt.legend()
    
    # Plot 3: Original vs shifted signal
    plt.subplot(223)
    plt.plot(t[:100], signal1[:100], label='Original')
    plt.plot(t[:100], shifted_signal[:100], label=f'Shifted by {frac_shift}')
    plt.title('Shifted Signal')
    plt.legend()
    
    # Plot 4: Overlap visualization
    plt.subplot(224)
    plt.plot(wave, signal_a, label='Template', alpha=0.7)
    plt.plot(wave, signal_b, label='Data', alpha=0.7)
    plt.axvspan(ov_start, ov_end, color='green', alpha=0.2, label='Overlap')
    plt.title('Overlap Test')
    plt.legend()
    
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    test_functions()