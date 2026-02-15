# ILI9341 Display Fix

## Problem

The ILI9341 (2.8" display) was not showing anything even though the connection to OpenClaw was successful.

## Root Cause

The display hardware was being initialized in the constructor, but:
1. The `initialize()` method was never called to set up the SPI hardware
2. The `run()` rendering loop was never started
3. No thread was created to continuously update the display

## Solution

Updated `main_pi4b.py` to:

1. **Call `initialize()` on both displays** before starting them
2. **Start the ILI9341 rendering loop** in a background thread
3. **Pass status callback** so the display can get live updates from OpenClaw
4. **Add proper error handling** for HDMI display (which may not work on all setups)

## Changes Made

### `main_pi4b.py`

- Added display initialization calls before starting
- Created a background thread for the ILI9341 display rendering loop
- Configured the display to poll status from the OpenClaw bridge every 500ms
- Added error handling for HDMI display (optional component)
- Added proper cleanup in `stop()` method

## Testing

After restarting the application, you should see:

1. **Console output**:
   ```
   Initializing display hardware...
   [Display2] Initialized: 320x240 (ILI9341 RGB565)
   [Pi4B] Starting ILI9341 display render loop...
   [Display2] Starting render loop
   ```

2. **ILI9341 Display** should show:
   - **Status bar** at top with connection indicator and model name
   - **Command buttons** in a grid layout:
     - INBOX, BRIEF
     - QUEUE, FOCUS
     - STATUS, RANDOM
   - **Cyberpunk theme** with neon colors

3. **Touch interaction**:
   - Touching the screen should trigger button presses
   - Console will show touch coordinates

## What the Display Shows

The ILI9341 display renders a **Cyberpunk Command Panel** with:

### Status Bar (top 35px)
- Connection indicator (● green when connected)
- Model name (e.g., "openrouter/aurora-alpha")
- API cost (e.g., "$0.0012")

### Command Buttons (6 buttons in 3x2 grid)
- **INBOX**: View inbox
- **BRIEF**: Brief mode
- **QUEUE**: View queue
- **FOCUS**: Focus mode
- **STATUS**: Show status
- **RANDOM**: Random mode

### Visual Style
- Black background
- Neon cyan primary accent (#00ffff)
- Hot pink secondary accent (#ff0066)
- Glowing borders on buttons
- Cyberpunk aesthetic

## Troubleshooting

### Display still blank?

1. **Check backlight**: The backlight should turn on after initialization
   ```bash
   # Manually test backlight
   echo 1 | sudo tee /sys/class/gpio/gpio23/value
   ```

2. **Check SPI connection**: Verify SPI is working
   ```bash
   ls -l /dev/spidev0.1
   ```
   Should show: `crw-rw---- 1 root spi 153, 1`

3. **Check console output**: Look for initialization errors
   ```
   [Display2] Initialized: 320x240 (ILI9341 RGB565)
   [Display2] Starting render loop
   ```

4. **Verify GPIO pins**: Make sure wiring matches config_pi4b.py:
   - GPIO 25 = DC (Data/Command)
   - GPIO 24 = RST (Reset)
   - GPIO 23 = BL (Backlight)
   - GPIO 8 (CE0) = CS (Chip Select)

### Display shows garbage/noise?

This usually means:
- SPI speed too high (try reducing in config_pi4b.py)
- Wrong SPI mode (should be mode 0)
- Incorrect DC pin wiring

### Display is dim or flickering?

- Check backlight connection (GPIO 23)
- Verify power supply is adequate (5V 3A recommended)

### Touch not working?

Touch is handled separately by `touch_handler.py`. Check:
- Touch CS pin (GPIO 17)
- Touch is in polling mode (no IRQ)
- Console should show touch coordinates when you tap

## Next Steps

Once the ILI9341 display is working:

1. **Test touch buttons**: Tap each button and verify console output
2. **Implement button actions**: Connect buttons to OpenClaw commands
3. **Monitor status updates**: Watch the status bar update as you use OpenClaw
4. **Customize theme**: Modify colors in `ui/cyberpunk_theme.py`

## Files Modified

- `main_pi4b.py` - Added display initialization and rendering loop
- `openclaw_config.py` - Added token support (already done)
- `websocket_client.py` - Added token parameter (already done)
- `openclaw_bridge.py` - Updated to use token (already done)

## Related Documentation

- `TOKEN_SETUP.md` - How to configure authentication token
- `config_pi4b.py` - Hardware pin configuration
- `TROUBLESHOOTING_PI4B.md` - General troubleshooting guide

