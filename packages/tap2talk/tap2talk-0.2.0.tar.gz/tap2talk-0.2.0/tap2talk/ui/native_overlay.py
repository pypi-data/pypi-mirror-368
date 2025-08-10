"""Native macOS overlay window that works with rumps."""

import time
import math
import threading
from AppKit import (
    NSWindow, NSView, NSTextField, NSColor, NSFont,
    NSBackingStoreBuffered, NSBorderlessWindowMask,
    NSFloatingWindowLevel, NSScreen, NSMakeRect,
    NSTextAlignmentCenter, NSTextAlignmentLeft,
    NSBezierPath, NSImageView, NSImage
)
from Foundation import NSRunLoop, NSDate, NSDefaultRunLoopMode
import objc


class StyledOverlayView(NSView):
    """Custom view with rounded corners and border."""
    
    def initWithFrame_(self, frame):
        self = objc.super(StyledOverlayView, self).initWithFrame_(frame)
        if self:
            self.backgroundColor = NSColor.colorWithRed_green_blue_alpha_(0.15, 0.15, 0.18, 0.95)
            self.borderColor = NSColor.colorWithRed_green_blue_alpha_(0.0, 0.8, 0.9, 1.0)  # Cyan
            self.cornerRadius = 12
            self.borderWidth = 2
        return self
    
    def drawRect_(self, rect):
        """Draw the custom view with rounded corners and border."""
        # Create rounded rectangle path
        path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            rect, self.cornerRadius, self.cornerRadius
        )
        
        # Fill background
        self.backgroundColor.setFill()
        path.fill()
        
        # Draw border
        self.borderColor.setStroke()
        path.setLineWidth_(self.borderWidth)
        path.stroke()


def create_icon(icon_type="mic", color=(0.0, 0.8, 0.9, 1.0)):
    """Create different icons for different states."""
    size = 24
    image = NSImage.alloc().initWithSize_((size, size))
    image.lockFocus()
    
    r, g, b, a = color
    icon_color = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
    
    if icon_type == "mic":
        # Draw microphone shape
        icon_color.setFill()
        
        # Mic body
        mic_rect = NSMakeRect(9, 10, 6, 10)
        mic_path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            mic_rect, 3, 3
        )
        mic_path.fill()
        
        # Mic stand arc
        icon_color.setStroke()
        stand_path = NSBezierPath.bezierPath()
        stand_path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
            (12, 10), 5, 180, 0, False
        )
        stand_path.setLineWidth_(1.5)
        stand_path.stroke()
        
        # Mic base
        base_path = NSBezierPath.bezierPath()
        base_path.moveToPoint_((12, 5))
        base_path.lineToPoint_((12, 2))
        base_path.moveToPoint_((8, 2))
        base_path.lineToPoint_((16, 2))
        base_path.setLineWidth_(1.5)
        base_path.stroke()
        
    elif icon_type == "processing":
        # Draw spinning dots
        icon_color.setFill()
        for angle in range(0, 360, 120):
            x = 12 + 6 * math.cos(math.radians(angle))
            y = 12 + 6 * math.sin(math.radians(angle))
            dot = NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(x - 2, y - 2, 4, 4)
            )
            dot.fill()
        
    elif icon_type == "done":
        # Draw checkmark
        icon_color.setStroke()
        check_path = NSBezierPath.bezierPath()
        check_path.setLineWidth_(2.5)
        check_path.setLineCapStyle_(1)  # Round cap
        check_path.moveToPoint_((6, 12))
        check_path.lineToPoint_((10, 8))
        check_path.lineToPoint_((18, 16))
        check_path.stroke()
    
    elif icon_type == "abort":
        # Draw X mark
        icon_color.setStroke()
        x_path = NSBezierPath.bezierPath()
        x_path.setLineWidth_(2.5)
        x_path.setLineCapStyle_(1)  # Round cap
        # First line of X
        x_path.moveToPoint_((7, 7))
        x_path.lineToPoint_((17, 17))
        # Second line of X
        x_path.moveToPoint_((17, 7))
        x_path.lineToPoint_((7, 17))
        x_path.stroke()
    
    elif icon_type == "error":
        # Draw exclamation mark
        icon_color.setFill()
        icon_color.setStroke()
        # Exclamation line
        exc_line = NSBezierPath.bezierPath()
        exc_line.setLineWidth_(3)
        exc_line.setLineCapStyle_(1)  # Round cap
        exc_line.moveToPoint_((12, 16))
        exc_line.lineToPoint_((12, 8))
        exc_line.stroke()
        # Exclamation dot
        dot = NSBezierPath.bezierPathWithOvalInRect_(
            NSMakeRect(10.5, 4, 3, 3)
        )
        dot.fill()
    
    image.unlockFocus()
    return image


