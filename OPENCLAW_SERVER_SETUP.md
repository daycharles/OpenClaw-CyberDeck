# OpenClaw Server Setup Guide

This guide will help you set up an OpenClaw server to connect with your Pi 4B dashboard.

---

## Option 1: Run OpenClaw Server on Raspberry Pi 4B (Easiest)

### Step 1: Install Node.js

```bash
# Install Node.js 18.x (LTS)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should show v18.x.x
npm --version   # Should show 9.x.x or higher
```

### Step 2: Clone OpenClaw Repository

```bash
cd ~
git clone https://github.com/openclawai/openclaw.git
cd openclaw
```

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Configure OpenClaw

OpenClaw will guide you through configuration on first run. You'll need:
- **API Keys** (OpenAI, Anthropic, etc.)
- **Port** (default: 18789)
- **Authentication** (optional password)

Create a `.env` file:

```bash
nano .env
```

Add your configuration:

```env
# OpenClaw Server Configuration
PORT=18789
HOST=0.0.0.0

# AI Provider API Keys (add at least one)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional: Authentication
# OPENCLAW_PASSWORD=your_secure_password

# Optional: Enable CORS for local development
CORS_ENABLED=true
```

### Step 5: Start the Server

```bash
npm start
```

You should see:
```
OpenClaw server listening on ws://0.0.0.0:18789
```

### Step 6: Test Connection from Dashboard

Open a **new terminal** and run:

```bash
cd ~/OpenClaw-CyberDeck
python3 main_pi4b.py --url ws://localhost:18789
```

You should see the dashboard connect successfully!

---

## Option 2: Run OpenClaw Server on Your Windows PC

### Step 1: Install Node.js

1. Download from: https://nodejs.org/
2. Install the LTS version (18.x)
3. Verify in PowerShell:
   ```powershell
   node --version
   npm --version
   ```

### Step 2: Clone and Setup

```powershell
# Clone repository
cd C:\
git clone https://github.com/openclawai/openclaw.git
cd openclaw

# Install dependencies
npm install
```

### Step 3: Configure

Create `.env` file in the `openclaw` directory:

```env
PORT=18789
HOST=0.0.0.0
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 4: Start Server

```powershell
npm start
```

### Step 5: Find Your PC's IP Address

```powershell
ipconfig
```

Look for your local IP (e.g., `192.168.1.100`)

### Step 6: Connect from Pi

On your Raspberry Pi:

```bash
# Replace with your PC's IP address
python3 main_pi4b.py --url ws://192.168.1.100:18789
```

---

## Option 3: Deploy to Cloud (Production)

### Using Hostinger VPS

1. **Get a VPS** from Hostinger or another provider
2. **SSH into your server**
3. **Install Node.js**:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```
4. **Clone and setup OpenClaw** (same as Option 1)
5. **Use PM2 for process management**:
   ```bash
   sudo npm install -g pm2
   pm2 start npm --name "openclaw" -- start
   pm2 save
   pm2 startup
   ```
6. **Setup SSL/TLS** (for wss:// connections):
   ```bash
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```
7. **Connect from Pi**:
   ```bash
   python3 main_pi4b.py --url wss://your-domain.com:18789
   ```

---

## Troubleshooting

### Server won't start

**Check Node.js version:**
```bash
node --version  # Should be 18.x or higher
```

**Check port availability:**
```bash
sudo netstat -tulpn | grep 18789
```

### Dashboard can't connect

**1. Check server is running:**
```bash
curl http://localhost:18789
```

**2. Check firewall (if on different machines):**
```bash
# On server
sudo ufw allow 18789
```

**3. Verify IP address:**
```bash
# On server
hostname -I
```

### Connection works but no AI responses

**Check API keys:**
- Make sure you have valid API keys in `.env`
- Test with OpenAI or Anthropic CLI tools

---

## Next Steps

Once your server is running:

1. ✅ **Test connection**: `python3 main_pi4b.py --url ws://localhost:18789`
2. ⚙️ **Configure auto-start**: Use systemd or PM2
3. 🔐 **Add authentication**: Set `OPENCLAW_PASSWORD` in `.env`
4. 🌐 **Set up remote access**: Use Tailscale or VPN

---

## Quick Reference

### Start Server (Pi)
```bash
cd ~/openclaw
npm start
```

### Start Dashboard (Pi)
```bash
cd ~/OpenClaw-CyberDeck
python3 main_pi4b.py --url ws://localhost:18789
```

### Check Server Status
```bash
curl http://localhost:18789/health
```

---

## Resources

- **OpenClaw GitHub**: https://github.com/openclawai/openclaw
- **OpenClaw Docs**: Check the repository README
- **Get API Keys**:
  - OpenAI: https://platform.openai.com/api-keys
  - Anthropic: https://console.anthropic.com/

---

**Ready to connect!** 🚀

