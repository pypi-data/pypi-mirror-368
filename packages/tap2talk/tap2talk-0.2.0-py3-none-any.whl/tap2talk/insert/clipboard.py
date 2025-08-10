"""Cross-platform clipboard management."""

import time
import platform

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False


class ClipboardManager:
    """Manage clipboard operations with preservation."""
    
    def __init__(self):
        if not PYPERCLIP_AVAILABLE:
            raise ImportError("pyperclip not available. Install with: pip install pyperclip")
        
        self.original_content = None
    
    def preserve(self):
        """Preserve current clipboard content."""
        try:
            self.original_content = pyperclip.paste()
        except Exception as e:
            print(f"Could not preserve clipboard: {e}")
            self.original_content = None
    
    def restore(self):
        """Restore preserved clipboard content."""
        if self.original_content is not None:
            try:
                pyperclip.copy(self.original_content)
            except Exception as e:
                print(f"Could not restore clipboard: {e}")
        self.original_content = None
    
    def set_text(self, text: str):
        """Set clipboard text."""
        pyperclip.copy(text)
    
    def get_text(self) -> str:
        """Get clipboard text."""
        return pyperclip.paste()


class ClipboardInserter:
    """Fallback text inserter using clipboard."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.clipboard = ClipboardManager()
    
    def insert_text(self, text: str) -> bool:
        """Insert text using clipboard and paste."""
        try:
            # Preserve original clipboard
            self.clipboard.preserve()
            
            # Set our text
            self.clipboard.set_text(text)
            
            # Trigger paste
            self._trigger_paste()
            
            # Wait a bit for paste to complete
            time.sleep(0.1)
            
            # Restore original clipboard
            self.clipboard.restore()
            
            return True
            
        except Exception as e:
            print(f"Failed to insert text via clipboard: {e}")
            return False
    
    def _trigger_paste(self):
        """Trigger paste keyboard shortcut."""
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                # Use AppleScript to trigger paste
                import subprocess
                script = 'tell application "System Events" to keystroke "v" using command down'
                subprocess.run(['osascript', '-e', script], check=True)
            
            elif system == "Windows":
                # Use pyautogui or keyboard to trigger Ctrl+V
                try:
                    import pyautogui
                    pyautogui.hotkey('ctrl', 'v')
                except ImportError:
                    try:
                        import keyboard
                        keyboard.press_and_release('ctrl+v')
                    except ImportError:
                        print("No keyboard automation library available")
                        return False
            
            else:  # Linux
                try:
                    import pyautogui
                    pyautogui.hotkey('ctrl', 'v')
                except ImportError:
                    print("pyautogui not available for paste")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Failed to trigger paste: {e}")
            return False