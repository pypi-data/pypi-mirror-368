"""
NIST database search functions for spectral line identification
"""
import os
import csv
import threading
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import numpy as np
from datetime import datetime

# Optional imports
try:
    # Try to import astroquery and astropy for NIST database access
    from astroquery.nist import Nist
    import astropy.units as u
    ASTROQUERY_AVAILABLE = True
except ImportError:
    ASTROQUERY_AVAILABLE = False

# Keep the requests import as a fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

def search_nist_for_lines(self):
    """Search NIST database for marked lines."""
    if not self.line_markers:
        messagebox.showinfo("No Lines", "No spectral lines have been marked. Use Ctrl+Click to mark lines on the plot.")
        return
    
    # Check for required dependencies
    if not ASTROQUERY_AVAILABLE:
        if not REQUESTS_AVAILABLE:
            messagebox.showerror("Dependencies Missing", 
                                "This feature requires either 'astroquery' and 'astropy' (recommended) or 'requests'.\n"
                                "Please install with: pip install astroquery astropy")
            return
        else:
            # Use old method with direct HTTP requests
            messagebox.showwarning("Using Legacy Method", 
                                  "For better results, install 'astroquery' and 'astropy' packages:\n"
                                  "pip install astroquery astropy")
            return _search_nist_direct_http(self)
    
    # Use line_search_species directly
    species = self.line_search_species
    if not species:
        messagebox.showinfo("No Species", "No elements selected. Please select at least one element from the species list.")
        return
    
    # Create the search window
    search_window = tk.Toplevel(self.master)
    search_window.title("NIST Database Search")
    search_window.geometry("600x400")
    search_window.transient(self.master)
    
    # Count how many lines are from matches (if we have line comparison data)
    matched_lines_count = 0
    total_lines = len(self.line_markers)
    if hasattr(self, 'line_comparison_data') and self.line_comparison_data and self.line_comparison_data['matches']:
        matched_wavelengths = set()
        for match in self.line_comparison_data['matches']:
            matched_wavelengths.add(match['observed']['wavelength'])
        
        # Count how many of our marked lines match these wavelengths
        for line in self.line_markers:
            if hasattr(line, 'get_xdata'):
                wave = line.get_xdata()[0]
                for match_wave in matched_wavelengths:
                    if abs(wave - match_wave) < 1.0:  # Within 1 Å
                        matched_lines_count += 1
                        break
    
    # Set up the UI for the search window
    main_frame = ttk.Frame(search_window, padding=10)
    main_frame.pack(fill='both', expand=True)
    
    # Status label
    initial_status = "Preparing to search NIST database..."
    if matched_lines_count > 0:
        initial_status += f" (Including {matched_lines_count} matched lines from analysis)"
    
    status_var = tk.StringVar(value=initial_status)
    ttk.Label(main_frame, textvariable=status_var).pack(fill='x', pady=5)
    
    # Line count label
    ttk.Label(main_frame, 
              text=f"Searching {total_lines} spectral lines across {len(species)} atomic species",
              font=('Arial', 9)).pack(fill='x', pady=2)
    
    # Progress bar
    progress = ttk.Progressbar(main_frame, mode='indeterminate')
    progress.pack(fill='x', pady=5)
    progress.start(10)
    
    # Results text
    result_frame = ttk.LabelFrame(main_frame, text="Results", padding=5)
    result_frame.pack(fill='both', expand=True, pady=5)
    
    # Add a text widget with scrollbar for the results
    text_frame = ttk.Frame(result_frame)
    text_frame.pack(fill='both', expand=True)
    
    results_text = tk.Text(text_frame, height=10, width=80, wrap=tk.WORD)
    results_text.pack(side='left', fill='both', expand=True)
    
    scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=results_text.yview)
    scrollbar.pack(side='right', fill='y')
    results_text.configure(yscrollcommand=scrollbar.set)
    
    # Add a label for formatting
    ttk.Label(main_frame, text="Results will be shown with the best matches at the top.").pack(anchor='w', pady=2)
    
    # Buttons frame
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill='x', pady=10)
    
    # Export button (initially disabled)
    export_btn = ttk.Button(btn_frame, text="Export to CSV", state='disabled')
    export_btn.pack(side='left', padx=5)
    
    # Close button
    ttk.Button(btn_frame, text="Close", command=search_window.destroy).pack(side='right', padx=5)
    
    # Function to update the UI from the search thread
    def update_ui():
        """Update the UI with search results."""
        # Update the UI
        progress.stop()
        progress.pack_forget()
        
        if not self.nist_matches:
            status_var.set("No matches found in NIST database.")
            results_text.insert(tk.END, "No spectral line matches were found in the NIST database for the selected species and wavelengths.")
            return
        
        # Update status
        total_matches = sum(len(m['matches']) for m in self.nist_matches)
        status_var.set(f"Found {total_matches} potential matches for {len(self.nist_matches)} wavelengths.")
        
        # Enable export button
        export_btn.config(state='normal', command=lambda: export_nist_results_to_csv(self, self.nist_matches))
        
        # Display results
        results_text.delete(1.0, tk.END)
        
        for line_result in self.nist_matches:
            wave = line_result['wavelength']
            results_text.insert(tk.END, f"Line at {wave:.2f} Å - {len(line_result['matches'])} potential matches\n")
            
            if line_result['matches']:
                results_text.insert(tk.END, "-" * 80 + "\n")
                
                # Sort matches by relative intensity
                sorted_matches = sorted(line_result['matches'], 
                                      key=lambda x: x['rel_intensity'] if x['rel_intensity'] is not None else 0, 
                                      reverse=True)
                
                for i, match in enumerate(sorted_matches[:10]):  # Show top 10 matches
                    species = match['species']
                    wave_match = match['wavelength']
                    diff = match['wavelength_diff']
                    rel_int = match['rel_intensity'] if match['rel_intensity'] is not None else "N/A"
                    conf = match['observed_type']
                    term = match['term']
                    
                    results_text.insert(tk.END, f"{i+1}. {species} - {wave_match:.2f} Å (Δ={diff:.3f} Å), ", "species")
                    results_text.insert(tk.END, f"Rel. Int: {rel_int}, Type: {conf}\n")
                    if term:
                        results_text.insert(tk.END, f"   Term: {term}\n")
                
                if len(line_result['matches']) > 10:
                    results_text.insert(tk.END, f"... and {len(line_result['matches']) - 10} more matches.\n")
            
            results_text.insert(tk.END, "\n")
        
        # Add tag for highlighting species
        results_text.tag_configure("species", foreground="blue")
    
    # Function to perform the NIST search using astroquery
    def do_search_astroquery():
        """Search NIST database using astroquery for all marked lines."""
        try:
            # Get all the wavelengths from line markers
            wavelengths = []
            for line in self.line_markers:
                if hasattr(line, 'get_xdata'):
                    wave = line.get_xdata()[0]
                    wavelengths.append(wave)
            
            # Update status
            search_window.after(0, lambda: status_var.set(f"Searching NIST database for {len(wavelengths)} lines across {len(species)} species..."))
            
            # Clear any existing cache to ensure fresh results
            Nist.clear_cache()
            
            # List to store all matches
            nist_matches = []
            
            # Search for each wavelength
            for wave in wavelengths:
                # Determine search range
                wave_min = wave - self.line_search_delta
                wave_max = wave + self.line_search_delta
                
                # List to store matches for this wavelength
                line_matches = []
                
                # Search for each species
                for spec in species:
                    # Clean up species name
                    spec_clean = spec.strip()
                    
                    try:
                        # Query NIST database using astroquery
                        result = Nist.query(wave_min * u.AA, wave_max * u.AA, linename=spec_clean)
                        
                        if result and len(result) > 0:
                            # Process each row in the result
                            for row in result:
                                try:
                                    # Get wavelength - prefer observed over Ritz
                                    match_wl = None
                                    if row['Observed'] and str(row['Observed']) != '--':
                                        match_wl = float(row['Observed'])
                                    elif row['Ritz'] and str(row['Ritz']) != '--':
                                        match_wl = float(row['Ritz'])
                                    else:
                                        continue  # Skip lines with no wavelength
                                    
                                    # Get other data
                                    rel_int = float(row['Rel.']) if row['Rel.'] and str(row['Rel.']) != '--' else None
                                    line_type = row['Type'] if row['Type'] and str(row['Type']) != '--' else None
                                    transition = row['Transition'] if row['Transition'] and str(row['Transition']) != '--' else None
                                    
                                    # Skip if out of range (redundant, but just to be safe)
                                    if match_wl < wave_min or match_wl > wave_max:
                                        continue
                                    
                                    # Calculate the wavelength difference
                                    wavelength_diff = abs(wave - match_wl)
                                    
                                    # Add the match
                                    line_matches.append({
                                        'species': spec_clean,
                                        'wavelength': match_wl,
                                        'wavelength_diff': wavelength_diff,
                                        'rel_intensity': rel_int,
                                        'observed_type': line_type,
                                        'term': transition,
                                        'transition_probability': None  # Not directly available in astroquery results
                                    })
                                    
                                except Exception as e:
                                    print(f"Error processing NIST result: {str(e)}")
                    
                    except Exception as e:
                        print(f"Error querying NIST for {spec_clean} near {wave} Å: {str(e)}")
                
                # Add all matches for this wavelength
                nist_matches.append({
                    'wavelength': wave,
                    'matches': line_matches
                })
            
            # Store the results
            self.nist_matches = nist_matches
            
            # Update the UI in the main thread
            search_window.after(0, update_ui)
            
        except Exception as e:
            # Handle any errors
            self.nist_matches = []
            search_window.after(0, lambda: messagebox.showerror("Search Error", f"Error searching NIST database: {str(e)}"))
            search_window.after(0, search_window.destroy)
    
    # Start the search in a separate thread
    search_thread = threading.Thread(target=do_search_astroquery)
    search_thread.daemon = True
    search_thread.start()

