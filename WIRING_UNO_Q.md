# Arduino UNO Q Wiring Reference

Quick reference for connecting three displays to Arduino UNO Q.

## Pin Overview

Arduino UNO Q uses the same 40-pin GPIO header as Raspberry Pi 4.

### SPI Bus 0 (Shared)
- **MOSI**: GPIO 10 (Pin 19)
- **MISO**: GPIO 9 (Pin 21)
- **SCLK**: GPIO 11 (Pin 23)
- **CE0**: GPIO 8 (Pin 24) - Waveshare ST7789
- **CE1**: GPIO 7 (Pin 26) - HiLetgo ILI9341

### Power
- **3.3V**: Pins 1, 17
- **5V**: Pins 2, 4 (for HDMI display power)
- **GND**: Pins 6, 9, 14, 20, 25, 30, 34, 39

---

## Display 1: Waveshare 1.3" ST7789 (240x240)

**Status/Notification Panel**

| Display Pin | Arduino UNO Q GPIO | Physical Pin | Notes |
|-------------|-------------------|--------------|-------|
| VCC | 3.3V | Pin 1 | **NOT 5V!** |
| GND | GND | Pin 6 | Any GND pin |
| DIN (MOSI) | GPIO 10 | Pin 19 | Shared SPI |
| CLK (SCLK) | GPIO 11 | Pin 23 | Shared SPI |
| CS | GPIO 8 (CE0) | Pin 24 | Chip select |
| DC | GPIO 24 | Pin 18 | Data/Command |
| RST | GPIO 25 | Pin 22 | Reset |
| BL | GPIO 18 | Pin 12 | Backlight (or 3.3V) |

**Config**: `config_uno_q.py` → `ST7789_DISPLAY`

---

## Display 2: HiLetgo 2.4" ILI9341 (240x320)

**Touch Command Panel**

| Display Pin | Arduino UNO Q GPIO | Physical Pin | Notes |
|-------------|-------------------|--------------|-------|
| VCC | 3.3V | Pin 1 | **NOT 5V!** |
| GND | GND | Pin 6 | Any GND pin |
| CS | GPIO 7 (CE1) | Pin 26 | Chip select |
| RESET | GPIO 27 | Pin 13 | Reset |
| DC/RS | GPIO 22 | Pin 15 | Data/Command |
| SDI (MOSI) | GPIO 10 | Pin 19 | Shared SPI |
| SCK (SCLK) | GPIO 11 | Pin 23 | Shared SPI |
| LED | GPIO 23 | Pin 16 | Backlight |
| SDO (MISO) | GPIO 9 | Pin 21 | Shared SPI |

### Touch Controller (XPT2046)

| Touch Pin | Arduino UNO Q GPIO | Physical Pin | Notes |
|-----------|-------------------|--------------|-------|
| T_CLK | GPIO 11 | Pin 23 | Shared with display |
| T_CS | GPIO 17 | Pin 11 | Touch chip select |
| T_DIN | GPIO 10 | Pin 19 | Shared with display |
| T_DO | GPIO 9 | Pin 21 | Shared with display |
| T_IRQ | Not connected | - | Polling mode |

**Config**: `config_uno_q.py` → `ILI9341_DISPLAY` and `TOUCH`

---

## Display 3: ElecLab 7" HDMI (1024x600)

**Main Conversation/Activity Display**

| Display Connection | Arduino UNO Q Port | Notes |
|-------------------|-------------------|-------|
| HDMI | Micro HDMI port | Use micro HDMI to HDMI cable |
| USB (touch) | USB port | If touch-enabled variant |
| 5V Power | External PSU | 5V 2A power supply |

**No GPIO wiring needed** - uses HDMI and framebuffer.

**Config**: `config_uno_q.py` → `HDMI_DISPLAY`

---

## Complete Wiring Diagram

```
Arduino UNO Q (40-pin GPIO)
┌─────────────────────────────────┐
│ 1  3.3V ●────────────────┐      │
│ 2  5V   ●                │      │
│ 3       ●                │      │
│ 4  5V   ●                │      │
│ 5       ●                │      │
│ 6  GND  ●────────────────┼────┐ │
│ 7       ●                │    │ │
│ 8       ●                │    │ │
│ 9  GND  ●                │    │ │
│ 10      ●                │    │ │
│ 11 GPIO17●─── T_CS       │    │ │
│ 12 GPIO18●─── ST7789 BL  │    │ │
│ 13 GPIO27●─── ILI9341 RST│    │ │
│ 14 GND  ●                │    │ │
│ 15 GPIO22●─── ILI9341 DC │    │ │
│ 16 GPIO23●─── ILI9341 BL │    │ │
│ 17 3.3V ●                │    │ │
│ 18 GPIO24●─── ST7789 DC  │    │ │
│ 19 GPIO10●─── MOSI ──────┼────┼─┼─ All displays
│ 20 GND  ●                │    │ │
│ 21 GPIO9 ●─── MISO ──────┼────┼─┼─ All displays
│ 22 GPIO25●─── ST7789 RST │    │ │
│ 23 GPIO11●─── SCLK ──────┼────┼─┼─ All displays
│ 24 GPIO8 ●─── ST7789 CS  │    │ │
│ 25 GND  ●                │    │ │
│ 26 GPIO7 ●─── ILI9341 CS │    │ │
│ ...                      │    │ │
└──────────────────────────┼────┼─┘
                           │    │
    ┌──────────────────────┘    │
    │  ┌────────────────────────┘
    │  │
    ▼  ▼
  VCC GND  ← Connect to all displays
```

---

## Checklist

Before powering on:

- [ ] All displays connected to **3.3V** (NOT 5V!)
- [ ] All GND pins connected
- [ ] SPI pins (MOSI, MISO, SCLK) shared correctly
- [ ] Each display has unique CS pin
- [ ] DC and RST pins connected correctly
- [ ] Touch CS pin (GPIO 17) connected
- [ ] HDMI cable connected
- [ ] No loose wires or shorts

---

## Testing

Test each display individually:

```bash
# Test ST7789
python3 test_st7789.py

# Test ILI9341
python3 test_ili9341.py

# Test HDMI
python3 test_hdmi.py
```

If a display doesn't work:
1. Check wiring (especially DC pin)
2. Verify 3.3V power
3. Check SPI is enabled: `ls /dev/spidev*`
4. Try lower SPI speed in config

---

## Color Code Suggestion

Use colored jumper wires for easier debugging:

- **Red**: 3.3V power
- **Black**: GND
- **Yellow**: MOSI (data out)
- **Blue**: MISO (data in)
- **Green**: SCLK (clock)
- **Orange**: CS (chip select)
- **Purple**: DC (data/command)
- **White**: RST (reset)
- **Brown**: Backlight

---

## Safety Notes

⚠️ **IMPORTANT**:
- Use **3.3V** for SPI displays, NOT 5V!
- 5V will damage the displays permanently
- Double-check polarity before powering on
- Disconnect power before changing wiring
- Use a multimeter to verify connections

---

## Support

See `SETUP_ARDUINO_UNO_Q.md` for detailed setup instructions.

