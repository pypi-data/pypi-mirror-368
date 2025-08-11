"""Cross-Platform Window Management Module for MCP Server."""

import platform
import subprocess
from typing import Optional

# Windows-specific imports
try:
    import ctypes
except ImportError:
    pass


def minimize_active_window() -> bool:
    """
    Cross-platform function to minimize the currently active window.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _minimize_windows()
    elif os_name == 'darwin': 
        return _minimize_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def toggle_fullscreen() -> bool:
    """
    Cross-platform function to toggle fullscreen mode.
    - Windows: Resizes to work area (fake fullscreen)
    - macOS: Triggers native fullscreen shortcut
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _toggle_fullscreen_windows()
    elif os_name == 'darwin': 
        return _toggle_fullscreen_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def relocate_to_top_half() -> bool:
    """
    Cross-platform function to relocate the active window to the top half of the screen.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _relocate_to_top_half_windows()
    elif os_name == 'darwin': 
        return _relocate_to_top_half_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def relocate_to_bottom_half() -> bool:
    """
    Cross-platform function to relocate the active window to the bottom half of the screen.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _relocate_to_bottom_half_windows()
    elif os_name == 'darwin': 
        return _relocate_to_bottom_half_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def relocate_to_left_half() -> bool:
    """
    Cross-platform function to relocate the active window to the left half of the screen.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _relocate_to_left_half_windows()
    elif os_name == 'darwin': 
        return _relocate_to_left_half_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def relocate_to_right_half() -> bool:
    """
    Cross-platform function to relocate the active window to the right half of the screen.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _relocate_to_right_half_windows()
    elif os_name == 'darwin': 
        return _relocate_to_right_half_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def move_to_top_left_quadrant() -> bool:
    """
    Cross-platform function to move the active window to the top-left quadrant.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _move_to_top_left_quadrant_windows()
    elif os_name == 'darwin': 
        return _move_to_top_left_quadrant_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def move_to_top_right_quadrant() -> bool:
    """
    Cross-platform function to move the active window to the top-right quadrant.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _move_to_top_right_quadrant_windows()
    elif os_name == 'darwin': 
        return _move_to_top_right_quadrant_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def move_to_bottom_left_quadrant() -> bool:
    """
    Cross-platform function to move the active window to the bottom-left quadrant.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _move_to_bottom_left_quadrant_windows()
    elif os_name == 'darwin': 
        return _move_to_bottom_left_quadrant_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def move_to_bottom_right_quadrant() -> bool:
    """
    Cross-platform function to move the active window to the bottom-right quadrant.
    Automatically detects OS and uses appropriate method.
    
    Returns:
        bool: True if successful, False otherwise
    """
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        return _move_to_bottom_right_quadrant_windows()
    elif os_name == 'darwin': 
        return _move_to_bottom_right_quadrant_macos()
    else:
        print("❌ Unsupported operating system")
        return False


def _minimize_windows() -> bool:
    """Windows-specific minimize implementation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        result = ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE = 6
        
        if result:
            print("✅ Successfully minimized active window")
            return True
        else:
            print("❌ Failed to minimize window")
            return False
            
    except Exception as e:
        print(f"❌ Error minimizing window: {e}")
        return False


def _minimize_macos() -> bool:
    """macOS-specific minimize implementation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                set value of attribute "AXMinimized" of frontWindow to true
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully minimized active window")
            return True
        else:
            print(f"❌ Failed to minimize window: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error minimizing window: {e}")
        return False


def _toggle_fullscreen_windows() -> bool:
    """Windows-specific fullscreen implementation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Get work area dimensions
        work_area_width = ctypes.windll.user32.GetSystemMetrics(78) # SM_CXWORKAREA
        work_area_height = ctypes.windll.user32.GetSystemMetrics(79) # SM_CYWORKAREA
        
        # Calculate new dimensions to fit work area
        new_width = work_area_width
        new_height = work_area_height
        
        # Set window position to 0,0
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, 0, 0, new_width, new_height, 
            0x0000  # No flags
        )
        
        if result:
            print("✅ Successfully toggled fullscreen")
            return True
        else:
            print("❌ Failed to toggle fullscreen")
            return False
            
    except Exception as e:
        print(f"❌ Error toggling fullscreen: {e}")
        return False