def _search_nist_direct_http(self):
    """Legacy method to search NIST database using direct HTTP requests."""
    # This is the original implementation using direct HTTP requests
    # It's kept as a fallback in case astroquery is not available
    # ... [original implementation here] ...
    
    # Create search window, progress bar, etc.
    # ... 
    
    # Search thread function
    def do_search():
        """Search NIST database for all marked lines using direct HTTP requests."""
        try:
            # Get all the wavelengths from line markers
            wavelengths = []
            for line in self.line_markers:
                if hasattr(line, 'get_xdata'):
                    wave = line.get_xdata()[0]
                    wavelengths.append(wave)
            
            # Update status
            status_var.set(f"Searching NIST database for {len(wavelengths)} lines across {len(species)} species...")
            
            # List to store all matches
            nist_matches = []
            
            # NIST API base URL
            base_url = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl"
            
            # Search for each wavelength
            for wave in wavelengths:
                # Determine search range
                wave_min = wave - self.line_search_delta
                wave_max = wave + self.line_search_delta
                
                # List to store matches for this wavelength
                line_matches = []
                
                # Search for each species
                for spec in species:
                    # Clean up species name for NIST query
                    spec_clean = spec.strip()
                    
                    # Query parameters
                    params = {
                        'spectra': spec_clean,
                        'low_w': wave_min,
                        'upp_w': wave_max,
                        'unit': '1',  # 1 = Angstroms
                        'format': '3', # TSV format
                        'remove_js': '1',  # No JavaScript
                        'show_obs_wl': '1',
                        'show_calc_wl': '1',
                    }
                    
                    try:
                        # Make the request
                        response = requests.get(base_url, params=params)
                        
                        if response.status_code == 200:
                            # Parse the TSV response
                            lines = response.text.strip().split('\n')
                            
                            # Skip header lines
                            data_lines = []
                            data_started = False
                            
                            for line in lines:
                                # Check if we're at the start of data
                                if line.startswith('----'):
                                    data_started = True
                                    continue
                                
                                # If we're in the data section
                                if data_started and line.strip() and not line.startswith('Obs'):
                                    data_lines.append(line)
                            
                            # Process each data line
                            for data_line in data_lines:
                                try:
                                    # Split by tabs or multiple spaces
                                    parts = [p.strip() for p in data_line.split('\t')]
                                    
                                    # Only continue if we have enough parts
                                    if len(parts) < 3:
                                        continue
                                    
                                    # Extract the data
                                    obs_wl = float(parts[0]) if parts[0] and parts[0] != '-' else None
                                    ritz_wl = float(parts[1]) if parts[1] and parts[1] != '-' else None
                                    rel_int = float(parts[2]) if parts[2] and parts[2] != '-' else None
                                    
                                    # Use observed wavelength if available, otherwise use calculated
                                    match_wl = obs_wl if obs_wl else ritz_wl
                                    
                                    # Skip if we don't have a wavelength
                                    if match_wl is None:
                                        continue
                                    
                                    # Extract additional data if available
                                    aki = float(parts[3]) if len(parts) > 3 and parts[3] and parts[3] != '-' else None
                                    conf = parts[4] if len(parts) > 4 and parts[4] != '-' else None
                                    term = parts[5] if len(parts) > 5 and parts[5] != '-' else None
                                    
                                    # Skip if out of range
                                    if match_wl < wave_min or match_wl > wave_max:
                                        continue
                                    
                                    # Calculate the wavelength difference
                                    wavelength_diff = abs(wave - match_wl)
                                    
                                    # Add the match
                                    line_matches.append({
                                        'species': spec_clean,
                                        'wavelength': match_wl,
                                        'wavelength_diff': wavelength_diff,
                                        'rel_intensity': rel_int,
                                        'observed_type': conf,
                                        'term': term,
                                        'transition_probability': aki
                                    })
                                except Exception as e:
                                    print(f"Error parsing line '{data_line}': {str(e)}")
                                    continue
                        else:
                            print(f"Error querying NIST database for {spec_clean}: {response.status_code}")
                    
                    except Exception as e:
                        print(f"Error searching NIST for {spec_clean} near {wave} Å: {str(e)}")
                
                # Add all matches for this wavelength
                nist_matches.append({
                    'wavelength': wave,
                    'matches': line_matches
                })
            
            # Store the results
            self.nist_matches = nist_matches
            
            # Update the UI in the main thread
            search_window.after(0, update_ui)
            
        except Exception as e:
            # Handle any errors
            self.nist_matches = []
            search_window.after(0, lambda: messagebox.showerror("Search Error", f"Error searching NIST database: {str(e)}"))
            search_window.after(0, search_window.destroy)
    
    # Start the search in a separate thread
    search_thread = threading.Thread(target=do_search)
    search_thread.daemon = True
    search_thread.start()
    
