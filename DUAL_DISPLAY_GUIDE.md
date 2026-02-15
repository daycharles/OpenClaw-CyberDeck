# Dual Display Setup - Pi 4B CyberDeck

Your CyberDeck has **two displays** working together to give you a complete OpenClaw interface:

## Display 1: 7" HDMI Display (1024x600) - Main View

**Purpose**: Conversation and activity monitoring

**What it shows**:
- **Left panel (300px)**: Molty mascot with animated states
  - IDLE: Waiting for activity
  - LISTENING: User is typing/speaking
  - THINKING: Processing request
  - TALKING: Assistant is responding
  - SLEEPING: Disconnected

- **Right panel (724px)**: Activity feed and status
  - **Header**: "OPENCLAW" title and current time
  - **Activity Feed**: Scrolling list of recent messages and events
  - **Footer**: Current status (model, task, connection state)

**Technology**: Linux framebuffer (`/dev/fb0`)

**Updates**: Every 500ms with new messages and status

---

## Display 2: 2.8" ILI9341 (320x240) - Touch Control Panel

**Purpose**: Quick commands and status monitoring

**What it shows**:
- **Status Bar (top 35px)**:
  - Connection indicator (● green/red)
  - Model name (e.g., "openrouter/aurora-alpha")
  - API cost (e.g., "$0.0012")

- **Command Buttons (6 buttons in 3x2 grid)**:
  - **INBOX**: View inbox
  - **BRIEF**: Brief mode
  - **QUEUE**: View queue
  - **FOCUS**: Focus mode
  - **STATUS**: Show status
  - **RANDOM**: Random mode

**Technology**: SPI display with touch controller

**Updates**: Continuous rendering loop (2 times per second)

**Touch**: XPT2046 touch controller in polling mode

---

## How They Work Together

### Data Flow

```
OpenClaw Server (WebSocket)
         ↓
   OpenClaw Bridge
    ↙          ↘
HDMI Display   ILI9341 Display
(Messages)     (Status/Commands)
```

### HDMI Display (7")
- Receives **all messages** from conversation
- Shows **activity feed** with user/assistant messages
- Updates **Molty state** based on activity
- Displays **status text** in footer

### ILI9341 Display (2.8")
- Shows **current status** in real-time
- Provides **touch buttons** for commands
- Displays **connection state** and **model info**
- Updates **API cost** as you use OpenClaw

---

## What You Should See

### On Startup

**Console output**:
```
[Config] Loaded .env from /home/pi/OpenClaw-CyberDeck/.env
[Pi4B] GPIO initialized (BCM mode)
Initializing HDMI display...
[HDMI] Using Pi 4B configuration
Initializing ILI9341 control display...
Initializing touch handler...
Initializing OpenClaw bridge...
[Touch] Initialized (polling mode with manual CS via GPIO 17)
[Touch] Starting touch handler (polling mode)
[WebSocket] Loaded device keys (ID: 6dd57380...)
Initializing display hardware...
[HDMI] Running in demo mode (no framebuffer)  ← May show this if framebuffer not available
[Display2] Initialized: 320x240 (ILI9341 RGB565)
[Pi4B] Starting ILI9341 display render loop...
[Display2] Starting render loop
[Bridge] Connecting to ws://localhost:18789
Dashboard running. Press Ctrl+C to exit.
[WebSocket] Connected successfully
[WebSocket] Using session: key=agent:main:main model=openrouter/aurora-alpha
```

### 7" HDMI Display
- Black background with cyberpunk theme
- Molty mascot on the left (animated)
- Activity feed on the right showing conversation
- Status bar at bottom

### 2.8" ILI9341 Display
- Neon cyan/pink cyberpunk theme
- Status bar at top with connection indicator
- 6 command buttons in grid layout
- Glowing borders and effects

---

## Troubleshooting

### HDMI Display Not Working

**Symptom**: Console shows "Running in demo mode (no framebuffer)"

**Cause**: Framebuffer `/dev/fb0` not accessible

**Solutions**:
1. Check if framebuffer exists:
   ```bash
   ls -l /dev/fb0
   ```

2. Check permissions:
   ```bash
   sudo usermod -a -G video $USER
   # Log out and back in
   ```

3. Verify HDMI is connected and detected:
   ```bash
   fbset -i
   ```

4. If using X11/desktop, framebuffer may be in use. Try:
   ```bash
   # Switch to console (Ctrl+Alt+F1)
   # Or run without desktop environment
   ```

### ILI9341 Display Not Working

See `DISPLAY_FIX.md` for detailed troubleshooting.

### Both Displays Blank

1. Check OpenClaw connection:
   - Console should show "Connected successfully"
   - If not, check token configuration (see `TOKEN_SETUP.md`)

2. Check for errors in console output

3. Verify GPIO and SPI are initialized

---

## Customization

### Change HDMI Display Layout

Edit `config_pi4b.py`:
```python
HDMI_LAYOUT = {
    "molty_panel_width": 300,  # Width of left panel
    "padding": 20,             # Padding around elements
    "activity_item_height": 80, # Height of each activity item
}
```

### Change ILI9341 Display Layout

Edit `config_pi4b.py`:
```python
ILI9341_LAYOUT = {
    "status_bar_height": 40,   # Height of status bar
    "button_rows": 3,          # Number of button rows
    "button_cols": 2,          # Number of button columns
    "button_padding": 10,      # Padding between buttons
}
```

### Change Colors

Edit `config_pi4b.py`:
```python
CYBERPUNK_COLORS = {
    "neon_cyan": (0, 255, 255),      # Primary accent
    "hot_pink": (255, 0, 102),       # Secondary accent
    "electric_purple": (191, 0, 255), # Tertiary accent
    # ... more colors
}
```

---

## Performance

- **HDMI Display**: Updates every 500ms (2 FPS) - sufficient for text
- **ILI9341 Display**: Updates every 500ms (2 FPS) - smooth for status
- **Touch Polling**: 100ms debounce for responsive touch
- **WebSocket**: Real-time updates from OpenClaw

---

## Next Steps

1. **Test both displays**: Verify both are showing content
2. **Send a message**: Use OpenClaw TUI/web to send a message and watch it appear
3. **Test touch**: Tap buttons on ILI9341 display
4. **Customize**: Adjust colors, layout, and button functions
5. **Implement commands**: Connect touch buttons to actual OpenClaw commands

---

## Files

- `main_pi4b.py` - Main coordinator for dual displays
- `display_hdmi.py` - 7" HDMI display driver
- `display_status.py` - 2.8" ILI9341 display driver
- `touch_handler.py` - Touch input handler
- `openclaw_bridge.py` - OpenClaw WebSocket interface
- `config_pi4b.py` - Hardware and layout configuration

