#!/bin/bash
# Verification script to check if main_pi4b.py has been updated

echo "=== Checking main_pi4b.py on your system ==="
echo ""

FILE="$HOME/OpenClaw-CyberDeck/main_pi4b.py"

if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found at $FILE"
    exit 1
fi

echo "File exists at: $FILE"
echo ""

echo "Checking for GPIO initialization code (should be on line 31-37):"
echo "---"
sed -n '31,37p' "$FILE"
echo "---"
echo ""

# Check if the GPIO.setmode line exists
if grep -q "GPIO.setmode(GPIO.BCM)" "$FILE"; then
    echo "✅ GPIO initialization code FOUND - file is updated!"
else
    echo "❌ GPIO initialization code NOT FOUND - file needs updating!"
    echo ""
    echo "To fix this, run:"
    echo "  cd ~/OpenClaw-CyberDeck"
    echo "  git pull"
    echo ""
    echo "Or manually download the file:"
    echo "  cd ~/OpenClaw-CyberDeck"
    echo "  mv main_pi4b.py main_pi4b.py.old"
    echo "  wget https://raw.githubusercontent.com/daycharles/OpenClaw-CyberDeck/main/main_pi4b.py"
fi

echo ""
echo "=== File modification time ==="
ls -lh "$FILE"

