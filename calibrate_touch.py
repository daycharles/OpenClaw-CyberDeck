#!/usr/bin/env python3
"""
Touch calibration script for XPT2046 touch controller.
Helps calibrate the HiLetgo 2.4" ILI9341 touch display.
"""

import time
import sys

try:
    import spidev
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("ERROR: RPi.GPIO or spidev not available")
    sys.exit(1)

import config_uno_q as config


class TouchCalibrator:
    """Simple touch calibration tool."""
    
    def __init__(self):
        self.cs_pin = config.TOUCH["cs_pin"]
        self.spi = None
        self.samples = []
        
    def initialize(self):
        """Initialize SPI and GPIO."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Use SPI0.0 for touch
        self.spi.max_speed_hz = config.TOUCH["spi_speed_hz"]
        self.spi.mode = 0
        
    def read_touch_raw(self):
        """Read raw touch coordinates."""
        GPIO.output(self.cs_pin, GPIO.LOW)
        time.sleep(0.001)
        
        # Read X
        x_data = self.spi.xfer([0x90, 0x00, 0x00])
        x = ((x_data[1] << 8) | x_data[2]) >> 3
        
        # Read Y
        y_data = self.spi.xfer([0xD0, 0x00, 0x00])
        y = ((y_data[1] << 8) | y_data[2]) >> 3
        
        # Read Z (pressure)
        z1_data = self.spi.xfer([0xB0, 0x00, 0x00])
        z1 = ((z1_data[1] << 8) | z1_data[2]) >> 3
        
        z2_data = self.spi.xfer([0xC0, 0x00, 0x00])
        z2 = ((z2_data[1] << 8) | z2_data[2]) >> 3
        
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
        # Calculate pressure
        z = z1 + 4095 - z2 if z1 > 0 else 0
        
        return x, y, z
        
    def wait_for_touch(self, prompt):
        """Wait for user to touch the screen."""
        print(f"\n{prompt}")
        print("Waiting for touch...")
        
        # Wait for no touch
        while True:
            _, _, z = self.read_touch_raw()
            if z < 300:
                break
            time.sleep(0.1)
            
        # Wait for touch
        samples = []
        while len(samples) < 10:
            x, y, z = self.read_touch_raw()
            if z > 300:
                samples.append((x, y))
                time.sleep(0.05)
            else:
                if samples:
                    # Touch released, calculate average
                    avg_x = sum(s[0] for s in samples) // len(samples)
                    avg_y = sum(s[1] for s in samples) // len(samples)
                    print(f"Touch detected: X={avg_x}, Y={avg_y}")
                    return avg_x, avg_y
                    
        # If we got here, calculate average of all samples
        avg_x = sum(s[0] for s in samples) // len(samples)
        avg_y = sum(s[1] for s in samples) // len(samples)
        print(f"Touch detected: X={avg_x}, Y={avg_y}")
        return avg_x, avg_y
        
    def calibrate(self):
        """Run calibration procedure."""
        print("=== Touch Calibration ===")
        print("This will calibrate the touch screen for accurate input.")
        print("\nMake sure the display is showing a calibration pattern")
        print("with markers in the corners.")
        
        input("\nPress Enter to start calibration...")
        
        # Get top-left corner
        x1, y1 = self.wait_for_touch("Touch the TOP-LEFT corner (20, 20)")
        time.sleep(1)
        
        # Get bottom-right corner
        x2, y2 = self.wait_for_touch("Touch the BOTTOM-RIGHT corner (220, 300)")
        time.sleep(1)
        
        # Calculate calibration
        print("\n=== Calibration Results ===")
        print(f"Top-left:     X={x1}, Y={y1}")
        print(f"Bottom-right: X={x2}, Y={y2}")
        
        # Determine if axes need swapping or inverting
        swap_xy = abs(x2 - x1) < abs(y2 - y1)
        invert_x = x2 < x1
        invert_y = y2 < y1
        
        print(f"\nCalibration settings:")
        print(f"  x_min: {min(x1, x2)}")
        print(f"  x_max: {max(x1, x2)}")
        print(f"  y_min: {min(y1, y2)}")
        print(f"  y_max: {max(y1, y2)}")
        print(f"  swap_xy: {swap_xy}")
        print(f"  invert_x: {invert_x}")
        print(f"  invert_y: {invert_y}")
        
        print("\nUpdate config_uno_q.py with these values:")
        print(f"""
TOUCH = {{
    "cs_pin": {self.cs_pin},
    "spi_speed_hz": {config.TOUCH["spi_speed_hz"]},
    "min_pressure": 300,
    "x_min": {min(x1, x2)},
    "x_max": {max(x1, x2)},
    "y_min": {min(y1, y2)},
    "y_max": {max(y1, y2)},
    "swap_xy": {swap_xy},
    "invert_x": {invert_x},
    "invert_y": {invert_y},
}}
""")
        
    def cleanup(self):
        """Cleanup resources."""
        if self.spi:
            self.spi.close()
        GPIO.cleanup([self.cs_pin])
        

def main():
    calibrator = TouchCalibrator()
    
    try:
        calibrator.initialize()
        calibrator.calibrate()
    except KeyboardInterrupt:
        print("\nCalibration cancelled")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        calibrator.cleanup()
        

if __name__ == "__main__":
    main()

