"""Path management for tap2talk application."""

import os
from pathlib import Path
import platform
import stat


def get_app_dir() -> Path:
    """Get the application data directory."""
    home = Path.home()
    app_dir = home / ".tap2talk"
    app_dir.mkdir(exist_ok=True)
    
    # Set restrictive permissions on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(app_dir, stat.S_IRWXU)  # 700 permissions
    
    return app_dir


def get_config_path() -> Path:
    """Get the configuration file path."""
    config_path = get_app_dir() / "config.yaml"
    return config_path


def get_recordings_dir() -> Path:
    """Get the temporary recordings directory."""
    recordings_dir = get_app_dir() / "recordings"
    recordings_dir.mkdir(exist_ok=True)
    return recordings_dir


def get_failed_dir() -> Path:
    """Get the failed recordings directory."""
    failed_dir = get_app_dir() / "failed"
    failed_dir.mkdir(exist_ok=True)
    return failed_dir


def get_logs_dir() -> Path:
    """Get the logs directory."""
    logs_dir = get_app_dir() / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def get_cache_dir() -> Path:
    """Get the cache directory."""
    cache_dir = get_app_dir() / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


def get_recording_filename() -> str:
    """Generate a unique recording filename."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"tap2talk_recording_{timestamp}.wav"


def cleanup_old_files(directory: Path, max_age_days: int = 7):
    """Clean up old files in a directory."""
    import time
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                except Exception:
                    pass  # Ignore errors during cleanup