def _toggle_fullscreen_macos() -> bool:
    """macOS-specific fullscreen implementation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                set value of attribute "AXFullScreen" of frontWindow to true
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully toggled fullscreen")
            return True
        else:
            print(f"❌ Failed to toggle fullscreen: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error toggling fullscreen: {e}")
        return False


def _relocate_to_top_half_windows() -> bool:
    """Windows-specific top half relocation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Calculate top half dimensions
        window_width = screen_width
        window_height = screen_height // 2
        
        # Set window position and size
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, 0, 0, window_width, window_height, 
            0x0040  # SWP_NOMOVE | SWP_NOZORDER
        )
        
        if result:
            print("✅ Successfully relocated window to top half")
            return True
        else:
            print("❌ Failed to relocate window to top half")
            return False
            
    except Exception as e:
        print(f"❌ Error relocating window to top half: {e}")
        return False


def _relocate_to_top_half_macos() -> bool:
    """macOS-specific top half relocation using AppleScript"""
    try:
        # Try multiple approaches for screen detection
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                
                -- Try to get screen bounds, fallback to common resolution
                try
                    set screenBounds to bounds of (get desktop)
                    set screenWidth to (item 3 of screenBounds) - (item 1 of screenBounds)
                    set screenHeight to (item 4 of screenBounds) - (item 2 of screenBounds)
                on error
                    -- Fallback to common screen resolution (adjust as needed)
                    set screenWidth to 1512
                    set screenHeight to 945
                end try
                
                set windowWidth to screenWidth
                set windowHeight to screenHeight / 2
                
                -- Try to set position and size separately instead of bounds
                try
                    set position of frontWindow to {0, 0}
                    set size of frontWindow to {windowWidth, windowHeight}
                on error
                    -- If that fails, try bounds as last resort
                    set bounds of frontWindow to {0, 0, windowWidth, windowHeight}
                end try
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully relocated window to top half")
            return True
        else:
            print(f"❌ Failed to relocate window to top half: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error relocating window to top half: {e}")
        return False


def _relocate_to_bottom_half_windows() -> bool:
    """Windows-specific bottom half relocation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Calculate bottom half dimensions and position
        window_width = screen_width
        window_height = screen_height // 2
        window_x = 0
        window_y = screen_height // 2  # Start at middle of screen
        
        # Set window position and size
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, window_x, window_y, window_width, window_height, 
            0x0000  # No flags
        )
        
        if result:
            print("✅ Successfully relocated window to bottom half")
            return True
        else:
            print("❌ Failed to relocate window to bottom half")
            return False
            
    except Exception as e:
        print(f"❌ Error relocating window to bottom half: {e}")
        return False


def _relocate_to_bottom_half_macos() -> bool:
    """macOS-specific bottom half relocation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                
                -- Try to get screen bounds, fallback to common resolution
                try
                    set screenBounds to bounds of (get desktop)
                    set screenWidth to (item 3 of screenBounds) - (item 1 of screenBounds)
                    set screenHeight to (item 4 of screenBounds) - (item 2 of screenBounds)
                on error
                    -- Fallback to common screen resolution (adjust as needed)
                    set screenWidth to 1512
                    set screenHeight to 945
                end try
                
                -- Adjust height to account for dock (reduce height by ~8% to fit above dock)
                set windowWidth to screenWidth
                set windowHeight to (screenHeight / 2) * 0.92
                set windowX to 0
                set windowY to screenHeight / 2
                
                -- Try to set position and size separately
                try
                    set position of frontWindow to {windowX, windowY}
                    set size of frontWindow to {windowWidth, windowHeight}
                on error
                    -- If that fails, try bounds as last resort
                    set bounds of frontWindow to {windowX, windowY, windowX + windowWidth, windowY + windowHeight}
                end try
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully relocated window to bottom half")
            return True
        else:
            print(f"❌ Failed to relocate window to bottom half: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error relocating window to bottom half: {e}")
        return False


