"""macOS hotkey listener using Quartz event tap."""

import threading
import time
from .base import HotkeyListener

try:
    from Quartz import (
        CGEventTapCreate, CGEventTapEnable, 
        kCGEventFlagsChanged, kCGEventKeyDown,
        kCGSessionEventTap, kCGHeadInsertEventTap,
        kCGEventTapOptionDefault, CGEventGetFlags,
        CGEventGetIntegerValueField, kCGKeyboardEventKeycode,
        CFRunLoopRun, CFRunLoopStop, CFRunLoopGetCurrent,
        kCGEventFlagMaskControl, kCGEventFlagMaskCommand,
        kCGEventFlagMaskAlternate, kCGEventFlagMaskShift,
        kCGEventTapDisabledByTimeout, kCGEventTapDisabledByUserInput
    )
    from ApplicationServices import AXIsProcessTrustedWithOptions
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False


class MacHotkeyListener(HotkeyListener):
    """macOS-specific hotkey listener using Quartz event tap."""
    
    def __init__(self, on_double_ctrl, on_double_esc, config):
        super().__init__(on_double_ctrl, on_double_esc, config)
        
        if not QUARTZ_AVAILABLE:
            raise ImportError("PyObjC not available. Install with: pip install pyobjc-framework-Quartz")
        
        self.tap = None
        self.run_loop = None
        self.thread = None
        
        # Track modifier state
        self.ctrl_pressed = False
        self.last_flags = 0
    
    def check_accessibility(self):
        """Check if accessibility permissions are granted."""
        options = {b'kAXTrustedCheckOptionPrompt': True}
        return AXIsProcessTrustedWithOptions(options)
    
    def event_callback(self, proxy, event_type, event, refcon):
        """Callback for Quartz event tap."""
        try:
            # Re-enable tap if it gets disabled (macOS does this automatically sometimes)
            if event_type == kCGEventTapDisabledByTimeout or event_type == kCGEventTapDisabledByUserInput:
                if self.tap:
                    CGEventTapEnable(self.tap, True)
                return event
            
            if event_type == kCGEventFlagsChanged:
                # Get current flags
                flags = CGEventGetFlags(event)
                
                # Check for control key changes
                ctrl_now = bool(flags & kCGEventFlagMaskControl)
                ctrl_before = bool(self.last_flags & kCGEventFlagMaskControl)
                
                # Only detect KEY DOWN (transition from not pressed to pressed)
                # Ignore KEY UP (transition from pressed to not pressed)
                if ctrl_now and not ctrl_before:
                    # This is a key down event
                    print(f"Ctrl DOWN detected")
                    if self.detect_double_press("ctrl"):
                        print("Double Ctrl detected!")
                        # Call handler in separate thread to avoid blocking
                        threading.Thread(target=self.on_double_ctrl, daemon=True).start()
                
                # Update last flags AFTER processing
                self.last_flags = flags
                
            elif event_type == kCGEventKeyDown:
                # Get keycode
                keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                
                # ESC key is keycode 53
                if keycode == 53:
                    print(f"ESC DOWN detected")
                    if self.detect_double_press("esc"):
                        print("Double ESC detected!")
                        # Call handler in separate thread
                        threading.Thread(target=self.on_double_esc, daemon=True).start()
        
        except Exception as e:
            print(f"Error in event callback: {e}")
        
        return event
    
    def run_event_loop(self):
        """Run the event loop in a separate thread."""
        try:
            # Create event tap
            event_mask = (1 << kCGEventFlagsChanged) | (1 << kCGEventKeyDown)
            
            self.tap = CGEventTapCreate(
                kCGSessionEventTap,
                kCGHeadInsertEventTap,
                kCGEventTapOptionDefault,
                event_mask,
                self.event_callback,
                None
            )
            
            if not self.tap:
                print("Failed to create event tap")
                return
            
            # Enable the tap
            CGEventTapEnable(self.tap, True)
            
            # Get current run loop
            self.run_loop = CFRunLoopGetCurrent()
            
            # Add tap to run loop
            from Quartz import CFMachPortCreateRunLoopSource, CFRunLoopAddSource, kCFRunLoopDefaultMode
            source = CFMachPortCreateRunLoopSource(None, self.tap, 0)
            CFRunLoopAddSource(self.run_loop, source, kCFRunLoopDefaultMode)
            
            # Run the loop
            self.running = True
            CFRunLoopRun()
            
        except Exception as e:
            print(f"Error in event loop: {e}")
        finally:
            self.running = False
    
    def start(self):
        """Start listening for hotkeys."""
        if self.running:
            return
        
        # Check accessibility permissions
        if not self.check_accessibility():
            print("Accessibility permissions required. Please grant access in System Preferences.")
            # Continue anyway, macOS will prompt
        
        # Start event loop in separate thread
        self.thread = threading.Thread(target=self.run_event_loop, daemon=True)
        self.thread.start()
        
        # Wait for startup
        time.sleep(0.1)
    
    def stop(self):
        """Stop listening for hotkeys."""
        if not self.running:
            return
        
        self.running = False
        
        # Stop the run loop
        if self.run_loop:
            CFRunLoopStop(self.run_loop)
        
        # Disable tap
        if self.tap:
            CGEventTapEnable(self.tap, False)
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)