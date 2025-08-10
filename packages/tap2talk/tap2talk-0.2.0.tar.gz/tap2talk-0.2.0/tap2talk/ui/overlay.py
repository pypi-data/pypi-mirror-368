"""Overlay using native window with fallback to notifications."""

import rumps
import threading
import time
import sys


class Overlay:
    """Overlay using native window for macOS, notifications as fallback."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.tray_app = None
        self.current_status = "Idle"
        self.native_overlay = None
        
        # Try to create native overlay window on macOS
        if sys.platform == 'darwin':
            try:
                from .native_overlay import RumpsOverlayWindow
                self.native_overlay = RumpsOverlayWindow()
                print("Native overlay window initialized for main app")
            except Exception as e:
                print(f"Could not create native overlay: {e}")
                self.native_overlay = None
        
    def _update_tray_title(self, status: str):
        """Update the tray icon title for visual feedback."""
        if self.tray_app:
            # This is thread-safe with rumps
            self.tray_app.title = status
            if hasattr(self.tray_app, 'status_item'):
                self.tray_app.status_item.title = f"Status: {status}"
    
    def _show_notification(self, title: str, message: str = ""):
        """Show a macOS notification."""
        try:
            # rumps notifications are thread-safe
            rumps.notification(
                title="Tap2Talk",
                subtitle=title,
                message=message,
                sound=False
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def show_recording(self):
        """Show recording status."""
        print("Recording started")
        self._update_tray_title("⏺ REC")
        if self.native_overlay:
            # Dispatch to main thread using AppHelper
            from PyObjCTools import AppHelper
            AppHelper.callAfter(self.native_overlay.show_recording)
        else:
            self._show_notification("Recording", "Speak now...")
        self.current_status = "Recording"
    
    def show_processing(self):
        """Show processing status."""
        print("Processing audio")
        self._update_tray_title("⏳ PROC")
        if self.native_overlay:
            from PyObjCTools import AppHelper
            AppHelper.callAfter(self.native_overlay.show_processing)
        else:
            self._show_notification("Processing", "Transcribing audio...")
        self.current_status = "Processing"
    
    def show_done(self):
        """Show completion status."""
        print("Done")
        self._update_tray_title("✓ DONE")
        if self.native_overlay:
            from PyObjCTools import AppHelper
            AppHelper.callAfter(self.native_overlay.show_done)
        else:
            self._show_notification("Done", "Text inserted successfully")
        self.current_status = "Done"
        
        # Reset tray title after delay
        def reset():
            time.sleep(2)
            self._update_tray_title("Tap2Talk")
            self.current_status = "Idle"
        threading.Thread(target=reset, daemon=True).start()
    
    def show_aborted(self):
        """Show abort status."""
        print("Aborted")
        self._update_tray_title("✗ STOP")
        if self.native_overlay:
            from PyObjCTools import AppHelper
            AppHelper.callAfter(self.native_overlay.show_aborted)
        else:
            self._show_notification("Aborted", "Operation cancelled")
        self.current_status = "Aborted"
        
        # Reset tray title after delay
        def reset():
            time.sleep(2)
            self._update_tray_title("Tap2Talk")
            self.current_status = "Idle"
        threading.Thread(target=reset, daemon=True).start()
    
    def show_error(self, message: str = "Error"):
        """Show error status."""
        print(f"Error: {message}")
        self._update_tray_title("⚠ ERR")
        if self.native_overlay:
            from PyObjCTools import AppHelper
            AppHelper.callAfter(lambda: self.native_overlay.show_error(message))
        else:
            self._show_notification("Error", message)
        self.current_status = "Error"
        
        # Reset tray title after delay
        def reset():
            time.sleep(2)
            self._update_tray_title("Tap2Talk")
            self.current_status = "Idle"
        threading.Thread(target=reset, daemon=True).start()
    
    def start(self):
        """Start the overlay."""
        pass
    
    def stop(self):
        """Stop the overlay."""
        pass