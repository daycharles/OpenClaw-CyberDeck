# Quick Start Guide - Arduino UNO Q

Get your OpenClaw Display Dashboard running in 15 minutes!

## Prerequisites

- ✅ Arduino UNO Q (CM4-based, 2GB RAM)
- ✅ Two displays wired according to `SETUP_ARDUINO_UNO_Q.md`
- ✅ **Debian OS** installed on UNO Q
- ✅ SSH access to UNO Q

## Step 1: Enable SPI (2 minutes)

```bash
ssh user@arduino-uno-q.local

# Check if SPI is available
ls /dev/spidev*

# If not, enable SPI in boot config
sudo nano /boot/config.txt
# Add: dtparam=spi=on
# Save and reboot
sudo reboot
```

## Step 2: Install Dependencies (5 minutes)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python libraries (Debian)
sudo apt install -y python3 python3-pip python3-venv git \
    python3-dev python3-pil python3-numpy \
    libfreetype6-dev libjpeg-dev build-essential

# Install Python packages
sudo pip3 install --break-system-packages \
    spidev RPi.GPIO pillow python-dotenv \
    websockets cryptography pynacl

# Add user to GPIO/SPI groups
sudo usermod -a -G gpio,spi $USER
```

## Step 3: Clone Repository (1 minute)

```bash
cd ~
git clone https://github.com/daycharles/OpenClaw-CyberDeck.git
cd OpenClaw-CyberDeck
```

## Step 4: Test Displays (2 minutes)

Test each display individually:

```bash
# Test HiLetgo 2.4" ILI9341 (command panel)
python3 test_ili9341.py

# Test ElecLab 7" HDMI (main display)
python3 test_hdmi.py
```

**Expected**: Each display should show a test pattern with text and graphics.

**If a display doesn't work**: Check wiring in `SETUP_ARDUINO_UNO_Q.md` Part 2.

## Step 5: Calibrate Touch (2 minutes)

```bash
python3 calibrate_touch.py
```

Follow the on-screen instructions to touch the corners. Update `config_uno_q.py` with the calibration values.

## Step 6: Run Dashboard (2 minutes)

### Demo Mode (no OpenClaw server needed):

```bash
python3 main_uno_q.py --demo
```

### Connect to OpenClaw Server:

```bash
# Local server
python3 main_uno_q.py --url ws://localhost:18789

# Remote server (Tailscale)
python3 main_uno_q.py --url wss://your-server.tailscale.net:18789
```

## Step 7: Auto-Start on Boot (Optional)

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
ExecStart=/usr/bin/python3 main_uno_q.py --url ws://localhost:18789
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-display.service
sudo systemctl start openclaw-display.service
```

Check status:

```bash
sudo systemctl status openclaw-display.service
```

---

## Display Layout

Once running, you should see:

### 📺 ElecLab 7" HDMI (Main Display)

- **Left panel**: Molty the space lobster mascot
- **Right panel**: Activity feed with conversation history
- **Header**: "OPENCLAW" title and clock
- **Footer**: Status bar

### 📱 HiLetgo 2.4" ILI9341 (Command Panel)

- **Top bar**: Connection status, model name, API cost
- **6 buttons**: INBOX, QUEUE, STATUS, BRIEF, FOCUS, RANDOM
- Touch buttons to send commands

---

## Troubleshooting

### Display shows garbage or nothing

- Check wiring (especially DC pin)
- Verify 3.3V power (NOT 5V!)
- Try lower SPI speed in `config_uno_q.py`

### HDMI display not detected

```bash
tvservice -s  # Check HDMI status

# Force HDMI in /boot/config.txt
sudo nano /boot/config.txt
# Add:
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=1024 600 60 6 0 0 0
```

### Touch not responding

- Run calibration: `python3 calibrate_touch.py`
- Check T_CS pin (GPIO 17)
- Touch uses polling (no IRQ needed)

### SPI not working

```bash
ls /dev/spidev*
# Should show: /dev/spidev0.0  /dev/spidev0.1

# Add user to SPI group
sudo usermod -a -G spi,gpio pi
```

---

## Next Steps

1. ✅ **Customize buttons**: Edit `ui/command_panel.py` to change button labels/commands
2. ✅ **Add Molty sprites**: Place custom sprites in `assets/sprites/`
3. ✅ **Configure OpenClaw**: Set up OpenClaw server (see main `README.md`)
4. ✅ **Adjust colors**: Modify `config_uno_q.py` CYBERPUNK_COLORS

---

## Support

- **Full setup guide**: `SETUP_ARDUINO_UNO_Q.md`
- **Hardware wiring**: `SETUP_ARDUINO_UNO_Q.md` Part 2
- **OpenClaw protocol**: `README.md` and `CLAUDE.md`
- **Issues**: https://github.com/daycharles/OpenClaw-CyberDeck/issues

Enjoy your cyberpunk command center! 🚀🦞
