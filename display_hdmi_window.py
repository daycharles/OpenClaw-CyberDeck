"""
ElecLab 7" HDMI Display Driver (1024x600) - Windowed Version
Main conversation/activity display using Tkinter window.

For use when running from desktop environment on Raspberry Pi 4B.
"""

import threading
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk

# Try to import the appropriate config
try:
    import config_pi4b as config
    print("[HDMI Window] Using Pi 4B configuration")
except ImportError:
    try:
        import config_uno_q as config
        print("[HDMI Window] Using UNO Q configuration")
    except ImportError:
        import config
        print("[HDMI Window] Using default configuration")

from ui.cyberpunk_theme import CyberpunkTheme
from ui.molty import Molty, MoltyState
from ui.activity_feed import ActivityFeed


class HDMIDisplayWindow:
    """
    ElecLab 7" 1024x600 HDMI display for main conversation/activity view.
    Uses Tkinter window for rendering (desktop-friendly).
    
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
        self.demo_mode = demo_mode
        
        self.window = None
        self.canvas = None
        self.photo_image = None
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
        """Initialize the Tkinter window."""
        print(f"[HDMI Window] Initializing display window ({self.width}x{self.height})")
        
        try:
            # Create Tkinter window
            self.window = tk.Tk()
            self.window.title("OpenClaw CyberDeck - Main Display")
            self.window.geometry(f"{self.width}x{self.height}")
            self.window.resizable(False, False)
            
            # Create canvas for image display
            self.canvas = tk.Canvas(
                self.window,
                width=self.width,
                height=self.height,
                bg='black',
                highlightthickness=0
            )
            self.canvas.pack()
            
            # Bind close event
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)
            
            print(f"[HDMI Window] Initialized: {self.width}x{self.height} window")
            return True
            
        except Exception as e:
            print(f"[HDMI Window] Initialization failed: {e}")
            return False
    
    def on_close(self):
        """Handle window close event."""
        print("[HDMI Window] Window closed by user")
        self.stop()
        if self.window:
            self.window.destroy()
            
    def display_image(self, image):
        """Display a PIL Image on the Tkinter canvas."""
        if not self.window or not self.canvas:
            return

        try:
            with self.lock:
                # Convert PIL image to PhotoImage
                self.photo_image = ImageTk.PhotoImage(image)

                # Update canvas
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

                # Update window
                self.window.update()
        except Exception as e:
            # Window might be closed
            pass

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
        molty_sprite = self.molty.get_sprite()
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
        feed_rect = (activity_x + 10, feed_y, self.width - activity_x - 30, feed_height)
        self.activity_feed.render(draw, feed_rect, self._status_text, self._scroll_offset)

        # Footer status bar (already rendered by activity_feed.render)
        # Just add the decorative line
        footer_y = self.height - footer_height
        draw.line([activity_x, footer_y, self.width, footer_y],
                 fill=config.CYBERPUNK_COLORS["neon_cyan"], width=2)

        self.display_image(img)

    def add_activity(self, activity_type, message, details=""):
        """Add an activity to the feed."""
        entry_type = "message"  # Default to message type
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
        """Update display with new messages from OpenClaw."""
        if not messages:
            return

        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')

            if len(content) > 100:
                content = content[:97] + "..."

            activity_type = "user" if role == "user" else "assistant"
            self.add_activity(activity_type, content)

        if messages:
            last_msg = messages[-1]
            if last_msg.get('role') == 'assistant':
                self.set_molty_state(MoltyState.WORKING)
            else:
                self.set_molty_state(MoltyState.LISTENING)

    def update_status(self, status: Dict[str, Any]]):
        """Update display with status information from OpenClaw."""
        if not status:
            return

        if status.get('is_streaming'):
            self.set_status("Streaming response...")
            self.set_molty_state(MoltyState.THINKING)
        elif status.get('connected'):
            task = status.get('task_summary', 'Idle')
            model = status.get('model', 'unknown')
            self.set_status(f"{task} • {model}")
            self.set_molty_state(MoltyState.IDLE)
        else:
            self.set_status("Disconnected from OpenClaw")
            self.set_molty_state(MoltyState.ERROR)

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
        if self.window:
            try:
                self.window.quit()
            except:
                pass

