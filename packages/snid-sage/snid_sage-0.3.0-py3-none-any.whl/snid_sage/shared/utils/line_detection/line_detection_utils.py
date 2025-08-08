"""
Line detection utility functions for spectral analysis
"""
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from scipy.signal import find_peaks, savgol_filter, find_peaks_cwt
from scipy.optimize import curve_fit, least_squares
from .spectrum_utils import plot_spectrum
import warnings

def gaussian_function(x, amplitude, center, sigma):
    """Gaussian function for curve fitting"""
    return amplitude * np.exp(-(x - center)**2 / (2 * sigma**2))

def fit_gaussian_line(wavelength, flux, center_guess, amplitude_guess, sigma_guess=2.0):
    """
    Fit a Gaussian profile to spectral line data using scipy
    
    Parameters
    ----------
    wavelength : array
        Wavelength array
    flux : array
        Flux array 
    center_guess : float
        Initial guess for line center
    amplitude_guess : float
        Initial guess for amplitude
    sigma_guess : float
        Initial guess for sigma (width)
        
    Returns
    -------
    dict or None
        Dictionary with fit parameters or None if fit failed
    """
    try:
        # Initial parameter guesses
        initial_guess = [amplitude_guess, center_guess, sigma_guess]
        
        # Set reasonable bounds
        amplitude_bounds = (0, amplitude_guess * 5)
        center_bounds = (center_guess - 5, center_guess + 5)
        sigma_bounds = (0.5, 8.0)
        
        bounds = ([amplitude_bounds[0], center_bounds[0], sigma_bounds[0]], 
                 [amplitude_bounds[1], center_bounds[1], sigma_bounds[1]])
        
        # Perform curve fit
        popt, pcov = curve_fit(gaussian_function, wavelength, flux, 
                              p0=initial_guess, bounds=bounds, maxfev=1000)
        
        # Extract parameters
        amplitude, center, sigma = popt
        
        # Calculate uncertainties from covariance matrix
        param_errors = np.sqrt(np.diag(pcov))
        center_err = param_errors[1] if len(param_errors) > 1 else None
        
        return {
            'amplitude': amplitude,
            'center': center,
            'sigma': sigma,
            'center_error': center_err,
            'fwhm': sigma * 2.355  # Convert sigma to FWHM
        }
        
    except Exception as e:
        # Fit failed
        return None

def toggle_obs_lines(self):
    """Toggle display of observed spectral lines."""
    self.show_obs_lines = not self.show_obs_lines
    
    # Only update if we have line comparison data
    if self.line_comparison_data:
        self._draw_line_comparisons()
    
    # Change button appearance
    if self.show_obs_lines:
        self.obs_lines_btn.config(text="Hide Observed Lines")
    else:
        self.obs_lines_btn.config(text="Show Observed Lines")

def toggle_tmpl_lines(self):
    """Toggle display of template spectral lines."""
    self.show_tmpl_lines = not self.show_tmpl_lines
    
    # Only update if we have line comparison data
    if self.line_comparison_data:
        self._draw_line_comparisons()
    
    # Change button appearance
    if self.show_tmpl_lines:
        self.tmpl_lines_btn.config(text="Hide Template Lines")
    else:
        self.tmpl_lines_btn.config(text="Show Template Lines")

def update_line_search_delta(self):
    """Update the wavelength delta for line searches."""
    try:
        new_delta = float(self.delta_entry.get().strip())
        if new_delta <= 0:
            messagebox.showerror("Invalid Value", "Delta must be greater than zero.")
            return
        self.line_search_delta = new_delta
        self.status_label.config(text=f"Search delta updated to {new_delta} Å")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

