# OpenClaw Display Setup for Raspberry Pi 4B

Complete setup guide for running the OpenClaw Display Dashboard on Raspberry Pi 4B with:
- **ElecLab 7" HDMI Display (1024x600)** - Main display
- **HiLetgo 2.4" ILI9341 SPI Display (240x320)** - Touch control panel

---

## Hardware Requirements

### Displays
1. **ElecLab 7" HDMI Display (1024x600)**
   - Connection: HDMI port (micro-HDMI on Pi 4B)
   - Power: USB or separate 5V supply

2. **HiLetgo 2.4" ILI9341 SPI Display with Touch (240x320)**
   - Connection: GPIO pins via SPI
   - Touch controller: XPT2046

### Raspberry Pi 4B
- Model: Raspberry Pi 4 Model B (2GB+ RAM recommended)
- OS: Raspberry Pi OS (Debian-based)
- MicroSD card: 16GB+ (Class 10 recommended)

---

## Part 1: Raspberry Pi OS Setup

### 1.1 Install Raspberry Pi OS

1. Download **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. Flash **Raspberry Pi OS (64-bit)** to your microSD card
3. Enable SSH and configure WiFi (optional) in the imager settings
4. Boot your Pi 4B

### 1.2 Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Enable SPI

```bash
sudo raspi-config
```

Navigate to:
- **3 Interface Options** → **I4 SPI** → **Yes**

Reboot:
```bash
sudo reboot
```

---

## Part 2: Hardware Wiring

### 2.1 HDMI Display

Connect the ElecLab 7" HDMI display to one of the Pi 4B's micro-HDMI ports using a micro-HDMI to HDMI cable.

### 2.2 ILI9341 SPI Display Wiring

Connect the HiLetgo 2.4" ILI9341 display to the Raspberry Pi 4B GPIO header:

| ILI9341 Pin | Pi 4B GPIO | Physical Pin | Function |
|-------------|------------|--------------|----------|
| VCC         | 3.3V       | 1 or 17      | Power    |
| GND         | GND        | 6, 9, 14, 20 | Ground   |
| CS          | GPIO 8     | 24           | SPI CE0  |
| RESET       | GPIO 24    | 18           | Reset    |
| DC/RS       | GPIO 25    | 22           | Data/Cmd |
| SDI (MOSI)  | GPIO 10    | 19           | SPI MOSI |
| SCK         | GPIO 11    | 23           | SPI CLK  |
| LED         | GPIO 23    | 16           | Backlight|
| SDO (MISO)  | GPIO 9     | 21           | SPI MISO |

### 2.3 Touch Controller Wiring

The XPT2046 touch controller shares the SPI bus:

| Touch Pin | Pi 4B GPIO | Physical Pin | Function |
|-----------|------------|--------------|----------|
| T_CLK     | GPIO 11    | 23           | SPI CLK  |
| T_CS      | GPIO 17    | 11           | Touch CS |
| T_DIN     | GPIO 10    | 19           | SPI MOSI |
| T_DO      | GPIO 9     | 21           | SPI MISO |
| T_IRQ     | (not used) | -            | Interrupt|

**Note**: We use polling mode for touch, so T_IRQ is not connected.

---

## Part 3: Software Installation

### 3.1 Install System Dependencies

```bash
sudo apt install -y python3-pip python3-dev python3-pil \
    git fonts-dejavu-core libfreetype6-dev libjpeg-dev \
    build-essential
```

### 3.2 Install Python Libraries

```bash
pip3 install --break-system-packages \
    spidev RPi.GPIO pillow websockets cryptography pynacl
```

### 3.3 Clone Repository

```bash
cd ~
git clone https://github.com/daycharles/OpenClaw-CyberDeck.git
cd OpenClaw-CyberDeck
```

---

## Part 4: Configuration

### 4.1 Test HDMI Display

The HDMI display should work automatically. Test it:

```bash
python3 test_hdmi.py
```

You should see a test pattern on the 7" HDMI display.

### 4.2 Test ILI9341 Display

```bash
python3 test_ili9341_pi4b.py
```

You should see a test pattern on the 2.4" SPI display.

### 4.3 Calibrate Touch

Run the touch calibration tool:

```bash
python3 calibrate_touch_pi4b.py
```

Follow the on-screen instructions to tap the corners. The calibration values will be saved to `config_pi4b.py`.

---

## Part 5: Running the Dashboard

### 5.1 Demo Mode (No OpenClaw Server)

Test the dashboard with simulated data:

```bash
python3 main_pi4b.py --demo
```

### 5.2 Connect to OpenClaw Server

Run with a local OpenClaw server:

```bash
python3 main_pi4b.py --url ws://localhost:18789
```

Or connect to a remote server:

```bash
python3 main_pi4b.py --url ws://192.168.1.100:18789
```

### 5.3 Auto-Start on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/openclaw-display.service
```

Add:

```ini
[Unit]
Description=OpenClaw Display Dashboard
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/OpenClaw-CyberDeck
ExecStart=/usr/bin/python3 /home/pi/OpenClaw-CyberDeck/main_pi4b.py --url ws://localhost:18789
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable openclaw-display.service
sudo systemctl start openclaw-display.service
```

---

## Troubleshooting

### HDMI Display Not Working

1. Check `/boot/config.txt` for HDMI settings:
   ```bash
   sudo nano /boot/config.txt
   ```

2. Add/uncomment:
   ```
   hdmi_force_hotplug=1
   hdmi_group=2
   hdmi_mode=87
   hdmi_cvt=1024 600 60 6 0 0 0
   ```

3. Reboot: `sudo reboot`

### SPI Display Not Working

1. Verify SPI is enabled:
   ```bash
   ls /dev/spi*
   ```
   Should show `/dev/spidev0.0` and `/dev/spidev0.1`

2. Check wiring connections
3. Try lowering SPI speed in `config_pi4b.py`

### Touch Not Responding

1. Run calibration: `python3 calibrate_touch_pi4b.py`
2. Check T_CS pin connection (GPIO 17)
3. Verify touch controller is XPT2046

---

## Next Steps

- Customize colors in `config_pi4b.py`
- Add Molty sprites to `assets/sprites/`
- Configure OpenClaw server connection
- Set up auto-start on boot

For more help, see the main README.md or visit the GitHub repository.

