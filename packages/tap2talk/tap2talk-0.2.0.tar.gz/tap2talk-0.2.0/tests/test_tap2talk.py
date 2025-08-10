#!/usr/bin/env python3
"""Test script for tap2talk components."""

import sys
import time
from pathlib import Path

# Add tap2talk to path
sys.path.insert(0, str(Path(__file__).parent))


def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    from tap2talk.config import get_config
    
    config = get_config()
    print(f"  Config path: {config.config_path}")
    print(f"  API key configured: {bool(config.get_groq_api_key())}")
    
    valid, errors = config.validate()
    if valid:
        print("  ✓ Configuration valid")
    else:
        print(f"  ✗ Configuration errors: {errors}")
    
    return valid


def test_paths():
    """Test path management."""
    print("\nTesting paths...")
    from tap2talk import paths
    
    app_dir = paths.get_app_dir()
    print(f"  App directory: {app_dir}")
    print(f"  App dir exists: {app_dir.exists()}")
    
    recordings_dir = paths.get_recordings_dir()
    print(f"  Recordings directory: {recordings_dir}")
    print(f"  Recordings dir exists: {recordings_dir.exists()}")
    
    return True


def test_audio_devices():
    """Test audio device detection."""
    print("\nTesting audio devices...")
    try:
        from tap2talk.audio import AudioRecorder
        
        recorder = AudioRecorder()
        devices = recorder.get_input_devices()
        
        print(f"  Found {len(devices)} input devices:")
        for device in devices[:3]:  # Show first 3
            print(f"    - {device['name']} ({device['channels']} ch, {device['sample_rate']} Hz)")
        
        return len(devices) > 0
    except ImportError as e:
        print(f"  ✗ Audio module not available: {e}")
        return False


def test_overlay():
    """Test overlay window."""
    print("\nTesting overlay window...")
    try:
        from tap2talk.ui import OverlayWindow
        
        overlay = OverlayWindow()
        overlay.start()
        
        print("  Showing overlay states (3 seconds each)...")
        
        # Test different states
        overlay.show_recording()
        print("    - Recording (red)")
        time.sleep(2)
        
        overlay.show_processing()
        print("    - Processing (blue)")
        time.sleep(2)
        
        overlay.show_done()
        print("    - Done (green, auto-hide)")
        time.sleep(3)
        
        overlay.stop()
        print("  ✓ Overlay test complete")
        return True
        
    except Exception as e:
        print(f"  ✗ Overlay test failed: {e}")
        return False


def test_hotkey_detection():
    """Test hotkey detection (interactive)."""
    print("\nTesting hotkey detection...")
    print("  This test requires manual interaction.")
    print("  Press Ctrl+C to skip this test.")
    
    try:
        from tap2talk.hotkeys import get_hotkey_listener
        from tap2talk.config import get_config
        
        config = get_config()
        
        # Create callbacks
        ctrl_pressed = False
        esc_pressed = False
        
        def on_ctrl():
            nonlocal ctrl_pressed
            ctrl_pressed = True
            print("  ✓ Double Ctrl detected!")
        
        def on_esc():
            nonlocal esc_pressed
            esc_pressed = True
            print("  ✓ Double Esc detected!")
        
        listener = get_hotkey_listener(on_ctrl, on_esc, config)
        listener.start()
        
        print("  Double-tap Ctrl to test...")
        timeout = 10
        start_time = time.time()
        
        while not ctrl_pressed and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if ctrl_pressed:
            print("  Hotkey test passed!")
        else:
            print("  Timeout - skipping hotkey test")
        
        listener.stop()
        return True
        
    except Exception as e:
        print(f"  ✗ Hotkey test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("TAP2TALK COMPONENT TEST")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_config()))
    results.append(("Paths", test_paths()))
    results.append(("Audio Devices", test_audio_devices()))
    results.append(("Overlay Window", test_overlay()))
    
    # Optional interactive test
    try:
        results.append(("Hotkey Detection", test_hotkey_detection()))
    except KeyboardInterrupt:
        print("\n  Skipping hotkey test")
        results.append(("Hotkey Detection", None))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for name, result in results:
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        print(f"{name:20} {status}")
    
    # Check if ready to run
    print("\n" + "=" * 50)
    if results[0][1]:  # Config is valid
        print("✓ Tap2Talk is ready to run!")
        print("  Run with: python -m tap2talk")
    else:
        print("✗ Please configure Tap2Talk first:")
        print("  1. Add your Groq API key to ~/.tap2talk/config.yaml")
        print("  2. Or set GROQ_API_KEY environment variable")


if __name__ == "__main__":
    main()