"""System tray icon for tap2talk using rumps."""

import rumps
import sys


def create_menu_bar_icon():
    """Create a small icon for the menu bar."""
    from AppKit import NSImage, NSColor, NSBezierPath, NSMakeRect
    
    # Menu bar icons should be 22x22 points (44x44 pixels for retina)
    size = 22
    image = NSImage.alloc().initWithSize_((size, size))
    image.setTemplate_(True)  # Make it a template image (adapts to dark/light mode)
    image.lockFocus()
    
    # Draw a simple microphone icon
    mic_color = NSColor.blackColor()  # Template images use black, system will adapt
    mic_color.setFill()
    mic_color.setStroke()
    
    # Mic body (centered, smaller)
    mic_body = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
        NSMakeRect(8, 6, 6, 10),
        3, 3
    )
    mic_body.fill()
    
    # Mic stand arc
    stand_path = NSBezierPath.bezierPath()
    stand_path.setLineWidth_(1.5)
    stand_path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
        (11, 11), 5, 180, 0, False
    )
    stand_path.stroke()
    
    # Mic base
    base_path = NSBezierPath.bezierPath()
    base_path.setLineWidth_(1.5)
    base_path.moveToPoint_((11, 6))
    base_path.lineToPoint_((11, 3))
    base_path.moveToPoint_((8, 3))
    base_path.lineToPoint_((14, 3))
    base_path.stroke()
    
    image.unlockFocus()
    return image


class TrayIcon(rumps.App):
    """System tray icon with menu using rumps."""

    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.native_overlay = None

        # Initialize rumps App
        super().__init__(
            "Tap2Talk",
            icon=None,  # We'll use text only in menu bar for now
            quit_button=None  # We'll handle quit ourselves
        )

        # Create menu items
        self.status_item = rumps.MenuItem("Status: Idle")

        # Set up menu
        self.menu = [
            rumps.MenuItem("Tap2Talk v0.1.0", callback=None),
            rumps.separator,
            self.status_item,
            rumps.separator,
            rumps.MenuItem("Test Overlay", callback=self.on_test_overlay),
            rumps.separator,
            rumps.MenuItem("About", callback=self.on_about),
            rumps.MenuItem("Restart", callback=self.on_restart),
            rumps.MenuItem("Exit", callback=self.on_exit)
        ]

    def update_status(self, status: str):
        """Update the status menu item."""
        self.status_item.title = f"Status: {status}"

    @rumps.clicked("Test Overlay")
    def on_test_overlay(self, sender):
        """Test the overlay window."""
        print("Testing native overlay...")

        # Create native overlay if not exists
        if not self.native_overlay:
            from .native_overlay import RumpsOverlayWindow
            self.native_overlay = RumpsOverlayWindow()
            print("Native overlay created")

        # Show recording immediately (we're on main thread from menu click)
        print("Showing recording...")
        self.native_overlay.show_recording()

        # Use NSTimer for actual delays
        from Foundation import NSTimer, NSRunLoop, NSDefaultRunLoopMode
        import objc
        
        # Create blocks for the timer callbacks (they need to accept timer argument)
        def show_processing(timer):
            print("Showing processing...")
            self.native_overlay.show_processing()
            
            # Schedule done after another 2 seconds
            def show_done(timer):
                print("Showing done...")
                self.native_overlay.show_done()
                
                # Schedule abort after another 3 seconds
                def show_abort(timer):
                    print("Showing abort...")
                    self.native_overlay.show_aborted()
                    
                    # Schedule error after another 3 seconds
                    def show_error(timer):
                        print("Showing error...")
                        self.native_overlay.show_error("Transcription failed")
                        print("Test sequence complete!")
                    
                    NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
                        3.0, False, show_error
                    )
                
                NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
                    3.0, False, show_abort
                )
            
            # Schedule the done timer
            NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
                2.0, False, show_done
            )
        
        # Schedule the processing timer
        NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
            2.0, False, show_processing
        )

    @rumps.clicked("About")
    def on_about(self, sender):
        """Handle About menu item."""
        rumps.alert(
            title="Tap2Talk",
            message="Voice transcription desktop app\n\nVersion: 0.1.0\n\nDouble-tap Ctrl to start/stop recording\nDouble-tap Esc to abort",
            ok="OK"
        )

    @rumps.clicked("Restart")
    def on_restart(self, sender):
        """Handle Restart menu item."""
        self.app_controller.restart()

    @rumps.clicked("Exit")
    def on_exit(self, sender):
        """Handle Exit menu item."""
        self.app_controller.quit()
        rumps.quit_application()

    def run(self):
        """Run the tray icon."""
        # Start components before running
        if hasattr(self.app_controller, 'hotkey_listener'):
            self.app_controller.hotkey_listener.start()

        # rumps.App.run() starts the event loop
        super().run()

    def stop(self):
        """Stop the tray icon."""
        rumps.quit_application()
