from .wx_helper import ensure_wxpython

# Optionally: auto-fix wxPython on import
if not ensure_wxpython():
    raise ImportError("wxPython could not be installed automatically. Please install it manually.")