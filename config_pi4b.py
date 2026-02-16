"""
Configuration for Raspberry Pi 4B with two displays:
- ElecLab 7" HDMI 1024x600 (main display via framebuffer)
- HiLetgo 2.4" ILI9341 240x320 (touch control panel via SPI)

Pin mappings and display settings for Raspberry Pi 4B.
"""

# Display Assignment
DISPLAY_ROLES = {
    "main": "hdmi",       # ElecLab 7" - conversation/activity feed
    "control": "ili9341",  # HiLetgo 2.4" - touch command panel
}

# ElecLab 7" HDMI (1024x600) - Main Display
HDMI_DISPLAY = {
    "width": 1024,
    "height": 600,
    "framebuffer": "/dev/fb0",  # Primary framebuffer
    "rotation": 0,  # 0, 90, 180, 270
}

# HiLetgo 2.4" ILI9341 (320x240 landscape) - Touch Control Display
# Using Raspberry Pi 4B GPIO pins:
# - GPIO 7 (CE1) for SPI CS
# - GPIO 22 for DC (Data/Command)
# - GPIO 27 for RST (Reset)
# - GPIO 23 for Backlight
ILI9341_DISPLAY = {
    "width": 320,
    "height": 240,
    "spi_bus": 0,
    "spi_device": 1,  # CE1 (GPIO 7)
    "dc_pin": 22,     # GPIO 22 - Data/Command
    "rst_pin": 27,    # GPIO 27 - Reset
    "bl_pin": 23,     # GPIO 23 - Backlight
    "spi_speed_hz": 16000000,  # 16MHz (per CLAUDE.md)
}

# Touch Controller (XPT2046) on ILI9341
# Using GPIO 17 for manual chip select
# Calibrated for landscape mode (320x240)
TOUCH = {
    "cs_pin": 17,  # GPIO 17 - Manual chip select
    "spi_speed_hz": 1500000,  # 1.5MHz for touch reads
    "min_pressure": 300,  # Minimum Z value to count as touch
    # Calibration values from CLAUDE.md (axes swapped, both inverted)
    "x_min": 572,
    "x_max": 3676,
    "y_min": 777,
    "y_max": 3476,
    "swap_xy": True,   # Swap X/Y for landscape mode
    "invert_x": True,  # Invert X axis
    "invert_y": True,  # Invert Y axis
}

# GPIO pins to cleanup (NO SPI pins 9, 10, 11, 7, 8)
# Only our custom GPIO pins
GPIO_PINS = [17, 22, 23, 27]

# Color Scheme - Cyberpunk Theme (RGB tuples)
CYBERPUNK_COLORS = {
    "background": (0, 0, 0),             # #000000 - Pure black
    "panel_bg": (15, 15, 25),           # #0f0f19 - Slightly lighter panel
    "panel_border": (30, 30, 45),       # Border for panels

    # Primary neon colors
    "neon_cyan": (0, 255, 255),         # #00ffff - Primary accent
    "hot_pink": (255, 0, 102),          # #ff0066 - Secondary accent
    "electric_purple": (191, 0, 255),   # #bf00ff - Tertiary accent

    # Status colors
    "amber": (255, 170, 0),             # #ffaa00 - Warning/running
    "neon_green": (0, 255, 102),        # #00ff66 - Success
    "neon_red": (255, 0, 51),           # #ff0033 - Error

    # Text colors
    "text_primary": (238, 238, 255),    # #eeeeff - Main text
    "text_dim": (68, 119, 119),         # #447777 - Dimmed text
    "text_secondary": (100, 150, 150),  # Secondary text
}

# Font Configuration
FONTS = {
    "default_path": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "bold_path": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "mono_path": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    # ILI9341 (240x320) - control panel fonts
    "ili9341_small": 12,
    "ili9341_medium": 16,
    "ili9341_large": 20,
    # HDMI (1024x600) - main display fonts
    "hdmi_small": 16,
    "hdmi_medium": 20,
    "hdmi_large": 28,
    "hdmi_title": 36,
}

# Sprite paths
SPRITES = {
    "molty_dir": "assets/sprites",
}

# OpenClaw WebSocket Configuration
OPENCLAW = {
    "default_url": "ws://localhost:18789",
    "reconnect_delay": 5,  # seconds
    "ping_interval": 30,   # seconds
}

# Demo Mode Settings
DEMO = {
    "enabled": False,
    "activity_interval": 3,  # seconds between demo activities
}

# Layout Configuration for HDMI Display
HDMI_LAYOUT = {
    "molty_panel_width": 300,  # Left panel for Molty mascot
    "padding": 20,
    "activity_item_height": 80,
    "header_height": 50,  # Top header bar height
    "footer_height": 30,  # Bottom status bar height
    "molty_position": (90, 150),  # Molty sprite position (x, y)
    "molty_label_y": 500,  # Y position for Molty state label
    "activity_panel_x": 300,  # X position where activity panel starts
}

# Layout Configuration for ILI9341 Control Display
ILI9341_LAYOUT = {
    "status_bar_height": 40,
    "button_rows": 3,
    "button_cols": 2,
    "button_padding": 10,
}

