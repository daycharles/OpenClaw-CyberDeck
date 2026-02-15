# OpenClaw Display Setup for Arduino UNO Q

Complete setup guide for running the OpenClaw Cyberpunk Display Dashboard on Arduino UNO Q with **two displays**.

## Hardware Overview

### Arduino UNO Q

- **Processor**: Raspberry Pi CM4 (Compute Module 4)
- **RAM**: 2GB
- **OS**: **Debian Linux** (not Raspberry Pi OS)
- **GPIO**: 40-pin header (same as Raspberry Pi 4)
- **Programming**: Python (recommended) or Arduino IDE

### Supported Displays (2 displays only)

1. **ElecLab 7" HDMI (1024x600)** - HDMI framebuffer
   - Main conversation/activity display
   - HDMI connection (no SPI)
2. **HiLetgo 2.4" TFT (240x320)** - ILI9341 SPI + Touch
   - Touch command panel
   - XPT2046 resistive touch controller

---

## Part 1: Arduino UNO Q Setup

### 1.1 Initial Boot

1. **Flash Debian OS** to the UNO Q's eMMC or microSD (follow Arduino's official guide)

2. **Enable SSH** and connect:
   ```bash
   ssh user@arduino-uno-q.local
   # Use your configured username/password
   ```

### 1.2 Enable SPI

On Debian, enable SPI by editing the boot configuration:

```bash
# Check if SPI is already available
ls /dev/spidev*
# Should show: /dev/spidev0.0  /dev/spidev0.1

# If not available, enable SPI
sudo nano /boot/config.txt
# Add or uncomment this line:
dtparam=spi=on

# Save (Ctrl+O, Enter, Ctrl+X) and reboot
sudo reboot
```

After reboot, verify SPI is enabled:

```bash
ls /dev/spidev*
# Should now show SPI devices
```

### 1.3 Install Dependencies (Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv git

# Install system libraries
sudo apt install -y \
    python3-dev \
    python3-pil \
    python3-numpy \
    libfreetype6-dev \
    libjpeg-dev \
    build-essential

# Install SPI/GPIO libraries (Debian may not have these in apt)
sudo pip3 install --break-system-packages \
    spidev \
    RPi.GPIO \
    pillow \
    python-dotenv \
    websockets \
    cryptography \
    pynacl

# Add user to GPIO/SPI groups
sudo usermod -a -G gpio,spi $USER
# Log out and back in for group changes to take effect
```

---

## Part 2: Hardware Wiring (2 Displays Only)

### 2.1 Pin Assignments

| Display      | Type    | SPI Bus | CS Pin       | DC Pin  | RST Pin | BL Pin  | Touch CS |
| ------------ | ------- | ------- | ------------ | ------- | ------- | ------- | -------- |
| HiLetgo 2.4" | ILI9341 | SPI0    | CE1 (GPIO 7) | GPIO 22 | GPIO 27 | GPIO 23 | GPIO 17  |
| ElecLab 7"   | HDMI    | -       | -            | -       | -       | -       | -        |

### 2.2 HiLetgo 2.4" ILI9341 Wiring

```
HiLetgo 2.4"      →    Arduino UNO Q
─────────────────────────────────────
VCC               →    3.3V (Pin 1)
GND               →    GND (Pin 6)
CS                →    GPIO 7 / CE1 (Pin 26)
RESET             →    GPIO 27 (Pin 13)
DC/RS             →    GPIO 22 (Pin 15)
SDI/MOSI          →    GPIO 10 / MOSI (Pin 19)
SCK               →    GPIO 11 / SCLK (Pin 23)
LED               →    GPIO 23 (Pin 16)
SDO/MISO          →    GPIO 9 / MISO (Pin 21)
T_CLK             →    GPIO 11 / SCLK (Pin 23) [shared]
T_CS              →    GPIO 17 (Pin 11)
T_DIN             →    GPIO 10 / MOSI (Pin 19) [shared]
T_DO              →    GPIO 9 / MISO (Pin 21) [shared]
T_IRQ             →    Not connected (polling mode)
```

### 2.3 ElecLab 7" HDMI Connection

```
ElecLab 7"        →    Arduino UNO Q
─────────────────────────────────────
HDMI              →    HDMI port (micro HDMI on CM4)
USB (touch)       →    USB port (if touch-enabled variant)
5V Power          →    External 5V 2A power supply
```

**Note**: The HDMI display uses the framebuffer, not SPI. No GPIO wiring needed.

---

## Part 3: Software Installation

### 3.1 Clone Repository

```bash
cd ~
git clone https://github.com/daycharles/OpenClaw-CyberDeck.git
cd OpenClaw-CyberDeck
```

### 3.2 Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3.3 Configure Displays

The `config_uno_q.py` file is already configured for two displays:

```python
# Display assignments (2 displays only)
DISPLAY_ROLES = {
    "main": "hdmi",       # ElecLab 7" - conversation/activity feed
    "control": "ili9341",  # HiLetgo 2.4" - touch command panel
}
```

---

## Part 4: Running the Dashboard

### 4.1 Test Individual Displays

```bash
# Test HiLetgo 2.4" ILI9341
python3 test_ili9341.py

