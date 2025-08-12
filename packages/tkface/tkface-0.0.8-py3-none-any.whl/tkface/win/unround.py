import sys

# Import Windows-specific modules only when needed
if sys.platform.startswith("win"):
    try:
        import ctypes
        from ctypes import wintypes
        import tkinter as tk
    except ImportError:
        ctypes = None
        wintypes = None
        tk = None

# DwmSetWindowAttribute constants
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_DONOTROUND = 1

# Global state for auto-unround feature
_auto_unround_enabled = False
_original_toplevel_init = None


def disable_window_corner_round(hwnd):
    """
    Disable window corner rounding for a specific window handle.
    Returns True if successful, False otherwise.
    """
    if not sys.platform.startswith("win") or ctypes is None:
        return False
    
    try:
        # Load dwmapi.dll
        dwmapi = ctypes.WinDLL("dwmapi")
        
        preference = ctypes.c_int(DWMWCP_DONOTROUND)
        result = dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            ctypes.c_uint(DWMWA_WINDOW_CORNER_PREFERENCE),
            ctypes.byref(preference),
            ctypes.sizeof(preference)
        )
        return result == 0
    except Exception:
        return False


def unround(root, auto_toplevel=True):
    """
    Disable window corner rounding for all windows under the given Tk root (Windows 11 only).
    Does nothing on other OSes.
    
    Args:
        root: Tkinter root window
        auto_toplevel (bool): If True, enables automatic unrounding for future Toplevel windows
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not sys.platform.startswith("win") or ctypes is None:
        return True  # Consider success on non-Windows platforms
    
    try:
        # Enable auto-unround for future Toplevel windows (like messageboxes)
        if auto_toplevel:
            enable_auto_unround()
        
        # Ensure window is fully created before applying unround
        root.update_idletasks()
        
        # Get the actual window handle using GetParent
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        success = disable_window_corner_round(hwnd)
        
        # Also handle existing Toplevel windows
        for w in root.winfo_children():
            if hasattr(w, 'winfo_id'):
                try:
                    child_hwnd = ctypes.windll.user32.GetParent(w.winfo_id())
                    disable_window_corner_round(child_hwnd)
                except Exception:
                    pass
        
        return success
    except Exception:
        return False

def _patched_toplevel_init(self, master=None, **kw):
    """Patched Toplevel.__init__ that automatically applies unround."""
    print(f"Creating Toplevel window with auto-unround...")
    
    # Call original __init__
    _original_toplevel_init(self, master, **kw)
    
    # Apply unround after window is created
    try:
        # Schedule multiple attempts at unround application
        self.after_idle(_apply_unround_to_toplevel, self)
        self.after(100, _apply_unround_to_toplevel, self)  # Retry after 100ms
        self.after(500, _apply_unround_to_toplevel, self)  # Retry after 500ms
        print("Scheduled multiple unround application attempts for Toplevel")
    except Exception as e:
        print(f"Failed to schedule unround, applying immediately: {e}")
        # If scheduling fails, try to apply immediately
        _apply_unround_to_toplevel(self)

def _apply_unround_to_toplevel(toplevel):
    """Apply unround to a Toplevel window."""
    if not sys.platform.startswith("win") or ctypes is None:
        return
    
    # Avoid duplicate applications
    if hasattr(toplevel, '_tkface_unround_applied'):
        return
    
    try:
        # Ensure window is fully created
        toplevel.update_idletasks()
        
        # Get window handle - try multiple methods
        hwnd = None
        
        # Method 1: Direct winfo_id (for Toplevel windows)
        try:
            hwnd = toplevel.winfo_id()
            if hwnd and hwnd != 0:
                print(f"Got Toplevel hwnd via winfo_id: {hwnd}")
            else:
                hwnd = None
        except Exception:
            hwnd = None
        
        # Method 2: GetParent (for embedded windows)
        if hwnd is None or hwnd == 0:
            try:
                hwnd = ctypes.windll.user32.GetParent(toplevel.winfo_id())
                if hwnd and hwnd != 0:
                    print(f"Got Toplevel hwnd via GetParent: {hwnd}")
                else:
                    hwnd = None
            except Exception:
                hwnd = None
        
        # Method 3: FindWindow by title (last resort)
        if hwnd is None or hwnd == 0:
            try:
                title = toplevel.title()
                if title:
                    hwnd = ctypes.windll.user32.FindWindowW(None, title)
                    if hwnd and hwnd != 0:
                        print(f"Got Toplevel hwnd via FindWindow: {hwnd}")
                    else:
                        hwnd = None
            except Exception:
                hwnd = None
        
        if hwnd and hwnd != 0:
            result = disable_window_corner_round(hwnd)
            print(f"Applied unround to Toplevel (hwnd: {hwnd}): {result}")
            if result:
                # Mark as successfully applied to avoid duplicate attempts
                toplevel._tkface_unround_applied = True
        else:
            print(f"Failed to get valid hwnd for Toplevel window")
            
    except Exception as e:
        print(f"Failed to apply unround to Toplevel: {e}")
        pass

def enable_auto_unround():
    """
    Enable automatic unrounding for all future Toplevel windows.
    This affects messageboxes, dialogs, and other popup windows.
    
    Returns:
        bool: True if auto-unround was enabled, False otherwise
    """
    global _auto_unround_enabled, _original_toplevel_init
    
    if not sys.platform.startswith("win") or ctypes is None or tk is None:
        print("Auto-unround: Not on Windows or missing dependencies")
        return False
    
    if _auto_unround_enabled:
        print("Auto-unround: Already enabled")
        return True  # Already enabled
    
    try:
        # Store original Toplevel.__init__
        _original_toplevel_init = tk.Toplevel.__init__
        
        # Replace with patched version
        tk.Toplevel.__init__ = _patched_toplevel_init
        
        _auto_unround_enabled = True
        print("Auto-unround: Successfully enabled, Toplevel.__init__ patched")
        return True
    except Exception as e:
        print(f"Auto-unround: Failed to enable: {e}")
        return False

def disable_auto_unround():
    """
    Disable automatic unrounding for Toplevel windows.
    
    Returns:
        bool: True if auto-unround was disabled, False otherwise
    """
    global _auto_unround_enabled, _original_toplevel_init
    
    if not _auto_unround_enabled or _original_toplevel_init is None:
        return True  # Already disabled or never enabled
    
    try:
        # Restore original Toplevel.__init__
        if tk is not None:
            tk.Toplevel.__init__ = _original_toplevel_init
        
        _auto_unround_enabled = False
        _original_toplevel_init = None
        return True
    except Exception:
        return False

def is_auto_unround_enabled():
    """
    Check if automatic unrounding is enabled.
    
    Returns:
        bool: True if auto-unround is enabled, False otherwise
    """
    return _auto_unround_enabled 