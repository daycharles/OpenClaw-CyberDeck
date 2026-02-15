#!/usr/bin/env python3
"""
Touch calibration tool for XPT2046 on Raspberry Pi 4B.
Helps determine the correct calibration values for your specific display.
"""

import time
import spidev
import RPi.GPIO as GPIO
import config_pi4b as config

class TouchCalibrator:
    """XPT2046 touch calibration tool."""
    
    def __init__(self):
        self.cs_pin = config.TOUCH["cs_pin"]
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Use same bus as display
        self.spi.max_speed_hz = config.TOUCH["spi_speed_hz"]
        self.spi.mode = 0
    
    def read_touch_raw(self):
        """Read raw touch coordinates."""
        GPIO.output(self.cs_pin, GPIO.LOW)
        
        # Read X
        x_data = self.spi.xfer2([0xD0, 0x00, 0x00])
        x = ((x_data[1] << 8) | x_data[2]) >> 3
        
        # Read Y
        y_data = self.spi.xfer2([0x90, 0x00, 0x00])
        y = ((y_data[1] << 8) | y_data[2]) >> 3
        
        # Read Z (pressure)
        z1_data = self.spi.xfer2([0xB0, 0x00, 0x00])
        z1 = ((z1_data[1] << 8) | z1_data[2]) >> 3
        
        z2_data = self.spi.xfer2([0xC0, 0x00, 0x00])
        z2 = ((z2_data[1] << 8) | z2_data[2]) >> 3
        
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
        # Calculate pressure
        z = z1 + 4095 - z2
        
        return x, y, z
    
    def wait_for_touch(self):
        """Wait for a touch event."""
        print("Waiting for touch...")
        while True:
            x, y, z = self.read_touch_raw()
            if z > config.TOUCH["min_pressure"]:
                # Wait for stable reading
                time.sleep(0.1)
                x, y, z = self.read_touch_raw()
                if z > config.TOUCH["min_pressure"]:
                    return x, y, z
            time.sleep(0.05)
    
    def wait_for_release(self):
        """Wait for touch release."""
        while True:
            x, y, z = self.read_touch_raw()
            if z < config.TOUCH["min_pressure"]:
                return
            time.sleep(0.05)
    
    def calibrate(self):
        """Run calibration procedure."""
        print("\n" + "=" * 50)
        print("Touch Calibration for XPT2046")
        print("=" * 50)
        print("\nYou will be asked to touch 4 corners of the screen.")
        print("Touch each corner firmly and hold for 1 second.\n")
        
        input("Press Enter to start calibration...")
        
        # Top-left
        print("\n1. Touch the TOP-LEFT corner...")
        tl_x, tl_y, _ = self.wait_for_touch()
        print(f"   Got: X={tl_x}, Y={tl_y}")
        self.wait_for_release()
        time.sleep(0.5)
        
        # Top-right
        print("\n2. Touch the TOP-RIGHT corner...")
        tr_x, tr_y, _ = self.wait_for_touch()
        print(f"   Got: X={tr_x}, Y={tr_y}")
        self.wait_for_release()
        time.sleep(0.5)
        
        # Bottom-left
        print("\n3. Touch the BOTTOM-LEFT corner...")
        bl_x, bl_y, _ = self.wait_for_touch()
        print(f"   Got: X={bl_x}, Y={bl_y}")
        self.wait_for_release()
        time.sleep(0.5)
        
        # Bottom-right
        print("\n4. Touch the BOTTOM-RIGHT corner...")
        br_x, br_y, _ = self.wait_for_touch()
        print(f"   Got: X={br_x}, Y={br_y}")
        self.wait_for_release()
        
        # Calculate calibration
        print("\n" + "=" * 50)
        print("Calibration Results")
        print("=" * 50)
        
        x_min = min(tl_x, bl_x)
        x_max = max(tr_x, br_x)
        y_min = min(tl_y, tr_y)
        y_max = max(bl_y, br_y)
        
        # Determine if axes need swapping
        x_range = abs(tr_x - tl_x)
        y_range = abs(bl_y - tl_y)
        swap_xy = x_range < y_range
        
        # Determine if axes need inverting
        invert_x = tl_x > tr_x
        invert_y = tl_y > bl_y
        
        print(f"\nX range: {x_min} - {x_max}")
        print(f"Y range: {y_min} - {y_max}")
        print(f"Swap X/Y: {swap_xy}")
        print(f"Invert X: {invert_x}")
        print(f"Invert Y: {invert_y}")
        
        print("\n" + "=" * 50)
        print("Add these values to config_pi4b.py:")
        print("=" * 50)
        print(f"""
TOUCH = {{
    "cs_pin": {config.TOUCH["cs_pin"]},
    "spi_speed_hz": {config.TOUCH["spi_speed_hz"]},
    "min_pressure": {config.TOUCH["min_pressure"]},
    "x_min": {x_min},
    "x_max": {x_max},
    "y_min": {y_min},
    "y_max": {y_max},
    "swap_xy": {swap_xy},
    "invert_x": {invert_x},
    "invert_y": {invert_y},
}}
""")
    
    def cleanup(self):
        """Cleanup GPIO."""
        self.spi.close()
        GPIO.cleanup()

def main():
    calibrator = TouchCalibrator()
    
    try:
        calibrator.calibrate()
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled.")
    finally:
        calibrator.cleanup()
        print("\nDone!")

if __name__ == "__main__":
    main()

