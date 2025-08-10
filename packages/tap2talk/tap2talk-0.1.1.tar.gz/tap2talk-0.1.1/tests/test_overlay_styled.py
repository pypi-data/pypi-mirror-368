#!/usr/bin/env python3
"""Beautifully styled overlay window with animations."""

import time
import sys
import math
from AppKit import (
    NSApplication, NSWindow, NSView, NSTextField, NSColor, NSFont,
    NSBackingStoreBuffered, NSBorderlessWindowMask,
    NSFloatingWindowLevel, NSScreen, NSMakeRect,
    NSTextAlignmentCenter, NSTextAlignmentLeft, NSApplicationActivationPolicyAccessory,
    NSBezierPath, NSImageView, NSImage, NSGraphicsContext,
    NSCompositingOperationSourceOver, NSAffineTransform
)
from Foundation import NSRunLoop, NSDate, NSDefaultRunLoopMode, NSTimer
from Quartz import CGPathCreateWithRoundedRect, CGRectMake
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
    # Create an image for the icon
    size = 24
    image = NSImage.alloc().initWithSize_((size, size))
    image.lockFocus()
    
    # Set color
    r, g, b, a = color
    icon_color = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
    
    if icon_type == "mic":
        # Draw microphone shape (corrected orientation)
        icon_color.setFill()
        
        # Mic body (rounded rectangle) - positioned higher
        mic_rect = NSMakeRect(9, 10, 6, 10)
        mic_path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            mic_rect, 3, 3
        )
        mic_path.fill()
        
        # Mic stand arc - below the mic
        icon_color.setStroke()
        stand_path = NSBezierPath.bezierPath()
        stand_path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
            (12, 10), 5, 180, 0, False
        )
        stand_path.setLineWidth_(1.5)
        stand_path.stroke()
        
        # Mic base line
        base_path = NSBezierPath.bezierPath()
        base_path.moveToPoint_((12, 5))
        base_path.lineToPoint_((12, 2))
        base_path.moveToPoint_((8, 2))
        base_path.lineToPoint_((16, 2))
        base_path.setLineWidth_(1.5)
        base_path.stroke()
        
    elif icon_type == "processing":
        # Draw spinning dots/gear icon
        icon_color.setFill()
        # Draw three dots in a triangle pattern
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
    
    image.unlockFocus()
    return image


