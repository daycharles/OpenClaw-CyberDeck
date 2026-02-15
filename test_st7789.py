#!/usr/bin/env python3
"""
Test script for Waveshare 1.3" ST7789 display.
Displays test pattern and notifications.
"""

import time
import sys

from display_st7789_uno_q import ST7789Display


def main():
    print("=== Waveshare 1.3\" ST7789 Display Test ===")
    print("Testing 240x240 status panel...")
    
    # Create display
    display = ST7789Display(demo_mode=False)
    
    # Initialize
    if not display.initialize():
        print("ERROR: Failed to initialize display")
        sys.exit(1)
        
    print("Display initialized successfully!")
    
    # Start display
    display.start()
    
    try:
        # Test 1: Initial status
        print("\nTest 1: Initial status")
        display.set_status("System ready", connected=False)
        time.sleep(2)
        
        # Test 2: Connected status
        print("Test 2: Connected status")
        display.set_status("Connected to OpenClaw", connected=True)
        time.sleep(2)
        
        # Test 3: Add notifications
        print("Test 3: Notifications")
        display.add_notification("Info", "System started", "info")
        time.sleep(1)
        
        display.add_notification("Success", "Connection established", "success")
        time.sleep(1)
        
        display.add_notification("Warning", "High CPU usage", "warning")
        time.sleep(1)
        
        display.add_notification("Error", "Network timeout", "error")
        time.sleep(2)
        
        # Test 4: Rapid notifications (test scrolling)
        print("Test 4: Rapid notifications")
        for i in range(5):
            display.add_notification(f"Message {i+1}", f"Test notification {i+1}", "info")
            time.sleep(0.5)
            
        print("\nTest complete! Display will remain on for 10 seconds...")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        
    finally:
        # Cleanup
        display.stop()
        print("Display stopped")
        

if __name__ == "__main__":
    main()

