"""Service management for tap2talk - run as background daemon."""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from typing import Optional
from .paths import get_app_dir


class ServiceManager:
    """Manages tap2talk as a background service."""
    
    def __init__(self):
        self.app_dir = get_app_dir()
        self.pid_file = self.app_dir / "tap2talk.pid"
        self.log_file = self.app_dir / "tap2talk.log"
        self.err_file = self.app_dir / "tap2talk.err"
        
    def _get_pid(self) -> Optional[int]:
        """Get PID from pid file if exists and process is running."""
        if not self.pid_file.exists():
            return None
            
        try:
            pid = int(self.pid_file.read_text().strip())
            # Check if process is actually running
            os.kill(pid, 0)
            return pid
        except (ValueError, ProcessLookupError, PermissionError):
            # Invalid PID or process not running
            self.pid_file.unlink(missing_ok=True)
            return None
    
    def is_running(self) -> bool:
        """Check if service is running."""
        return self._get_pid() is not None
    
    def status(self) -> str:
        """Get service status."""
        pid = self._get_pid()
        if pid:
            return f"\033[32m[OK]\033[0m Tap2Talk is running (PID: {pid})"
        else:
            return "\033[31m[X]\033[0m Tap2Talk is not running"
    
    def start(self) -> tuple[bool, str]:
        """Start tap2talk as a background service."""
        if self.is_running():
            pid = self._get_pid()
            return False, f"Tap2Talk is already running (PID: {pid})"
        
        # Ensure app directory exists
        self.app_dir.mkdir(exist_ok=True)
        
        # Get the tap2talk executable path
        tap2talk_cmd = sys.executable
        tap2talk_module = [tap2talk_cmd, "-m", "tap2talk", "--daemon"]
        
        # Start the process in background
        with open(self.log_file, 'a') as out, open(self.err_file, 'a') as err:
            process = subprocess.Popen(
                tap2talk_module,
                stdout=out,
                stderr=err,
                start_new_session=True,  # Detach from parent
                env=os.environ.copy()
            )
            
        # Write PID file
        self.pid_file.write_text(str(process.pid))
        
        # Give it a moment to start
        time.sleep(1)
        
        # Verify it's running
        if self.is_running():
            return True, f"\033[32m[OK]\033[0m Tap2Talk started successfully (PID: {process.pid})\n   Logs: {self.log_file}"
        else:
            return False, "\033[31m[FAIL]\033[0m Failed to start Tap2Talk service"
    
    def stop(self) -> tuple[bool, str]:
        """Stop the tap2talk service."""
        pid = self._get_pid()
        if not pid:
            return False, "Tap2Talk is not running"
        
        try:
            # Send SIGTERM for graceful shutdown
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to terminate (max 5 seconds)
            for _ in range(10):
                time.sleep(0.5)
                try:
                    os.kill(pid, 0)  # Check if still running
                except ProcessLookupError:
                    # Process terminated
                    self.pid_file.unlink(missing_ok=True)
                    return True, f"\033[32m[OK]\033[0m Tap2Talk stopped (was PID: {pid})"
            
            # If still running, force kill
            os.kill(pid, signal.SIGKILL)
            self.pid_file.unlink(missing_ok=True)
            return True, f"\033[33m[OK]\033[0m Tap2Talk force stopped (was PID: {pid})"
            
        except Exception as e:
            return False, f"Failed to stop Tap2Talk: {e}"
    
    def restart(self) -> tuple[bool, str]:
        """Restart the service."""
        stop_success, stop_msg = self.stop()
        if stop_success or "not running" in stop_msg:
            time.sleep(1)
            return self.start()
        return False, f"Failed to restart: {stop_msg}"
    
    def logs(self, lines: int = 20) -> str:
        """Get recent log output."""
        output = []
        
        if self.log_file.exists():
            logs = self.log_file.read_text().splitlines()
            if logs:
                output.append("=== Recent Output ===")
                output.extend(logs[-lines:])
        
        if self.err_file.exists():
            errors = self.err_file.read_text().splitlines()
            if errors:
                if output:
                    output.append("")
                output.append("=== Recent Errors ===")
                output.extend(errors[-lines:])
        
        if not output:
            output.append("No logs available")
            
        return "\n".join(output)