# Test HDMI framebuffer
python3 test_hdmi.py
```

### 4.2 Run Full Dashboard

```bash
# Demo mode (no OpenClaw server)
python3 main_uno_q.py --demo

# Connect to OpenClaw server
python3 main_uno_q.py --url ws://localhost:18789

# Connect via Tailscale
python3 main_uno_q.py --url wss://your-tailscale-hostname:18789
```

### 4.3 Auto-start on Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/openclaw-display.service
```

Paste:

```ini
[Unit]
Description=OpenClaw Display Dashboard
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/OpenClaw-CyberDeck
ExecStart=/home/pi/OpenClaw-CyberDeck/venv/bin/python3 main_uno_q.py --url ws://localhost:18789
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-display.service
sudo systemctl start openclaw-display.service
```

---

## Part 5: Touch Calibration

The HiLetgo 2.4" display includes an XPT2046 touch controller that needs calibration.

### 5.1 Run Calibration Script

```bash
cd ~/OpenClaw-CyberDeck
python3 calibrate_touch.py
```

Follow the on-screen instructions:

1. Touch the top-left corner when prompted
2. Touch the bottom-right corner when prompted
3. Calibration values will be saved to `config_uno_q.py`

### 5.2 Manual Calibration

If automatic calibration doesn't work, edit `config_uno_q.py`:

```python
TOUCH = {
    "x_min": 300,    # Adjust based on your display
    "x_max": 3900,
    "y_min": 300,
    "y_max": 3900,
    "swap_xy": False,  # Set to True if axes are swapped
    "invert_x": False, # Set to True if X is inverted
    "invert_y": False, # Set to True if Y is inverted
}
```

---

## Part 6: Programming with Arduino App Lab (Optional)

The Arduino UNO Q can run Arduino sketches via **Arduino App Lab** (web-based IDE), but **Python is strongly recommended** for this project.

### Why Python is Better for This Project:

✅ **Complex UI rendering** (PIL/Pillow library)
✅ **WebSocket client** with Ed25519 cryptography
✅ **Multi-threading** for simultaneous display updates
✅ **Framebuffer access** for HDMI display
✅ **Rich ecosystem** of libraries

### If You Want to Use Arduino App Lab:

**Note**: This would require a **complete rewrite** from scratch in C++.

1. **Access Arduino App Lab**: https://app.arduino.cc/
2. **Connect UNO Q**: Via USB or network
3. **Limitations**:
   - CM4 is not a traditional Arduino microcontroller
   - No native Arduino libraries for framebuffer, complex graphics
   - Would need to write low-level SPI drivers in C++
   - Memory/performance constraints for complex UI

**Recommendation**: Use Python on the UNO Q's Linux OS. If you want to use Arduino C++, consider using an ESP32 or Arduino Mega with simpler displays (no HDMI).

---

## Part 7: Arduino C++ Example (Simple Version)

If you want to experiment with Arduino C++ on a traditional Arduino board (e.g., ESP32, Mega), here's a simplified example for a single ILI9341 display:

```cpp
// Simple ILI9341 display example for Arduino
// Requires: Adafruit_ILI9341 and Adafruit_GFX libraries

#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

#define TFT_CS   10
#define TFT_DC   9
#define TFT_RST  8

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);

void setup() {
  Serial.begin(115200);
  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(ILI9341_BLACK);

  // Draw simple UI
  tft.setTextColor(ILI9341_CYAN);
  tft.setTextSize(2);
  tft.setCursor(10, 10);
  tft.println("OPENCLAW");

  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(1);
  tft.setCursor(10, 40);
  tft.println("Status: Ready");
}

void loop() {
  // Update display
  delay(1000);
}
```

**This is NOT compatible with the Arduino UNO Q** - it's for traditional Arduino boards only.

---

## Troubleshooting

### SPI Not Working

```bash
# Check SPI is enabled
ls /dev/spidev*
# Should show: /dev/spidev0.0  /dev/spidev0.1

# Check permissions
sudo usermod -a -G spi,gpio pi
```

### Display Shows Garbage

- Check wiring (especially DC pin)
- Verify 3.3V power (not 5V!)
- Try lower SPI speed in config

### HDMI Display Not Detected

```bash
# Check HDMI output
tvservice -s

# Force HDMI mode in /boot/config.txt
sudo nano /boot/config.txt
# Add: hdmi_force_hotplug=1
# Add: hdmi_group=2
# Add: hdmi_mode=87
# Add: hdmi_cvt=1024 600 60 6 0 0 0
```

### Touch Not Responding

- Touch uses polling (no IRQ)
- Check T_CS pin connection
- Run calibration: `python3 calibrate_touch.py`

---

## Next Steps

1. ✅ Hardware wired and tested
2. ✅ Software installed
3. ✅ Displays working
4. 🔄 Configure OpenClaw connection
5. 🔄 Customize button commands
6. 🔄 Add custom Molty sprites

See `README.md` for OpenClaw server setup and WebSocket protocol details.
