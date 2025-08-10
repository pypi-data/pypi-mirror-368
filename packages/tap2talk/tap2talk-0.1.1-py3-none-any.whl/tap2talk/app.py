"""Main application controller and state machine."""

import asyncio
import threading
from enum import Enum, auto
from typing import Optional, Callable
from pathlib import Path
import time

from .config import get_config
from .log import get_logger, setup_logging
from .paths import get_recordings_dir, get_failed_dir, get_recording_filename


class AppState(Enum):
    """Application states."""
    IDLE = auto()
    RECORDING = auto()
    PROCESSING = auto()


class AppController:
    """Main application controller managing state and coordination."""
    
    def __init__(self):
        self.config = get_config()
        setup_logging(self.config.get("log_level", "info"))
        self.logger = get_logger()
        
        self.state = AppState.IDLE
        self.state_lock = threading.Lock()
        
        # Components (will be initialized later)
        self.hotkey_listener = None
        self.audio_recorder = None
        self.transcriber = None
        self.text_inserter = None
        self.ui_overlay = None
        self.tray_icon = None
        
        # Current operation data
        self.current_recording_path: Optional[Path] = None
        self.recording_start_time: Optional[float] = None
        
        # Async event loop for transcription
        self.async_loop = None
        self.async_thread = None
        self.transcription_task = None
        
        # Callbacks
        self.on_state_change: Optional[Callable] = None
        
        self.logger.info("AppController initialized")
    
    def start(self):
        """Start the application."""
        self.logger.info("Starting Tap2Talk application")
        
        # Validate configuration
        valid, errors = self.config.validate()
        if not valid:
            self.logger.error(f"Configuration errors: {errors}")
            if self.ui_overlay:
                self.ui_overlay.show_error("Configuration error: " + ", ".join(errors))
            return False
        
        # Start async event loop in separate thread
        self._start_async_loop()
        
        # Initialize components
        self._init_components()
        
        # Start hotkey listener
        if self.hotkey_listener:
            self.hotkey_listener.start()
        
        # Show tray icon
        if self.tray_icon:
            self.tray_icon.run()
        
        return True
    
    def _start_async_loop(self):
        """Start asyncio event loop in separate thread."""
        def run_loop():
            self.async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.async_loop)
            self.async_loop.run_forever()
        
        self.async_thread = threading.Thread(target=run_loop, daemon=True)
        self.async_thread.start()
        
        # Wait for loop to be ready
        while self.async_loop is None:
            time.sleep(0.01)
    
    def _init_components(self):
        """Initialize all components."""
        try:
            # Initialize UI overlay first (for error display)
            from .ui.overlay import Overlay
            self.ui_overlay = Overlay(self.config)
            self.ui_overlay.start()
            
            # Initialize hotkey listener
            from .hotkeys import get_hotkey_listener
            self.hotkey_listener = get_hotkey_listener(
                self.handle_double_ctrl,
                self.handle_double_esc,
                self.config
            )
            
            # Initialize audio recorder
            from .audio import AudioRecorder
            self.audio_recorder = AudioRecorder(self.config)
            
            # Initialize transcriber
            api_key = self.config.get_groq_api_key()
            if api_key:
                from .transcribe import GroqTranscriber
                self.transcriber = GroqTranscriber(api_key, self.config)
            else:
                self.logger.warning("No Groq API key configured, using mock transcriber")
                from .transcribe.groq_client import MockTranscriber
                self.transcriber = MockTranscriber(config=self.config)
            
            # Initialize text inserter
            from .insert import get_text_inserter
            self.text_inserter = get_text_inserter(self.config)
            
            # Initialize tray icon (must be last as it blocks)
            from .ui import TrayIcon
            self.tray_icon = TrayIcon(self)
            
            # Connect overlay to tray for visual feedback
            if self.ui_overlay:
                self.ui_overlay.tray_app = self.tray_icon
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            if self.ui_overlay:
                self.ui_overlay.show_error("Initialization failed")
            raise
    
    def handle_double_ctrl(self):
        """Handle double Ctrl press event."""
        with self.state_lock:
            if self.state == AppState.IDLE:
                self.logger.info("Starting recording")
                self._start_recording()
            elif self.state == AppState.RECORDING:
                self.logger.info("Stopping recording")
                self._stop_recording()
            else:
                self.logger.debug("Double Ctrl ignored in PROCESSING state")
    
    def handle_double_esc(self):
        """Handle double Esc press event."""
        with self.state_lock:
            if self.state in (AppState.RECORDING, AppState.PROCESSING):
                self.logger.info("Aborting operation")
                self._abort_operation()
    
    def _set_state(self, new_state: AppState):
        """Update application state."""
        old_state = self.state
        self.state = new_state
        self.logger.debug(f"State transition: {old_state.name} -> {new_state.name}")
        
        # Notify UI
        if self.on_state_change:
            self.on_state_change(new_state)
        
        # Update overlay
        if self.ui_overlay:
            if new_state == AppState.RECORDING:
                self.ui_overlay.show_recording()
            elif new_state == AppState.PROCESSING:
                self.ui_overlay.show_processing()
            elif new_state == AppState.IDLE:
                pass  # Overlay will auto-hide
    
    def _start_recording(self):
        """Start audio recording."""
        try:
            self._set_state(AppState.RECORDING)
            
            # Generate recording filename
            filename = get_recording_filename()
            self.current_recording_path = get_recordings_dir() / filename
            self.recording_start_time = time.time()
            
            # Start audio recording
            if self.audio_recorder:
                self.audio_recorder.start_recording(self.current_recording_path)
            
            self.logger.info(f"Recording started: {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            self._set_state(AppState.IDLE)
            if self.ui_overlay:
                self.ui_overlay.show_error("Failed to start recording")
    
    def _stop_recording(self):
        """Stop audio recording and start transcription."""
        try:
            # Check timeout
            if self.recording_start_time:
                duration = time.time() - self.recording_start_time
                timeout = self.config.get("recording_timeout", 30)
                if duration > timeout:
                    self.logger.warning(f"Recording exceeded timeout ({timeout}s)")
            
            # Stop recording
            if self.audio_recorder:
                self.audio_recorder.stop_recording()
            
            self._set_state(AppState.PROCESSING)
            
            # Start transcription
            if self.current_recording_path and self.current_recording_path.exists():
                self._start_transcription(self.current_recording_path)
            else:
                raise Exception("Recording file not found")
            
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            self._cleanup_recording(failed=True)
            self._set_state(AppState.IDLE)
            if self.ui_overlay:
                self.ui_overlay.show_error("Failed to stop recording")
    
    def _start_transcription(self, audio_path: Path):
        """Start async transcription."""
        if not self.transcriber:
            self.logger.error("Transcriber not initialized")
            self._cleanup_recording(failed=True)
            self._set_state(AppState.IDLE)
            return
        
        # Create async task
        async def transcribe():
            try:
                text = await self.transcriber.transcribe(audio_path)
                # Run callback in main thread
                self._on_transcription_complete(text)
            except asyncio.CancelledError:
                self.logger.info("Transcription cancelled")
            except Exception as e:
                self.logger.error(f"Transcription failed: {e}")
                self._on_transcription_failed(str(e))
        
        # Schedule task in async loop
        self.transcription_task = asyncio.run_coroutine_threadsafe(
            transcribe(), self.async_loop
        )
    
    def _on_transcription_complete(self, text: str):
        """Handle successful transcription."""
        with self.state_lock:
            if self.state != AppState.PROCESSING:
                return  # Aborted
            
            self.logger.info(f"Transcription complete: {len(text)} characters")
            
            # Insert text
            if self.text_inserter and text.strip():
                success = self.text_inserter.insert_text(text)
                if success:
                    if self.ui_overlay:
                        self.ui_overlay.show_done()
                else:
                    if self.ui_overlay:
                        self.ui_overlay.show_error("Failed to insert text")
            
            # Cleanup
            self._cleanup_recording(failed=False)
            self._set_state(AppState.IDLE)
    
    def _on_transcription_failed(self, error: str):
        """Handle failed transcription."""
        with self.state_lock:
            self.logger.error(f"Transcription failed: {error}")
            
            # Store the failed audio path before cleanup
            failed_audio_path = self.current_recording_path
            
            if self.ui_overlay:
                if "401" in error:
                    self.ui_overlay.show_error("Invalid API key")
                elif "413" in error:
                    self.ui_overlay.show_error("Recording too large")
                elif "429" in error:
                    self.ui_overlay.show_error("Rate limit exceeded")
                else:
                    self.ui_overlay.show_error("Transcription failed")
            
            # Move to failed directory (this updates the path)
            self._cleanup_recording(failed=True)
            
            # Get the new path in failed directory
            if failed_audio_path and failed_audio_path.name:
                from .paths import get_failed_dir
                saved_path = get_failed_dir() / failed_audio_path.name
                
                # Show retry dialog on main thread
                if saved_path.exists():
                    self._show_retry_dialog(saved_path, error)
            
            self._set_state(AppState.IDLE)
    
    def _show_retry_dialog(self, audio_path: Path, error: str):
        """Show dialog with retry options."""
        # Use rumps.alert which is thread-safe
        import rumps
        from PyObjCTools import AppHelper
        
        def show_dialog():
            response = rumps.alert(
                title="Transcription Failed",
                message=f"Your audio has been saved.\n\nError: {error[:100]}",
                ok="Retry",
                cancel="Cancel",
                other="Open in Finder"
            )
            
            if response == 1:  # OK/Retry button
                self.logger.info("User chose to retry transcription")
                # Retry transcription with the saved audio
                self._retry_transcription(audio_path)
            elif response == -1:  # Other/Open in Finder button
                self.logger.info("User chose to open in Finder")
                self._open_in_finder(audio_path)
            else:  # Cancel button or closed
                self.logger.info("User cancelled retry dialog")
        
        # Run in a thread to avoid blocking, then schedule dialog on main thread
        def delayed_show():
            time.sleep(1)  # Let error overlay show first
            AppHelper.callAfter(show_dialog)
        
        threading.Thread(target=delayed_show, daemon=True).start()
    
    def _retry_transcription(self, audio_path: Path):
        """Retry transcription with existing audio file."""
        self.logger.info(f"Retrying transcription for {audio_path}")
        
        # Set state and show UI
        with self.state_lock:
            self._set_state(AppState.PROCESSING)
            # Store the path so cleanup knows about it
            self.current_recording_path = audio_path
        
        # Start transcription again
        self._start_transcription(audio_path)
    
    def _open_in_finder(self, file_path: Path):
        """Open file location in Finder (macOS) or Explorer (Windows)."""
        import subprocess
        import sys
        
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', '-R', str(file_path)])
        elif sys.platform == 'win32':  # Windows
            subprocess.run(['explorer', '/select,', str(file_path)])
        else:  # Linux
            # Open the directory containing the file
            subprocess.run(['xdg-open', str(file_path.parent)])
    
    def _abort_operation(self):
        """Abort current operation."""
        # Cancel transcription if in progress
        if self.transcription_task and not self.transcription_task.done():
            self.transcription_task.cancel()
        
        # Stop recording if in progress
        if self.state == AppState.RECORDING and self.audio_recorder:
            self.audio_recorder.stop_recording()
        
        # Show abort message
        if self.ui_overlay:
            self.ui_overlay.show_aborted()
        
        # Cleanup and reset
        self._cleanup_recording(failed=True)
        self._set_state(AppState.IDLE)
    
    def _cleanup_recording(self, failed: bool):
        """Clean up recording file."""
        if not self.current_recording_path:
            return
        
        try:
            if self.current_recording_path.exists():
                # Check if file is already in failed directory (retry case)
                if str(get_failed_dir()) in str(self.current_recording_path):
                    if not failed:
                        # Successful retry - delete from failed directory
                        self.current_recording_path.unlink()
                        self.logger.debug("Deleted successful retry recording from failed directory")
                    # If still failed, leave it in failed directory
                else:
                    # Normal recording flow
                    if failed:
                        # Move to failed directory
                        failed_path = get_failed_dir() / self.current_recording_path.name
                        self.current_recording_path.rename(failed_path)
                        self.logger.debug(f"Moved failed recording to {failed_path}")
                    else:
                        # Delete successful recording
                        self.current_recording_path.unlink()
                        self.logger.debug("Deleted successful recording")
        except Exception as e:
            self.logger.error(f"Failed to cleanup recording: {e}")
        finally:
            self.current_recording_path = None
            self.recording_start_time = None
    
    def restart(self):
        """Restart the application."""
        self.logger.info("Restarting application")
        # Implementation depends on packaging method
        pass
    
    def quit(self):
        """Quit the application."""
        self.logger.info("Quitting application")
        
        # Stop components
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        if self.audio_recorder:
            self.audio_recorder.cleanup()
        
        # Stop async loop
        if self.async_loop:
            self.async_loop.call_soon_threadsafe(self.async_loop.stop)
        
        # Exit
        if self.tray_icon:
            self.tray_icon.stop()