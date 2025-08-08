"""
Games Integration Feature

Handles all games-related functionality including:
- Game menu display
- Game launching during analysis
- Progress window games integration
- Game positioning and window management

Extracted from sage_gui.py to improve maintainability and modularity.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time

# Check for games availability
try:
    from snid_sage.snid.games import show_game_menu, run_game_in_thread
    GAMES_AVAILABLE = True
except ImportError:
    GAMES_AVAILABLE = False


class GamesIntegration:
    """Handles games integration for entertainment during analysis"""
    
    def __init__(self, gui_instance):
        """Initialize games integration with reference to main GUI"""
        self.gui = gui_instance
        self.game_thread = None
        self.current_game_panel = None
    
    def start_games_menu(self):
        """Show games menu"""
        if not GAMES_AVAILABLE:
            messagebox.showinfo("Games Not Available", 
                              "Games are not available. Install pygame to enable games:\n\n"
                              "pip install pygame")
            return
        
        try:
            # Offer choice between immediate games or games during analysis
            choice = messagebox.askyesnocancel(
                "Games Menu 🎮",
                "Would you like to play games?\n\n"
                "🎯 Yes: Start analysis with games available\n"
                "🎮 No: Launch games immediately\n"
                "❌ Cancel: Return to main interface\n\n"
                "Choose your gaming preference!"
            )
            
            if choice is True:
                # Start analysis with integrated games
                messagebox.showinfo("Starting Analysis", 
                                  "Starting SNID analysis...\n\n"
                                  "Games will be available in the progress window!")
                if hasattr(self.gui, 'analysis_controller'):
                    self.gui.analysis_controller.run_snid_analysis_only()
                else:
                    self.gui.run_snid_analysis_only()
                
            elif choice is False:
                # Launch games immediately using original popup method
                try:
                    def game_callback():
                        game_func = show_game_menu()
                        if game_func:
                            import threading
                            game_thread = threading.Thread(target=game_func, daemon=True)
                            game_thread.start()
                            if hasattr(self.gui, 'update_header_status'):
                                self.gui.update_header_status("🎮 Game started!")
                        else:
                            if hasattr(self.gui, 'update_header_status'):
                                self.gui.update_header_status("Ready for SNID analysis")
                    
                    # Run in thread to avoid blocking GUI
                    game_thread = threading.Thread(target=game_callback, daemon=True)
                    game_thread.start()
                    
                except Exception as e:
                    messagebox.showerror("Games Error", f"Could not start games: {e}")
            
            # If cancelled (choice is None), do nothing
            
        except Exception as e:
            messagebox.showerror("Games Error", f"Error starting games menu: {e}")
    
    def _offer_games_during_analysis(self):
        """Games are integrated into the progress window – no extra progress message needed"""
        # Games are automatically shown in the progress window's right panel.
        # Suppress the progress log entry to keep the analysis steps focused.
        pass
    
    def _show_integrated_games(self, game_panel=None):
        """Show the integrated game selection in the game panel"""
        if game_panel is None:
            game_panel = self.current_game_panel
        else:
            self.current_game_panel = game_panel
            
        if game_panel is None:
            return
        
        # Check if the widget still exists before trying to use it
        try:
            if not game_panel.winfo_exists():
                self.current_game_panel = None
                return
        except (tk.TclError, AttributeError):
            self.current_game_panel = None
            return
        
        # Clear any existing content
        try:
            for widget in game_panel.winfo_children():
                widget.destroy()
        except (tk.TclError, AttributeError):
            # Widget already destroyed, just return
            self.current_game_panel = None
            return
        
        # Game panel header
        game_header = tk.Label(game_panel, text="🎮 Entertainment Center",
                             font=('Arial', 16, 'bold'),
                             bg='#2c3e50', fg='#ecf0f1')
        game_header.pack(pady=(15, 10))
        
        # Subtitle
        subtitle = tk.Label(game_panel, text="Play while SNID analysis runs in the background",
                          font=('Arial', 12),
                          bg='#2c3e50', fg='#bdc3c7')
        subtitle.pack(pady=(0, 20))
        
        # Check if games are available
        if not GAMES_AVAILABLE:
            self._show_games_unavailable(game_panel)
            return
        
        # Game selection area - Only Space Debris now
        self.game_selection_frame = tk.Frame(game_panel, bg='#2c3e50')
        self.game_selection_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Space Debris game button
        btn = tk.Button(self.game_selection_frame, text="🛰️ Space Debris Cleanup",
                       font=('Arial', 14, 'bold'),
                       bg='#e74c3c', fg='white',
                       relief='flat', bd=0, padx=20, pady=15,
                       cursor='hand2',
                       command=self._start_debris)
        btn.pack(fill='x', pady=8)
        
        # Description
        desc = tk.Label(self.game_selection_frame, text="Advanced space simulation with realistic spacecraft and satellite debris!\nFeatures detailed satellites, particle effects, and deep space visuals.",
                       font=('Arial', 11),
                       bg='#2c3e50', fg='#95a5a6',
                       justify='center')
        desc.pack(pady=(0, 15))
        
        # Features list
        features_label = tk.Label(self.game_selection_frame, 
                                text="✨ Enhanced Features:\n• 4 types of realistic satellites with solar panels\n• Detailed spacecraft with wings and thrusters\n• Energy bullets with particle trail effects\n• Deep space background with Earth and stars",
                                font=('Arial', 10),
                                bg='#2c3e50', fg='#7fb3d3',
                                justify='left')
        features_label.pack(pady=(0, 20))
        
        # No thanks button
        no_thanks_btn = tk.Button(self.game_selection_frame, text="🚫 Focus on Analysis",
                                font=('Arial', 10),
                                bg='#7f8c8d', fg='white',
                                relief='flat', bd=0, padx=15, pady=8,
                                cursor='hand2',
                                command=self._focus_on_analysis)
        no_thanks_btn.pack(fill='x', pady=(10, 0))
    
    def _show_games_unavailable(self, game_panel):
        """Show message when games are not available"""
        unavailable_label = tk.Label(game_panel,
                                    text="🚫 Games Not Available\n\nPygame is required for games.\nInstall with: pip install pygame",
                                    font=('Arial', 13),
                                    bg='#2c3e50', fg='#e74c3c',
                                    justify='center')
        unavailable_label.pack(expand=True)
    
    def _start_debris(self):
        """Start Space Debris game in positioned window"""
        self._start_positioned_game("Space Debris", "run_debris_game")
    
    def _start_positioned_game(self, game_name, game_function_name):
        """Start a game and position its window next to the progress window"""
        try:
            from snid_sage.snid import games
            
            # Get the game function
            game_func = getattr(games, game_function_name)
            
            # Update the game panel to show game status
            self._show_game_running_status(game_name)
            
            # Update progress if analysis controller is available
            if hasattr(self.gui, 'analysis_controller'):
                self.gui.analysis_controller._update_progress(f"🎮 Starting {game_name} game...")
            
            def run_positioned_game():
                try:
                    # Enlarge game window size (e.g., 1024x768) before starting
                    try:
                        # snid_sage.snid.games
                        games.DEBRIS_WIDTH = max(getattr(games, 'DEBRIS_WIDTH', 800), 1024)
                        games.DEBRIS_HEIGHT = max(getattr(games, 'DEBRIS_HEIGHT', 600), 768)
                    except Exception:
                        pass  # Safe fallback if attributes unavailable

                    # Start the game
                    game_func()
                    
                    # When game ends, restore game selection
                    self.gui.master.after(1000, lambda: self._on_game_ended(game_name))
                    
                except Exception as e:
                    print(f"Error running {game_name}: {e}")
                    if hasattr(self.gui, 'analysis_controller'):
                        error_msg = f"❌ {game_name} game error: {e}"
                        self.gui.master.after(100, lambda msg=error_msg: 
                            self.gui.analysis_controller._update_progress(msg))
                    self.gui.master.after(1000, lambda: self._show_integrated_games())
            
            # Start game in background thread
            self.game_thread = threading.Thread(target=run_positioned_game, daemon=True)
            self.game_thread.start()
            
        except Exception as e:
            if hasattr(self.gui, 'analysis_controller'):
                self.gui.analysis_controller._update_progress(f"❌ Could not start {game_name}: {e}")
    
    def _show_game_running_status(self, game_name):
        """Show game running status in the game panel"""
        if self.current_game_panel is None:
            return
        
        # Clear game selection
        for widget in self.current_game_panel.winfo_children():
            widget.destroy()
            
        # Game running header
        game_header = tk.Label(self.current_game_panel, text=f"🎮 {game_name} Running",
                             font=('Arial', 18, 'bold'),
                             bg='#2c3e50', fg='#27ae60')
        game_header.pack(pady=(30, 20))
        
        # Game window info
        info_frame = tk.Frame(self.current_game_panel, bg='#34495e', relief='raised', bd=2)
        info_frame.pack(fill='x', padx=30, pady=20)
        
        info_text = f"""
