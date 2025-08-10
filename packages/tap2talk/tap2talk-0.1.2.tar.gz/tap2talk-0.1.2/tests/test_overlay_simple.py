#!/usr/bin/env python3
"""Simple test for overlay window that actually shows."""

import time
import sys
from AppKit import (
    NSApplication, NSWindow, NSTextField, NSColor, NSFont,
    NSBackingStoreBuffered, NSBorderlessWindowMask,
    NSFloatingWindowLevel, NSScreen, NSMakeRect,
    NSTextAlignmentCenter, NSApplicationActivationPolicyAccessory,
    NSApp
)
from Foundation import NSRunLoop, NSDate, NSDefaultRunLoopMode


def test_window():
    """Test creating and showing a window."""
    # Initialize NSApplication
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    
    print("Creating window...")
    
    # Get screen dimensions
    screen = NSScreen.mainScreen()
    if not screen:
        print("No screen found!")
        return
    
    screen_frame = screen.frame()
    print(f"Screen size: {screen_frame.size.width} x {screen_frame.size.height}")
    
    # Window settings
    width = 200
    height = 60
    x = screen_frame.size.width - width - 20
    y = screen_frame.size.height - height - 50
    
    print(f"Window position: {x}, {y}")
    
    # Create window
    frame = NSMakeRect(x, y, width, height)
    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        frame,
        NSBorderlessWindowMask,
        NSBackingStoreBuffered,
        False
    )
    
    if not window:
        print("Failed to create window!")
        return
    
    print("Window created")
    
    # Configure window  
    window.setLevel_(NSFloatingWindowLevel)
    window.setCollectionBehavior_(1 << 7)  # NSWindowCollectionBehaviorCanJoinAllSpaces
    window.setOpaque_(False)
    window.setBackgroundColor_(NSColor.clearColor())
    window.setHasShadow_(True)
    window.setIgnoresMouseEvents_(True)
    
    # Create text field
    text_frame = NSMakeRect(0, 0, width, height)
    text_field = NSTextField.alloc().initWithFrame_(text_frame)
    text_field.setStringValue_("TEST OVERLAY")
    text_field.setBezeled_(False)
    text_field.setDrawsBackground_(True)
    text_field.setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(1.0, 0.2, 0.2, 0.9))
    text_field.setEditable_(False)
    text_field.setSelectable_(False)
    text_field.setAlignment_(NSTextAlignmentCenter)
    text_field.setFont_(NSFont.boldSystemFontOfSize_(14))
    text_field.setTextColor_(NSColor.whiteColor())
    
    print("Text field created")
    
    # Add text field to window
    window.contentView().addSubview_(text_field)
    
    # Make window visible
    window.makeKeyAndOrderFront_(None)
    window.orderFrontRegardless()
    
    print("Window should be visible now in top-right corner!")
    print("Look for a red box with 'TEST OVERLAY' text")
    
    # Run event loop for 10 seconds
    print("\nRunning for 10 seconds...")
    runLoop = NSRunLoop.currentRunLoop()
    end_time = NSDate.dateWithTimeIntervalSinceNow_(10.0)
    
    # Cycle through colors
    colors = [
        (1.0, 0.2, 0.2, 0.9),  # Red
        (0.2, 0.2, 1.0, 0.9),  # Blue
        (0.2, 1.0, 0.2, 0.9),  # Green
    ]
    
    color_index = 0
    last_color_change = time.time()
    
    while NSDate.date().compare_(end_time) == -1:  # While current time < end_time
        # Change color every 2 seconds
        if time.time() - last_color_change > 2:
            color_index = (color_index + 1) % len(colors)
            r, g, b, a = colors[color_index]
            new_color = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
            text_field.setBackgroundColor_(new_color)
            
            texts = ["⏺ Recording", "⏳ Processing", "✓ Done"]
            text_field.setStringValue_(texts[color_index])
            
            # Force window to front again
            window.orderFrontRegardless()
            
            print(f"Changed to color {color_index}: {texts[color_index]}")
            last_color_change = time.time()
        
        # Process events
        runLoop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.dateWithTimeIntervalSinceNow_(0.1))
    
    print("\nHiding window...")
    window.orderOut_(None)
    
    print("Done!")


if __name__ == "__main__":
    try:
        test_window()
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)