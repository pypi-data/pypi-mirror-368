"""Base class for hotkey listeners."""

import time
import threading
from abc import ABC, abstractmethod
from typing import Callable, Optional


class HotkeyListener(ABC):
    """Base class for platform-specific hotkey listeners."""
    
    def __init__(self, on_double_ctrl: Callable, on_double_esc: Callable, config):
        self.on_double_ctrl = on_double_ctrl
        self.on_double_esc = on_double_esc
        self.config = config
        
        # Double press detection
        self.threshold_ms = config.get("double_press_threshold_ms", 400)
        self.debounce_ms = 150  # Prevent holding key from triggering
        
        # Tracking for double press
        self.ctrl_last_press = 0
        self.ctrl_press_count = 0
        self.esc_last_press = 0
        self.esc_press_count = 0
        
        # Thread safety
        self.lock = threading.Lock()
        self.running = False
    
    def detect_double_press(self, key_type: str) -> bool:
        """Detect double press for a key type."""
        current_time = time.time() * 1000  # Convert to milliseconds
        
        with self.lock:
            if key_type == "ctrl":
                time_diff = current_time - self.ctrl_last_press
                
                if time_diff < self.threshold_ms:
                    self.ctrl_press_count += 1
                    if self.ctrl_press_count == 2:
                        self.ctrl_press_count = 0
                        self.ctrl_last_press = 0
                        return True
                else:
                    self.ctrl_press_count = 1
                    self.ctrl_last_press = current_time
                    
            elif key_type == "esc":
                time_diff = current_time - self.esc_last_press
                
                if time_diff < self.threshold_ms:
                    self.esc_press_count += 1
                    if self.esc_press_count == 2:
                        self.esc_press_count = 0
                        self.esc_last_press = 0
                        return True
                else:
                    self.esc_press_count = 1
                    self.esc_last_press = current_time
        
        return False
    
    def reset_counters(self):
        """Reset all press counters."""
        with self.lock:
            self.ctrl_press_count = 0
            self.ctrl_last_press = 0
            self.esc_press_count = 0
            self.esc_last_press = 0
    
    @abstractmethod
    def start(self):
        """Start listening for hotkeys."""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop listening for hotkeys."""
        pass