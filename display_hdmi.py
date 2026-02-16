"""
ElecLab 7" HDMI Display Driver (1024x600)
Main conversation/activity display using Linux framebuffer.

Works with both Arduino UNO Q (CM4-based) and Raspberry Pi 4B.
"""

import threading
import time
import mmap
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from PIL import Image, ImageDraw, ImageFont

# Try to import the appropriate config
try:
    import config_pi4b as config
    print("[HDMI] Using Pi 4B configuration")
except ImportError:
    try:
        import config_uno_q as config
        print("[HDMI] Using UNO Q configuration")
    except ImportError:
        import config
        print("[HDMI] Using default configuration")

from ui.cyberpunk_theme import CyberpunkTheme
from ui.molty import Molty, MoltyState
from ui.activity_feed import ActivityFeed


class HDMIDisplay:
    """
    ElecLab 7" 1024x600 HDMI display for main conversation/activity view.
    Uses Linux framebuffer (/dev/fb0) for rendering.
    
    Layout (1024x600):
    ┌──────────────┬─────────────────────────────────────────┐
    │              │ OPENCLAW                     12:34:07   │  Header 50px
    │    MOLTY     ├─────────────────────────────────────────┤
    │   300x500    │  Activity Feed (8-10 entries)           │  520px
    │              │                                         │
    │   State      │                                         │
    │   Label      ├─────────────────────────────────────────┤
    │              │ ▌Waiting for commands...                │  Status 30px
    └──────────────┴─────────────────────────────────────────┘
    """

    def __init__(self, demo_mode=False):
        cfg = config.HDMI_DISPLAY
        self.width = cfg["width"]
        self.height = cfg["height"]
        self.framebuffer_path = cfg["framebuffer"]
        self.rotation = cfg.get("rotation", 0)
        self.demo_mode = demo_mode
        
        self.fb = None
        self.fb_mem = None
        self.lock = threading.Lock()
        self.running = False
        
        # UI components
        self.theme = CyberpunkTheme()
        self.molty = Molty(sprite_dir=config.SPRITES.get("molty_dir"))
        self.activity_feed = ActivityFeed(theme=self.theme)
        
        # Status
        self._status_text = "Waiting for commands..."
        self._scroll_offset = 0
        
        # Fonts
        self.fonts = {}
        self._load_fonts()
        
    def _load_fonts(self):
        """Load fonts for HDMI display (larger sizes)."""
        try:
            self.fonts["small"] = ImageFont.truetype(
                config.FONTS["default_path"],
                config.FONTS["hdmi_small"]
            )
            self.fonts["medium"] = ImageFont.truetype(
                config.FONTS["default_path"],
                config.FONTS["hdmi_medium"]
            )
            self.fonts["large"] = ImageFont.truetype(
                config.FONTS["default_path"],
                config.FONTS["hdmi_large"]
            )
            self.fonts["title"] = ImageFont.truetype(
                config.FONTS["bold_path"],
                config.FONTS["hdmi_title"]
            )
        except (IOError, OSError):
            self.fonts["small"] = ImageFont.load_default()
            self.fonts["medium"] = ImageFont.load_default()
            self.fonts["large"] = ImageFont.load_default()
            self.fonts["title"] = ImageFont.load_default()
            
    def initialize(self):
        """Initialize the framebuffer."""
        print(f"[HDMI] Initializing display (demo_mode={self.demo_mode})")

        if self.demo_mode:
            print("[HDMI] Running in demo mode (no framebuffer)")
            return True

        try:
            print(f"[HDMI] Opening framebuffer: {self.framebuffer_path}")
            # Open framebuffer
            self.fb = os.open(self.framebuffer_path, os.O_RDWR)
            
            # Memory map the framebuffer
            # Assuming 32-bit color (RGBA or BGRA)
            fb_size = self.width * self.height * 4
            self.fb_mem = mmap.mmap(self.fb, fb_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
            
            print(f"[HDMI] Initialized: {self.width}x{self.height} @ {self.framebuffer_path}")
            return True
            
        except Exception as e:
            print(f"[HDMI] Initialization failed: {e}")
            if self.demo_mode:
                print("[HDMI] Continuing in demo mode")
                return True
            return False
            
    def display_image(self, image):
        """Display a PIL Image on the framebuffer."""
        if self.demo_mode or not self.fb_mem:
            return
            
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))
            
        # Convert to RGBA (or BGRA depending on framebuffer format)
        rgba_image = image.convert("RGBA")
        
        # Write to framebuffer
        with self.lock:
            self.fb_mem.seek(0)
            self.fb_mem.write(rgba_image.tobytes())
            
    def render(self):
        """Render the main display with Molty and activity feed."""
        # Create image
        img = Image.new("RGB", (self.width, self.height), config.CYBERPUNK_COLORS["background"])
        draw = ImageDraw.Draw(img)
        
        layout = config.HDMI_LAYOUT
        molty_width = layout["molty_panel_width"]
        header_height = layout["header_height"]
        footer_height = layout["footer_height"]
        
        # Left panel - Molty
        draw.rectangle([0, 0, molty_width, self.height], fill=config.CYBERPUNK_COLORS["panel_bg"])
        draw.line([molty_width, 0, molty_width, self.height], fill=config.CYBERPUNK_COLORS["neon_cyan"], width=3)
        
        # Render Molty sprite
        molty_sprite = self.molty.get_current_sprite()
        if molty_sprite:
            # Scale sprite for larger display
            molty_sprite = molty_sprite.resize((120, 120))
            molty_x, molty_y = layout["molty_position"]
            img.paste(molty_sprite, (molty_x, molty_y), molty_sprite if molty_sprite.mode == "RGBA" else None)
        
        # Molty state label
        state_text = self.molty.state.value.upper()
        draw.text((molty_width // 2, layout["molty_label_y"]), state_text, 
                 font=self.fonts["medium"], fill=config.CYBERPUNK_COLORS["neon_cyan"], anchor="mm")
        
        # Right panel - Header
        activity_x = layout["activity_panel_x"]
        draw.rectangle([activity_x, 0, self.width, header_height], fill=config.CYBERPUNK_COLORS["panel_bg"])
        draw.line([activity_x, header_height, self.width, header_height], 
                 fill=config.CYBERPUNK_COLORS["neon_cyan"], width=2)
        
        draw.text((activity_x + 20, header_height // 2), "OPENCLAW", 
                 font=self.fonts["title"], fill=config.CYBERPUNK_COLORS["hot_pink"], anchor="lm")
        
        time_str = datetime.now().strftime("%H:%M:%S")
        draw.text((self.width - 20, header_height // 2), time_str,
                 font=self.fonts["medium"], fill=config.CYBERPUNK_COLORS["text_dim"], anchor="rm")

        # Activity feed
        feed_y = header_height + 10
        feed_height = self.height - header_height - footer_height - 20
        self.activity_feed.render_on_image(img, activity_x + 10, feed_y,
                                          self.width - activity_x - 20, feed_height,
                                          self.fonts, self._scroll_offset)

        # Footer status bar
        footer_y = self.height - footer_height
        draw.line([activity_x, footer_y, self.width, footer_y],
                 fill=config.CYBERPUNK_COLORS["neon_cyan"], width=2)
        draw.text((activity_x + 20, footer_y + footer_height // 2), f"▌{self._status_text}",
                 font=self.fonts["small"], fill=config.CYBERPUNK_COLORS["text_primary"], anchor="lm")

        self.display_image(img)

    def add_activity(self, activity_type, message, details=""):
        """Add an activity to the feed."""
        # ActivityFeed uses add_entry, not add_activity
        # Map activity_type to entry type
        entry_type = "message"  # Default to message type
        if activity_type == "user":
            entry_type = "message"
        elif activity_type == "assistant":
            entry_type = "message"

        self.activity_feed.add_entry(entry_type, message, details)
        self.render()

    def set_molty_state(self, state: MoltyState):
        """Update Molty's state."""
        self.molty.set_state(state)
        self.render()

    def set_status(self, text):
        """Update status text."""
        with self.lock:
            self._status_text = text
        self.render()

    def update_messages(self, messages: List[Dict[str, Any]]):
        """
        Update display with new messages from OpenClaw.

        Args:
            messages: List of message dicts with 'role', 'content', 'timestamp'
        """
        print(f"[HDMI] update_messages called with {len(messages) if messages else 0} messages")

        if not messages:
            print("[HDMI] No messages to update")
            return

        # Add messages to activity feed
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')

            print(f"[HDMI] Adding message: {role}: {content[:50]}...")

            # Truncate long messages for activity feed
            if len(content) > 100:
                content = content[:97] + "..."

            activity_type = "user" if role == "user" else "assistant"
            self.add_activity(activity_type, content)

        # Update Molty state based on activity
        if messages:
            last_msg = messages[-1]
            if last_msg.get('role') == 'assistant':
                print("[HDMI] Setting Molty to WORKING (assistant response)")
                self.set_molty_state(MoltyState.WORKING)
            else:
                print("[HDMI] Setting Molty to LISTENING (user message)")
                self.set_molty_state(MoltyState.LISTENING)

    def update_status(self, status: Dict[str, Any]):
        """
        Update display with status information from OpenClaw.

        Args:
            status: Dict with 'connected', 'model', 'task_summary', etc.
        """
        print(f"[HDMI] update_status called with: {status}")

        if not status:
            print("[HDMI] No status to update")
            return

        # Update status text
        if status.get('is_streaming'):
            print("[HDMI] Status: Streaming")
            self.set_status("Streaming response...")
            self.set_molty_state(MoltyState.THINKING)
        elif status.get('connected'):
            task = status.get('task_summary', 'Idle')
            model = status.get('model', 'unknown')
            print(f"[HDMI] Status: Connected - {task} • {model}")
            self.set_status(f"{task} • {model}")
            self.set_molty_state(MoltyState.IDLE)
        else:
            print("[HDMI] Status: Disconnected")
            self.set_status("Disconnected from OpenClaw")
            self.set_molty_state(MoltyState.ERROR)  # Use ERROR state for disconnected

    def scroll(self, delta):
        """Scroll the activity feed."""
        with self.lock:
            self._scroll_offset += delta
            self._scroll_offset = max(0, self._scroll_offset)
        self.render()

    def start(self):
        """Start the display."""
        self.running = True
        self.render()

    def stop(self):
        """Stop the display and cleanup."""
        self.running = False
        if self.fb_mem:
            self.fb_mem.close()
        if self.fb:
            os.close(self.fb)

