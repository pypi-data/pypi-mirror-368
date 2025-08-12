"""
Windows-specific features for tkface.

This module provides Windows-specific enhancements for Tkinter applications.
All functions in this module are designed to work on Windows platforms and
will gracefully degrade or do nothing on other platforms.

Available features:
- DPI awareness and scaling
- Windows-specific button styling (flat buttons)
- Windows system sounds
- Windows 11 corner rounding control
"""

import sys

def is_windows():
    """
    Check if running on Windows platform.
    
    Returns:
        bool: True if running on Windows, False otherwise
    """
    return sys.platform == 'win32'

from .dpi import (
    dpi,
    get_scaling_factor,
    enable_dpi_geometry,
    get_actual_window_size,
    enable_dpi_awareness,
    calculate_dpi_sizes,
    scale_icon,
    scale_font_size,
    get_effective_dpi,
    logical_to_physical,
    physical_to_logical,
    enable_auto_dpi_scaling,
    disable_auto_dpi_scaling,
    is_auto_dpi_scaling_enabled,
    scale_widget_dimensions,
    scale_widget_tree,
    get_scalable_properties,
    add_scalable_property,
    remove_scalable_property,
)
from .button import configure_button_for_windows, get_button_label_with_shortcut, FlatButton, create_flat_button
from .unround import unround, enable_auto_unround, disable_auto_unround, is_auto_unround_enabled
from .bell import bell

__all__ = [
    'is_windows',
    'dpi', 'get_scaling_factor', 'enable_dpi_geometry', 'get_actual_window_size', 'enable_dpi_awareness', 'calculate_dpi_sizes', 'scale_icon', 'scale_font_size',
    'get_effective_dpi', 'logical_to_physical', 'physical_to_logical',
    'enable_auto_dpi_scaling', 'disable_auto_dpi_scaling', 'is_auto_dpi_scaling_enabled',
    'scale_widget_dimensions', 'scale_widget_tree', 'get_scalable_properties', 'add_scalable_property', 'remove_scalable_property',
    'configure_button_for_windows', 'get_button_label_with_shortcut', 
    'FlatButton', 'create_flat_button',
    'unround', 'enable_auto_unround', 'disable_auto_unround', 'is_auto_unround_enabled', 
    'bell'
]