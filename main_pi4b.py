#!/usr/bin/env python3
"""
OpenClaw Display Dashboard for Raspberry Pi 4B
Dual-display setup: HDMI main + ILI9341 touch control
"""

import time
import threading
import argparse
from pathlib import Path

# Import display drivers
from display_hdmi import HDMIDisplay
from display_status import StatusDisplay  # Reuse existing ILI9341 driver
from touch_handler import TouchHandler
from openclaw_bridge import OpenClawBridge
import config_pi4b
import config

# Copy Pi 4B touch settings to main config so TouchHandler can use them
config.TOUCH = config_pi4b.TOUCH

class OpenClawDashboard:
    """Main coordinator for dual-display OpenClaw dashboard on Pi 4B."""

    def __init__(self, demo_mode=False, openclaw_url=None):
        self.demo_mode = demo_mode
        self.openclaw_url = openclaw_url or config_pi4b.OPENCLAW["default_url"]
        self.running = False

        # Initialize displays
        print("Initializing HDMI display...")
        self.hdmi_display = HDMIDisplay(demo_mode=demo_mode)

        print("Initializing ILI9341 control display...")
        self.control_display = StatusDisplay(demo_mode=demo_mode)

        # Initialize touch handler
        print("Initializing touch handler...")
        self.touch = TouchHandler(demo_mode=demo_mode)

        # Set up touch callbacks
        self.touch.on_tap_top = lambda: self.handle_touch_region("top")
        self.touch.on_tap_bottom = lambda: self.handle_touch_region("bottom")
        
        # Initialize OpenClaw bridge (if not in demo mode)
        self.bridge = None
        if not demo_mode:
            print(f"Connecting to OpenClaw at {self.openclaw_url}...")
            self.bridge = OpenClawBridge(
                url=self.openclaw_url,
                on_activity=self.handle_activity,
                on_status_change=self.handle_status_change
            )

    def handle_touch_region(self, region):
        """Handle touch events from the control display."""
        # Simple region-based commands
        # Top half = New Chat, Bottom half = Clear
        if region == "top":
            print("Touch: Top region - New Chat")
            self.execute_command("new_chat")
        elif region == "bottom":
            print("Touch: Bottom region - Clear")
            self.execute_command("clear")
    
    def execute_command(self, command):
        """Execute a command from button press."""
        if command == "new_chat":
            if self.bridge:
                self.bridge.send_command("new_chat")
            self.hdmi_display.add_activity("system", "Started new conversation")
        
        elif command == "clear":
            self.hdmi_display.clear_activities()
            self.control_display.update_status("cleared", "Ready")
        
        elif command == "pause":
            if self.bridge:
                self.bridge.send_command("pause")
            self.control_display.update_status("paused", "Paused")
        
        elif command == "resume":
            if self.bridge:
                self.bridge.send_command("resume")
            self.control_display.update_status("running", "Active")
        
        elif command == "settings":
            # Show settings on HDMI display
            self.hdmi_display.show_settings()
        
        elif command == "help":
            # Show help on HDMI display
            self.hdmi_display.show_help()
    
    def handle_activity(self, activity_type, content):
        """Handle activity updates from OpenClaw."""
        self.hdmi_display.add_activity(activity_type, content)
        
        # Update control display with notification
        if activity_type == "user_message":
            self.control_display.show_notification("User message")
        elif activity_type == "assistant_message":
            self.control_display.show_notification("Assistant reply")
        elif activity_type == "tool_use":
            self.control_display.show_notification(f"Tool: {content[:20]}")
    
    def handle_status_change(self, status, details):
        """Handle status changes from OpenClaw."""
        self.control_display.update_status(status, details)
        self.hdmi_display.update_connection_status(status)
    
    def demo_loop(self):
        """Run demo mode with simulated activities."""
        demo_activities = [
            ("user_message", "How do I configure the display?"),
            ("assistant_message", "I'll help you configure the display settings..."),
            ("tool_use", "Reading config_pi4b.py"),
            ("system", "Configuration loaded successfully"),
        ]

        idx = 0
        while self.running:
            activity_type, content = demo_activities[idx % len(demo_activities)]
            self.handle_activity(activity_type, content)
            idx += 1
            time.sleep(config_pi4b.DEMO["activity_interval"])
    
    def run(self):
        """Start the dashboard."""
        self.running = True

        # Initialize and start touch polling
        if not self.demo_mode:
            self.touch.initialize()
        self.touch.start()
        
        # Start OpenClaw bridge or demo mode
        if self.demo_mode:
            print("Running in DEMO mode")
            demo_thread = threading.Thread(target=self.demo_loop, daemon=True)
            demo_thread.start()
        elif self.bridge:
            self.bridge.start()
        
        print("Dashboard running. Press Ctrl+C to exit.")
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()
    
    def stop(self):
        """Stop the dashboard and cleanup."""
        self.running = False
        
        if self.touch:
            self.touch.stop()
        
        if self.bridge:
            self.bridge.stop()
        
        if self.hdmi_display:
            self.hdmi_display.cleanup()
        
        if self.control_display:
            self.control_display.cleanup()
        
        print("Shutdown complete.")

def main():
    parser = argparse.ArgumentParser(description="OpenClaw Display Dashboard for Pi 4B")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    parser.add_argument("--url", type=str, help="OpenClaw WebSocket URL")
    args = parser.parse_args()
    
    dashboard = OpenClawDashboard(
        demo_mode=args.demo,
        openclaw_url=args.url
    )
    dashboard.run()

if __name__ == "__main__":
    main()

