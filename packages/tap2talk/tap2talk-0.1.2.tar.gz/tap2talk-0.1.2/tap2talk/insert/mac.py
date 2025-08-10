"""macOS text insertion using Quartz and fallback methods."""

import time
import subprocess
from .clipboard import ClipboardManager

try:
    from Quartz import (
        CGEventCreateKeyboardEvent, CGEventPost,
        CGEventSetUnicodeString, kCGHIDEventTap,
        CGEventCreateWithEventSource, CGEventSourceCreate,
        kCGEventSourceStateHIDSystemState, CGEventKeyboardSetUnicodeString
    )
    from CoreGraphics import kCGEventKeyDown, kCGEventKeyUp
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False


class MacTextInserter:
    """macOS-specific text inserter with direct injection and clipboard fallback."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.clipboard = ClipboardManager()
    
    def insert_text(self, text: str) -> bool:
        """Insert text at current cursor position."""
        # Try direct injection first
        if QUARTZ_AVAILABLE:
            if self._inject_unicode(text):
                return True
        
        # Fallback to clipboard method
        return self._insert_via_clipboard(text)
    
    def _inject_unicode(self, text: str) -> bool:
        """Directly inject Unicode text using Quartz events."""
        try:
            # Create event source
            source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
            
            # Split text into manageable chunks (Quartz has limits)
            chunk_size = 20  # Characters per event
            
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                
                # Create keyboard event
                event = CGEventCreateKeyboardEvent(source, 0, True)
                
                # Set Unicode string
                CGEventKeyboardSetUnicodeString(event, len(chunk), chunk)
                
                # Post event
                CGEventPost(kCGHIDEventTap, event)
                
                # Small delay between chunks
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            print(f"Direct injection failed: {e}")
            return False
    
    def _insert_via_clipboard(self, text: str) -> bool:
        """Insert text using clipboard and paste."""
        try:
            # Preserve clipboard
            self.clipboard.preserve()
            
            # Set text
            self.clipboard.set_text(text)
            
            # Trigger paste using AppleScript
            self._trigger_paste_applescript()
            
            # Wait for paste
            time.sleep(0.1)
            
            # Restore clipboard
            self.clipboard.restore()
            
            return True
            
        except Exception as e:
            print(f"Clipboard insertion failed: {e}")
            return False
    
    def _trigger_paste_applescript(self):
        """Trigger paste using AppleScript."""
        script = 'tell application "System Events" to keystroke "v" using command down'
        subprocess.run(['osascript', '-e', script], check=True)
    
    def _trigger_paste_quartz(self):
        """Trigger Cmd+V using Quartz events."""
        if not QUARTZ_AVAILABLE:
            return False
        
        try:
            source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
            
            # Key codes
            CMD_KEY = 55
            V_KEY = 9
            
            # Press Cmd
            cmd_down = CGEventCreateKeyboardEvent(source, CMD_KEY, True)
            CGEventPost(kCGHIDEventTap, cmd_down)
            
            # Press V
            v_down = CGEventCreateKeyboardEvent(source, V_KEY, True)
            CGEventSetFlags(v_down, kCGEventFlagMaskCommand)
            CGEventPost(kCGHIDEventTap, v_down)
            
            # Release V
            v_up = CGEventCreateKeyboardEvent(source, V_KEY, False)
            CGEventSetFlags(v_up, kCGEventFlagMaskCommand)
            CGEventPost(kCGHIDEventTap, v_up)
            
            # Release Cmd
            cmd_up = CGEventCreateKeyboardEvent(source, CMD_KEY, False)
            CGEventPost(kCGHIDEventTap, cmd_up)
            
            return True
            
        except Exception as e:
            print(f"Quartz paste failed: {e}")
            return False