class RumpsOverlayWindow:
    """Overlay window that works with rumps main thread."""
    
    def __init__(self):
        self.window = None
        self.custom_view = None
        self.icon_view = None
        self.text_field = None
        self.subtitle_field = None
        self.is_visible = False
        self.hide_timer = None
        self._error_message = "Error"
        self._create_window()
    
    def _create_window(self):
        """Create the overlay window."""
        # Get screen dimensions
        screen = NSScreen.mainScreen()
        if not screen:
            print("No screen found!")
            return
        
        screen_frame = screen.frame()
        
        # Window settings
        width = 220
        height = 65
        x = screen_frame.size.width - width - 25
        y = screen_frame.size.height - height - 55
        
        # Create window
        frame = NSMakeRect(x, y, width, height)
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSBorderlessWindowMask,
            NSBackingStoreBuffered,
            False
        )
        
        # Configure window
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setCollectionBehavior_(1 << 7)  # NSWindowCollectionBehaviorCanJoinAllSpaces
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setHasShadow_(True)
        self.window.setIgnoresMouseEvents_(True)
        
        # Create custom view
        self.custom_view = StyledOverlayView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))
        self.window.setContentView_(self.custom_view)
        
        # Create icon
        self.icon_view = NSImageView.alloc().initWithFrame_(NSMakeRect(15, 20, 24, 24))
        self.icon_view.setImage_(create_icon("mic", (0.0, 0.8, 0.9, 1.0)))
        self.custom_view.addSubview_(self.icon_view)
        
        # Create status text
        text_frame = NSMakeRect(50, 25, width - 65, 25)
        self.text_field = NSTextField.alloc().initWithFrame_(text_frame)
        self.text_field.setStringValue_("Ready")
        self.text_field.setBezeled_(False)
        self.text_field.setDrawsBackground_(False)
        self.text_field.setEditable_(False)
        self.text_field.setSelectable_(False)
        self.text_field.setAlignment_(NSTextAlignmentLeft)
        self.text_field.setFont_(NSFont.systemFontOfSize_weight_(16, 0.3))
        self.text_field.setTextColor_(NSColor.whiteColor())
        self.custom_view.addSubview_(self.text_field)
        
        # Create subtitle text
        subtitle_frame = NSMakeRect(50, 10, width - 65, 20)
        self.subtitle_field = NSTextField.alloc().initWithFrame_(subtitle_frame)
        self.subtitle_field.setStringValue_("Double-tap Ctrl to start")
        self.subtitle_field.setBezeled_(False)
        self.subtitle_field.setDrawsBackground_(False)
        self.subtitle_field.setEditable_(False)
        self.subtitle_field.setSelectable_(False)
        self.subtitle_field.setAlignment_(NSTextAlignmentLeft)
        self.subtitle_field.setFont_(NSFont.systemFontOfSize_(11))
        self.subtitle_field.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.7, 0.7, 0.7, 1.0))
        self.custom_view.addSubview_(self.subtitle_field)
        
        # Start hidden
        self.window.setAlphaValue_(0.0)
    
    def show_recording(self):
        """Show recording state."""
        self._update_state("Recording", "Listening...", "mic", 
                          (1.0, 0.3, 0.3, 1.0), (1.0, 0.3, 0.3, 1.0))
        self._show()
    
    def show_processing(self):
        """Show processing state."""
        self._update_state("Processing", "Transcribing audio...", "processing",
                          (0.3, 0.5, 1.0, 1.0), (0.3, 0.5, 1.0, 1.0))
        self._show()
    
    def show_done(self):
        """Show done state."""
        self._update_state("Done", "Text inserted", "done",
                          (0.3, 0.9, 0.4, 1.0), (0.3, 0.9, 0.4, 1.0))
        self._show()
        # Auto-hide after 2 seconds
        self._schedule_hide()
    
    def show_aborted(self):
        """Show aborted state."""
        self._update_state("Aborted", "Recording cancelled", "abort",
                          (0.8, 0.3, 0.3, 1.0), (0.8, 0.3, 0.3, 1.0))
        self._show()
        # Auto-hide after 2 seconds
        self._schedule_hide()
    
    def show_error(self, message="Error"):
        """Show error state."""
        self._update_state("Error", message, "error",
                          (1.0, 0.5, 0.3, 1.0), (1.0, 0.5, 0.3, 1.0))
        self._show()
        # Auto-hide after 2 seconds
        self._schedule_hide()
    
    def _schedule_hide(self):
        """Schedule hide after 2 seconds."""
        # Cancel any existing timer
        if self.hide_timer:
            self.hide_timer.cancel()
        
        # Create new timer
        import threading
        self.hide_timer = threading.Timer(2.0, self._delayed_hide)
        self.hide_timer.start()
    
    def _dispatch_to_main(self, func):
        """Dispatch a function to the main thread."""
        from Foundation import NSThread
        
        # Check if we're already on main thread
        if NSThread.isMainThread():
            func()
        else:
            # Use rumps.Timer with 0 delay to run on main thread
            import rumps
            timer = rumps.Timer(lambda _: func(), 0.001)
            timer.start()
    
    def _delayed_hide(self):
        """Hide the window (called from timer thread)."""
        # We need to make this work from a background thread
        # Let's use a different approach - dispatch_sync to main queue
        from PyObjCTools import AppHelper
        AppHelper.callAfter(self.hide)
    
    def _update_state(self, title, subtitle, icon_type, icon_color, border_color):
        """Update the overlay state."""
        # Update text
        self.text_field.setStringValue_(title)
        self.subtitle_field.setStringValue_(subtitle)
        
        # Update icon
        self.icon_view.setImage_(create_icon(icon_type, icon_color))
        
        # Update border color
        r, g, b, a = border_color
        self.custom_view.borderColor = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
        self.custom_view.setNeedsDisplay_(True)
    
    def _show(self):
        """Show the overlay window."""
        if not self.is_visible:
            self.window.setAlphaValue_(0.85)
            self.window.makeKeyAndOrderFront_(None)
            self.window.orderFrontRegardless()
            self.is_visible = True
    
    def hide(self):
        """Hide the overlay window."""
        if self.is_visible:
            self.window.setAlphaValue_(0.0)
            self.window.orderOut_(None)
            self.is_visible = False