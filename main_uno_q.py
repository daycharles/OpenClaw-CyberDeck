#!/usr/bin/env python3
"""
OpenClaw Display Dashboard for Arduino UNO Q
Main coordinator for two displays:
- ElecLab 7" HDMI (main conversation/activity)
- HiLetgo 2.4" ILI9341 (touch command panel)

Usage:
    python3 main_uno_q.py --demo                    # Demo mode
    python3 main_uno_q.py --url ws://localhost:18789  # Connect to OpenClaw
"""

import argparse
import signal
import sys
import time
import threading
from datetime import datetime

try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("WARNING: RPi.GPIO not available, running in demo mode")

import config_uno_q as config
from display_hdmi import HDMIDisplay
from display_status import StatusDisplay  # Reuse existing ILI9341 driver
from display_st7789_uno_q import ST7789Display
from touch_handler import TouchHandler
from openclaw_bridge import OpenClawBridge
from ui.molty import MoltyState


class UnoQDashboard:
    """Main coordinator for Arduino UNO Q dual-display dashboard."""

    def __init__(self, demo_mode=False, openclaw_url=None):
        self.demo_mode = demo_mode
        self.openclaw_url = openclaw_url
        self.running = False

        # Initialize displays
        print("[UNO-Q] Initializing displays...")
        self.hdmi_display = HDMIDisplay(demo_mode=demo_mode)
        self.control_display = StatusDisplay(demo_mode=demo_mode)  # ILI9341
        
        # Touch handler for control display
        self.touch_handler = None
        
        # OpenClaw bridge
        self.bridge = None
        
        # Setup GPIO
        if HARDWARE_AVAILABLE and not demo_mode:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
    def initialize(self):
        """Initialize all components."""
        print("[UNO-Q] Starting initialization...")
        
        # Initialize displays
        if not self.hdmi_display.initialize():
            print("[UNO-Q] WARNING: HDMI display initialization failed")
            
        if not self.control_display.initialize():
            print("[UNO-Q] WARNING: Control display initialization failed")
            
        # Initialize touch handler
        if not self.demo_mode:
            self.touch_handler = TouchHandler(
                on_tap=self._handle_tap,
                demo_mode=self.demo_mode
            )
            if self.touch_handler.initialize():
                self.touch_handler.start()
            else:
                print("[UNO-Q] WARNING: Touch handler initialization failed")
                
        # Setup command callbacks
        self.control_display.command_panel.set_command_callback(self._handle_command)
        
        # Initialize OpenClaw bridge if URL provided
        if self.openclaw_url:
            self.bridge = OpenClawBridge(
                url=self.openclaw_url,
                on_activity=self._handle_activity,
                on_status_change=self._handle_status_change,
                on_connection_change=self._handle_connection_change
            )
            
        print("[UNO-Q] Initialization complete!")
        return True
        
    def _handle_tap(self, x, y):
        """Handle touch tap events."""
        # Forward to control display for button detection
        button = self.control_display.command_panel.get_button_at(x, y)
        if button:
            print(f"[UNO-Q] Button tapped: {button.label}")
            self._handle_command(button.command)
            
    def _handle_command(self, command):
        """Handle command button presses."""
        print(f"[UNO-Q] Command: {command}")

        # Update main display
        self.hdmi_display.add_activity("command", f"Sent: {command}")

        # Send to OpenClaw if connected
        if self.bridge and self.bridge.is_connected():
            self.bridge.send_message(command)
        else:
            self.control_display.show_notification("error", "Error", "Not connected")
            
    def _handle_activity(self, activity_type, message, details=""):
        """Handle activity from OpenClaw."""
        self.hdmi_display.add_activity(activity_type, message, details)
        
        # Update Molty state based on activity
        if activity_type == "thinking":
            self.hdmi_display.set_molty_state(MoltyState.THINKING)
        elif activity_type == "responding":
            self.hdmi_display.set_molty_state(MoltyState.HAPPY)
        elif activity_type == "error":
            self.hdmi_display.set_molty_state(MoltyState.ALERT)
            
    def _handle_status_change(self, status_data):
        """Handle status updates from OpenClaw."""
        self.control_display.update_status(status_data)
        
    def _handle_connection_change(self, connected):
        """Handle connection state changes."""
        # Update control display status
        self.control_display.update_status({"connected": connected})

        if connected:
            self.hdmi_display.set_molty_state(MoltyState.IDLE)
            self.hdmi_display.add_activity("system", "Connected to OpenClaw")
        else:
            self.hdmi_display.set_molty_state(MoltyState.SLEEPING)
            self.hdmi_display.add_activity("system", "Disconnected from OpenClaw")

    def start(self):
        """Start the dashboard."""
        self.running = True

        # Start displays
        self.hdmi_display.start()
        self.control_display.start()

        # Start OpenClaw bridge if configured
        if self.bridge:
            self.bridge.start()
        elif self.demo_mode:
            # Start demo mode
            self._start_demo_mode()

        print("[UNO-Q] Dashboard running!")
        print("[UNO-Q] Press Ctrl+C to exit")

    def _start_demo_mode(self):
        """Start demo mode with simulated activity."""
        def demo_loop():
            demo_messages = [
                ("command", "Inbox check", ""),
                ("thinking", "Processing request", "Analyzing inbox..."),
                ("responding", "Found 3 new messages", ""),
                ("command", "Brief me", ""),
                ("thinking", "Generating brief", "Summarizing..."),
                ("responding", "Brief ready", "5 key points"),
            ]

            idx = 0
            while self.running:
                time.sleep(3)
                if not self.running:
                    break

                activity_type, message, details = demo_messages[idx % len(demo_messages)]
                self._handle_activity(activity_type, message, details)
                idx += 1

        demo_thread = threading.Thread(target=demo_loop, daemon=True)
        demo_thread.start()

    def stop(self):
        """Stop the dashboard and cleanup."""
        print("\n[UNO-Q] Shutting down...")
        self.running = False

        # Stop bridge
        if self.bridge:
            self.bridge.stop()

        # Stop touch handler
        if self.touch_handler:
            self.touch_handler.stop()

        # Stop displays
        self.hdmi_display.stop()
        self.control_display.stop()

        # Cleanup GPIO
        if HARDWARE_AVAILABLE:
            GPIO.cleanup(config.GPIO_PINS)

        print("[UNO-Q] Shutdown complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="OpenClaw Display Dashboard for Arduino UNO Q")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    parser.add_argument("--url", type=str, help="OpenClaw WebSocket URL (e.g., ws://localhost:18789)")
    args = parser.parse_args()

    # Create dashboard
    dashboard = UnoQDashboard(
        demo_mode=args.demo or not HARDWARE_AVAILABLE,
        openclaw_url=args.url or config.OPENCLAW["default_url"] if not args.demo else None
    )

    # Setup signal handlers
    def signal_handler(sig, frame):
        dashboard.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize and start
    if dashboard.initialize():
        dashboard.start()

        # Keep running
        try:
            while dashboard.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

        dashboard.stop()
    else:
        print("[UNO-Q] Initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

