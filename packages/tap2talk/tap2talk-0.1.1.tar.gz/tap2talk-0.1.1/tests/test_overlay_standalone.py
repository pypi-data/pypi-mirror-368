#!/usr/bin/env python3
"""Standalone test for native macOS overlay window."""

from AppKit import (
    NSApplication, NSWindow, NSTextField, NSColor, NSFont,
    NSBackingStoreBuffered, NSBorderlessWindowMask,
    NSFloatingWindowLevel, NSScreen, NSMakeRect,
    NSTextAlignmentCenter, NSApp, NSTimer,
    NSApplicationActivationPolicyAccessory
)
import time


class TestOverlayWindow:
    """Test native macOS floating overlay window."""
    
    def __init__(self):
        # Create the NSApplication if it doesn't exist
        self.app = NSApplication.sharedApplication()
        
        # Set activation policy to accessory (no dock icon)
        self.app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        self.window = None
        self.text_field = None
        self.create_window()
    
    def create_window(self):
        """Create the native window."""
        # Get screen dimensions
        screen = NSScreen.mainScreen()
        screen_frame = screen.frame()
        
        # Window settings
        width = 200
        height = 60
        margin = 20
        
        # Calculate position (top-right corner)
        x = screen_frame.size.width - width - margin
        y = screen_frame.size.height - height - margin - 30  # Account for menu bar
        
        # Create window
        frame = NSMakeRect(x, y, width, height)
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSBorderlessWindowMask,
            NSBackingStoreBuffered,
            False
        )
        
        # Configure window
        self.window.setLevel_(NSFloatingWindowLevel)  # Always on top
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setHasShadow_(True)
        self.window.setIgnoresMouseEvents_(True)  # Click-through
        
        # Create text field
        text_frame = NSMakeRect(0, 0, width, height)
        self.text_field = NSTextField.alloc().initWithFrame_(text_frame)
        self.text_field.setStringValue_("Test Overlay")
        self.text_field.setBezeled_(False)
        self.text_field.setDrawsBackground_(True)
        self.text_field.setEditable_(False)
        self.text_field.setSelectable_(False)
        self.text_field.setAlignment_(NSTextAlignmentCenter)
        
        # Set font
        font = NSFont.boldSystemFontOfSize_(14)
        self.text_field.setFont_(font)
        self.text_field.setTextColor_(NSColor.whiteColor())
        
        # Set initial background
        self.text_field.setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.2, 0.2, 0.8, 0.9)
        )
        
        # Add text field to window
        self.window.contentView().addSubview_(self.text_field)
        
        print(f"Window created at position: {x}, {y}")
    
    def show_recording(self):
        """Show recording status."""
        print("Showing Recording state")
        # Red background
        bg_color = NSColor.colorWithRed_green_blue_alpha_(1.0, 0.27, 0.27, 0.9)
        self.text_field.setStringValue_("⏺ Recording")
        self.text_field.setBackgroundColor_(bg_color)
        self.window.orderFront_(None)
        self.window.makeKeyAndOrderFront_(None)
    
    def show_processing(self):
        """Show processing status."""
        print("Showing Processing state")
        # Blue background
        bg_color = NSColor.colorWithRed_green_blue_alpha_(0.27, 0.27, 1.0, 0.9)
        self.text_field.setStringValue_("⏳ Processing")
        self.text_field.setBackgroundColor_(bg_color)
        self.window.orderFront_(None)
    
    def show_done(self):
        """Show done status."""
        print("Showing Done state")
        # Green background
        bg_color = NSColor.colorWithRed_green_blue_alpha_(0.27, 1.0, 0.27, 0.9)
        self.text_field.setStringValue_("✓ Done")
        self.text_field.setBackgroundColor_(bg_color)
        self.window.orderFront_(None)
    
    def hide(self):
        """Hide the window."""
        print("Hiding window")
        self.window.orderOut_(None)
    
    def run_test_sequence(self):
        """Run a test sequence of states."""
        print("Starting test sequence...")
        
        # Show recording
        self.show_recording()
        time.sleep(2)
        
        # Show processing
        self.show_processing()
        time.sleep(2)
        
        # Show done
        self.show_done()
        time.sleep(2)
        
        # Hide
        self.hide()
        time.sleep(1)
        
        print("Test sequence complete!")


def main():
    """Run the standalone overlay test."""
    print("Creating overlay window...")
    overlay = TestOverlayWindow()
    
    print("\nWindow should be visible in top-right corner")
    print("Running test sequence...")
    
    # Run test sequence
    overlay.run_test_sequence()
    
    print("\nPress Ctrl+C to exit")
    
    # Keep the app running
    try:
        # Run the event loop
        NSApp.run()
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()