def _relocate_to_left_half_windows() -> bool:
    """Windows-specific left half relocation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Calculate left half dimensions
        window_width = screen_width // 2
        window_height = screen_height
        window_x = 0
        window_y = 0
        
        # Set window position and size
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, window_x, window_y, window_width, window_height, 
            0x0000  # No flags
        )
        
        if result:
            print("✅ Successfully relocated window to left half")
            return True
        else:
            print("❌ Failed to relocate window to left half")
            return False
            
    except Exception as e:
        print(f"❌ Error relocating window to left half: {e}")
        return False


def _relocate_to_left_half_macos() -> bool:
    """macOS-specific left half relocation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                
                -- Try to get screen bounds, fallback to common resolution
                try
                    set screenBounds to bounds of (get desktop)
                    set screenWidth to (item 3 of screenBounds) - (item 1 of screenBounds)
                    set screenHeight to (item 4 of screenBounds) - (item 2 of screenBounds)
                on error
                    -- Fallback to common screen resolution (adjust as needed)
                    set screenWidth to 1512
                    set screenHeight to 945
                end try
                
                set windowWidth to screenWidth / 2
                set windowHeight to screenHeight
                set windowX to 0
                set windowY to 0
                
                -- Try to set position and size separately
                try
                    set position of frontWindow to {windowX, windowY}
                    set size of frontWindow to {windowWidth, windowY}
                on error
                    -- If that fails, try bounds as last resort
                    set bounds of frontWindow to {windowX, windowY, windowX + windowWidth, windowY + windowHeight}
                end try
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully relocated window to left half")
            return True
        else:
            print(f"❌ Failed to relocate window to left half: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error relocating window to left half: {e}")
        return False


def _relocate_to_right_half_windows() -> bool:
    """Windows-specific right half relocation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Calculate right half dimensions and position
        window_width = screen_width // 2
        window_height = screen_height
        window_x = screen_width // 2  # Start at middle of screen
        window_y = 0
        
        # Set window position and size
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, window_x, window_y, window_width, window_height, 
            0x0000  # No flags
        )
        
        if result:
            print("✅ Successfully relocated window to right half")
            return True
        else:
            print("❌ Failed to relocate window to right half")
            return False
            
    except Exception as e:
        print(f"❌ Error relocating window to right half: {e}")
        return False


def _relocate_to_right_half_macos() -> bool:
    """macOS-specific right half relocation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                
                -- Try to get screenBounds, fallback to common resolution
                try
                    set screenBounds to bounds of (get desktop)
                    set screenWidth to (item 3 of screenBounds) - (item 1 of screenBounds)
                    set screenHeight to (item 4 of screenBounds) - (item 2 of screenBounds)
                on error
                    -- Fallback to common screen resolution (adjust as needed)
                    set screenWidth to 1512
                    set screenHeight to 945
                end try
                
                set windowWidth to screenWidth / 2
                set windowHeight to screenHeight
                set windowX to screenWidth / 2
                set windowY to 0
                
                -- Try to set position and size separately
                try
                    set position of frontWindow to {windowX, windowY}
                    set size of frontWindow to {windowWidth, windowHeight}
                on error
                    -- If that fails, try bounds as last resort
                    set bounds of frontWindow to {windowX, windowY, windowX + windowWidth, windowY + windowHeight}
                end try
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully relocated window to right half")
            return True
        else:
            print(f"❌ Failed to relocate window to right half: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error relocating window to right half: {e}")
        return False


