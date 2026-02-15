#!/usr/bin/env python3
"""
Check SPI configuration on Raspberry Pi.
"""

import os
import sys

print("SPI Configuration Check")
print("=" * 50)

# Check if SPI device files exist
spi_devices = [
    "/dev/spidev0.0",
    "/dev/spidev0.1",
]

print("\n1. Checking SPI device files:")
for device in spi_devices:
    if os.path.exists(device):
        print(f"   ✓ {device} exists")
        # Check permissions
        if os.access(device, os.R_OK | os.W_OK):
            print(f"     ✓ Read/write access OK")
        else:
            print(f"     ✗ No read/write access (try: sudo usermod -a -G spi $USER)")
    else:
        print(f"   ✗ {device} NOT FOUND")

# Check if SPI is enabled in boot config
print("\n2. Checking /boot/config.txt:")
config_paths = ["/boot/config.txt", "/boot/firmware/config.txt"]
found_config = False
for config_path in config_paths:
    if os.path.exists(config_path):
        found_config = True
        print(f"   Found config at: {config_path}")
        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()
                spi_enabled = False
                for line in lines:
                    if 'dtparam=spi=on' in line and not line.strip().startswith('#'):
                        spi_enabled = True
                        print(f"   ✓ SPI is enabled: {line.strip()}")
                        break
                if not spi_enabled:
                    print(f"   ✗ SPI not enabled in config")
                    print(f"     Add 'dtparam=spi=on' to {config_path}")
        except PermissionError:
            print(f"   ⚠ Cannot read {config_path} (need sudo)")
        break

if not found_config:
    print("   ✗ Could not find boot config file")

# Check if spidev module is loaded
print("\n3. Checking kernel modules:")
try:
    with open('/proc/modules', 'r') as f:
        modules = f.read()
        if 'spidev' in modules:
            print("   ✓ spidev module is loaded")
        else:
            print("   ✗ spidev module NOT loaded")
            print("     Try: sudo modprobe spidev")
        
        if 'spi_bcm2835' in modules:
            print("   ✓ spi_bcm2835 module is loaded")
        else:
            print("   ⚠ spi_bcm2835 module NOT loaded")
except Exception as e:
    print(f"   ✗ Error checking modules: {e}")

# Check user groups
print("\n4. Checking user groups:")
try:
    import grp
    import pwd
    username = pwd.getpwuid(os.getuid()).pw_name
    user_groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
    gid = pwd.getpwuid(os.getuid()).pw_gid
    user_groups.append(grp.getgrgid(gid).gr_name)
    
    print(f"   User: {username}")
    print(f"   Groups: {', '.join(user_groups)}")
    
    if 'spi' in user_groups or 'gpio' in user_groups:
        print("   ✓ User is in SPI/GPIO group")
    else:
        print("   ⚠ User not in 'spi' or 'gpio' group")
        print("     Try: sudo usermod -a -G spi,gpio $USER")
        print("     Then log out and back in")
except Exception as e:
    print(f"   ✗ Error checking groups: {e}")

print("\n" + "=" * 50)
print("\nSUMMARY:")
if all(os.path.exists(d) for d in spi_devices):
    print("✓ SPI appears to be configured correctly")
    print("  You can try running the test script again")
else:
    print("✗ SPI is NOT properly configured")
    print("\nTo enable SPI:")
    print("1. Run: sudo raspi-config")
    print("2. Select: Interface Options → SPI → Enable")
    print("3. Reboot: sudo reboot")
    print("\nOR manually:")
    print("1. Edit: sudo nano /boot/config.txt (or /boot/firmware/config.txt)")
    print("2. Add: dtparam=spi=on")
    print("3. Reboot: sudo reboot")

