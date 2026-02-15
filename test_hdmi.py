#!/usr/bin/env python3
"""
Test script for ElecLab 7" HDMI display.
Displays test pattern with Molty and activity feed.
"""

import time
import sys

from display_hdmi import HDMIDisplay
from ui.molty import MoltyState


def main():
    print("=== ElecLab 7\" HDMI Display Test ===")
    print("Testing 1024x600 main display...")
    
    # Create display
    display = HDMIDisplay(demo_mode=False)
    
    # Initialize
    if not display.initialize():
        print("ERROR: Failed to initialize display")
        sys.exit(1)
        
    print("Display initialized successfully!")
    
    # Start display
    display.start()
    
    try:
        # Test 1: Initial state
        print("\nTest 1: Initial state (Molty sleeping)")
        display.set_molty_state(MoltyState.SLEEPING)
        display.set_status("Waiting for commands...")
        time.sleep(2)
        
        # Test 2: Molty idle
        print("Test 2: Molty idle")
        display.set_molty_state(MoltyState.IDLE)
        display.add_activity("system", "System initialized")
        time.sleep(2)
        
        # Test 3: Activity feed
        print("Test 3: Adding activities")
        display.add_activity("command", "Check inbox", "User command")
        time.sleep(1)
        
        display.set_molty_state(MoltyState.THINKING)
        display.add_activity("thinking", "Processing request", "Analyzing inbox...")
        time.sleep(2)
        
        display.set_molty_state(MoltyState.HAPPY)
        display.add_activity("responding", "Found 3 new messages", "")
        time.sleep(2)
        
        # Test 4: Multiple activities
        print("Test 4: Multiple activities")
        activities = [
            ("command", "Brief me", ""),
            ("thinking", "Generating brief", "Summarizing..."),
            ("responding", "Brief ready", "5 key points"),
            ("command", "Focus mode", ""),
            ("system", "Focus mode activated", ""),
            ("command", "Random task", ""),
            ("thinking", "Selecting random task", ""),
            ("responding", "Task: Review documentation", ""),
        ]
        
        for activity_type, message, details in activities:
            display.add_activity(activity_type, message, details)
            
            # Update Molty state
            if activity_type == "thinking":
                display.set_molty_state(MoltyState.THINKING)
            elif activity_type == "responding":
                display.set_molty_state(MoltyState.HAPPY)
            else:
                display.set_molty_state(MoltyState.IDLE)
                
            time.sleep(1)
            
        # Test 5: Scrolling
        print("Test 5: Scrolling (if implemented)")
        display.scroll(5)
        time.sleep(1)
        display.scroll(-5)
        time.sleep(1)
        
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