def _move_to_top_left_quadrant_windows() -> bool:
    """Windows-specific top-left quadrant implementation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Calculate quadrant dimensions and position
        window_width = screen_width // 2
        window_height = screen_height // 2
        window_x = 0
        window_y = 0
        
        # Set window position and size
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, window_x, window_y, window_width, window_height, 
            0x0000  # No flags
        )
        
        if result:
            print("✅ Successfully moved window to top-left quadrant")
            return True
        else:
            print("❌ Failed to move window to top-left quadrant")
            return False
            
    except Exception as e:
        print(f"❌ Error moving window to top-left quadrant: {e}")
        return False


def _move_to_top_right_quadrant_windows() -> bool:
    """Windows-specific top-right quadrant implementation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Calculate quadrant dimensions and position
        window_width = screen_width // 2
        window_height = screen_height // 2
        window_x = screen_width // 2
        window_y = 0
        
        # Set window position and size
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, window_x, window_y, window_width, window_height, 
            0x0000  # No flags
        )
        
        if result:
            print("✅ Successfully moved window to top-right quadrant")
            return True
        else:
            print("❌ Failed to move window to top-right quadrant")
            return False
            
    except Exception as e:
        print(f"❌ Error moving window to top-right quadrant: {e}")
        return False


def _move_to_bottom_left_quadrant_windows() -> bool:
    """Windows-specific bottom-left quadrant implementation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Calculate quadrant dimensions and position
        window_width = screen_width // 2
        window_height = screen_height // 2
        window_x = 0
        window_y = screen_height // 2
        
        # Set window position and size
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, window_x, window_y, window_width, window_height, 
            0x0000  # No flags
        )
        
        if result:
            print("✅ Successfully moved window to bottom-left quadrant")
            return True
        else:
            print("❌ Failed to move window to bottom-left quadrant")
            return False
            
    except Exception as e:
        print(f"❌ Error moving window to bottom-left quadrant: {e}")
        return False


def _move_to_bottom_right_quadrant_windows() -> bool:
    """Windows-specific bottom-right quadrant implementation using user32.dll"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        if hwnd == 0:
            print("❌ No active window found")
            return False
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # Calculate quadrant dimensions and position
        window_width = screen_width // 2
        window_height = screen_height // 2
        window_x = screen_width // 2
        window_y = screen_height // 2
        
        # Set window position and size
        result = ctypes.windll.user32.SetWindowPos(
            hwnd, 0, window_x, window_y, window_width, window_height, 
            0x0000  # No flags
        )
        
        if result:
            print("✅ Successfully moved window to bottom-right quadrant")
            return True
        else:
            print("❌ Failed to move window to bottom-right quadrant")
            return False
            
    except Exception as e:
        print(f"❌ Error moving window to bottom-right quadrant: {e}")
        return False


def _move_to_top_left_quadrant_macos() -> bool:
    """macOS-specific top-left quadrant implementation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                
                -- Try to get screen bounds, fallback to common resolution
                try
                    set screenBounds to bounds of (get desktop)
                    set screenWidth to (item 3 of screenBounds) - (item 1 of screenBounds)
                    set screenHeight to (item 4 of screenBounds) - (item 2 of screenBounds)
                on error
                    -- Fallback to common screen resolution (adjust as needed)
                    set screenWidth to 1512
                    set screenHeight to 945
                end try
                
                set windowWidth to screenWidth / 2
                set windowHeight to screenHeight / 2
                set windowX to 0
                set windowY to 0
                
                -- Try to set position and size separately
                try
                    set position of frontWindow to {windowX, windowY}
                    set size of frontWindow to {windowWidth, windowHeight}
                on error
                    -- If that fails, try bounds as last resort
                    set bounds of frontWindow to {windowX, windowY, windowX + windowWidth, windowY + windowHeight}
                end try
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully moved window to top-left quadrant")
            return True
        else:
            print(f"❌ Failed to move window to top-left quadrant: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error moving window to top-left quadrant: {e}")
        return False


def _move_to_top_right_quadrant_macos() -> bool:
    """macOS-specific top-right quadrant implementation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                
                -- Try to get screen bounds, fallback to common resolution
                try
                    set screenBounds to bounds of (get desktop)
                    set screenWidth to (item 3 of screenBounds) - (item 1 of screenBounds)
                    set screenHeight to (item 4 of screenBounds) - (item 2 of screenBounds)
                on error
                    -- Fallback to common screen resolution (adjust as needed)
                    set screenWidth to 1512
                    set screenHeight to 945
                end try
                
                set windowWidth to screenWidth / 2
                set windowHeight to screenHeight / 2
                set windowX to screenWidth / 2
                set windowY to 0
                
                -- Try to set position and size separately
                try
                    set position of frontWindow to {windowX, windowY}
                    set size of frontWindow to {windowWidth, windowHeight}
                on error
                    -- If that fails, try bounds as last resort
                    set bounds of frontWindow to {windowX, windowY, windowX + windowWidth, windowY + windowHeight}
                end try
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully moved window to top-right quadrant")
            return True
        else:
            print(f"❌ Failed to move window to top-right quadrant: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error moving window to top-right quadrant: {e}")
        return False