def configure_line_detection(self):
    """Configure line detection parameters."""
    # Create a dialog window
    dialog = tk.Toplevel(self.master)
    dialog.title("Line Detection Parameters")
    dialog.transient(self.master)
    dialog.grab_set()
    
    # Center on parent
    dialog.geometry("450x400")
    dialog.update_idletasks()
    x = self.master.winfo_rootx() + (self.master.winfo_width() - dialog.winfo_width()) // 2
    y = self.master.winfo_rooty() + (self.master.winfo_height() - dialog.winfo_height()) // 2
    dialog.geometry(f"+{x}+{y}")
    
    # Ensure line_detection_params exists with defaults
    if not hasattr(self, 'line_detection_params'):
        self.line_detection_params = {
            'smoothing_window': 5,
            'noise_factor': 1.5,  # Default sensitivity for line detection
            'use_smoothing': True,
            'solid_match_threshold': 150,
            'weak_match_threshold': 300,
            'max_intensity_factor': 2.5  # Higher default to be more flexible with strong peaks
        }
    
    # Create a main frame with padding
    main_frame = ttk.Frame(dialog, padding=10)
    main_frame.pack(fill='both', expand=True)
    
    # Create a form frame for the parameters
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill='x', pady=5)
    
    # Smoothing Parameters
    ttk.Label(form_frame, text="Line Detection Parameters", 
             font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=3, sticky='w', pady=(0,2))
    
    # Smoothing window
    ttk.Label(form_frame, text="Smoothing Window:").grid(row=1, column=0, sticky='w', pady=2)
    smoothing_window_var = tk.StringVar(value=str(self.line_detection_params['smoothing_window']))
    smoothing_window_entry = ttk.Entry(form_frame, width=10, textvariable=smoothing_window_var)
    smoothing_window_entry.grid(row=1, column=1, sticky='w', pady=2)
    ttk.Label(form_frame, text="(Lower = less smoothing, preserves more detail)").grid(row=1, column=2, sticky='w', pady=2)
    
    # Use smoothing checkbox
    use_smoothing_var = tk.BooleanVar(value=self.line_detection_params.get('use_smoothing', True))
    ttk.Checkbutton(form_frame, text="Use Smoothing", variable=use_smoothing_var).grid(
        row=2, column=0, columnspan=2, sticky='w', pady=2)
    
    # Noise factor
    ttk.Label(form_frame, text="Sensitivity:").grid(row=3, column=0, sticky='w', pady=2)
    noise_factor_var = tk.StringVar(value=str(self.line_detection_params['noise_factor']))
    noise_factor_entry = ttk.Entry(form_frame, width=10, textvariable=noise_factor_var)
    noise_factor_entry.grid(row=3, column=1, sticky='w', pady=2)
    ttk.Label(form_frame, text="(Lower = more lines detected, higher = fewer)").grid(row=3, column=2, sticky='w', pady=2)
    
    # Match thresholds
    ttk.Label(form_frame, text="Match Thresholds (km/s)", 
             font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=3, sticky='w', pady=(10,2))
    
    # Solid match threshold
    ttk.Label(form_frame, text="Solid Match:").grid(row=5, column=0, sticky='w', pady=2)
    solid_match_var = tk.StringVar(value=str(self.line_detection_params['solid_match_threshold']))
    solid_match_entry = ttk.Entry(form_frame, width=10, textvariable=solid_match_var)
    solid_match_entry.grid(row=5, column=1, sticky='w', pady=2)
    ttk.Label(form_frame, text="(Maximum velocity difference for solid matches)").grid(row=5, column=2, sticky='w', pady=2)
    
    # Weak match threshold
    ttk.Label(form_frame, text="Weak Match:").grid(row=6, column=0, sticky='w', pady=2)
    weak_match_var = tk.StringVar(value=str(self.line_detection_params['weak_match_threshold']))
    weak_match_entry = ttk.Entry(form_frame, width=10, textvariable=weak_match_var)
    weak_match_entry.grid(row=6, column=1, sticky='w', pady=2)
    ttk.Label(form_frame, text="(Maximum velocity difference for weak matches)").grid(row=6, column=2, sticky='w', pady=2)
    
    # Intensity-based scaling
    ttk.Label(form_frame, text="Intensity-based Scaling", 
             font=('Arial', 10, 'bold')).grid(row=7, column=0, columnspan=3, sticky='w', pady=(10,2))
    
    # Max intensity factor
    ttk.Label(form_frame, text="Max Factor:").grid(row=8, column=0, sticky='w', pady=2)
    max_intensity_var = tk.StringVar(value=str(self.line_detection_params.get('max_intensity_factor', 2.0)))
    max_intensity_entry = ttk.Entry(form_frame, width=10, textvariable=max_intensity_var)
    max_intensity_entry.grid(row=8, column=1, sticky='w', pady=2)
    ttk.Label(form_frame, text="(Higher = more flexible matching for strong peaks)").grid(row=8, column=2, sticky='w', pady=2)
    
    # Explanation
    ttk.Label(form_frame, text="Note: Lines are considered matching if their wavelength difference,", 
             font=('Arial', 8)).grid(row=9, column=0, columnspan=3, sticky='w', pady=(15,0))
    ttk.Label(form_frame, text="converted to velocity, is less than the threshold value.", 
             font=('Arial', 8)).grid(row=10, column=0, columnspan=3, sticky='w', pady=(0,0))
    ttk.Label(form_frame, text="Stronger peaks get scaled thresholds based on intensity.", 
             font=('Arial', 8)).grid(row=11, column=0, columnspan=3, sticky='w', pady=(0,10))
    
    # Create button frame
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill='x', pady=10)
    
    def apply_settings():
        """Apply the settings and close the dialog."""
        try:
            # Validate and store the settings
            smoothing_window = int(smoothing_window_var.get())
            noise_factor = float(noise_factor_var.get())
            solid_match = float(solid_match_var.get())
            weak_match = float(weak_match_var.get())
            max_intensity = float(max_intensity_var.get())
            
            # Check if the smoothing window is odd
            if smoothing_window % 2 == 0:
                messagebox.showerror("Invalid Value", "Smoothing window must be an odd number.")
                return
            
            # Check if thresholds are valid
            if solid_match <= 0 or weak_match <= 0:
                messagebox.showerror("Invalid Value", "Thresholds must be positive numbers.")
                return
                
            if solid_match >= weak_match:
                messagebox.showerror("Invalid Value", "Solid match threshold must be less than weak match threshold.")
                return
                
            # Check if intensity factor is valid
            if max_intensity <= 0:
                messagebox.showerror("Invalid Value", "Max intensity factor must be positive.")
                return
            
            # Update the parameters
            self.line_detection_params = {
                'smoothing_window': smoothing_window,
                'noise_factor': noise_factor,
                'use_smoothing': use_smoothing_var.get(),
                'solid_match_threshold': solid_match,
                'weak_match_threshold': weak_match,
                'max_intensity_factor': max_intensity
            }
            
            # Close the dialog
            dialog.destroy()
            
            # Show confirmation
            self.status_label.config(text="Line detection settings updated")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for all fields.")
    
    # Add buttons
    ttk.Button(btn_frame, text="Apply", command=apply_settings).pack(side='right', padx=5)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='right', padx=5)

