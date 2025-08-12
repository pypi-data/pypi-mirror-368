"""
Cross-platform window utilities and keyboard shortcuts provider.

This minimal module exists to provide `CrossPlatformWindowManager` so that
imports in GUI components resolve correctly. It centralizes platform-aware
keyboard shortcut strings and can be extended with additional windowing helpers.
"""

from __future__ import annotations

import platform
from typing import Dict


class CrossPlatformWindowManager:
    """Cross-platform helpers for GUI behavior.

    Currently provides keyboard shortcuts mapping with OS-aware modifiers.
    """

    @staticmethod
    def get_keyboard_shortcuts() -> Dict[str, str]:
        """Return a minimal set of keyboard shortcuts adjusted per OS.

        Returns a mapping used by dialogs to present shortcuts consistently.
        """
        is_mac = platform.system() == "Darwin"
        mod = "Cmd" if is_mac else "Ctrl"
        return {
            "quick_workflow": f"{mod}+Enter",
            "quit": f"{mod}+Q",
            "copy": f"{mod}+C",
            "paste": f"{mod}+V",
        }


