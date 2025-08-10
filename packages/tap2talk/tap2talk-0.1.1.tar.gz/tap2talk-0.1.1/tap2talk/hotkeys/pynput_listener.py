"""Cross-platform hotkey listener using pynput."""

import threading
from .base import HotkeyListener

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class PynputHotkeyListener(HotkeyListener):
    """Cross-platform hotkey listener using pynput."""
    
    def __init__(self, on_double_ctrl, on_double_esc, config):
        super().__init__(on_double_ctrl, on_double_esc, config)
        
        if not PYNPUT_AVAILABLE:
            raise ImportError("pynput not available. Install with: pip install pynput")
        
        self.listener = None
    
    def on_press(self, key):
        """Handle key press events."""
        try:
            # Check for Control key
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                if self.detect_double_press("ctrl"):
                    threading.Thread(target=self.on_double_ctrl, daemon=True).start()
            
            # Check for Escape key
            elif key == keyboard.Key.esc:
                if self.detect_double_press("esc"):
                    threading.Thread(target=self.on_double_esc, daemon=True).start()
        
        except Exception as e:
            print(f"Error handling key press: {e}")
    
    def start(self):
        """Start listening for hotkeys."""
        if self.running:
            return
        
        self.running = True
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
    
    def stop(self):
        """Stop listening for hotkeys."""
        if not self.running:
            return
        
        self.running = False
        
        if self.listener:
            self.listener.stop()
            self.listener = None