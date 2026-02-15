"""
Waveshare 1.3" ST7789 Display Driver (240x240)
Status/notification panel with cyberpunk theme for Arduino UNO Q.

Uses raw spidev + RPi.GPIO.
"""

import threading
import time
from datetime import datetime
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont

try:
    import spidev
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

from spi_lock import spi_lock
import config_uno_q as config


# ST7789 Commands
ST7789_SWRESET = 0x01
ST7789_SLPOUT = 0x11
ST7789_NORON = 0x13
ST7789_INVON = 0x21
ST7789_DISPON = 0x29
ST7789_CASET = 0x2A
ST7789_RASET = 0x2B
ST7789_RAMWR = 0x2C
ST7789_MADCTL = 0x36
ST7789_COLMOD = 0x3A


class ST7789Display:
    """
    Waveshare 1.3" 240x240 ST7789 display for status/notifications.
    
    Layout (240x240):
    ┌────────────────────────┐
    │  OPENCLAW   12:34:07   │  Header 30px
    ├────────────────────────┤
    │                        │
    │   Notification 1       │  Notification
    │   Notification 2       │  stack
    │   Notification 3       │  (3 max)
    │                        │
    ├────────────────────────┤
    │  ● Connected           │  Status 30px
    └────────────────────────┘
    """

    def __init__(self, demo_mode=False):
        cfg = config.ST7789_DISPLAY
        self.spi_bus = cfg["spi_bus"]
        self.spi_device = cfg["spi_device"]
        self.dc_pin = cfg["dc_pin"]
        self.rst_pin = cfg["rst_pin"]
        self.bl_pin = cfg["bl_pin"]
        self.spi_speed_hz = cfg["spi_speed_hz"]
        self.demo_mode = demo_mode
        
        self.width = cfg["width"]
        self.height = cfg["height"]
        
        self.spi = None
        self.lock = threading.Lock()
        self.running = False
        
        # UI state
        self.notifications = []
        self.status_text = "Initializing..."
        self.connected = False
        self.fonts = {}
        
        self._load_fonts()
        
    def _load_fonts(self):
        """Load fonts for rendering."""
        try:
            self.fonts["small"] = ImageFont.truetype(
                config.FONTS["default_path"],
                config.FONTS["st7789_small"]
            )
            self.fonts["medium"] = ImageFont.truetype(
                config.FONTS["default_path"],
                config.FONTS["st7789_medium"]
            )
            self.fonts["bold"] = ImageFont.truetype(
                config.FONTS["bold_path"],
                config.FONTS["st7789_large"]
            )
        except (IOError, OSError):
            self.fonts["small"] = ImageFont.load_default()
            self.fonts["medium"] = ImageFont.load_default()
            self.fonts["bold"] = ImageFont.load_default()
            
    def initialize(self):
        """Initialize the ST7789 display."""
        if self.demo_mode and not HARDWARE_AVAILABLE:
            print("[ST7789] Running in demo mode (no hardware)")
            return True
            
        if not HARDWARE_AVAILABLE:
            print("[ST7789] ERROR: spidev/RPi.GPIO not available")
            return False
            
        try:
            # Setup GPIO
            GPIO.setup(self.dc_pin, GPIO.OUT)
            GPIO.setup(self.rst_pin, GPIO.OUT)
            GPIO.setup(self.bl_pin, GPIO.OUT)
            GPIO.output(self.bl_pin, GPIO.LOW)  # Backlight off initially
            
            # Setup SPI
            self.spi = spidev.SpiDev()
            self.spi.open(self.spi_bus, self.spi_device)
            self.spi.max_speed_hz = self.spi_speed_hz
            self.spi.mode = 0
            
            # Initialize display
            self._reset()
            self._init_display()
            
            # Turn on backlight
            GPIO.output(self.bl_pin, GPIO.HIGH)
            
            print(f"[ST7789] Initialized: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            print(f"[ST7789] Initialization failed: {e}")
            if self.demo_mode:
                print("[ST7789] Continuing in demo mode")
                return True
            return False
            
    def _reset(self):
        """Hardware reset."""
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)
        
    def _command(self, cmd):
        """Send command byte."""
        with spi_lock:
            GPIO.output(self.dc_pin, GPIO.LOW)
            self.spi.xfer([cmd])

    def _data(self, data):
        """Send data bytes."""
        with spi_lock:
            GPIO.output(self.dc_pin, GPIO.HIGH)
            if isinstance(data, int):
                self.spi.xfer([data])
            else:
                data = list(data) if isinstance(data, bytes) else data
                for i in range(0, len(data), 4096):
                    self.spi.xfer(data[i:i + 4096])

    def _init_display(self):
        """Initialize ST7789 with proper settings."""
        self._command(ST7789_SWRESET)
        time.sleep(0.15)

        self._command(ST7789_SLPOUT)
        time.sleep(0.5)

        self._command(ST7789_COLMOD)
        self._data(0x55)  # 16-bit color (RGB565)

        self._command(ST7789_MADCTL)
        self._data(0x00)  # Normal orientation

        self._command(ST7789_INVON)  # Inversion on (common for ST7789)

        self._command(ST7789_NORON)
        time.sleep(0.01)

        self._command(ST7789_DISPON)
        time.sleep(0.01)

    def _set_window(self, x0, y0, x1, y1):
        """Set the pixel address window for writing."""
        self._command(ST7789_CASET)
        self._data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])

        self._command(ST7789_RASET)
        self._data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

        self._command(ST7789_RAMWR)

    def display_image(self, image):
        """Display a PIL Image on the screen."""
        if self.demo_mode and not HARDWARE_AVAILABLE:
            return

        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))

        # Convert to RGB565
        rgb_image = image.convert("RGB")
        pixels = list(rgb_image.getdata())

        # Convert RGB888 to RGB565
        rgb565_data = []
        for r, g, b in pixels:
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            rgb565_data.append(rgb565 >> 8)  # High byte
            rgb565_data.append(rgb565 & 0xFF)  # Low byte

        # Send to display
        with spi_lock:
            self._set_window(0, 0, self.width - 1, self.height - 1)
            self._data(rgb565_data)

    def render(self):
        """Render the status panel."""
        # Create image
        img = Image.new("RGB", (self.width, self.height), config.CYBERPUNK_COLORS["background"])
        draw = ImageDraw.Draw(img)

        # Header
        header_y = config.STATUS_PANEL_LAYOUT["header_height"]
        draw.rectangle([0, 0, self.width, header_y], fill=config.CYBERPUNK_COLORS["panel_bg"])
        draw.line([0, header_y, self.width, header_y], fill=config.CYBERPUNK_COLORS["neon_cyan"], width=2)

        # Title and time
        draw.text((10, 8), "OPENCLAW", font=self.fonts["bold"], fill=config.CYBERPUNK_COLORS["neon_cyan"])
        time_str = datetime.now().strftime("%H:%M:%S")
        draw.text((self.width - 70, 8), time_str, font=self.fonts["small"], fill=config.CYBERPUNK_COLORS["text_dim"])

        # Notifications
        y_offset = header_y + 10
        for notif in self.notifications[:3]:  # Max 3
            notif_height = config.STATUS_PANEL_LAYOUT["notification_height"]
            color = config.CYBERPUNK_COLORS.get("neon_cyan")

            draw.rectangle([5, y_offset, self.width - 5, y_offset + notif_height - 5],
                          outline=color, width=1)
            draw.text((10, y_offset + 5), notif.get("title", ""),
                     font=self.fonts["medium"], fill=color)
            draw.text((10, y_offset + 25), notif.get("message", "")[:30],
                     font=self.fonts["small"], fill=config.CYBERPUNK_COLORS["text_dim"])
            y_offset += notif_height

        # Footer status
        footer_y = self.height - config.STATUS_PANEL_LAYOUT["footer_height"]
        draw.line([0, footer_y, self.width, footer_y], fill=config.CYBERPUNK_COLORS["neon_cyan"], width=2)

        status_color = config.CYBERPUNK_COLORS["neon_green"] if self.connected else config.CYBERPUNK_COLORS["neon_red"]
        draw.ellipse([10, footer_y + 10, 20, footer_y + 20], fill=status_color)
        draw.text((25, footer_y + 8), self.status_text, font=self.fonts["small"], fill=config.CYBERPUNK_COLORS["text_primary"])

        self.display_image(img)

    def add_notification(self, title, message="", type="info"):
        """Add a notification to the display."""
        with self.lock:
            self.notifications.insert(0, {"title": title, "message": message, "type": type})
            if len(self.notifications) > 5:
                self.notifications = self.notifications[:5]
        self.render()

    def set_status(self, text, connected=False):
        """Update status text."""
        with self.lock:
            self.status_text = text
            self.connected = connected
        self.render()

    def start(self):
        """Start the display update loop."""
        self.running = True
        self.render()

    def stop(self):
        """Stop the display."""
        self.running = False
        if self.spi:
            self.spi.close()

