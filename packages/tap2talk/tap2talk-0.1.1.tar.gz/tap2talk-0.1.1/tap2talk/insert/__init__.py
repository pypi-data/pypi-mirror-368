"""Text insertion module."""

import platform
from typing import Optional


def get_text_inserter(config=None):
    """Get platform-specific text inserter."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        from .mac import MacTextInserter
        return MacTextInserter(config)
    elif system == "Windows":
        from .win import WindowsTextInserter
        return WindowsTextInserter(config)
    else:
        # Fallback to clipboard-only inserter
        from .clipboard import ClipboardInserter
        return ClipboardInserter(config)