def detect_and_fit_lines(wavelength, flux, min_width=1, max_width=10, min_snr=2.0, max_fit_window=20, smoothing_window=5, use_smoothing=True):
    """
    Detect spectral lines using scipy-based peak detection and Gaussian fitting.
    
    Parameters
    ----------
    wavelength : array
        Wavelength array
    flux : array
        Flux array
    min_width : float
        Minimum expected line width 
    max_width : float
        Maximum expected line width
    min_snr : float
        Minimum signal-to-noise ratio for line detection
    max_fit_window : int
        Maximum window size for fitting
    smoothing_window : int
        Size of the smoothing window (odd number)
    use_smoothing : bool
        Whether to apply smoothing
        
    Returns
    -------
    list
        List of dictionaries containing line information
    """
    
    # First determine if we're working with flattened data (centered around 0 or 1)
    flux_mean = np.mean(flux)
    is_centered_at_zero = abs(flux_mean) < 0.5
    if is_centered_at_zero:
        # If data is still centered at 0, add offset for better peak detection
        flux = flux + 1.0
    
    # Apply smoothing if requested
    if use_smoothing and len(flux) > smoothing_window:
        # Ensure smoothing window is odd
        if smoothing_window % 2 == 0:
            smoothing_window += 1
        flux_smooth = savgol_filter(flux, smoothing_window, 2)
    else:
        flux_smooth = flux.copy()
    
    # Note: PySpecKit has been replaced with scipy-based fitting for better compatibility
    
    # Estimate noise level using median absolute deviation (more robust than std)
    flux_median = np.median(flux_smooth)
    noise_level = np.median(np.abs(flux_smooth - flux_median)) * 1.4826  # Scale factor for Gaussian noise
    
    # For very low noise cases, set a minimum threshold
    noise_level = max(noise_level, 0.01 * np.max(np.abs(flux_smooth)))
    
    # Find emission and absorption lines separately, then combine them
    all_lines = []
    
    # Look for emission features (positive peaks)
    try:
        # Find peaks directly first to identify potential starting points
        # Use more sensitive parameters to detect peaks over the entire spectrum
        peak_indices, _ = find_peaks(
            flux_smooth, 
            height=noise_level*min_snr,  # Use min_snr directly
            distance=min_width,
            prominence=noise_level*min_snr*0.5,  # Scale prominence with min_snr
            width=min_width*0.5,  # Add width parameter to help with peak identification
        )
        
        # For each peak, fit a Gaussian model
        for peak_idx in peak_indices:
            # Define fitting region
            window_size = max(min_width*2, 10)  # Reasonable window size
            min_idx = max(0, peak_idx - window_size)
            max_idx = min(len(wavelength) - 1, peak_idx + window_size)
            
            if max_idx - min_idx < 5:
                continue  # Skip if not enough points
            
            # Create a sub-spectrum for this peak
            peak_wl = wavelength[min_idx:max_idx+1]
            peak_flux = flux_smooth[min_idx:max_idx+1]
            
            # Quick baseline removal using the edges
            baseline = np.percentile(peak_flux, 10)
            peak_flux_adj = peak_flux - baseline
            
            # Use scipy-based Gaussian fitting
            try:
                # Estimate the amplitude, mean and width for Gaussian fitting
                amp_guess = peak_flux_adj[peak_idx - min_idx]
                cen_guess = wavelength[peak_idx]
                sigma_guess = 2.0 / 2.355  # Convert FWHM guess to sigma
                
                # Perform Gaussian fit
                fit_result = fit_gaussian_line(peak_wl, peak_flux_adj, cen_guess, amp_guess, sigma_guess)
                
                # Extract fit results
                if fit_result is not None:
                    amp = fit_result['amplitude']
                    cen = fit_result['center']
                    sigma = fit_result['sigma']
                    cen_err = fit_result['center_error']
                    
                    # Less stringent amplitude threshold to include more lines
                    if amp > noise_level * 0.8:
                        all_lines.append({
                            'wavelength': cen,
                            'uncertainty': cen_err,
                            'type': 'emission',
                            'amplitude': amp,
                            'sigma': sigma,
                            'snr': amp / noise_level if noise_level > 0 else None
                        })
            except Exception as e:
                # Fall back to simple measurement if fit fails
                all_lines.append({
                    'wavelength': wavelength[peak_idx],
                    'uncertainty': None,
                    'type': 'emission',
                    'amplitude': flux_smooth[peak_idx] - baseline,
                    'sigma': 2.0,  # Default width
                    'snr': (flux_smooth[peak_idx] - baseline) / noise_level if noise_level > 0 else None
                })
    except Exception as e:
        # Handle any errors in emission line finding
        print(f"Error finding emission lines: {str(e)}")
    
    # Look for absorption features (negative peaks)
    try:
        # Use the negative of the flux to find troughs
        negative_flux = -flux_smooth
        
        # Find troughs with improved parameters
        trough_indices, _ = find_peaks(
            negative_flux, 
            height=noise_level*min_snr,  # Use min_snr directly
            distance=min_width,
            prominence=noise_level*min_snr*0.5,  # Scale prominence with min_snr
            width=min_width*0.5,  # Add width parameter
        )
        
        # For each trough, fit a Gaussian model
        for trough_idx in trough_indices:
            # Define fitting region
            window_size = max(min_width*2, 10)  # Reasonable window size
            min_idx = max(0, trough_idx - window_size)
            max_idx = min(len(wavelength) - 1, trough_idx + window_size)
            
            if max_idx - min_idx < 5:
                continue  # Skip if not enough points
            
            # Create a sub-spectrum for this trough
            trough_wl = wavelength[min_idx:max_idx+1]
            trough_flux = flux_smooth[min_idx:max_idx+1]
            
            # Quick baseline removal using the edges - for absorption we use higher percentile
            baseline = np.percentile(trough_flux, 90)
            trough_flux_adj = -(trough_flux - baseline)  # Make it positive for fitting
            
            # Use scipy-based Gaussian fitting
            try:
                # Estimate the amplitude, mean and width for Gaussian fitting
                amp_guess = trough_flux_adj[trough_idx - min_idx]
                cen_guess = wavelength[trough_idx]
                sigma_guess = 2.0 / 2.355  # Convert FWHM guess to sigma
                
                # Perform Gaussian fit
                fit_result = fit_gaussian_line(trough_wl, trough_flux_adj, cen_guess, amp_guess, sigma_guess)
                
                # Extract fit results
                if fit_result is not None:
                    amp = fit_result['amplitude']
                    cen = fit_result['center']
                    sigma = fit_result['sigma']
                    cen_err = fit_result['center_error']
                    
                    # Less stringent amplitude threshold to include more lines
                    if amp > noise_level * 0.8:
                        all_lines.append({
                            'wavelength': cen,
                            'uncertainty': cen_err,
                            'type': 'absorption',
                            'amplitude': amp,
                            'sigma': sigma,
                            'snr': amp / noise_level if noise_level > 0 else None
                        })
            except Exception as e:
                # Fall back to simple measurement if fit fails
                all_lines.append({
                    'wavelength': wavelength[trough_idx],
                    'uncertainty': None,
                    'type': 'absorption',
                    'amplitude': negative_flux[trough_idx] - baseline,
                    'sigma': 2.0,  # Default width
                    'snr': (negative_flux[trough_idx] - baseline) / noise_level if noise_level > 0 else None
                })
    except Exception as e:
        # Handle any errors in absorption line finding
        print(f"Error finding absorption lines: {str(e)}")
    
    # Filter out duplicates
    filtered_lines = []
    seen_wavelengths = set()
    
    # Sort by SNR (descending) so we keep the strongest detections
    sorted_lines = sorted(all_lines, key=lambda x: x.get('snr', 0), reverse=True)
    
    for line in sorted_lines:
        # Round wavelength to nearest 0.1 Å for duplicate check
        rounded_wave = round(line['wavelength'] * 10) / 10
        
        # If we haven't seen this wavelength before, add it
        if rounded_wave not in seen_wavelengths:
            seen_wavelengths.add(rounded_wave)
            filtered_lines.append(line)
    
    # Sort by wavelength for final output
    return sorted(filtered_lines, key=lambda x: x['wavelength'])