🎯 {game_name} is now running in a separate window!

🎮 Game Controls:
• Check the game window for specific controls
• Press ESC to exit most games
• Close the game window when done

📊 SNID Analysis:
• Analysis continues in the background
• Progress updates appear on the left
• You can play while waiting for results!

⚡ Having fun while science runs! ⚡
        """
        
        info_label = tk.Label(info_frame, text=info_text,
                            font=('Arial', 12),
                            bg='#34495e', fg='#ecf0f1',
                            justify='left', anchor='w')
        info_label.pack(padx=20, pady=15)
        
        # Back to selection button
        back_btn = tk.Button(self.current_game_panel, text="🔄 Choose Different Game",
                           font=('Arial', 13, 'bold'),
                           bg='#3498db', fg='white',
                           relief='flat', bd=0, padx=20, pady=10,
                           cursor='hand2',
                           command=self._show_integrated_games)
        back_btn.pack(pady=(20, 0))
        
        # Stop game button
        stop_btn = tk.Button(self.current_game_panel, text="🛑 Focus on Analysis Only",
                           font=('Arial', 12),
                           bg='#e74c3c', fg='white',
                           relief='flat', bd=0, padx=20, pady=8,
                           cursor='hand2',
                           command=self._focus_on_analysis)
        stop_btn.pack(pady=(10, 0))
    
    def _on_game_ended(self, game_name):
        """Handle when a game ends"""
        if hasattr(self.gui, 'analysis_controller'):
            self.gui.analysis_controller._update_progress(f"🎮 {game_name} game ended")
        
        # Check if the current game panel still exists before trying to access it
        if self.current_game_panel is not None:
            try:
                # Test if the widget still exists
                self.current_game_panel.winfo_exists()
                self._show_integrated_games()
            except (tk.TclError, AttributeError):
                # Widget has been destroyed, just clear the reference
                self.current_game_panel = None
    
    def _focus_on_analysis(self):
        """Hide games and focus on analysis"""
        if self.current_game_panel is None:
            return
            
        # Clear game panel and show focus message
        for widget in self.current_game_panel.winfo_children():
            widget.destroy()
            
        focus_header = tk.Label(self.current_game_panel, text="🔬 Focused on Analysis",
                              font=('Arial', 18, 'bold'),
                              bg='#2c3e50', fg='#3498db')
        focus_header.pack(pady=(50, 20))
        
        focus_text = """
📊 Analysis Focus Mode

✅ Games disabled for this session
✅ Full attention on SNID analysis  
✅ Faster processing (maybe!)

Watch the progress updates on the left
for real-time analysis status.

When analysis completes, you'll see
the results in the main window.
        """
        
        focus_label = tk.Label(self.current_game_panel, text=focus_text,
                             font=('Arial', 13),
                             bg='#2c3e50', fg='#ecf0f1',
                             justify='center')
        focus_label.pack(pady=20)
        
        # Re-enable games button
        enable_btn = tk.Button(self.current_game_panel, text="🎮 Re-enable Games",
                             font=('Arial', 12),
                             bg='#27ae60', fg='white',
                             relief='flat', bd=0, padx=20, pady=8,
                             cursor='hand2',
                             command=self._show_integrated_games)
        enable_btn.pack(pady=(30, 0))
        
        if hasattr(self.gui, 'analysis_controller'):
            self.gui.analysis_controller._update_progress("🔬 Games disabled - focusing on analysis") 
