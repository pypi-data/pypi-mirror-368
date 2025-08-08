"""
Twemoji Manager for SNID SAGE GUI
=================================

This module provides Twemoji icon integration for consistent emoji rendering
across all platforms, especially fixing the emoji display issues on Linux.

Features:
- Automatic Twemoji asset management
- SVG to QIcon conversion
- Emoji Unicode to filename mapping
- Caching for performance
- Fallback to text emojis if icons unavailable

Usage:
    manager = TwemojiManager()
    icon = manager.get_icon("⚙️")  # Returns QIcon
    manager.set_button_icon(button, "⚙️")  # Sets icon on button

Developed by Fiorenzo Stoppa for SNID SAGE
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Union, Tuple
from urllib.request import urlretrieve
from urllib.error import URLError

# PySide6 imports
try:
    from PySide6 import QtWidgets, QtGui, QtCore, QtSvg
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

# Logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.twemoji')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.twemoji')


class TwemojiManager:
    """
    Manager for Twemoji icons in PySide6 applications.
    
    This class handles downloading, caching, and converting Twemoji SVG icons
    to QIcons for use in Qt applications, providing consistent emoji rendering
    across all platforms.
    """
    
    # Twemoji CDN base URL for SVG icons
    TWEMOJI_CDN_BASE = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/"
    
    # Common emojis used in SNID SAGE with their Unicode codepoints
    # Note: Some emojis don't use variation selectors in Twemoji filenames
    EMOJI_MAPPING = {
        # Main export/data buttons
        "📊": "1f4ca",          # Bar Chart/Export Data/Charts
        "💾": "1f4be",          # Floppy Disk/Save
        "🔍": "1f50d",          # Magnifying Glass/Search
        "📈": "1f4c8",          # Chart Up/Export Plot
        "📉": "1f4c9",          # Chart Down  
        "📋": "1f4cb",          # Clipboard/Copy
        
        # Utility buttons for dialogs  
        "🛰️": "1f6f0",         # Satellite/Space (no fe0f in Twemoji)
        "👁️": "1f441",          # Eye/Hide (no fe0f in Twemoji)
        "🗑️": "1f5d1",          # Wastebasket/Remove (no fe0f in Twemoji)
        "⭐": "2b50",           # Star
        "🤖": "1f916",          # Robot/AI
        "⚠️": "26a0",           # Warning (no fe0f in Twemoji)
        "❌": "274c",           # Cross Mark/Error
        "✅": "2705",           # Check Mark/Success
        
        # Analysis results buttons
        "📋": "1f4cb",          # Clipboard/Summary Report
        "🎯": "1f3af",          # Target/GMM Clustering
        "🍰": "1f370",          # Shortcake/Pie Chart
        "🎨": "1f3a8",          # Artist Palette
    }
    
    def __init__(self, cache_dir: Optional[Path] = None, icon_size: int = 16):
        """
        Initialize the Twemoji manager.
        
        Args:
            cache_dir: Directory to cache downloaded icons (defaults to user cache)
            icon_size: Size in pixels for the icons (default 16 for buttons)
        """
        self.icon_size = icon_size
        self.cache: Dict[str, QtGui.QIcon] = {}
        
        # Set up cache directory
        if cache_dir is None:
            # Use platform-appropriate cache directory
            if sys.platform == "win32":
                cache_base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            else:
                cache_base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
            
            self.cache_dir = cache_base / "snid_sage" / "twemoji"
        else:
            self.cache_dir = Path(cache_dir)
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        _LOGGER.info(f"TwemojiManager initialized with cache at: {self.cache_dir}")
    
    def _get_unicode_codepoint(self, emoji: str) -> Optional[str]:
        """
        Get the Unicode codepoint for an emoji.
        
        Args:
            emoji: The emoji character
            
        Returns:
            Unicode codepoint string or None if not found
        """
        # Check our predefined mapping first
        if emoji in self.EMOJI_MAPPING:
            return self.EMOJI_MAPPING[emoji]
        
        # For other emojis, convert to Unicode codepoint
        try:
            # Convert emoji to Unicode codepoints
            codepoints = []
            for char in emoji:
                cp = ord(char)
                if cp != 0xfe0f:  # Skip variation selector
                    codepoints.append(f"{cp:x}")
            
            if codepoints:
                result = "-".join(codepoints)
                _LOGGER.debug(f"Converted emoji '{emoji}' to codepoint: {result}")
                return result
        except Exception as e:
            _LOGGER.warning(f"Failed to convert emoji '{emoji}' to codepoint: {e}")
        
        return None
    
    def _download_icon(self, emoji: str, codepoint: str) -> Optional[Path]:
        """
        Download a Twemoji SVG icon if not cached.
        
        Args:
            emoji: The emoji character  
            codepoint: Unicode codepoint string
            
        Returns:
            Path to the downloaded SVG file or None if failed
        """
        # Check if already cached
        cache_file = self.cache_dir / f"{codepoint}.svg"
        if cache_file.exists():
            return cache_file
        
        # Download from Twemoji CDN
        url = f"{self.TWEMOJI_CDN_BASE}{codepoint}.svg"
        
        try:
            _LOGGER.info(f"Downloading Twemoji icon for '{emoji}' from: {url}")
            urlretrieve(url, cache_file)
            return cache_file
        except URLError as e:
            _LOGGER.warning(f"Failed to download Twemoji icon for '{emoji}': {e}")
            return None
        except Exception as e:
            _LOGGER.error(f"Unexpected error downloading icon for '{emoji}': {e}")
            return None
    
    def get_icon(self, emoji: str) -> Optional[QtGui.QIcon]:
        """
        Get a QIcon for the specified emoji.
        
        Args:
            emoji: The emoji character
            
        Returns:
            QIcon object or None if unavailable
        """
        if not PYSIDE6_AVAILABLE:
            _LOGGER.warning("PySide6 not available, cannot create QIcon")
            return None
        
        # Check cache first
        if emoji in self.cache:
            return self.cache[emoji]
        
        # Get Unicode codepoint
        codepoint = self._get_unicode_codepoint(emoji)
        if not codepoint:
            _LOGGER.warning(f"No codepoint mapping found for emoji: {emoji}")
            return None
        
        # Download icon if needed
        svg_path = self._download_icon(emoji, codepoint)
        if not svg_path or not svg_path.exists():
            _LOGGER.warning(f"Failed to get SVG file for emoji: {emoji}")
            return None
        
        try:
            # Create QIcon from SVG
            icon = QtGui.QIcon(str(svg_path))
            
            # Cache the icon
            self.cache[emoji] = icon
            
            _LOGGER.debug(f"Created QIcon for emoji: {emoji}")
            return icon
        
        except Exception as e:
            _LOGGER.error(f"Failed to create QIcon for emoji '{emoji}': {e}")
            return None
    
    def set_button_icon(self, button: QtWidgets.QPushButton, emoji: str, keep_text: bool = True) -> bool:
        """
        Set a Twemoji icon on a QPushButton.
        
        Args:
            button: The QPushButton to modify
            emoji: The emoji character
            keep_text: Whether to keep the text after the emoji (default True)
            
        Returns:
            True if icon was set successfully, False otherwise
        """
        if not PYSIDE6_AVAILABLE:
            return False
        
        icon = self.get_icon(emoji)
        if not icon:
            _LOGGER.warning(f"Could not get icon for emoji '{emoji}', keeping text")
            return False
        
        try:
            # Set the icon
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(self.icon_size, self.icon_size))
            
            if keep_text:
                # Remove emoji from text but keep the rest
                current_text = button.text()
                if current_text.startswith(emoji):
                    new_text = current_text[len(emoji):].strip()
                    button.setText(new_text)
            else:
                # Remove all text
                button.setText("")
            
            _LOGGER.debug(f"Set Twemoji icon for '{emoji}' on button")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Failed to set icon on button for emoji '{emoji}': {e}")
            return False
    
    def convert_all_buttons(self, widget: QtWidgets.QWidget) -> int:
        """
        Convert all buttons in a widget hierarchy to use Twemoji icons.
        
        Args:
            widget: Root widget to search for buttons
            
        Returns:
            Number of buttons converted
        """
        converted = 0
        
        # Find all QPushButton widgets recursively
        buttons = widget.findChildren(QtWidgets.QPushButton)
        
        for button in buttons:
            text = button.text()
            if not text:
                continue
            
            # Check if button text starts with any known emoji
            for emoji in self.EMOJI_MAPPING.keys():
                if text.startswith(emoji):
                    if self.set_button_icon(button, emoji, keep_text=True):
                        converted += 1
                    break
        
        _LOGGER.info(f"Converted {converted} buttons to use Twemoji icons")
        return converted
    
    def preload_common_icons(self) -> int:
        """
        Preload all common SNID SAGE emoji icons for better performance.
        
        Returns:
            Number of icons successfully preloaded
        """
        loaded = 0
        
        for emoji in self.EMOJI_MAPPING.keys():
            if self.get_icon(emoji):
                loaded += 1
        
        _LOGGER.info(f"Preloaded {loaded}/{len(self.EMOJI_MAPPING)} Twemoji icons")
        return loaded
    
    def clear_cache(self) -> None:
        """Clear the in-memory icon cache."""
        self.cache.clear()
        _LOGGER.info("Cleared Twemoji icon cache")
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Twemoji manager can be used (PySide6 available)."""
        return PYSIDE6_AVAILABLE


# Global instance for convenience
_TWEMOJI_MANAGER: Optional[TwemojiManager] = None

def get_twemoji_manager(icon_size: int = 16) -> Optional[TwemojiManager]:
    """
    Get the global TwemojiManager instance.
    
    Args:
        icon_size: Size for icons (only used on first call)
        
    Returns:
        TwemojiManager instance or None if PySide6 unavailable
    """
    global _TWEMOJI_MANAGER
    
    if not TwemojiManager.is_available():
        return None
    
    if _TWEMOJI_MANAGER is None:
        _TWEMOJI_MANAGER = TwemojiManager(icon_size=icon_size)
    
    return _TWEMOJI_MANAGER

def convert_button_to_twemoji(button: QtWidgets.QPushButton, emoji: str) -> bool:
    """
    Convenience function to convert a single button to use Twemoji.
    
    Args:
        button: The button to convert
        emoji: The emoji character
        
    Returns:
        True if conversion was successful
    """
    manager = get_twemoji_manager()
    if manager:
        return manager.set_button_icon(button, emoji)
    return False 