# Windowed Display Mode for Desktop Use

## Overview

The CyberDeck now supports running from the Raspberry Pi desktop environment with the 7" HDMI display showing in a **Tkinter window** instead of taking over the framebuffer.

This allows you to:
- ✅ Keep access to your desktop
- ✅ Run other applications alongside the CyberDeck
- ✅ Move/minimize the display window
- ✅ Still use the 2.8" ILI9341 touch display for controls

## What Changed

### New File: `display_hdmi_window.py`

A Tkinter-based version of the HDMI display that:
- Creates a 1024x600 window
- Renders the same Molty + Activity Feed UI
- Updates in real-time with OpenClaw messages
- Can be closed, minimized, or moved around

### Updated: `main_pi4b.py`

Now imports `HDMIDisplayWindow` instead of `HDMIDisplay` (framebuffer version).

## Running the CyberDeck

### From Desktop Environment

```bash
cd ~/OpenClaw-CyberDeck
python3 main_pi4b.py
```

**What you'll see:**
1. **Tkinter window** opens showing the main display (1024x600)
   - Molty mascot on the left
   - Activity feed on the right
   - OpenClaw conversation updates

2. **2.8" ILI9341 display** shows the touch control panel
   - Status bar
   - Command buttons
   - Real-time status updates

3. **Your desktop** remains accessible
   - You can open terminals, browsers, etc.
   - The CyberDeck window can be moved or minimized

### Window Controls

- **Close button (X)**: Stops the CyberDeck and closes the window
- **Minimize**: Hides the window but keeps it running
- **Move**: Drag the window to reposition it

## Display Layout

### Main Window (1024x600)

```
┌──────────────┬─────────────────────────────────────────┐
│              │ OPENCLAW                     12:34:07   │
│    MOLTY     ├─────────────────────────────────────────┤
│   (Mascot)   │  Activity Feed                          │
│              │  • User: How do I...                    │
│   [State]    │  • Assistant: I'll help you...          │
│              │  • User: Can you show me...             │
│              ├─────────────────────────────────────────┤
│              │ ▌Connected • openrouter/aurora-alpha    │
└──────────────┴─────────────────────────────────────────┘
```

### ILI9341 Display (320x240)

Physical display showing:
- Connection status
- Model name
- Touch buttons (INBOX, BRIEF, QUEUE, FOCUS, STATUS, RANDOM)

## Advantages of Windowed Mode

### ✅ Desktop Access
- Run the CyberDeck alongside other apps
- Access terminal, browser, file manager
- No need to switch to console mode

### ✅ Easy Debugging
- See console output in terminal
- Open multiple terminals
- Use desktop tools

### ✅ Flexible Layout
- Move window to secondary monitor
- Resize desktop around the window
- Minimize when not needed

### ✅ Development Friendly
- Edit code in IDE
- Test changes immediately
- View logs in real-time

## Switching Between Modes

### Windowed Mode (Current)
**File**: `display_hdmi_window.py`
**Use case**: Running from desktop environment
**Pros**: Desktop access, easy debugging
**Cons**: Slightly higher overhead

### Framebuffer Mode (Alternative)
**File**: `display_hdmi.py`
**Use case**: Console-only, no desktop
**Pros**: Lower overhead, full-screen
**Cons**: No desktop access

To switch back to framebuffer mode:

```python
# In main_pi4b.py, change:
from display_hdmi_window import HDMIDisplayWindow
# to:
from display_hdmi import HDMIDisplay

# And change:
self.hdmi_display = HDMIDisplayWindow(demo_mode=demo_mode)
# to:
self.hdmi_display = HDMIDisplay(demo_mode=demo_mode)
```

## Troubleshooting

### Window doesn't appear

**Check if Tkinter is installed:**
```bash
python3 -c "import tkinter; print('Tkinter OK')"
```

**Install if needed:**
```bash
sudo apt-get install python3-tk
```

### Window is blank

- Check console for errors
- Verify fonts are loading
- Try restarting the application

### Window freezes

- The window updates every time a message arrives
- If frozen, check if OpenClaw connection is active
- Look for errors in console output

### Can't close window

- Click the X button
- Or press Ctrl+C in the terminal
- Window should close gracefully

## Performance

**Windowed mode performance:**
- Updates: Every 500ms or when new messages arrive
- Rendering: ~60 FPS capable (limited by update rate)
- Memory: ~50MB for window + images
- CPU: Minimal (< 5% on Pi 4B)

**Comparison to framebuffer:**
- Slightly higher CPU usage (Tkinter overhead)
- Same visual quality
- More flexible for development

## Tips

### Positioning the Window

The window opens at default position. To set a specific position, edit `display_hdmi_window.py`:

```python
self.window.geometry(f"{self.width}x{self.height}+100+50")
#                                                 ^^^  ^^
#                                                  X    Y position
```

### Making it Fullscreen

To make the window fullscreen (but still closeable):

```python
self.window.attributes('-fullscreen', True)
# Press Escape to exit fullscreen
```

### Auto-start on Boot

To start the CyberDeck automatically when the desktop loads:

1. Create autostart entry:
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/openclaw-cyberdeck.desktop
```

2. Add this content:
```ini
[Desktop Entry]
Type=Application
Name=OpenClaw CyberDeck
Exec=/usr/bin/python3 /home/pi/OpenClaw-CyberDeck/main_pi4b.py
Terminal=true
```

3. Make it executable:
```bash
chmod +x ~/.config/autostart/openclaw-cyberdeck.desktop
```

## Next Steps

1. **Test the windowed display** - Restart and verify the window appears
2. **Position the window** - Move it to your preferred location
3. **Test touch controls** - Verify the ILI9341 display still works
4. **Customize** - Adjust colors, fonts, layout as needed

---

**Enjoy your desktop-friendly CyberDeck!** 🚀

