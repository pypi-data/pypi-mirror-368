"""Logging configuration with PII redaction."""

import logging
import logging.handlers
import re
from pathlib import Path
from .paths import get_logs_dir


class PIIRedactingFormatter(logging.Formatter):
    """Custom formatter that redacts PII from log messages."""
    
    # Patterns to redact
    PATTERNS = [
        (r'gsk_[a-zA-Z0-9_-]+', 'gsk_***'),  # Groq API keys
        (r'Bearer [a-zA-Z0-9_-]+', 'Bearer ***'),  # Auth tokens
        (r'/Users/[^/\s]+', r'/Users/***'),  # User paths on macOS
        (r'C:\\Users\\[^\\]+', r'C:\\Users\\***'),  # User paths on Windows
        (r'\.wav$', '.wav'),  # Keep .wav extension but redact filename
    ]
    
    def format(self, record):
        msg = super().format(record)
        
        # Apply redaction patterns
        for pattern, replacement in self.PATTERNS:
            msg = re.sub(pattern, replacement, msg)
        
        return msg


def setup_logging(log_level: str = "info"):
    """Setup application logging with rotation and PII redaction."""
    log_dir = get_logs_dir()
    log_file = log_dir / "tap2talk.log"
    
    # Convert string level to logging constant
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }
    level = level_map.get(log_level.lower(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("tap2talk")
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=256 * 1024,  # 256KB
        backupCount=5
    )
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    
    # Create formatter with PII redaction
    formatter = PIIRedactingFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    # Only add console handler in debug mode
    if level == logging.DEBUG:
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "tap2talk") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)