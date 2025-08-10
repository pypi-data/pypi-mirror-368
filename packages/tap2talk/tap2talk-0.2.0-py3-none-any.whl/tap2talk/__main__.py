"""Main entry point for tap2talk application."""

import sys
import signal
import logging
import argparse
from .app import AppController
from .service import ServiceManager


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


def run_app(daemon=False):
    """Run the tap2talk application."""
    # Hide from Dock on macOS (run as accessory/menu bar app)
    if sys.platform == 'darwin':
        from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        # Set custom app icon (will be used in alerts)
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


def main():
    """Main entry point with service management."""
    parser = argparse.ArgumentParser(
        description="Tap2Talk - Voice transcription desktop app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  tap2talk              Run interactively (asks to run as service)
  tap2talk start        Start as background service
  tap2talk stop         Stop background service
  tap2talk status       Check service status
  tap2talk restart      Restart service
  tap2talk logs         Show recent logs
  tap2talk --daemon     Run in daemon mode (internal use)

Usage:
  Double-tap Ctrl to start/stop recording
  Double-tap Esc to abort recording
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['start', 'stop', 'status', 'restart', 'logs'],
        help='Service management command'
    )
    
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run in daemon mode (internal use)'
    )
    
    args = parser.parse_args()
    
    # Handle service commands
    if args.command:
        service = ServiceManager()
        
        if args.command == 'start':
            success, message = service.start()
            print(message)
            sys.exit(0 if success else 1)
            
        elif args.command == 'stop':
            success, message = service.stop()
            print(message)
            sys.exit(0 if success else 1)
            
        elif args.command == 'status':
            print(service.status())
            sys.exit(0)
            
        elif args.command == 'restart':
            success, message = service.restart()
            print(message)
            sys.exit(0 if success else 1)
            
        elif args.command == 'logs':
            print(service.logs())
            sys.exit(0)
    
    # If --daemon flag, run directly
    if args.daemon:
        run_app(daemon=True)
        return
    
    # Interactive mode - ask user how to run
    service = ServiceManager()
    
    # Display ASCII logo with gradient colors
    logo = """
\033[96m ████████╗  █████╗  ██████╗  ██████╗  ████████╗  █████╗  ██╗      ██╗  ██╗
\033[96m ╚══██╔══╝ ██╔══██╗ ██╔══██╗ ╚════██╗ ╚══██╔══╝ ██╔══██╗ ██║      ██║ ██╔╝
\033[36m    ██║    ███████║ ██████╔╝  █████╔╝    ██║    ███████║ ██║      █████╔╝ 
\033[36m    ██║    ██╔══██║ ██╔═══╝  ██╔═══╝     ██║    ██╔══██║ ██║      ██╔═██╗ 
\033[94m    ██║    ██║  ██║ ██║      ███████╗    ██║    ██║  ██║ ███████╗ ██║  ██╗
\033[94m    ╚═╝    ╚═╝  ╚═╝ ╚═╝      ╚══════╝    ╚═╝    ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝\033[0m
"""
    
    print(logo)
    print("\033[90m" + "="*78 + "\033[0m")
    print("\nHow would you like to run Tap2Talk?")
    print("\n1. Run as background service (recommended)")
    print("   - Runs in background")
    print("   - Survives terminal close")
    print("   - Access via menu bar icon")
    print("\n2. Run interactively")
    print("   - Runs in this terminal")
    print("   - Stops when terminal closes")
    print("   - See logs directly")
    print("\n3. Cancel")
    print("   - Exit without starting")
    
    while True:
        choice = input("\nEnter choice [1/2/3]: ").strip()
        
        if choice == '1':
            print("\nStarting Tap2Talk as background service...")
            success, message = service.start()
            print(message)
            if success:
                print("\nTap2Talk is now running in the background!")
                print("Look for the icon in your menu bar.")
                print("\nUseful commands:")
                print("  tap2talk status  - Check if running")
                print("  tap2talk stop    - Stop the service")
                print("  tap2talk logs    - View recent logs")
            sys.exit(0 if success else 1)
            
        elif choice == '2':
            print("\nStarting Tap2Talk interactively...")
            print("Press Ctrl+C to stop")
            print("-"*50)
            run_app(daemon=False)
            break
            
        elif choice == '3':
            print("\nCancelled. Exiting...")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()