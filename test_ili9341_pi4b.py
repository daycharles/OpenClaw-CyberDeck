#!/usr/bin/env python3
"""
Test script for HiLetgo 2.4" ILI9341 display on Raspberry Pi 4B.
Displays a test pattern to verify wiring and SPI communication.
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import config_pi4b as config

class ILI9341Test:
    """Simple ILI9341 test driver."""
    
    def __init__(self):
        self.width = config.ILI9341_DISPLAY["width"]
        self.height = config.ILI9341_DISPLAY["height"]
        self.dc_pin = config.ILI9341_DISPLAY["dc_pin"]
        self.rst_pin = config.ILI9341_DISPLAY["rst_pin"]
        self.bl_pin = config.ILI9341_DISPLAY["bl_pin"]
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.bl_pin, GPIO.OUT)
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(
            config.ILI9341_DISPLAY["spi_bus"],
            config.ILI9341_DISPLAY["spi_device"]
        )
        self.spi.max_speed_hz = config.ILI9341_DISPLAY["spi_speed_hz"]
        self.spi.mode = 0
        
        # Initialize display
        self.reset()
        self.init_display()
        
        # Turn on backlight
        GPIO.output(self.bl_pin, GPIO.HIGH)
    
    def reset(self):
        """Hardware reset."""
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)
    
    def write_cmd(self, cmd):
        """Write command byte."""
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])
    
    def write_data(self, data):
        """Write data bytes."""
        GPIO.output(self.dc_pin, GPIO.HIGH)
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)
    
    def init_display(self):
        """Initialize ILI9341."""
        self.write_cmd(0x01)  # Software reset
        time.sleep(0.15)
        
        self.write_cmd(0x28)  # Display OFF
        
        # Power control
        self.write_cmd(0xC0)
        self.write_data([0x23])
        
        self.write_cmd(0xC1)
        self.write_data([0x10])
        
        # VCOM control
        self.write_cmd(0xC5)
        self.write_data([0x3E, 0x28])
        
        self.write_cmd(0xC7)
        self.write_data([0x86])
        
        # Memory access control (rotation)
        self.write_cmd(0x36)
        self.write_data([0x48])  # MX, BGR
        
        # Pixel format
        self.write_cmd(0x3A)
        self.write_data([0x55])  # 16-bit color
        
        # Frame rate
        self.write_cmd(0xB1)
        self.write_data([0x00, 0x18])
        
        # Display function control
        self.write_cmd(0xB6)
        self.write_data([0x08, 0x82, 0x27])
        
        # Gamma
        self.write_cmd(0xF2)
        self.write_data([0x00])
        
        self.write_cmd(0x26)
        self.write_data([0x01])
        
        # Sleep out
        self.write_cmd(0x11)
        time.sleep(0.12)
        
        # Display on
        self.write_cmd(0x29)
        time.sleep(0.02)
    
    def set_window(self, x0, y0, x1, y1):
        """Set drawing window."""
        self.write_cmd(0x2A)  # Column address
        self.write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        
        self.write_cmd(0x2B)  # Row address
        self.write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        
        self.write_cmd(0x2C)  # Memory write
    
    def display_image(self, image):
        """Display PIL image."""
        # Convert to RGB565
        rgb_image = image.convert('RGB')
        pixels = list(rgb_image.getdata())
        
        # Convert to RGB565 bytes
        data = []
        for r, g, b in pixels:
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            data.append(rgb565 >> 8)
            data.append(rgb565 & 0xFF)
        
        # Send to display
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # Send in chunks
        chunk_size = 4096
        for i in range(0, len(data), chunk_size):
            self.write_data(data[i:i + chunk_size])
    
    def cleanup(self):
        """Cleanup GPIO."""
        GPIO.output(self.bl_pin, GPIO.LOW)
        self.spi.close()
        GPIO.cleanup()

def main():
    print("ILI9341 Test for Raspberry Pi 4B")
    print("=" * 40)
    
    # Initialize display
    print("Initializing display...")
    display = ILI9341Test()
    
    # Create test image
    print("Creating test pattern...")
    image = Image.new('RGB', (display.width, display.height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw color bars
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 255, 255),# White
    ]
    
    bar_height = display.height // len(colors)
    for i, color in enumerate(colors):
        y = i * bar_height
        draw.rectangle([0, y, display.width, y + bar_height], fill=color)
    
    # Add text
    try:
        font = ImageFont.truetype(config.FONTS["bold_path"], 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), "ILI9341 Test", fill=(0, 0, 0), font=font)
    draw.text((10, 40), "Pi 4B", fill=(0, 0, 0), font=font)
    
    # Display
    print("Displaying test pattern...")
    display.display_image(image)
    
    print("\nTest pattern displayed!")
    print("You should see colored bars on the display.")
    print("Press Ctrl+C to exit...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCleaning up...")
        display.cleanup()
        print("Done!")

if __name__ == "__main__":
    main()

