# Troubleshooting Guide - Raspberry Pi 4B Setup

## ✅ Fixed Issues

### 1. GPIO Mode Not Set Error

**Error:**
```
[Touch] Initialization failed: Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)
```

**Fix:**
Added GPIO initialization in `main_pi4b.py` before initializing components:

```python
# Initialize GPIO system first (only in production mode)
if not demo_mode:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
```

This is now done in the `__init__()` method before creating the TouchHandler.

---

## 🔌 WebSocket Connection Issues

### Error: Connection Refused

**Error:**
```
[WebSocket] Connection error: Multiple exceptions: [Errno 111] Connect call failed ('::1', 18789, 0, 0), [Errno 111] Connect call failed ('127.0.0.1', 18789)
```

**Cause:**
No OpenClaw server is running on `localhost:18789`.

**Solutions:**

#### Option 1: Use Demo Mode (Recommended for Testing)

```bash
python3 main_pi4b.py --demo
```

This runs the dashboard with simulated data - no server needed!

#### Option 2: Start an OpenClaw Server

You need to have an OpenClaw server running. Options:

**A. Run OpenClaw locally:**
```bash
# Clone and run OpenClaw server
git clone https://github.com/openclawai/openclaw.git
cd openclaw
# Follow OpenClaw setup instructions
npm install
npm start
```

**B. Connect to a remote OpenClaw server:**
```bash
# Replace with your actual server URL
python3 main_pi4b.py --url wss://your-server.com:18789
```

**C. Use Hostinger or another hosting service:**
- Deploy OpenClaw to a cloud server
- Get the WebSocket URL (e.g., `wss://your-domain.com:18789`)
- Connect: `python3 main_pi4b.py --url wss://your-domain.com:18789`

---

## 📋 Current Status

### What's Working ✅

- GPIO initialization (BCM mode)
- Touch handler initialization
- Display initialization (HDMI + ILI9341)
- OpenClaw bridge initialization
- Demo mode with simulated messages
- Touch callbacks (top/bottom tap detection)

### What Needs Configuration ⚙️

1. **OpenClaw Server** - You need a running server to connect to
2. **Touch Calibration** - Run `calibrate_touch_pi4b.py` to calibrate touch input
3. **Display Wiring** - Make sure displays are wired correctly per `SETUP_PI4B.md`

---

## 🧪 Testing Steps

### 1. Test in Demo Mode (No Server Needed)

```bash
cd ~/OpenClaw-CyberDeck
python3 main_pi4b.py --demo
```

**Expected Output:**
```
[Pi4B] GPIO initialized (BCM mode)
Initializing HDMI display...
Initializing ILI9341 control display...
Initializing touch handler...
Initializing OpenClaw bridge...
[Touch] Initialized (polling mode with manual CS via GPIO 17)
[Touch] Starting touch handler (polling mode)
Running in DEMO mode
Dashboard running. Press Ctrl+C to exit.
[Bridge] Message: user: How do I configure the display?...
[Bridge] Message: assistant: I'll help you configure the display settings.....
```

### 2. Test Touch Input

While running in demo mode, tap the ILI9341 display:
- **Top half** → Should print "Touch: Top region"
- **Bottom half** → Should print "Touch: Bottom region"

### 3. Test with OpenClaw Server

**First, make sure you have a server running:**
```bash
# Check if server is accessible
curl http://localhost:18789
# or
telnet localhost 18789
```

**Then connect:**
```bash
python3 main_pi4b.py --url ws://localhost:18789
```

---

## 🐛 Common Issues

### Issue: "Connection refused" even with server running

**Check:**
1. Is the server actually listening on port 18789?
   ```bash
   netstat -an | grep 18789
   ```

2. Is it listening on the right interface?
   - `127.0.0.1` = localhost only
   - `0.0.0.0` = all interfaces

3. Firewall blocking the connection?
   ```bash
   sudo ufw status
   ```

### Issue: Touch not responding

**Solutions:**
1. Run calibration: `python3 calibrate_touch_pi4b.py`
2. Check wiring (see `SETUP_PI4B.md`)
3. Verify GPIO 17 is connected to Touch CS pin

### Issue: Display not showing anything

**Solutions:**
1. Check SPI is enabled: `ls /dev/spidev*`
2. Run individual tests:
   ```bash
   python3 test_ili9341_pi4b.py
   python3 test_hdmi.py
   ```
3. Verify wiring matches `SETUP_PI4B.md`

---

## 📚 Next Steps

1. ✅ **Test in demo mode** - Verify everything initializes
2. ⚙️ **Calibrate touch** - Run `calibrate_touch_pi4b.py`
3. 🔌 **Set up OpenClaw server** - Deploy or run locally
4. 🚀 **Connect and test** - Run with `--url` parameter

---

## 🆘 Getting Help

If you're still having issues:

1. Check the full error output
2. Verify hardware connections
3. Test each component individually
4. Check OpenClaw server logs
5. Review `SETUP_PI4B.md` for wiring details

**GitHub Issues:** https://github.com/daycharles/OpenClaw-CyberDeck/issues

