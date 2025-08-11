"""Computer Split Screen MCP Server - Cross-platform window management via MCP."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import WindowManagementMCPServer
from .window_manager import (
    minimize_active_window,
    toggle_fullscreen,
    relocate_to_top_half,
    relocate_to_bottom_half,
    relocate_to_left_half,
    relocate_to_right_half,
    move_to_top_left_quadrant,
    move_to_top_right_quadrant,
    move_to_bottom_left_quadrant,
    move_to_bottom_right_quadrant,
)

__all__ = [
    "WindowManagementMCPServer",
    "minimize_active_window",
    "toggle_fullscreen",
    "relocate_to_top_half",
    "relocate_to_bottom_half",
    "relocate_to_left_half",
    "relocate_to_right_half",
    "move_to_top_left_quadrant",
    "move_to_top_right_quadrant",
    "move_to_bottom_left_quadrant",
    "move_to_bottom_right_quadrant",
]
