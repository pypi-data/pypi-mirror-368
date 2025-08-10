"""Windows hotkey listener."""

import threading
import time
from .base import HotkeyListener

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

try:
    import win32api
    import win32con
    import win32gui
    import ctypes
    from ctypes import wintypes
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class WindowsHotkeyListener(HotkeyListener):
    """Windows-specific hotkey listener."""
    
    def __init__(self, on_double_ctrl, on_double_esc, config):
        super().__init__(on_double_ctrl, on_double_esc, config)
        self.thread = None
        self.use_keyboard_lib = KEYBOARD_AVAILABLE
        
        if not KEYBOARD_AVAILABLE and not WIN32_AVAILABLE:
            raise ImportError("No keyboard library available. Install with: pip install keyboard or pywin32")
    
    def _keyboard_lib_listener(self):
        """Listen using keyboard library."""
        def on_ctrl():
            if self.detect_double_press("ctrl"):
                threading.Thread(target=self.on_double_ctrl, daemon=True).start()
        
        def on_esc():
            if self.detect_double_press("esc"):
                threading.Thread(target=self.on_double_esc, daemon=True).start()
        
        # Register hotkeys
        keyboard.on_press_key('ctrl', lambda _: on_ctrl())
        keyboard.on_press_key('esc', lambda _: on_esc())
        
        # Keep thread alive
        while self.running:
            time.sleep(0.1)
    
    def _win32_hook_listener(self):
        """Listen using Win32 low-level keyboard hook."""
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        WH_KEYBOARD_LL = 13
        VK_CONTROL = 0x11
        VK_LCONTROL = 0xA2
        VK_RCONTROL = 0xA3
        VK_ESCAPE = 0x1B
        
        def low_level_keyboard_proc(nCode, wParam, lParam):
            if nCode >= 0:
                if wParam == win32con.WM_KEYDOWN:
                    kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    vk_code = kb.vkCode
                    
                    # Check for control keys
                    if vk_code in (VK_CONTROL, VK_LCONTROL, VK_RCONTROL):
                        if self.detect_double_press("ctrl"):
                            threading.Thread(target=self.on_double_ctrl, daemon=True).start()
                    
                    # Check for escape key
                    elif vk_code == VK_ESCAPE:
                        if self.detect_double_press("esc"):
                            threading.Thread(target=self.on_double_esc, daemon=True).start()
            
            return ctypes.windll.user32.CallNextHookEx(hook, nCode, wParam, lParam)
        
        # Define hook structure
        class KBDLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [
                ("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
            ]
        
        # Set hook
        HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        hook_proc = HOOKPROC(low_level_keyboard_proc)
        
        hook = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            hook_proc,
            kernel32.GetModuleHandleW(None),
            0
        )
        
        if not hook:
            print("Failed to install hook")
            return
        
        # Message loop
        msg = wintypes.MSG()
        while self.running:
            bRet = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if bRet == 0:  # WM_QUIT
                break
            elif bRet == -1:  # Error
                print("Error in message loop")
                break
            else:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        
        # Unhook
        user32.UnhookWindowsHookEx(hook)
    
    def run_listener(self):
        """Run the appropriate listener."""
        try:
            if self.use_keyboard_lib:
                self._keyboard_lib_listener()
            else:
                self._win32_hook_listener()
        except Exception as e:
            print(f"Error in hotkey listener: {e}")
        finally:
            self.running = False
    
    def start(self):
        """Start listening for hotkeys."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.run_listener, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop listening for hotkeys."""
        if not self.running:
            return
        
        self.running = False
        
        # Unregister keyboard hooks if using keyboard lib
        if self.use_keyboard_lib and KEYBOARD_AVAILABLE:
            keyboard.unhook_all()
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)