"""Main entry point for tap2talk application."""

import sys
import signal
import logging
from .app import AppController


def create_app_icon():
    """Create a custom app icon for alerts and system dialogs."""
    if sys.platform != 'darwin':
        return None
    
    from AppKit import NSImage, NSColor, NSBezierPath, NSMakeRect
    
    # Create a 512x512 icon (standard app icon size)
    size = 512
    image = NSImage.alloc().initWithSize_((size, size))
    image.lockFocus()
    
    # Draw background circle with gradient effect
    # Dark background
    bg_color = NSColor.colorWithRed_green_blue_alpha_(0.1, 0.1, 0.12, 1.0)
    bg_color.setFill()
    bg_circle = NSBezierPath.bezierPathWithOvalInRect_(NSMakeRect(20, 20, size-40, size-40))
    bg_circle.fill()
    
    # Draw cyan border
    border_color = NSColor.colorWithRed_green_blue_alpha_(0.0, 0.8, 0.9, 1.0)
    border_color.setStroke()
    bg_circle.setLineWidth_(8)
    bg_circle.stroke()
    
    # Draw microphone icon in center
    mic_color = NSColor.colorWithRed_green_blue_alpha_(0.0, 0.8, 0.9, 1.0)
    mic_color.setFill()
    mic_color.setStroke()
    
    # Scale for icon
    scale = size / 100.0
    
    # Mic body (rounded rectangle)
    mic_body = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
        NSMakeRect(44*scale, 35*scale, 12*scale, 25*scale),
        6*scale, 6*scale
    )
    mic_body.fill()
    
    # Mic stand arc
    stand_path = NSBezierPath.bezierPath()
    stand_path.setLineWidth_(3*scale)
    # Create arc from left to right under the mic
    center_x = 50*scale
    center_y = 47*scale
    radius = 15*scale
    stand_path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
        (center_x, center_y), radius, 180, 0, False
    )
    stand_path.stroke()
    
    # Mic base (vertical line and horizontal line)
    base_path = NSBezierPath.bezierPath()
    base_path.setLineWidth_(3*scale)
    base_path.moveToPoint_((50*scale, 32*scale))
    base_path.lineToPoint_((50*scale, 25*scale))
    base_path.moveToPoint_((40*scale, 25*scale))
    base_path.lineToPoint_((60*scale, 25*scale))
    base_path.stroke()
    
    image.unlockFocus()
    return image


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print("\nShutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Hide from Dock on macOS (run as accessory/menu bar app)
    if sys.platform == 'darwin':
        from AppKit import NSApplication, NSApplicationActivationPolicyAccessory, NSImage
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        # Set custom app icon (will be used in alerts)
        # You can create a custom icon or use a system icon
        # For now, let's create a simple microphone icon
        icon = create_app_icon()
        if icon:
            app.setApplicationIconImage_(icon)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and start application
        app = AppController()
        
        # Start the application
        if not app.start():
            print("Failed to start application")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()