#!/usr/bin/env python3
"""Example script demonstrating basic usage of the window management functions."""

import time
from computer_split_screen_mcp import (
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


def demo_window_management():
    """Demonstrate various window management operations."""
    print("🚀 Computer Split Screen MCP - Demo Mode")
    print("=" * 50)
    print("This demo will move your active window to different positions.")
    print("Make sure you have a window active/focused!")
    print()
    
    # Wait for user to focus a window
    print("⏳ Please focus a window you want to control, then press Enter...")
    input()
    
    print("\n🎯 Starting window management demo...")
    print("Each operation will wait 3 seconds before proceeding.")
    
    # Demo half-screen operations
    print("\n📱 Testing Half-Screen Operations:")
    
    print("  → Moving to top half...")
    relocate_to_top_half()
    time.sleep(3)
    
    print("  → Moving to bottom half...")
    relocate_to_bottom_half()
    time.sleep(3)
    
    print("  → Moving to left half...")
    relocate_to_left_half()
    time.sleep(3)
    
    print("  → Moving to right half...")
    relocate_to_right_half()
    time.sleep(3)
    
    # Demo quadrant operations
    print("\n🔲 Testing Quadrant Operations:")
    
    print("  → Moving to top-left quadrant...")
    move_to_top_left_quadrant()
    time.sleep(3)
    
    print("  → Moving to top-right quadrant...")
    move_to_top_right_quadrant()
    time.sleep(3)
    
    print("  → Moving to bottom-left quadrant...")
    move_to_bottom_left_quadrant()
    time.sleep(3)
    
    print("  → Moving to bottom-right quadrant...")
    move_to_bottom_right_quadrant()
    time.sleep(3)
    
    # Demo window state operations
    print("\n🔄 Testing Window State Operations:")
    
    print("  → Toggling fullscreen...")
    toggle_fullscreen()
    time.sleep(3)
    
    print("  → Minimizing window...")
    minimize_active_window()
    time.sleep(2)
    
    print("\n✅ Demo completed!")
    print("Your window should now be minimized.")
    print("You can restore it from your taskbar/dock.")


if __name__ == "__main__":
    try:
        demo_window_management()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("Make sure you have the package installed and a window focused.")
