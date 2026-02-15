"""
Configuration for Arduino UNO Q with two displays:
- HiLetgo 2.4" ILI9341 240x320 (touch control panel)
- ElecLab 7" HDMI 1024x600 (main display)

Pin mappings for Arduino UNO Q (14 digital + 6 analog pins).

Arduino UNO Q GPIO Mapping:
- Digital pins: 0-13 (D0-D13)
- Analog pins: A0-A5 (can be used as digital 14-19)
- SPI pins: D11 (MOSI), D12 (MISO), D13 (SCK), D10 (SS/CE0)
"""

# Display Assignment (2 displays only)
DISPLAY_ROLES = {
    "main": "hdmi",       # ElecLab 7" - conversation/activity feed
    "control": "ili9341",  # HiLetgo 2.4" - touch command panel
}

# HiLetgo 2.4" ILI9341 (240x320) - Touch Control Display
# Using Arduino UNO Q pins:
# - D10 (CE0) for SPI CS
# - D8 for DC (Data/Command)
# - D9 for RST (Reset)
# - D7 for Backlight
ILI9341_DISPLAY = {
    "width": 240,
    "height": 320,
    "spi_bus": 0,
    "spi_device": 0,  # CE0 (D10)
    "dc_pin": 8,      # D8 - Data/Command
    "rst_pin": 9,     # D9 - Reset
    "bl_pin": 7,      # D7 - Backlight
    "spi_speed_hz": 24000000,  # 24MHz
}

# ElecLab 7" HDMI (1024x600) - Main Display
HDMI_DISPLAY = {
    "width": 1024,
    "height": 600,
    "framebuffer": "/dev/fb0",  # Primary framebuffer
    "rotation": 0,  # 0, 90, 180, 270
}

# Touch Controller (XPT2046) on ILI9341
# Using D6 for manual chip select
TOUCH = {
    "cs_pin": 6,  # D6 - Manual chip select via GPIO
    "spi_speed_hz": 1500000,  # 1.5MHz for touch reads
    "min_pressure": 300,  # Minimum Z value to count as touch
    # Calibration values (will need calibration for your specific display)
    "x_min": 300,
    "x_max": 3900,
    "y_min": 300,
    "y_max": 3900,
    "swap_xy": False,  # Adjust based on orientation
    "invert_x": False,
    "invert_y": False,
}

# GPIO pins to cleanup (NO SPI pins 11, 12, 13, 10)
# Only our custom GPIO pins: D6, D7, D8, D9
GPIO_PINS = [6, 7, 8, 9]

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
    # ST7789 (240x240) - smaller fonts
    "st7789_small": 10,
    "st7789_medium": 12,
    "st7789_large": 14,
    # ILI9341 (240x320) - medium fonts
    "ili9341_small": 12,
    "ili9341_medium": 16,
    "ili9341_large": 20,
    # HDMI (1024x600) - larger fonts
    "hdmi_small": 16,
    "hdmi_medium": 20,
    "hdmi_large": 28,
    "hdmi_title": 36,
}

# Sprite paths
SPRITES = {
    "molty_dir": "assets/sprites",
}

# HDMI Display Layout (1024x600)
HDMI_LAYOUT = {
    "molty_panel_width": 300,           # Left panel for Molty
    "activity_panel_x": 300,            # Right panel starts here
    "header_height": 50,
    "footer_height": 30,
    "molty_position": (80, 100),        # Molty sprite position (scaled up)
    "molty_label_y": 280,               # State label Y position
}

# ILI9341 Command Panel Layout (240x320)
COMMAND_PANEL_LAYOUT = {
    "header_height": 35,
    "button_rows": 3,
    "button_cols": 2,
    "button_margin": 4,
    "button_padding": 8,
}

# ST7789 Status Panel Layout (240x240)
STATUS_PANEL_LAYOUT = {
    "header_height": 30,
    "footer_height": 30,
    "notification_max": 3,
    "notification_height": 50,
}

# OpenClaw Connection Settings
OPENCLAW = {
    "default_url": "ws://localhost:18789",
    "connection_timeout": 30.0,  # seconds
    "reconnect_delay": 1.0,  # initial delay in seconds
    "max_reconnect_delay": 60.0,  # max delay between reconnects
    "auto_reconnect": True,
}

# Demo Mode Settings
DEMO = {
    "message_interval": 3.0,  # seconds between new messages
    "status_change_interval": 2.0,  # seconds between status updates
}

# Notification Settings
NOTIFICATIONS = {
    "default_duration": 2.0,  # seconds
    "info_duration": 2.0,
    "success_duration": 1.5,
    "warning_duration": 3.0,
    "error_duration": 5.0,
    "persistent_types": ["connection_lost"],
    "max_visible": 3,
}