def export_nist_results_to_csv(self, nist_matches):
    """Export NIST search results to a CSV file."""
    if not nist_matches:
        messagebox.showinfo("No Data", "No NIST search results to export.")
        return
    
    # Ask for save location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save NIST Results"
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, 'w', newline='') as csvfile:
            # Create CSV writer
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                "Observed Wavelength (Å)", 
                "NIST Wavelength (Å)", 
                "Difference (Å)",
                "Species", 
                "Rel. Intensity", 
                "Type",
                "Term",
                "Transition Probability"
            ])
            
            # Write data
            for line_result in nist_matches:
                observed_wave = line_result['wavelength']
                
                if not line_result['matches']:
                    # Write a row for observed wavelength with no matches
                    writer.writerow([
                        f"{observed_wave:.3f}",
                        "", "", "", "", "", "", ""
                    ])
                else:
                    # Sort matches by relative intensity
                    sorted_matches = sorted(
                        line_result['matches'], 
                        key=lambda x: x['rel_intensity'] if x['rel_intensity'] is not None else 0, 
                        reverse=True
                    )
                    
                    # Write a row for each match
                    for match in sorted_matches:
                        try:
                            writer.writerow([
                                f"{observed_wave:.3f}",
                                f"{match['wavelength']:.3f}",
                                f"{match['wavelength_diff']:.3f}",
                                match['species'],
                                match['rel_intensity'] if match['rel_intensity'] is not None else "",
                                match['observed_type'] if match['observed_type'] else "",
                                match['term'] if match['term'] else "",
                                match['transition_probability'] if match['transition_probability'] is not None else ""
                            ])
                        except Exception as e:
                            print(f"Error writing NIST result row: {str(e)}")
                            continue
        
        messagebox.showinfo("Export Complete", f"NIST results exported to {file_path}")
        
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")

