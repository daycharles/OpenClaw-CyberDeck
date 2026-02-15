#!/usr/bin/env python3
"""
Test script for HiLetgo 2.4" ILI9341 display.
Displays test pattern with command buttons.
"""

import time
import sys

from display_status import StatusDisplay


def main():
    print("=== HiLetgo 2.4\" ILI9341 Display Test ===")
    print("Testing 240x320 command panel...")
    
    # Create display
    display = StatusDisplay(demo_mode=False)
    
    # Initialize
    if not display.initialize():
        print("ERROR: Failed to initialize display")
        sys.exit(1)
        
    print("Display initialized successfully!")
    
    # Setup command callback
    def on_command(command):
        print(f"Command received: {command}")
        display.show_notification("info", "Command", command)
        
    display.command_panel.set_command_callback(on_command)
    
    # Start display
    display.start()
    
    try:
        # Test 1: Initial state
        print("\nTest 1: Initial state")
        display.update_status({
            "connected": False,
            "model": "unknown",
            "api_cost": 0.0,
        })
        time.sleep(2)
        
        # Test 2: Connected state
        print("Test 2: Connected state")
        display.update_status({
            "connected": True,
            "model": "gpt-4",
            "api_cost": 0.0012,
            "queue_count": 3,
        })
        time.sleep(2)
        
        # Test 3: Notifications
        print("Test 3: Notifications")
        display.show_notification("info", "Info", "System ready")
        time.sleep(1)
        
        display.show_notification("success", "Success", "Connected")
        time.sleep(1)
        
        display.show_notification("warning", "Warning", "High usage")
        time.sleep(1)
        
        display.show_notification("error", "Error", "Network timeout")
        time.sleep(2)
        
        # Test 4: Simulate button presses
        print("Test 4: Simulating button presses")
        buttons = ["INBOX", "QUEUE", "STATUS", "BRIEF", "FOCUS", "RANDOM"]
        for button in buttons:
            print(f"  Simulating: {button}")
            on_command(button)
            time.sleep(1)
            
        print("\nTest complete! Display will remain on for 10 seconds...")
        print("Try touching the buttons if touch is connected!")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        
    finally:
        # Cleanup
        display.stop()
        print("Display stopped")
        

if __name__ == "__main__":
    main()