def auto_detect_and_compare_lines(self):
    """Automatically detect and compare spectral lines in the observed and template spectra."""
    if not self.snid_results or not self.snid_results['templates_info']:
        messagebox.showinfo("No Data", "No template data available.")
        return
    
    # Get current template info and data
    template_info = self.snid_results['templates_info'][self.current_template]
    inp = self.snid_results['input_flux'] if self.view_mode == 'flux' else self.snid_results['input_flat']
    tmpl = (self.snid_results['templates_flux'][self.current_template] 
            if self.view_mode == 'flux' 
            else self.snid_results['templates_flat'][self.current_template])
    
    if inp is None or tmpl is None:
        messagebox.showinfo("Data Missing", f"No data available for comparison.")
        return
    
    # Make copies of the data to avoid modifying the original
    obs_data = inp.copy()
    tmpl_data = tmpl.copy()
    
    # Tell the user we're working
    self.status_label.config(text="Detecting spectral lines with scipy...")
    self.master.update()  # Force update to show status
    
    try:
        # Function to convert wavelength difference to velocity
        def wavelength_to_velocity(w1, w2):
            # Avoid division by zero or very small values
            if w1 < 1e-6 or w2 < 1e-6:
                return float('inf')
            
            # Speed of light in km/s
            c = 299792.458
            
            # Calculate relativistic Doppler shift
            beta = (w2*w2 - w1*w1) / (w2*w2 + w1*w1)
            v = c * beta
            
            return v
        
        # Multi-Gaussian model for fitting multiple overlapping peaks
        def multi_gaussian_model(x, *params):
            y = np.zeros_like(x)
            n_gaussians = len(params) // 3
            
            for i in range(n_gaussians):
                amp = params[i*3]
                cen = params[i*3 + 1]
                sigma = params[i*3 + 2]
                y = y + amp * np.exp(-(x - cen)**2 / (2 * sigma**2))
            
            return y
        
        # Detect lines in the observed spectrum
        obs_wave = obs_data[:,0]
        obs_flux = obs_data[:,1]
        
        # Template redshift from SNID
        template_z = template_info['z']
        
        # Verify data alignment for flattened spectra (centered at 0, not 1)
        if self.view_mode == 'flat':
            # Check if data is actually flattened - should have mean near 0.0 for SNID flattened data
            mean_flux = np.mean(obs_flux)
            if abs(mean_flux) > 0.5:  # If mean is far from 0.0
                messagebox.showwarning(
                    "Data Misalignment", 
                    f"The data may not be properly flattened (mean={mean_flux:.2f}, expected ~0.0).\n"
                    "This might affect line detection accuracy."
                )
            
            # For flat spectra we need to adjust the flux to find peaks properly
            # (Find peaks expects peaks to be above baseline, valleys to be below)
            # For flattened data, we'll look for relative peaks/valleys from the mean
            
            # Add offset to make flux centered around 0 to be centered around 1
            # This helps with relative peak detection
            obs_flux = obs_flux + 1.0
            
            # Do same for template
            tmpl_data[:,1] = tmpl_data[:,1] + 1.0
        
        # OPTIMIZATION: Downsample very dense spectra to speed up processing
        # But use a more moderate approach to preserve spectral features
        if len(obs_wave) > 2000:  # Higher threshold before downsampling
            # Use a more conservative downsampling factor to keep more points
            downsample_factor = max(1, len(obs_wave) // 2000)  # Preserve 2000 points
            # Use a rolling window average instead of simple decimation to preserve features
            obs_wave_ds = np.array([np.mean(obs_wave[i:i+downsample_factor]) 
                          for i in range(0, len(obs_wave), downsample_factor)])
            obs_flux_ds = np.array([np.mean(obs_flux[i:i+downsample_factor]) 
                          for i in range(0, len(obs_flux), downsample_factor)])
            obs_wave = obs_wave_ds
            obs_flux = obs_flux_ds
        
        # Configure parameters based on data characteristics
        data_range = np.max(obs_wave) - np.min(obs_wave)
        point_density = len(obs_wave) / data_range
        
        # Scale min_width and max_width based on data point density
        # OPTIMIZATION: Use smaller width ranges
        min_width = max(1, int(1 * point_density))
        max_width = max(5, int(8 * point_density))  # Reduced from 10
        
        # Make sure max_width is sensible relative to data length
        max_width = min(max_width, len(obs_wave) // 15)  # Stricter limit
        
        # Use the wavelet-based detection
        observed_lines = detect_and_fit_lines(
            obs_wave, obs_flux,
            min_width=min_width,
            max_width=max_width,
            min_snr=self.line_detection_params.get('noise_factor', 1.5),  # Use noise_factor directly as sensitivity threshold
            smoothing_window=self.line_detection_params['smoothing_window'],
            use_smoothing=self.line_detection_params['use_smoothing']
        )
        
        # Get template data
        tmpl_wave = tmpl_data[:,0]
        tmpl_flux = tmpl_data[:,1]
        
        # OPTIMIZATION: Downsample very dense spectra
        # Use the same improved approach as for the observed spectrum
        if len(tmpl_wave) > 2000:  # Higher threshold before downsampling
            # Use a more conservative downsampling factor
            downsample_factor = max(1, len(tmpl_wave) // 2000)  # Preserve 2000 points
            # Use a rolling window average to preserve features
            tmpl_wave_ds = np.array([np.mean(tmpl_wave[i:i+downsample_factor]) 
                          for i in range(0, len(tmpl_wave), downsample_factor)])
            tmpl_flux_ds = np.array([np.mean(tmpl_flux[i:i+downsample_factor]) 
                          for i in range(0, len(tmpl_flux), downsample_factor)])
            tmpl_wave = tmpl_wave_ds
            tmpl_flux = tmpl_flux_ds
        
        # Configure parameters for template
        tmpl_data_range = np.max(tmpl_wave) - np.min(tmpl_wave)
        tmpl_point_density = len(tmpl_wave) / tmpl_data_range
        
        tmpl_min_width = max(1, int(1 * tmpl_point_density))
        tmpl_max_width = max(5, int(8 * tmpl_point_density))  # Reduced from 10
        tmpl_max_width = min(tmpl_max_width, len(tmpl_wave) // 15)  # Stricter limit
        
        # Detect template lines
        template_lines_raw = detect_and_fit_lines(
            tmpl_wave, tmpl_flux,
            min_width=tmpl_min_width,
            max_width=tmpl_max_width,
            min_snr=self.line_detection_params.get('noise_factor', 1.5),  # Use noise_factor directly as sensitivity threshold
            smoothing_window=self.line_detection_params['smoothing_window'],
            use_smoothing=self.line_detection_params['use_smoothing']
        )
        
        # Add rest wavelength information to template lines
        template_lines = []
        for line in template_lines_raw:
            # Standard redshift calculation using the template redshift
            rest_wavelength = line['wavelength'] / (1 + template_z)
            line['rest_wavelength'] = rest_wavelength
            template_lines.append(line)
        
        # Keep more lines for comparison
        MAX_OBSERVED_LINES = 100  # Increased from 50 to capture more of the spectrum
        MAX_TEMPLATE_LINES = 100  # Increased from 50 for better matching
        
        if len(observed_lines) > MAX_OBSERVED_LINES:
            # Keep the strongest lines
            observed_lines = sorted(
                observed_lines, 
                key=lambda x: x.get('snr', 0), 
                reverse=True
            )[:MAX_OBSERVED_LINES]
            observed_lines = sorted(observed_lines, key=lambda x: x['wavelength'])
            
        if len(template_lines) > MAX_TEMPLATE_LINES:
            # Keep the strongest lines
            template_lines = sorted(
                template_lines, 
                key=lambda x: x.get('snr', 0), 
                reverse=True
            )[:MAX_TEMPLATE_LINES]
            template_lines = sorted(template_lines, key=lambda x: x['wavelength'])
        
        # Compare the observed lines with the template lines
        solid_match_threshold = self.line_detection_params['solid_match_threshold']
        weak_match_threshold = self.line_detection_params['weak_match_threshold']
        max_intensity_factor = self.line_detection_params.get('max_intensity_factor', 2.0)
        
        matches = []
        
        # OPTIMIZATION: Precompute all velocity differences for faster matching
        velocity_diffs = {}
        for i, obs_line in enumerate(observed_lines):
            for j, tmpl_line in enumerate(template_lines):
                # Only compute if same type
                if obs_line['type'] == tmpl_line['type']:
                    vel_diff = abs(wavelength_to_velocity(
                        obs_line['wavelength'], 
                        tmpl_line['wavelength']
                    ))
                    velocity_diffs[(i, j)] = vel_diff
        
        # Now do the matching with precomputed values
        for i, obs_line in enumerate(observed_lines):
            best_match = None
            best_score = -float('inf')
            best_vel_diff = float('inf')
            best_j = -1
            
            # Get the observed line SNR
            obs_snr = obs_line.get('snr', 1.0)
            
            for j, tmpl_line in enumerate(template_lines):
                # Skip if not same type
                if obs_line['type'] != tmpl_line['type']:
                    continue
                
                # Get precomputed velocity difference
                vel_diff = velocity_diffs.get((i, j), float('inf'))
                
                # Quick reject if beyond maximum possible threshold
                if vel_diff > weak_match_threshold * max_intensity_factor:
                    continue
                
                # Get the template line SNR
                tmpl_snr = tmpl_line.get('snr', 1.0)
                
                # Calculate intensity factor based on combined SNR
                combined_snr = np.sqrt(obs_snr * tmpl_snr) if obs_snr and tmpl_snr else 1.0
                intensity_factor = np.sqrt(max(1.0, combined_snr / 3.0))
                intensity_factor = min(max_intensity_factor, intensity_factor)
                
                # Calculate adjusted thresholds
                adjusted_solid_threshold = solid_match_threshold * intensity_factor
                adjusted_weak_threshold = weak_match_threshold * intensity_factor
                
                # Skip if beyond adjusted threshold
                if vel_diff > adjusted_weak_threshold:
                    continue
                
                # Calculate a score - give bonus if types match
                score = intensity_factor - (vel_diff / adjusted_weak_threshold)
                
                if score > best_score:
                    best_score = score
                    best_match = tmpl_line
                    best_vel_diff = vel_diff
                    best_j = j
            
            # Assign a match quality
            if best_match is not None:
                # Get the template line SNR
                tmpl_snr = best_match.get('snr', 1.0)
                
                # Calculate combined SNR
                combined_snr = np.sqrt(obs_snr * tmpl_snr) if obs_snr and tmpl_snr else 1.0
                intensity_factor = np.sqrt(max(1.0, combined_snr / 3.0))
                intensity_factor = min(max_intensity_factor, intensity_factor)
                
                # Scale the thresholds
                adjusted_solid_threshold = solid_match_threshold * intensity_factor
                adjusted_weak_threshold = weak_match_threshold * intensity_factor
                
                match_quality = None
                if best_vel_diff <= adjusted_solid_threshold:
                    match_quality = 'solid'
                elif best_vel_diff <= adjusted_weak_threshold:
                    match_quality = 'weak'
                
                if match_quality:
                    matches.append({
                        'observed': obs_line,
                        'template': best_match,
                        'velocity_diff': best_vel_diff,
                        'quality': match_quality,
                        'intensity_factor': intensity_factor,
                        'score': best_score
                    })
        
        # Create a summary of the results
        result = {
            'observed_lines': observed_lines,
            'template_lines': template_lines,
            'matches': matches,
            'template_info': template_info,
            'template_z': template_z,
            'method': 'scipy',
            'is_flat': self.view_mode == 'flat'
        }
        
        # Store the results for later use
        self.line_comparison_data = result
        
        # Update observation plot with lines
        self.obs_lines_btn.config(state='normal')
        self.tmpl_lines_btn.config(state='normal')
        
        # Enable NIST search button
        self.nist_search_btn.config(state='normal')
        
        # Draw the line comparisons
        self.show_obs_lines = True
        self.show_tmpl_lines = True
        self._draw_line_comparisons()
        
        # Show a brief summary message
        avg_intensity_factor = np.mean([m.get('intensity_factor', 1.0) for m in matches]) if matches else 1.0
        
        messagebox.showinfo(
            "Line Detection Results",
            (f"Detected {len(observed_lines)} lines in the observed spectrum and "
             f"{len(template_lines)} lines in the template.\n\n"
             f"Found {len(matches)} potential matches "
             f"({sum(1 for m in matches if m['quality'] == 'solid')} solid, "
             f"{sum(1 for m in matches if m['quality'] == 'weak')} weak).\n\n"
             f"Average intensity scaling factor: {avg_intensity_factor:.2f}x")
        )
        
        # Update status
        self.status_label.config(text=f"Detected and analyzed spectral lines with scipy")
    
    except Exception as e:
        messagebox.showerror("Detection Error", f"Error detecting lines: {str(e)}")
        self.status_label.config(text=f"Line detection failed: {str(e)}")

def add_custom_species(self):
    """Add custom species to the list."""
    species = simpledialog.askstring("Add Species", "Enter species (e.g., 'Fe II'):")
    if species:
        # Check if it already exists
        items = self.species_listbox.get(0, tk.END)
        if species not in items:
            self.species_listbox.insert(tk.END, species)
            self.species_listbox.selection_set(tk.END)
        else:
            # If it exists, just select it
            for i, item in enumerate(items):
                if item == species:
                    self.species_listbox.selection_set(i)
                    self.species_listbox.see(i)

def remove_selected_species(self):
    """Remove selected species from the list."""
    sel = self.species_listbox.curselection()
    if sel:
        # Convert to a list and sort in reverse order
        items = sorted(list(sel), reverse=True)
        for idx in items:
            self.species_listbox.delete(idx)

def select_all_species(self):
    """Select all species in the list."""
    self.species_listbox.select_set(0, tk.END)

def clear_all_species(self):
    """Clear all selected species."""
    self.species_listbox.selection_clear(0, tk.END)

def get_selected_species(self):
    """Get the list of selected species."""
    sel = self.species_listbox.curselection()
    return [self.species_listbox.get(idx) for idx in sel]

def clear_line_markers(self):
    """Clear all line markers from the plot."""
    # Remove all line markers
    for line in self.line_markers:
        if line in self.ax.lines:
            self.ax.lines.remove(line)
    
    # Clear the list
    self.line_markers = []
    
    # Update the canvas
    self.canvas.draw()
    
    # Update the status bar
    self.status_label.config(text="Cleared all line markers")

def on_click(self, event):
    """Handle click events on the plot for line identification and information."""
    # Check if the click is within the plot area
    if not event.inaxes or not self.ax:
        return
    
    # Extract wavelength and flux from the click position
    wavelength = event.xdata
    flux = event.ydata
    
    # Check if it's a control+click (add line marker)
    if event.button == 1 and event.key == 'control':
        # Add a marker for this line
        line = self.ax.axvline(x=wavelength, color='blue', linestyle='--', alpha=0.7)
        self.line_markers.append(line)
        self.canvas.draw()
        
        # Update status
        rounded_wave = round(wavelength, 2)
        self.status_label.config(text=f"Marked line at {rounded_wave} Å")
    
    # Check if it's a control+right-click (remove line marker)
    elif event.button == 3 and event.key == 'control':
        # Find the closest line marker
        closest_line = None
        min_distance = float('inf')
        
        for i, line in enumerate(self.line_markers):
            if line in self.ax.lines:
                try:
                    line_x = line.get_xdata()[0]  # For vertical lines
                    distance = abs(line_x - wavelength)
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_line = i
                except Exception:
                    continue
        
        # Remove the closest line if it's within a reasonable distance
        if closest_line is not None and min_distance < 10:  # 10 Å threshold
            line = self.line_markers[closest_line]
            if line in self.ax.lines:
                self.ax.lines.remove(line)
            del self.line_markers[closest_line]
            self.canvas.draw()
            
            # Update status
            self.status_label.config(text=f"Removed line marker near {round(wavelength, 2)} Å")
    
    # Normal click (show wavelength info)
    elif event.button == 1:
        # Update status
        rounded_wave = round(wavelength, 2)
        rounded_flux = round(flux, 3)
        self.status_label.config(text=f"Position: {rounded_wave} Å, Flux: {rounded_flux}")

def toggle_savgol_filter(self):
    """Toggle Savitzky-Golay filter smoothing."""
    self.use_savgol_filter = not self.use_savgol_filter
    
    # Update button text
    if self.use_savgol_filter:
        self.savgol_var.set(True)
    else:
        self.savgol_var.set(False)
    
    # Redraw the current plot
    if self.snid_results and hasattr(self, 'show_template'):
        self.show_template()
    elif self.file_path:
        # If no template is showing, but we have a file loaded, redraw that
        try:
            data = np.loadtxt(self.file_path)
            # Extract wavelength and flux from data (assuming 2-column format)
            wavelength = data[:, 0]
            flux = data[:, 1]
            
            # Get current theme colors to preserve theme
            theme_colors = None
            if hasattr(self, 'theme_manager'):
                theme_colors = self.theme_manager.get_theme_colors()
            
            # Plot with current theme colors
            plot_spectrum(
                self.ax, wavelength, flux, 
                use_savgol=self.use_savgol_filter,
                savgol_window=self.savgol_window,
                savgol_order=self.savgol_order,
                theme_colors=theme_colors
            )
            
            # Ensure axis background matches the theme
            if theme_colors:
                self.ax.set_facecolor(theme_colors["plot_bg"])
                self.fig.patch.set_facecolor(theme_colors["plot_bg"])
            
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Plot Error", str(e))
    
    # Update status
    status = "Savitzky-Golay filter enabled" if self.use_savgol_filter else "Savitzky-Golay filter disabled"
    self.status_label.config(text=status)

def update_savgol_filter(self):
    """Update the Savitzky-Golay filter parameters."""
    try:
        # Get window size
        window = int(self.savgol_window_entry.get().strip())
        if window < 3:
            messagebox.showerror("Invalid Value", "Window size must be at least 3.")
            return
        
        # Make sure window is odd
        if window % 2 == 0:
            window += 1
            self.savgol_window_entry.delete(0, tk.END)
            self.savgol_window_entry.insert(0, str(window))
        
        # Get polynomial order
        order = int(self.savgol_order_entry.get().strip())
        if order < 1:
            messagebox.showerror("Invalid Value", "Polynomial order must be at least 1.")
            return
        
        # Make sure order is less than window size
        if order >= window:
            order = window - 1
            self.savgol_order_entry.delete(0, tk.END)
            self.savgol_order_entry.insert(0, str(order))
        
        self.savgol_window = window
        self.savgol_order = order
        
        # Redraw if Savitzky-Golay filter is enabled
        if self.use_savgol_filter:
            # Get current theme colors to preserve theme
            theme_colors = None
            if hasattr(self, 'theme_manager'):
                theme_colors = self.theme_manager.get_theme_colors()
            
            if self.snid_results and hasattr(self, 'show_template'):
                self.show_template()
            elif self.file_path:
                data = np.loadtxt(self.file_path)
                # Extract wavelength and flux from data (assuming 2-column format)
                wavelength = data[:, 0]
                flux = data[:, 1]
                
                # Plot with current theme colors
                plot_spectrum(
                    self.ax, wavelength, flux, 
                    use_savgol=self.use_savgol_filter,
                    savgol_window=self.savgol_window,
                    savgol_order=self.savgol_order,
                    theme_colors=theme_colors
                )
                
                # Ensure axis background matches the theme
                if theme_colors:
                    self.ax.set_facecolor(theme_colors["plot_bg"])
                    self.fig.patch.set_facecolor(theme_colors["plot_bg"])
                
                self.canvas.draw()
        
        # Update status
        self.status_label.config(text=f"Savitzky-Golay filter updated: window={window}, order={order}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid integers for window size and polynomial order.")

def _draw_line_comparisons(self):
    """Draw line comparison markings on the plot"""
    # Only proceed if data exists
    if self.line_comparison_data is None:
        return
    
    # Clear any existing line markers that might be from line comparisons
    # (don't remove user-added markers)
    lines_to_remove = []
    for line in self.ax.lines:
        if hasattr(line, 'is_line_comparison'):
            lines_to_remove.append(line)
    
    # Also remove any text annotations we've added
    texts_to_remove = []
    for text in self.ax.texts:
        if hasattr(text, 'is_line_comparison_text'):
            texts_to_remove.append(text)
    
    for line in lines_to_remove:
        line.remove()
    
    for text in texts_to_remove:
        text.remove()
    
    # Get detection method and spectrum type
    detection_method = self.line_comparison_data.get('method', 'wavelet')
    is_flat = self.line_comparison_data.get('is_flat', False)
    
    # Draw matched lines
    for match in self.line_comparison_data['matches']:
        obs_line = match['observed']
        tmpl_line = match['template']
        match_quality = match['quality']
        intensity_factor = match.get('intensity_factor', 1.0)
        
        # Get wavelengths
        obs_wl = obs_line['wavelength']
        tmpl_wl = tmpl_line['wavelength']
        
        # Set line styles based on match type
        obs_style = 'solid' if match_quality == 'solid' else 'dashed'
        tmpl_style = 'solid' if match_quality == 'solid' else 'dashed'
        obs_alpha = 0.7 if match_quality == 'solid' else 0.5  # Increased visibility
        tmpl_alpha = 0.7 if match_quality == 'solid' else 0.5  # Increased visibility
        
        # Adjust line widths based on intensity factor
        # Base width is 1.0, scale up for higher intensity lines
        obs_width = 1.0 + (intensity_factor - 1.0) * 0.5  # Subtle width increase
        tmpl_width = 1.0 + (intensity_factor - 1.0) * 0.5
        
        # Plot observed line if enabled
        if self.show_obs_lines:
            line = self.ax.axvline(obs_wl, color='blue', linestyle=obs_style, 
                                 alpha=obs_alpha, linewidth=obs_width)
            line.is_line_comparison = True  # Mark this as a comparison line
            
        # Plot template line if enabled
        if self.show_tmpl_lines:
            line = self.ax.axvline(tmpl_wl, color='green', linestyle=tmpl_style, 
                                 alpha=tmpl_alpha, linewidth=tmpl_width)
            line.is_line_comparison = True  # Mark this as a comparison line
    
    # Plot unmatched observed lines if enabled - make these more visible
    if self.show_obs_lines:
        # Find lines that aren't in matches
        matched_obs_lines = set(match['observed']['wavelength'] for match in self.line_comparison_data['matches'])
        for line_info in self.line_comparison_data['observed_lines']:
            if line_info['wavelength'] not in matched_obs_lines:
                # Use different colors for emission/absorption
                if line_info['type'] == 'emission':
                    color = 'red'  # Unmached observed emission
                else:
                    color = 'purple'  # Unmatched observed absorption
                
                # Make unmatched lines more visible (thicker, higher alpha)
                line = self.ax.axvline(line_info['wavelength'], color=color, 
                                     linestyle=':', alpha=0.6, linewidth=1.2)
                line.is_line_comparison = True
    
    # Plot unmatched template lines if enabled - make these more visible too
    if self.show_tmpl_lines:
        # Find lines that aren't in matches
        matched_tmpl_lines = set(match['template']['wavelength'] for match in self.line_comparison_data['matches'])
        for line_info in self.line_comparison_data['template_lines']:
            if line_info['wavelength'] not in matched_tmpl_lines:
                # Use different colors for emission/absorption
                if line_info['type'] == 'emission':
                    color = 'orange'  # Unmatched template emission
                else:
                    color = 'cyan'  # Unmatched template absorption
                
                line = self.ax.axvline(line_info['wavelength'], color=color, 
                                     linestyle=':', alpha=0.6, linewidth=1.2)
                line.is_line_comparison = True
    
    # Add legend entries for lines
    if self.show_obs_lines:
        self.ax.plot([], [], color='blue', linestyle='solid', label='Solid Match (Observed)', alpha=0.7)
        self.ax.plot([], [], color='blue', linestyle='dashed', label='Weak Match (Observed)', alpha=0.5)
        self.ax.plot([], [], color='red', linestyle=':', label='Unmatched Emission (Observed)', alpha=0.6)
        self.ax.plot([], [], color='purple', linestyle=':', label='Unmatched Absorption (Observed)', alpha=0.6)
    if self.show_tmpl_lines:
        self.ax.plot([], [], color='green', linestyle='solid', label='Solid Match (Template)', alpha=0.7)
        self.ax.plot([], [], color='green', linestyle='dashed', label='Weak Match (Template)', alpha=0.5)
        self.ax.plot([], [], color='orange', linestyle=':', label='Unmatched Emission (Template)', alpha=0.6)
        self.ax.plot([], [], color='cyan', linestyle=':', label='Unmatched Absorption (Template)', alpha=0.6)
    
    # Add a note about the detection method and spectrum type
    method_text = f"Method: scipy | Mode: {'Flattened' if is_flat else 'Flux'}"
    
    # Create theme-aware bbox if theme manager is available
    bbox_props = dict(facecolor='white', alpha=0.7)
    if hasattr(self, 'theme_manager') and self.theme_manager:
        try:
            bbox_props = self.theme_manager.create_theme_aware_bbox()
        except:
            pass  # Fallback to white if theme manager fails
    
    info_text = self.ax.text(0.02, 0.02, method_text, transform=self.ax.transAxes, 
                fontsize=8, bbox=bbox_props)
    info_text.is_line_comparison_text = True
    
    # Redraw the canvas
    self.canvas.draw_idle() 