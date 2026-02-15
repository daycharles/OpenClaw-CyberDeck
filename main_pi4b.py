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

        # Initialize GPIO system first (only in production mode)
        if not demo_mode:
            try:
                import RPi.GPIO as GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                print("[Pi4B] GPIO initialized (BCM mode)")
            except Exception as e:
                print(f"[Pi4B] GPIO initialization warning: {e}")

        # Initialize displays
        print("Initializing HDMI display...")
        self.hdmi_display = HDMIDisplay(demo_mode=demo_mode)

        print("Initializing ILI9341 control display...")
        self.control_display = StatusDisplay(demo_mode=demo_mode)

        # Initialize touch handler
        print("Initializing touch handler...")
        self.touch = TouchHandler(demo_mode=demo_mode)

        # Set up touch callbacks (they receive x, y coordinates)
        self.touch.on_tap_top = lambda x, y: self.handle_touch_region("top", x, y)
        self.touch.on_tap_bottom = lambda x, y: self.handle_touch_region("bottom", x, y)

        # Initialize OpenClaw bridge
        print("Initializing OpenClaw bridge...")
        self.bridge = OpenClawBridge(demo_mode=demo_mode)
        self.bridge.set_callbacks(
            on_message_complete=self.handle_message_complete,
            on_status_change=self.handle_status_change
        )

    def handle_touch_region(self, region, x, y):
        """Handle touch events from the control display."""
        # Simple region-based commands
        # Top half = New Chat, Bottom half = Clear
        if region == "top":
            print(f"Touch: Top region at ({x}, {y}) - Simulating activity")
            # In demo mode, just add a test message
            print("[Touch] Top tap - adding test message")
        elif region == "bottom":
            print(f"Touch: Bottom region at ({x}, {y}) - Simulating clear")
            print("[Touch] Bottom tap - would clear display")

    def handle_message_complete(self, message):
        """Handle completed message from OpenClaw."""
        # Message is a dict with 'role' and 'content'
        role = message.get('role', 'unknown')
        content = message.get('content', '')
        print(f"[Bridge] Message: {role}: {content[:50]}...")

    def handle_status_change(self, status):
        """Handle status changes from OpenClaw."""
        # Status is a dict with various status fields
        print(f"[Bridge] Status update: {status}")
    
    def demo_loop(self):
        """Run demo mode with simulated activities."""
        demo_messages = [
            {"role": "user", "content": "How do I configure the display?"},
            {"role": "assistant", "content": "I'll help you configure the display settings..."},
            {"role": "user", "content": "Can you show me the pin mappings?"},
            {"role": "assistant", "content": "Sure! The ILI9341 uses GPIO 8 for CS, GPIO 25 for DC..."},
        ]

        idx = 0
        while self.running:
            message = demo_messages[idx % len(demo_messages)]
            self.handle_message_complete(message)
            idx += 1
            time.sleep(config_pi4b.DEMO["activity_interval"])
    
    def run(self):
        """Start the dashboard."""
        self.running = True

        # Initialize displays
        if not self.demo_mode:
            print("Initializing display hardware...")
            # Initialize HDMI display (may not work on all setups)
            try:
                if not self.hdmi_display.initialize():
                    print("[WARNING] HDMI display initialization failed (continuing anyway)")
            except Exception as e:
                print(f"[WARNING] HDMI display error: {e}")

            # Initialize ILI9341 control display
            if not self.control_display.initialize():
                print("[ERROR] Failed to initialize ILI9341 display")

        # Start HDMI display (may fail silently if not available)
        try:
            self.hdmi_display.start()
        except Exception as e:
            print(f"[WARNING] HDMI display start failed: {e}")

        # Start control display rendering loop in a thread
        print("[Pi4B] Starting ILI9341 display render loop...")
        control_display_thread = threading.Thread(
            target=self.control_display.run,
            kwargs={
                "get_status_func": lambda: self.bridge.get_status(),
                "interval": 0.5  # Update twice per second
            },
            daemon=True
        )
        control_display_thread.start()

        # Initialize and start touch polling in a thread
        if not self.demo_mode:
            self.touch.initialize()

        touch_thread = threading.Thread(target=self.touch.run, daemon=True)
        touch_thread.start()

        # Start OpenClaw bridge or demo mode
        if self.demo_mode:
            print("Running in DEMO mode")
            demo_thread = threading.Thread(target=self.demo_loop, daemon=True)
            demo_thread.start()
        else:
            # Connect to OpenClaw
            self.bridge.connect()

        print("Dashboard running. Press Ctrl+C to exit.")

        try:
            last_message_count = 0
            print("[Pi4B] Starting main update loop...")

            while self.running:
                # Update HDMI display with new messages and status
                try:
                    messages = self.bridge.get_all_messages()
                    status = self.bridge.get_status()

                    print(f"[Pi4B] Got {len(messages)} messages, {last_message_count} seen before")

                    # Only update if there are new messages
                    if len(messages) > last_message_count:
                        new_messages = messages[last_message_count:]
                        print(f"[Pi4B] Updating HDMI with {len(new_messages)} new messages")
                        self.hdmi_display.update_messages(new_messages)
                        last_message_count = len(messages)

                    # Update status
                    print(f"[Pi4B] Updating HDMI status: {status}")
                    self.hdmi_display.update_status(status)

                except Exception as e:
                    # Log HDMI display errors for debugging
                    print(f"[Pi4B] HDMI display error: {e}")
                    import traceback
                    traceback.print_exc()

                time.sleep(0.5)  # Update every 500ms
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()
    
    def stop(self):
        """Stop the dashboard and cleanup."""
        self.running = False

        # Stop displays
        if self.hdmi_display:
            self.hdmi_display.stop()

        if self.control_display:
            self.control_display.stop()

        if self.touch:
            self.touch.stop()
            self.touch.cleanup()

        # Cleanup GPIO pins (only non-SPI pins)
        if not self.demo_mode:
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup(config_pi4b.GPIO_PINS)
                print("[Pi4B] GPIO cleanup complete")
            except Exception as e:
                print(f"[Pi4B] GPIO cleanup warning: {e}")

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