def show_nist_results(self, nist_matches):
    """Show NIST database search results in a detailed window."""
    if not nist_matches:
        messagebox.showinfo("No Matches", "No matches found in the NIST database.")
        return
    
    # Create the results window
    results_window = tk.Toplevel(self.master)
    results_window.title("NIST Database Matches")
    results_window.geometry("800x600")
    results_window.transient(self.master)
    
    # Main frame
    main_frame = ttk.Frame(results_window, padding=10)
    main_frame.pack(fill='both', expand=True)
    
    # Add a notebook for each wavelength
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill='both', expand=True, pady=5)
    
    # Add a tab for each wavelength
    for i, line_result in enumerate(nist_matches):
        wave = line_result['wavelength']
        num_matches = len(line_result['matches'])
        
        # Create a tab
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text=f"{wave:.2f} Å ({num_matches})")
        
        # If no matches, show a message
        if not line_result['matches']:
            ttk.Label(tab, text=f"No matches found for {wave:.2f} Å in the NIST database.").pack(pady=20)
            continue
        
        # Sort matches by relative intensity
        sorted_matches = sorted(
            line_result['matches'], 
            key=lambda x: x['rel_intensity'] if x['rel_intensity'] is not None else 0, 
            reverse=True
        )
        
        # Create a frame for the details
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', pady=5)
        
        # General information
        ttk.Label(top_frame, text=f"Searching ±{self.line_search_delta} Å around {wave:.2f} Å", 
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(top_frame, text=f"Found {num_matches} potential matches").pack(anchor='w')
        
        # Create a treeview to show the matches
        columns = ("wavelength", "diff", "species", "intensity", "type", "term")
        tree = ttk.Treeview(tab, columns=columns, show='headings')
        tree.pack(fill='both', expand=True, pady=5)
        
        # Define headings
        tree.heading("wavelength", text="Wavelength (Å)")
        tree.heading("diff", text="Diff (Å)")
        tree.heading("species", text="Species")
        tree.heading("intensity", text="Rel. Int.")
        tree.heading("type", text="Type")
        tree.heading("term", text="Term")
        
        # Define columns widths
        tree.column("wavelength", width=100, anchor='center')
        tree.column("diff", width=70, anchor='center')
        tree.column("species", width=100, anchor='w')
        tree.column("intensity", width=70, anchor='center')
        tree.column("type", width=50, anchor='center')
        tree.column("term", width=200, anchor='w')
        
        # Add vertical scrollbar
        tree_scroll = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        tree_scroll.pack(side='right', fill='y')
        tree.configure(yscrollcommand=tree_scroll.set)
        
        # Add data to the treeview
        for match in sorted_matches:
            match_wl = match['wavelength']
            diff = match['wavelength_diff']
            spec = match['species']
            rel_int = match['rel_intensity'] if match['rel_intensity'] is not None else "N/A"
            obs_type = match['observed_type'] if match['observed_type'] else "-"
            term = match['term'] if match['term'] else "-"
            
            tree.insert("", "end", values=(
                f"{match_wl:.3f}", 
                f"{diff:.3f}", 
                spec, 
                rel_int, 
                obs_type, 
                term
            ))
        
        # Add the detail info box
        detail_frame = ttk.LabelFrame(tab, text="Element Information")
        detail_frame.pack(fill='x', pady=10)
        
        # Info text widget
        info_text = tk.Text(detail_frame, height=5, wrap=tk.WORD)
        info_text.pack(fill='both', expand=True, pady=5)
        
        # Function to update the element info when a row is selected
        def update_element_info(*args):
            """Update element information when a row is selected."""
            selected = tree.selection()
            if not selected:
                info_text.delete(1.0, tk.END)
                info_text.insert(tk.END, "Select a row to see more information.")
                return
            
            item = tree.item(selected[0])
            values = item['values']
            
            if len(values) >= 6:
                wavelength, diff, species, intensity, obs_type, term = values
                
                # Get the full match data
                match_data = None
                for match in sorted_matches:
                    if (abs(match['wavelength'] - float(wavelength)) < 0.001 and 
                        match['species'] == species):
                        match_data = match
                        break
                
                if match_data:
                    # Update the info text
                    info_text.delete(1.0, tk.END)
                    
                    # Basic info
                    info_text.insert(tk.END, f"Element: {species}\n", "heading")
                    info_text.insert(tk.END, f"Wavelength: {wavelength} Å (Difference: {diff} Å)\n")
                    info_text.insert(tk.END, f"Relative Intensity: {intensity}\n")
                    
                    # Type/Classification
                    if obs_type and obs_type != "-":
                        info_text.insert(tk.END, f"Type: {obs_type}")
                        if obs_type in self.TYPE_MAP:
                            info_text.insert(tk.END, f" ({self.TYPE_MAP[obs_type]})")
                        info_text.insert(tk.END, "\n")
                    
                    # Term information
                    if term and term != "-":
                        info_text.insert(tk.END, f"Term: {term}\n")
                    
                    # Transition probability
                    aki = match_data.get('transition_probability')
                    if aki is not None:
                        info_text.insert(tk.END, f"Transition Probability (Aki): {aki:.2e} s⁻¹\n")
                    
                    # Add styling
                    info_text.tag_configure("heading", font=('Arial', 10, 'bold'))
                else:
                    info_text.delete(1.0, tk.END)
                    info_text.insert(tk.END, "Error retrieving detailed information.")
        
        # Bind the selection event
        tree.bind("<<TreeviewSelect>>", update_element_info)
        
        # Set initial info text
        info_text.insert(tk.END, "Select a row to see more information.")
    
    # Bottom buttons
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill='x', pady=10)
    
    # Add export button
    ttk.Button(btn_frame, text="Export to CSV", 
              command=lambda: self._export_nist_results_to_csv(nist_matches)).pack(side='left', padx=5)
    
    # Add close button
    ttk.Button(btn_frame, text="Close", 
              command=results_window.destroy).pack(side='right', padx=5) 