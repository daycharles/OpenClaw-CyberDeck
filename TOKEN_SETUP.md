# OpenClaw CyberDeck - Authentication Token Setup

## The Problem

You're seeing this error:
```
unauthorized: gateway token missing (set gateway.remote.token to match gateway.auth.token)
```

This means your OpenClaw server requires authentication, but the CyberDeck client isn't providing the correct token.

## Solution

You need to configure the authentication token in your CyberDeck configuration.

### Step 1: Find Your OpenClaw Server Token

The token is set in your OpenClaw server configuration. Here's how to find it:

#### Option A: Check OpenClaw Server Config File

Look for the token in your OpenClaw server's configuration:

```bash
# Common locations:
cat ~/.openclaw/config.json
cat ~/.config/openclaw/config.json
```

Look for a line like:
```json
{
  "gateway": {
    "auth": {
      "token": "your-secret-token-here"
    }
  }
}
```

#### Option B: Check Environment Variables

If OpenClaw is running with environment variables:

```bash
echo $GATEWAY_AUTH_TOKEN
```

#### Option C: Check OpenClaw Server Logs

When OpenClaw starts, it may print the token in the logs. Check the terminal where you started OpenClaw.

#### Option D: Set a New Token on the Server

If you control the OpenClaw server, you can set a token:

1. Edit your OpenClaw config file
2. Add or update:
   ```json
   {
     "gateway": {
       "auth": {
         "token": "choose-a-secure-token-here"
       }
     }
   }
   ```
3. Restart OpenClaw server

### Step 2: Configure the Token on CyberDeck

Once you have the token, configure it on your Raspberry Pi:

#### Option A: Use the Setup Script (Recommended)

```bash
cd ~/OpenClaw-CyberDeck
python3 setup_token.py
```

Follow the prompts to enter your token.

#### Option B: Manual Configuration

Create or edit `.env` file in the project directory:

```bash
cd ~/OpenClaw-CyberDeck
nano .env
```

Add this line (replace with your actual token):
```
OPENCLAW_TOKEN=your-secret-token-here
```

Save and exit (Ctrl+X, then Y, then Enter).

#### Option C: Set Environment Variable

You can also set it as an environment variable:

```bash
export OPENCLAW_TOKEN=your-secret-token-here
python3 main_pi4b.py
```

Or add it to your `~/.bashrc` to make it permanent:

```bash
echo 'export OPENCLAW_TOKEN=your-secret-token-here' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Verify Configuration

Run the CyberDeck display:

```bash
cd ~/OpenClaw-CyberDeck
python3 main_pi4b.py
```

You should see:
- No more "unauthorized" errors
- Successful connection to OpenClaw
- Display showing OpenClaw data

## Configuration Priority

The token can be set in multiple places. The priority (highest to lowest) is:

1. **Command line argument** (not currently supported, but could be added)
2. **Environment variable**: `OPENCLAW_TOKEN`
3. **`.env` file** in project directory
4. **`~/.openclaw_display.env`** in home directory
5. **`~/.openclaw_display.json`** config file

## Security Notes

- **Never commit your token to git!** The `.env` file is already in `.gitignore`
- Keep your token secret - it grants full access to your OpenClaw instance
- Use a strong, random token (at least 32 characters recommended)
- If you're accessing OpenClaw over the internet, use HTTPS/WSS and Tailscale

## Troubleshooting

### Still getting "unauthorized" error?

1. **Verify the token is correct**: Double-check you copied it exactly
2. **Check for spaces**: Make sure there are no extra spaces in the token
3. **Restart the display**: After changing the token, restart the CyberDeck
4. **Check server logs**: Look at OpenClaw server logs for more details

### Token not being loaded?

Check if the configuration is being loaded:

```bash
cd ~/OpenClaw-CyberDeck
python3 -c "from openclaw_config import OpenClawConfig; print(OpenClawConfig.load())"
```

You should see:
```
OpenClawConfig(
  url=ws://localhost:18789
  token=***
  ...
)
```

If `token=None`, the token isn't being loaded. Check your `.env` file.

## Example .env File

Here's a complete example `.env` file:

```bash
# OpenClaw Display Configuration

# WebSocket URL (change if OpenClaw is on another machine)
OPENCLAW_URL=ws://localhost:18789

# Gateway authentication token (REQUIRED)
OPENCLAW_TOKEN=your-secret-token-here

# Optional: Connection behavior
OPENCLAW_AUTO_RECONNECT=true
OPENCLAW_RECONNECT_DELAY=1.0
OPENCLAW_TIMEOUT=30.0
```

## Need Help?

If you're still having issues:

1. Check the OpenClaw server is running: `curl http://localhost:18789/health` (if available)
2. Verify network connectivity between Pi and OpenClaw server
3. Check firewall settings aren't blocking port 18789
4. Review both CyberDeck and OpenClaw server logs for errors

