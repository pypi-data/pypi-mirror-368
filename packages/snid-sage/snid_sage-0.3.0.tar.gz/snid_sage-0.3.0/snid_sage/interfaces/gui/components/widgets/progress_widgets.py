"""
SNID SAGE - Progress Widgets
============================

Progress bar and status indicator widgets for SNID SAGE GUI.
Provides visual feedback for long-running operations and system status.

Part of the SNID SAGE GUI restructuring - Components Module
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional, Callable, Dict, Any


class AnalysisProgressBar(ttk.Frame):
    """
    Enhanced progress bar specifically designed for SNID analysis operations.
    Provides detailed status updates and cancellation support.
    """
    
    def __init__(self, parent, title="Analysis Progress", **kwargs):
        """
        Initialize the analysis progress bar.
        
        Args:
            parent: Parent widget
            title: Title text for the progress bar
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.is_running = False
        self.cancel_callback = None
        self.total_steps = 100
        self.current_step = 0
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Create the progress bar widgets"""
        # Title label
        self.title_label = ttk.Label(self, text=self.title, font=('TkDefaultFont', 10, 'bold'))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            mode='determinate',
            length=300
        )
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        
        # Percentage label
        self.percent_var = tk.StringVar(value="0%")
        self.percent_label = ttk.Label(self, textvariable=self.percent_var)
        
        # Cancel button
        self.cancel_button = ttk.Button(
            self,
            text="Cancel",
            command=self._on_cancel,
            state='disabled'
        )
        
        # Time remaining label
        self.time_var = tk.StringVar(value="")
        self.time_label = ttk.Label(self, textvariable=self.time_var, font=('TkDefaultFont', 8))
        
        # Start time tracking
        self.start_time = None
        self.last_update_time = None
    
    def _setup_layout(self):
        """Setup the widget layout"""
        # Title at top
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky='w')
        
        # Progress bar in center
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky='ew', padx=(0, 10))
        
        # Cancel button on right
        self.cancel_button.grid(row=1, column=2, sticky='e')
        
        # Status and percentage
        self.status_label.grid(row=2, column=0, sticky='w', pady=(5, 0))
        self.percent_label.grid(row=2, column=1, sticky='e', pady=(5, 0))
        
        # Time remaining
        self.time_label.grid(row=3, column=0, columnspan=2, sticky='w', pady=(2, 0))
        
        # Configure column weights
        self.grid_columnconfigure(0, weight=1)
    
    def start(self, total_steps: int = 100, cancel_callback: Optional[Callable] = None):
        """
        Start the progress tracking.
        
        Args:
            total_steps: Total number of steps in the operation
            cancel_callback: Function to call when cancel is clicked
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.cancel_callback = cancel_callback
        self.is_running = True
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
        # Reset progress
        self.progress_var.set(0)
        self.percent_var.set("0%")
        self.status_var.set("Starting...")
        self.time_var.set("")
        
        # Enable cancel button if callback provided
        if cancel_callback:
            self.cancel_button.configure(state='normal')
        
        # Start indeterminate mode initially
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start(10)
    
    def update_progress(self, step: int, status: str = ""):
        """
        Update the progress bar.
        
        Args:
            step: Current step number
            status: Status message
        """
        if not self.is_running:
            return
        
        self.current_step = step
        current_time = time.time()
        
        # Switch to determinate mode if we have meaningful progress
        if step > 0 and self.progress_bar['mode'] == 'indeterminate':
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
        
        # Calculate percentage
        if self.total_steps > 0:
            percentage = min((step / self.total_steps) * 100, 100)
            self.progress_var.set(percentage)
            self.percent_var.set(f"{percentage:.1f}%")
        
        # Update status
        if status:
            self.status_var.set(status)
        
        # Calculate time remaining
        if step > 0 and self.start_time:
            elapsed = current_time - self.start_time
            if step < self.total_steps:
                rate = step / elapsed
                remaining_steps = self.total_steps - step
                remaining_time = remaining_steps / rate
                self._update_time_display(remaining_time)
            else:
                self.time_var.set(f"Completed in {elapsed:.1f}s")
        
        self.last_update_time = current_time
        self.update_idletasks()
    
    def _update_time_display(self, remaining_seconds: float):
        """Update the time remaining display"""
        if remaining_seconds < 60:
            self.time_var.set(f"~{remaining_seconds:.0f}s remaining")
        elif remaining_seconds < 3600:
            minutes = remaining_seconds / 60
            self.time_var.set(f"~{minutes:.1f}m remaining")
        else:
            hours = remaining_seconds / 3600
            self.time_var.set(f"~{hours:.1f}h remaining")
    
    def complete(self, final_status: str = "Completed"):
        """
        Mark the progress as complete.
        
        Args:
            final_status: Final status message
        """
        self.is_running = False
        
        # Stop any indeterminate animation
        if self.progress_bar['mode'] == 'indeterminate':
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
        
        # Set to 100%
        self.progress_var.set(100)
        self.percent_var.set("100%")
        self.status_var.set(final_status)
        
        # Calculate total time
        if self.start_time:
            total_time = time.time() - self.start_time
            self.time_var.set(f"Completed in {total_time:.1f}s")
        
        # Disable cancel button
        self.cancel_button.configure(state='disabled')
    
    def cancel(self):
        """Cancel the current operation"""
        self.is_running = False
        
        # Stop any animation
        if self.progress_bar['mode'] == 'indeterminate':
            self.progress_bar.stop()
        
        self.status_var.set("Cancelled")
        self.time_var.set("")
        
        # Disable cancel button
        self.cancel_button.configure(state='disabled')
    
    def _on_cancel(self):
        """Handle cancel button click"""
        if self.cancel_callback:
            self.cancel_callback()
        self.cancel()
    
    def reset(self):
        """Reset the progress bar to initial state"""
        self.is_running = False
        self.current_step = 0
        
        # Stop any animation
        if self.progress_bar['mode'] == 'indeterminate':
            self.progress_bar.stop()
        
        self.progress_bar.configure(mode='determinate')
        self.progress_var.set(0)
        self.percent_var.set("0%")
        self.status_var.set("Ready")
        self.time_var.set("")
        
        self.cancel_button.configure(state='disabled')


