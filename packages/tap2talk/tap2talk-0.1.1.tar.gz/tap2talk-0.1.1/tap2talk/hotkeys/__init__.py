"""Hotkey detection module."""

import platform
from typing import Optional

def get_hotkey_listener(on_double_ctrl, on_double_esc, config):
    """Get platform-specific hotkey listener."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        from .mac import MacHotkeyListener
        return MacHotkeyListener(on_double_ctrl, on_double_esc, config)
    elif system == "Windows":
        from .win import WindowsHotkeyListener
        return WindowsHotkeyListener(on_double_ctrl, on_double_esc, config)
    else:
        # Fallback to pynput for Linux or other systems
        from .pynput_listener import PynputHotkeyListener
        return PynputHotkeyListener(on_double_ctrl, on_double_esc, config)