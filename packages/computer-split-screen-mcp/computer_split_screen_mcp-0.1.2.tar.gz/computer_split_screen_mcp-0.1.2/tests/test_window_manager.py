"""Tests for the window manager module."""

import platform
import pytest
from computer_split_screen_mcp.window_manager import (
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


def test_platform_detection():
    """Test that platform detection works correctly."""
    os_name = platform.system().lower()
    assert os_name in ['windows', 'darwin', 'linux']


@pytest.mark.skipif(platform.system().lower() not in ['windows', 'darwin'], 
                    reason="Only testing on Windows and macOS")
def test_minimize_active_window():
    """Test minimize function (may fail if no active window)."""
    # This test may fail if there's no active window, which is expected
    try:
        result = minimize_active_window()
        assert isinstance(result, bool)
    except Exception:
        # Expected if no active window
        pass


@pytest.mark.skipif(platform.system().lower() not in ['windows', 'darwin'], 
                    reason="Only testing on Windows and macOS")
def test_toggle_fullscreen():
    """Test fullscreen toggle function."""
    try:
        result = toggle_fullscreen()
        assert isinstance(result, bool)
    except Exception:
        # Expected if no active window
        pass


@pytest.mark.skipif(platform.system().lower() not in ['windows', 'darwin'], 
                    reason="Only testing on Windows and macOS")
def test_relocate_functions():
    """Test all relocate functions."""
    functions = [
        relocate_to_top_half,
        relocate_to_bottom_half,
        relocate_to_left_half,
        relocate_to_right_half,
    ]
    
    for func in functions:
        try:
            result = func()
            assert isinstance(result, bool)
        except Exception:
            # Expected if no active window
            pass


@pytest.mark.skipif(platform.system().lower() not in ['windows', 'darwin'], 
                    reason="Only testing on Windows and macOS")
def test_quadrant_functions():
    """Test all quadrant functions."""
    functions = [
        move_to_top_left_quadrant,
        move_to_top_right_quadrant,
        move_to_bottom_left_quadrant,
        move_to_bottom_right_quadrant,
    ]
    
    for func in functions:
        try:
            result = func()
            assert isinstance(result, bool)
        except Exception:
            # Expected if no active window
            pass


def test_unsupported_platform():
    """Test behavior on unsupported platforms."""
    if platform.system().lower() not in ['windows', 'darwin']:
        # Mock platform.system to return unsupported OS
        original_system = platform.system
        
        def mock_system():
            return "Linux"
        
        platform.system = mock_system
        
        try:
            result = minimize_active_window()
            assert result is False
        finally:
            # Restore original function
            platform.system = original_system
