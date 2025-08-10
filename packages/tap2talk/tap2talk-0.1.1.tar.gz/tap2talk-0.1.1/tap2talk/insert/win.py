"""Windows text insertion using SendInput and clipboard."""

import time
import ctypes
from ctypes import wintypes
from .clipboard import ClipboardManager

try:
    import win32clipboard
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class WindowsTextInserter:
    """Windows-specific text inserter with SendInput and clipboard fallback."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.clipboard = ClipboardManager()
        
        # Windows API setup
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
    
    def insert_text(self, text: str) -> bool:
        """Insert text at current cursor position."""
        # Try direct injection first
        if self._inject_text(text):
            return True
        
        # Fallback to clipboard method
        return self._insert_via_clipboard(text)
    
    def _inject_text(self, text: str) -> bool:
        """Directly inject text using SendInput."""
        try:
            # Define INPUT structure
            class KEYBDINPUT(ctypes.Structure):
                _fields_ = [
                    ("wVk", wintypes.WORD),
                    ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                ]
            
            class INPUT(ctypes.Structure):
                class _INPUT(ctypes.Union):
                    _fields_ = [("ki", KEYBDINPUT)]
                
                _anonymous_ = ("_input",)
                _fields_ = [
                    ("type", wintypes.DWORD),
                    ("_input", _INPUT)
                ]
            
            KEYEVENTF_UNICODE = 0x0004
            KEYEVENTF_KEYUP = 0x0002
            INPUT_KEYBOARD = 1
            
            # Process each character
            inputs = []
            for char in text:
                # Get Unicode code point
                code = ord(char)
                
                # Handle special characters
                if char == '\n':
                    # Enter key
                    key_down = INPUT()
                    key_down.type = INPUT_KEYBOARD
                    key_down.ki.wVk = 0x0D  # VK_RETURN
                    inputs.append(key_down)
                    
                    key_up = INPUT()
                    key_up.type = INPUT_KEYBOARD
                    key_up.ki.wVk = 0x0D
                    key_up.ki.dwFlags = KEYEVENTF_KEYUP
                    inputs.append(key_up)
                else:
                    # Unicode character
                    key_down = INPUT()
                    key_down.type = INPUT_KEYBOARD
                    key_down.ki.wScan = code
                    key_down.ki.dwFlags = KEYEVENTF_UNICODE
                    inputs.append(key_down)
                    
                    key_up = INPUT()
                    key_up.type = INPUT_KEYBOARD
                    key_up.ki.wScan = code
                    key_up.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
                    inputs.append(key_up)
            
            # Send all inputs
            if inputs:
                n_inputs = len(inputs)
                input_array = (INPUT * n_inputs)(*inputs)
                sent = self.user32.SendInput(n_inputs, ctypes.byref(input_array), ctypes.sizeof(INPUT))
                
                if sent != n_inputs:
                    print(f"SendInput only sent {sent}/{n_inputs} inputs")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Direct injection failed: {e}")
            return False
    
    def _insert_via_clipboard(self, text: str) -> bool:
        """Insert text using clipboard and paste."""
        try:
            # Preserve clipboard
            original = self._get_clipboard_text()
            
            # Set text
            self._set_clipboard_text(text)
            
            # Trigger paste
            self._trigger_paste()
            
            # Wait for paste
            time.sleep(0.1)
            
            # Restore clipboard
            if original is not None:
                self._set_clipboard_text(original)
            
            return True
            
        except Exception as e:
            print(f"Clipboard insertion failed: {e}")
            return False
    
    def _get_clipboard_text(self) -> str:
        """Get text from Windows clipboard."""
        if WIN32_AVAILABLE:
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    return data
                return None
            except Exception as e:
                print(f"Failed to get clipboard: {e}")
                return None
            finally:
                win32clipboard.CloseClipboard()
        else:
            return self.clipboard.get_text()
    
    def _set_clipboard_text(self, text: str):
        """Set text to Windows clipboard."""
        if WIN32_AVAILABLE:
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            except Exception as e:
                print(f"Failed to set clipboard: {e}")
            finally:
                win32clipboard.CloseClipboard()
        else:
            self.clipboard.set_text(text)
    
    def _trigger_paste(self):
        """Trigger Ctrl+V using SendInput."""
        try:
            class KEYBDINPUT(ctypes.Structure):
                _fields_ = [
                    ("wVk", wintypes.WORD),
                    ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                ]
            
            class INPUT(ctypes.Structure):
                class _INPUT(ctypes.Union):
                    _fields_ = [("ki", KEYBDINPUT)]
                
                _anonymous_ = ("_input",)
                _fields_ = [
                    ("type", wintypes.DWORD),
                    ("_input", _INPUT)
                ]
            
            INPUT_KEYBOARD = 1
            KEYEVENTF_KEYUP = 0x0002
            VK_CONTROL = 0x11
            VK_V = 0x56
            
            inputs = []
            
            # Press Ctrl
            ctrl_down = INPUT()
            ctrl_down.type = INPUT_KEYBOARD
            ctrl_down.ki.wVk = VK_CONTROL
            inputs.append(ctrl_down)
            
            # Press V
            v_down = INPUT()
            v_down.type = INPUT_KEYBOARD
            v_down.ki.wVk = VK_V
            inputs.append(v_down)
            
            # Release V
            v_up = INPUT()
            v_up.type = INPUT_KEYBOARD
            v_up.ki.wVk = VK_V
            v_up.ki.dwFlags = KEYEVENTF_KEYUP
            inputs.append(v_up)
            
            # Release Ctrl
            ctrl_up = INPUT()
            ctrl_up.type = INPUT_KEYBOARD
            ctrl_up.ki.wVk = VK_CONTROL
            ctrl_up.ki.dwFlags = KEYEVENTF_KEYUP
            inputs.append(ctrl_up)
            
            # Send inputs
            n_inputs = len(inputs)
            input_array = (INPUT * n_inputs)(*inputs)
            self.user32.SendInput(n_inputs, ctypes.byref(input_array), ctypes.sizeof(INPUT))
            
            return True
            
        except Exception as e:
            print(f"Failed to trigger paste: {e}")
            return False