def _move_to_bottom_left_quadrant_macos() -> bool:
    """macOS-specific bottom-left quadrant implementation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                
                -- Try to get screen bounds, fallback to common resolution
                try
                    set screenBounds to bounds of (get desktop)
                    set screenWidth to (item 3 of screenBounds) - (item 1 of screenBounds)
                    set screenHeight to (item 4 of screenBounds) - (item 2 of screenBounds)
                on error
                    -- Fallback to common screen resolution (adjust as needed)
                    set screenWidth to 1512
                    set screenHeight to 945
                end try
                
                -- Adjust height to account for dock (reduce height by ~8% to fit above dock)
                set windowWidth to screenWidth / 2
                set windowHeight to (screenHeight / 2) * 0.92
                set windowX to 0
                set windowY to screenHeight / 2
                
                -- Try to set position and size separately
                try
                    set position of frontWindow to {windowX, windowY}
                    set size of frontWindow to {windowWidth, windowHeight}
                on error
                    -- If that fails, try bounds as last resort
                    set bounds of frontWindow to {windowX, windowY, windowX + windowWidth, windowY + windowHeight}
                end try
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully moved window to bottom-left quadrant")
            return True
        else:
            print(f"❌ Failed to move window to bottom-left quadrant: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error moving window to bottom-left quadrant: {e}")
        return False


def _move_to_bottom_right_quadrant_macos() -> bool:
    """macOS-specific bottom-right quadrant implementation using AppleScript"""
    try:
        apple_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            tell process frontApp
                set frontWindow to window 1
                
                -- Try to get screen bounds, fallback to common resolution
                try
                    set screenBounds to bounds of (get desktop)
                    set screenWidth to (item 3 of screenBounds) - (item 1 of screenBounds)
                    set screenHeight to (item 4 of screenBounds) - (item 2 of screenBounds)
                on error
                    -- Fallback to common screen resolution (adjust as needed)
                    set screenWidth to 1512
                    set screenHeight to 945
                end try
                
                -- Adjust height to account for dock (reduce height by ~8% to fit above dock)
                set windowWidth to screenWidth / 2
                set windowHeight to (screenHeight / 2) * 0.92
                set windowX to screenWidth / 2
                set windowY to screenHeight / 2
                
                -- Try to set position and size separately
                try
                    set position of frontWindow to {windowX, windowY}
                    set size of frontWindow to {windowWidth, windowHeight}
                on error
                    -- If that fails, try bounds as last resort
                    set bounds of frontWindow to {windowX, windowY, windowX + windowWidth, windowY + windowHeight}
                end try
            end tell
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', apple_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully moved window to bottom-right quadrant")
            return True
        else:
            print(f"❌ Failed to move window to bottom-right quadrant: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AppleScript execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error moving window to bottom-right quadrant: {e}")
        return False
