"""Configuration management for tap2talk."""

import os
import sys
import yaml
import getpass
from pathlib import Path
from typing import Optional, Dict, Any
from .paths import get_config_path, get_app_dir


class Config:
    """Configuration manager for tap2talk."""
    
    DEFAULT_CONFIG = {
        "groq_api_key": "",
        "log_level": "info",
        "auto_paste": True,
        "recording_timeout": 30,
        "model": "whisper-large-v3-turbo",
        "double_press_threshold_ms": 400,
        "overlay_position": "top-right",
        "overlay_hide_delay_ms": 2000
    }
    
    def __init__(self):
        self.config_path = get_config_path()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f) or {}
                    # Merge with defaults to ensure all keys exist
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            # Ensure directory exists
            get_app_dir().mkdir(exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Set restrictive permissions
            if os.name != 'nt':  # Unix-like systems
                os.chmod(self.config_path, 0o600)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self._save_config(self.config)
    
    def get_groq_api_key(self) -> Optional[str]:
        """Get Groq API key from config or environment."""
        # First check config file
        api_key = self.config.get("groq_api_key")
        if api_key and api_key.strip():
            return api_key.strip()
        
        # Then check environment variable
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key and api_key.strip():
            # Save to config for next time
            self.set_groq_api_key(api_key.strip())
            return api_key.strip()
        
        # If not found anywhere, prompt user
        api_key = self.prompt_for_api_key()
        if api_key:
            self.set_groq_api_key(api_key)
            return api_key
        
        return None
    
    def prompt_for_api_key(self) -> Optional[str]:
        """Prompt user for Groq API key."""
        print("\n" + "="*60)
        print("Welcome to Tap2Talk!")
        print("="*60)
        print("\nTo use Tap2Talk, you need a Groq API key.")
        print("Get your free API key at: https://console.groq.com/keys")
        print("\nYour API key will be saved securely in ~/.tap2talk/config.yaml")
        print("="*60 + "\n")
        
        while True:
            api_key = getpass.getpass("Enter your Groq API key (input hidden): ").strip()
            
            if not api_key:
                print("[ERROR] API key cannot be empty.")
                response = input("Try again? (y/n): ").lower()
                if response != 'y':
                    print("\n[WARNING] Tap2Talk cannot run without an API key.")
                    print("Exiting...")
                    sys.exit(1)
                continue
            
            # Basic validation - Groq keys usually start with "gsk_"
            if not api_key.startswith("gsk_"):
                print("[WARNING] Groq API keys usually start with 'gsk_'")
                response = input("Continue anyway? (y/n): ").lower()
                if response != 'y':
                    continue
            
            print("[OK] API key saved successfully!")
            print("\nYou can now use Tap2Talk:")
            print("  - Double-tap Ctrl to start/stop recording")
            print("  - Double-tap Esc to abort")
            print("\nStarting Tap2Talk...\n")
            return api_key
    
    def set_groq_api_key(self, api_key: str):
        """Set and save Groq API key."""
        self.set("groq_api_key", api_key)
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration."""
        errors = []
        
        if not self.get_groq_api_key():
            errors.append("Groq API key not configured")
        
        recording_timeout = self.get("recording_timeout", 30)
        if not isinstance(recording_timeout, (int, float)) or recording_timeout <= 0:
            errors.append("Invalid recording_timeout value")
        
        return len(errors) == 0, errors


# Global config instance
_config = None

def get_config() -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config