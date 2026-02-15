#!/usr/bin/env python3
"""
Helper script to set up OpenClaw authentication token.
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("OpenClaw CyberDeck - Token Setup")
    print("=" * 60)
    print()
    print("The OpenClaw server requires a gateway authentication token.")
    print("You need to find this token from your OpenClaw server configuration.")
    print()
    print("How to find your token:")
    print("-" * 60)
    print("1. On your OpenClaw server, check the configuration file:")
    print("   - Look for 'gateway.auth.token' in your config")
    print("   - Or check environment variable GATEWAY_AUTH_TOKEN")
    print()
    print("2. If you're running OpenClaw locally, check:")
    print("   - ~/.openclaw/config.json")
    print("   - Or the terminal output when OpenClaw starts")
    print()
    print("3. The token is usually a random string like:")
    print("   'abc123def456' or similar")
    print()
    print("-" * 60)
    print()
    
    # Check if .env file exists
    env_path = Path.cwd() / ".env"
    env_exists = env_path.exists()
    
    if env_exists:
        print(f"Found existing .env file at: {env_path}")
        print()
        # Read current content
        with open(env_path, "r") as f:
            content = f.read()
        
        # Check if token is already set
        if "OPENCLAW_TOKEN=" in content:
            lines = content.split("\n")
            for line in lines:
                if line.startswith("OPENCLAW_TOKEN=") and not line.startswith("#"):
                    token_value = line.split("=", 1)[1].strip()
                    if token_value:
                        print(f"✓ Token is already configured: {token_value[:8]}...")
                        print()
                        response = input("Do you want to update it? (y/N): ").strip().lower()
                        if response != 'y':
                            print("Keeping existing token.")
                            return
                    break
    else:
        print(f"No .env file found. Will create one at: {env_path}")
        print()
    
    # Prompt for token
    print("Enter your OpenClaw gateway token:")
    print("(Press Ctrl+C to cancel)")
    try:
        token = input("> ").strip()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    if not token:
        print("Error: Token cannot be empty.")
        return
    
    # Update or create .env file
    if env_exists:
        # Update existing file
        with open(env_path, "r") as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("OPENCLAW_TOKEN="):
                lines[i] = f"OPENCLAW_TOKEN={token}\n"
                updated = True
                break
        
        if not updated:
            # Add token line
            lines.append(f"\nOPENCLAW_TOKEN={token}\n")
        
        with open(env_path, "w") as f:
            f.writelines(lines)
        
        print(f"\n✓ Updated token in {env_path}")
    else:
        # Create new .env file
        content = f"""# OpenClaw Display Configuration

# Required: WebSocket URL to your OpenClaw instance
OPENCLAW_URL=ws://localhost:18789

# Required: Gateway authentication token
OPENCLAW_TOKEN={token}

# Optional: Connection behavior
OPENCLAW_AUTO_RECONNECT=true
OPENCLAW_RECONNECT_DELAY=1.0
OPENCLAW_TIMEOUT=30.0
"""
        with open(env_path, "w") as f:
            f.write(content)
        
        print(f"\n✓ Created {env_path} with token")
    
    print()
    print("=" * 60)
    print("Setup complete!")
    print()
    print("You can now run the CyberDeck display:")
    print("  python3 main_pi4b.py")
    print()
    print("To change the token later, edit .env or run this script again.")
    print("=" * 60)

if __name__ == "__main__":
    main()

