from . import lang
from . import win
from . import widget
from . import dialog

# Export Windows-specific flat button as Button
from .win.button import FlatButton as Button

# Export DPI functions for easy access
from .win.dpi import enable_dpi_geometry as dpi

# Export Calendar and DateEntry for backward compatibility
from .widget.calendar import Calendar
from .widget.datepicker import DateFrame, DateEntry

# Export messagebox and simpledialog for backward compatibility
from .dialog import messagebox, simpledialog

__version__ = "0.0.8"
__all__ = ["lang", "win", "widget", "dialog", "Button", "dpi", "Calendar", "DateFrame", "DateEntry", "messagebox", "simpledialog"] 