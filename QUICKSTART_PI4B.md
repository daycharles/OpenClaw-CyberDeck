# Quick Start Guide - Raspberry Pi 4B

Get your OpenClaw Display Dashboard running in 15 minutes!

---

## What You Need

- Raspberry Pi 4B with Raspberry Pi OS installed
- ElecLab 7" HDMI display
- HiLetgo 2.4" ILI9341 SPI display with touch
- Jumper wires for GPIO connections
- Internet connection

---

## Step 1: Enable SPI (2 minutes)

```bash
sudo raspi-config
```

- Navigate to: **3 Interface Options** → **I4 SPI** → **Yes**
- Reboot: `sudo reboot`

---

## Step 2: Install Dependencies (5 minutes)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y python3-pip python3-dev python3-pil git \
    fonts-dejavu-core libfreetype6-dev libjpeg-dev

# Install Python libraries
pip3 install --break-system-packages \
    spidev RPi.GPIO pillow websockets cryptography pynacl
```

---

## Step 3: Clone Repository (1 minute)

```bash
cd ~
git clone https://github.com/daycharles/OpenClaw-CyberDeck.git
cd OpenClaw-CyberDeck
```

---

## Step 4: Wire the Displays (5 minutes)

### HDMI Display
Connect to Pi 4B's micro-HDMI port with a micro-HDMI to HDMI cable.

### ILI9341 SPI Display

| Display Pin | Pi GPIO | Physical Pin |
|-------------|---------|--------------|
| VCC         | 3.3V    | 1            |
| GND         | GND     | 6            |
| CS          | GPIO 8  | 24           |
| RESET       | GPIO 24 | 18           |
| DC          | GPIO 25 | 22           |
| MOSI        | GPIO 10 | 19           |
| SCK         | GPIO 11 | 23           |
| LED         | GPIO 23 | 16           |
| MISO        | GPIO 9  | 21           |
| T_CLK       | GPIO 11 | 23           |
| T_CS        | GPIO 17 | 11           |
| T_DIN       | GPIO 10 | 19           |
| T_DO        | GPIO 9  | 21           |
| T_IRQ       | (skip)  | -            |

---

## Step 5: Test Displays (2 minutes)

### Test HDMI:
```bash
python3 test_hdmi.py
```

### Test ILI9341:
```bash
python3 test_ili9341_pi4b.py
```

You should see test patterns on both displays!

---

## Step 6: Calibrate Touch (2 minutes)

```bash
python3 calibrate_touch_pi4b.py
```

Follow the prompts to touch the 4 corners. Copy the output values to `config_pi4b.py`.

---

## Step 7: Run the Dashboard!

### Demo Mode (no server needed):
```bash
python3 main_pi4b.py --demo
```

### With OpenClaw Server:
```bash
python3 main_pi4b.py --url ws://localhost:18789
```

---

## What You Should See

- **HDMI Display**: Molty mascot on the left, activity feed on the right
- **ILI9341 Display**: 6 touch buttons with status bar at top

---

## Touch Buttons

| Button | Function |
|--------|----------|
| New Chat | Start new conversation |
| Clear | Clear activity feed |
| Pause | Pause OpenClaw |
| Resume | Resume OpenClaw |
| Settings | Show settings |
| Help | Show help |

---

## Troubleshooting

### HDMI display not working?
```bash
sudo nano /boot/config.txt
```
Add:
```
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=1024 600 60 6 0 0 0
```
Reboot: `sudo reboot`

### SPI display not working?
Check that SPI is enabled:
```bash
ls /dev/spi*
```
Should show `/dev/spidev0.0` and `/dev/spidev0.1`

### Touch not responding?
Run calibration again: `python3 calibrate_touch_pi4b.py`

---

## Next Steps

- Customize colors in `config_pi4b.py`
- Add Molty sprites to `assets/sprites/`
- Set up auto-start on boot (see SETUP_PI4B.md)
- Connect to your OpenClaw server

---

## Need More Help?

See the full setup guide: **SETUP_PI4B.md**

Or visit: https://github.com/daycharles/OpenClaw-CyberDeck