class StatusIndicator(ttk.Frame):
    """
    Status indicator widget that shows system state with colored indicators
    and descriptive text.
    """
    
    STATUS_COLORS = {
        'ready': '#28a745',      # Green
        'running': '#007bff',    # Blue
        'warning': '#ffc107',    # Yellow
        'error': '#dc3545',      # Red
        'disabled': '#6c757d'    # Gray
    }
    
    def __init__(self, parent, status='ready', message='Ready', **kwargs):
        """
        Initialize the status indicator.
        
        Args:
            parent: Parent widget
            status: Initial status ('ready', 'running', 'warning', 'error', 'disabled')
            message: Initial status message
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.current_status = status
        self.message_history = []
        
        self._create_widgets()
        self._setup_layout()
        
        # Set initial status
        self.set_status(status, message)
    
    def _create_widgets(self):
        """Create the status indicator widgets"""
        # Status indicator (colored circle)
        self.indicator_canvas = tk.Canvas(self, width=16, height=16, highlightthickness=0)
        
        # Status message label
        self.message_var = tk.StringVar()
        self.message_label = ttk.Label(self, textvariable=self.message_var)
        
        # Timestamp label
        self.timestamp_var = tk.StringVar()
        self.timestamp_label = ttk.Label(self, textvariable=self.timestamp_var, 
                                       font=('TkDefaultFont', 8), foreground='gray')
    
    def _setup_layout(self):
        """Setup the widget layout"""
        self.indicator_canvas.grid(row=0, column=0, padx=(0, 8), pady=2)
        self.message_label.grid(row=0, column=1, sticky='w', pady=2)
        self.timestamp_label.grid(row=1, column=1, sticky='w')
        
        # Configure column weights
        self.grid_columnconfigure(1, weight=1)
    
    def set_status(self, status: str, message: str = "", add_timestamp: bool = True):
        """
        Set the current status.
        
        Args:
            status: Status type ('ready', 'running', 'warning', 'error', 'disabled')
            message: Status message
            add_timestamp: Whether to add timestamp to the message
        """
        self.current_status = status
        
        # Update indicator color
        self._update_indicator()
        
        # Update message
        if message:
            self.message_var.set(message)
            
            # Add to history
            timestamp = time.strftime('%H:%M:%S')
            self.message_history.append((timestamp, status, message))
            
            # Keep only last 50 messages
            if len(self.message_history) > 50:
                self.message_history = self.message_history[-50:]
            
            # Update timestamp
            if add_timestamp:
                self.timestamp_var.set(f"Last updated: {timestamp}")
    
    def _update_indicator(self):
        """Update the visual indicator"""
        self.indicator_canvas.delete("all")
        
        color = self.STATUS_COLORS.get(self.current_status, self.STATUS_COLORS['disabled'])
        
        # Draw filled circle
        self.indicator_canvas.create_oval(2, 2, 14, 14, fill=color, outline=color)
        
        # Add pulsing effect for 'running' status
        if self.current_status == 'running':
            self._start_pulse_animation()
    
    def _start_pulse_animation(self):
        """Start pulsing animation for running status"""
        def pulse():
            if self.current_status == 'running':
                # Alternate between normal and lighter color
                colors = [self.STATUS_COLORS['running'], '#4dabf7']
                current_color = colors[int(time.time() * 2) % 2]
                
                self.indicator_canvas.delete("all")
                self.indicator_canvas.create_oval(2, 2, 14, 14, fill=current_color, outline=current_color)
                
                # Schedule next update
                self.after(500, pulse)
        
        pulse()
    
    def get_status(self) -> str:
        """Get the current status"""
        return self.current_status
    
    def get_message_history(self) -> list:
        """Get the message history"""
        return self.message_history.copy()
    
    def clear_history(self):
        """Clear the message history"""
        self.message_history.clear()


class MultiStepProgressDialog:
    """
    Dialog showing progress for multi-step operations with individual step status.
    """
    
    def __init__(self, parent, title="Operation Progress", steps=None):
        """
        Initialize the multi-step progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            steps: List of step names
        """
        self.parent = parent
        self.title = title
        self.steps = steps or []
        self.current_step_index = -1
        self.dialog = None
        self.step_indicators = []
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the progress dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self._setup_interface()
    
    def _setup_interface(self):
        """Setup the dialog interface"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Overall progress
        overall_frame = ttk.LabelFrame(main_frame, text="Overall Progress", padding=10)
        overall_frame.pack(fill='x', pady=(0, 15))
        
        self.overall_progress = AnalysisProgressBar(overall_frame, title="")
        self.overall_progress.pack(fill='x')
        
        # Step details
        if self.steps:
            steps_frame = ttk.LabelFrame(main_frame, text="Step Details", padding=10)
            steps_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            # Create scrollable frame for steps
            canvas = tk.Canvas(steps_frame)
            scrollbar = ttk.Scrollbar(steps_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Create step indicators
            for i, step_name in enumerate(self.steps):
                step_frame = ttk.Frame(scrollable_frame)
                step_frame.pack(fill='x', pady=2)
                
                indicator = StatusIndicator(step_frame, status='disabled', message=step_name)
                indicator.pack(side='left', fill='x', expand=True)
                
                self.step_indicators.append(indicator)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        self.close_button = ttk.Button(button_frame, text="Close", command=self.close, state='disabled')
        self.close_button.pack(side='right')
    
    def start(self, total_steps: int = None):
        """Start the multi-step operation"""
        if total_steps is None:
            total_steps = len(self.steps)
        
        self.overall_progress.start(total_steps)
        self.current_step_index = -1
    
    def next_step(self, step_name: str = None, status_message: str = ""):
        """Move to the next step"""
        self.current_step_index += 1
        
        # Update overall progress
        self.overall_progress.update_progress(
            self.current_step_index + 1,
            step_name or f"Step {self.current_step_index + 1}"
        )
        
        # Update step indicators
        if self.step_indicators:
            # Mark previous steps as complete
            for i in range(self.current_step_index):
                if i < len(self.step_indicators):
                    self.step_indicators[i].set_status('ready', 'Completed')
            
            # Mark current step as running
            if self.current_step_index < len(self.step_indicators):
                self.step_indicators[self.current_step_index].set_status(
                    'running', status_message or 'In progress...'
                )
    
    def update_current_step(self, status_message: str):
        """Update the status of the current step"""
        if (self.current_step_index >= 0 and 
            self.current_step_index < len(self.step_indicators)):
            self.step_indicators[self.current_step_index].set_status(
                'running', status_message
            )
    
    def complete_step(self, status_message: str = "Completed"):
        """Mark the current step as completed"""
        if (self.current_step_index >= 0 and 
            self.current_step_index < len(self.step_indicators)):
            self.step_indicators[self.current_step_index].set_status(
                'ready', status_message
            )
    
    def error_step(self, error_message: str = "Error"):
        """Mark the current step as having an error"""
        if (self.current_step_index >= 0 and 
            self.current_step_index < len(self.step_indicators)):
            self.step_indicators[self.current_step_index].set_status(
                'error', error_message
            )
    
    def complete(self, final_message: str = "All steps completed"):
        """Complete the entire operation"""
        self.overall_progress.complete(final_message)
        
        # Mark all steps as complete
        for indicator in self.step_indicators:
            if indicator.get_status() == 'running':
                indicator.set_status('ready', 'Completed')
        
        # Enable close button
        self.close_button.configure(state='normal')
    
    def close(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.destroy()
    
    def show(self):
        """Show the dialog"""
        if self.dialog:
            self.dialog.wait_window()


# Example usage and testing
if __name__ == "__main__":
    def test_progress_widgets():
        root = tk.Tk()
        root.title("Progress Widgets Test")
        root.geometry("600x500")
        
        # Test AnalysisProgressBar
        progress_frame = ttk.LabelFrame(root, text="Analysis Progress Bar", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        progress_bar = AnalysisProgressBar(progress_frame, title="SNID Analysis")
        progress_bar.pack(fill='x')
        
        # Test StatusIndicator
        status_frame = ttk.LabelFrame(root, text="Status Indicators", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        status1 = StatusIndicator(status_frame, 'ready', 'System ready')
        status1.pack(fill='x', pady=2)
        
        status2 = StatusIndicator(status_frame, 'running', 'Analysis in progress')
        status2.pack(fill='x', pady=2)
        
        status3 = StatusIndicator(status_frame, 'warning', 'Low memory warning')
        status3.pack(fill='x', pady=2)
        
        status4 = StatusIndicator(status_frame, 'error', 'Template not found')
        status4.pack(fill='x', pady=2)
        
        # Test controls
        control_frame = ttk.Frame(root)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        def simulate_analysis():
            def run_simulation():
                progress_bar.start(10, lambda: print("Cancelled!"))
                
                steps = [
                    "Loading spectrum data",
                    "Preprocessing spectrum", 
                    "Loading templates",
                    "Running correlations",
                    "Finding best matches",
                    "Calculating statistics",
                    "Generating plots",
                    "Preparing results",
                    "Saving output",
                    "Analysis complete"
                ]
                
                for i, step in enumerate(steps):
                    time.sleep(0.5)  # Simulate work
                    progress_bar.update_progress(i + 1, step)
                    root.update()
                
                progress_bar.complete("Analysis completed successfully!")
            
            # Run in thread to prevent GUI freezing
            thread = threading.Thread(target=run_simulation)
            thread.daemon = True
            thread.start()
        
        def test_multi_step():
            steps = [
                "Initialize SNID engine",
                "Load spectrum file", 
                "Preprocess spectrum",
                "Load template library",
                "Run cross-correlation",
                "Analyze results",
                "Generate summary"
            ]
            
            dialog = MultiStepProgressDialog(root, "SNID Analysis Steps", steps)
            
            def run_steps():
                dialog.start()
                
                for i, step in enumerate(steps):
                    dialog.next_step(step, f"Processing {step.lower()}...")
                    time.sleep(1)  # Simulate work
                    dialog.complete_step("Done")
                    root.update()
                
                dialog.complete("SNID analysis completed!")
            
            # Run in thread
            thread = threading.Thread(target=run_steps)
            thread.daemon = True
            thread.start()
            
            dialog.show()
        
        ttk.Button(control_frame, text="Simulate Analysis", 
                  command=simulate_analysis).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Multi-Step Dialog", 
                  command=test_multi_step).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Reset Progress", 
                  command=progress_bar.reset).pack(side='left', padx=5)
        
        root.mainloop()
    
    test_progress_widgets() 