def test_styled_window():
    """Test creating and showing a styled window."""
    # Initialize NSApplication
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    
    print("Creating styled overlay window...")
    
    # Get screen dimensions
    screen = NSScreen.mainScreen()
    screen_frame = screen.frame()
    
    # Window settings
    width = 220
    height = 65
    x = screen_frame.size.width - width - 25
    y = screen_frame.size.height - height - 55
    
    # Create window
    frame = NSMakeRect(x, y, width, height)
    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        frame,
        NSBorderlessWindowMask,
        NSBackingStoreBuffered,
        False
    )
    
    # Configure window
    window.setLevel_(NSFloatingWindowLevel)
    window.setCollectionBehavior_(1 << 7)  # NSWindowCollectionBehaviorCanJoinAllSpaces
    window.setOpaque_(False)
    window.setBackgroundColor_(NSColor.clearColor())
    window.setHasShadow_(True)
    window.setIgnoresMouseEvents_(True)
    
    # Create custom view with rounded corners
    custom_view = StyledOverlayView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))
    window.setContentView_(custom_view)
    
    # Create icon
    icon_view = NSImageView.alloc().initWithFrame_(NSMakeRect(15, 20, 24, 24))
    icon_view.setImage_(create_icon("mic", (0.0, 0.8, 0.9, 1.0)))
    custom_view.addSubview_(icon_view)
    
    # Create status text field
    text_frame = NSMakeRect(50, 15, width - 65, 35)
    text_field = NSTextField.alloc().initWithFrame_(text_frame)
    text_field.setStringValue_("Ready")
    text_field.setBezeled_(False)
    text_field.setDrawsBackground_(False)
    text_field.setEditable_(False)
    text_field.setSelectable_(False)
    text_field.setAlignment_(NSTextAlignmentLeft)
    text_field.setFont_(NSFont.systemFontOfSize_weight_(16, 0.3))  # Medium weight
    text_field.setTextColor_(NSColor.whiteColor())
    custom_view.addSubview_(text_field)
    
    # Create subtitle text field
    subtitle_frame = NSMakeRect(50, 5, width - 65, 20)
    subtitle_field = NSTextField.alloc().initWithFrame_(subtitle_frame)
    subtitle_field.setStringValue_("Double-tap Ctrl to start")
    subtitle_field.setBezeled_(False)
    subtitle_field.setDrawsBackground_(False)
    subtitle_field.setEditable_(False)
    subtitle_field.setSelectable_(False)
    subtitle_field.setAlignment_(NSTextAlignmentLeft)
    subtitle_field.setFont_(NSFont.systemFontOfSize_(11))
    subtitle_field.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.7, 0.7, 0.7, 1.0))
    custom_view.addSubview_(subtitle_field)
    
    # Animate window appearance with fade in
    window.setAlphaValue_(0.0)
    window.makeKeyAndOrderFront_(None)
    window.orderFrontRegardless()
    
    # Fade in animation
    def fade_in():
        for i in range(20):
            window.setAlphaValue_(i / 20.0)
            time.sleep(0.02)
    
    fade_in()
    
    print("Styled window visible in top-right corner!")
    print("Running animation sequence...")
    
    # Animation states
    states = [
        {
            "title": "Recording",
            "subtitle": "Listening...",
            "icon_type": "mic",
            "icon_color": (1.0, 0.3, 0.3, 1.0),  # Red
            "border_color": (1.0, 0.3, 0.3, 1.0),
            "animate": True
        },
        {
            "title": "Processing",
            "subtitle": "Transcribing audio...",
            "icon_type": "processing",
            "icon_color": (0.3, 0.5, 1.0, 1.0),  # Blue
            "border_color": (0.3, 0.5, 1.0, 1.0),
            "animate": True
        },
        {
            "title": "Done",
            "subtitle": "Text inserted",
            "icon_type": "done",
            "icon_color": (0.3, 0.9, 0.4, 1.0),  # Green
            "border_color": (0.3, 0.9, 0.4, 1.0),
            "animate": False
        }
    ]
    
    # Run event loop for animation
    runLoop = NSRunLoop.currentRunLoop()
    end_time = NSDate.dateWithTimeIntervalSinceNow_(12.0)
    
    state_index = 0
    last_state_change = time.time()
    pulse_phase = 0
    
    while NSDate.date().compare_(end_time) == -1:
        # Change state every 3 seconds
        if time.time() - last_state_change > 3:
            state_index = (state_index + 1) % len(states)
            state = states[state_index]
            
            # Update text
            text_field.setStringValue_(state["title"])
            subtitle_field.setStringValue_(state["subtitle"])
            
            # Update icon
            icon_view.setImage_(create_icon(state["icon_type"], state["icon_color"]))
            
            # Update colors
            r, g, b, a = state["border_color"]
            custom_view.borderColor = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
            custom_view.setNeedsDisplay_(True)
            
            print(f"State: {state['title']}")
            last_state_change = time.time()
        
        # Pulse animation for recording/processing states
        current_state = states[state_index]
        if current_state["animate"]:
            pulse_phase += 0.1
            pulse_alpha = 0.7 + 0.3 * math.sin(pulse_phase)
            r, g, b, _ = current_state["border_color"]
            custom_view.borderColor = NSColor.colorWithRed_green_blue_alpha_(r, g, b, pulse_alpha)
            custom_view.setNeedsDisplay_(True)
        
        # Process events
        runLoop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.dateWithTimeIntervalSinceNow_(0.05))
    
    # Fade out animation
    print("\nFading out...")
    for i in range(20, -1, -1):
        window.setAlphaValue_(i / 20.0)
        runLoop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.dateWithTimeIntervalSinceNow_(0.02))
    
    window.orderOut_(None)
    print("Done!")


if __name__ == "__main__":
    try:
        test_styled_window()
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)