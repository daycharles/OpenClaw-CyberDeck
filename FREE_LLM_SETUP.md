# Free Local LLM Setup with Ollama

No API keys needed! Run everything locally and for free.

---

## 🆓 Option 1: Ollama on Raspberry Pi 4B (All-in-One)

### Step 1: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama
```

### Step 2: Pull a Model

Choose based on your Pi's RAM:

```bash
# For 2GB Pi - Smallest model (fast but basic)
ollama pull phi3:mini

# For 4GB Pi - Better quality (recommended)
ollama pull llama3.2:3b

# For 8GB Pi - Best quality
ollama pull llama3.2:8b
```

### Step 3: Test Ollama

```bash
# Test the model
ollama run phi3:mini
# Type a message and press Enter
# Press Ctrl+D to exit
```

### Step 4: Configure OpenClaw to Use Ollama

When you set up OpenClaw, configure it to use Ollama's OpenAI-compatible API:

```bash
cd ~/openclaw
nano .env
```

Add this configuration:

```env
# Use Ollama instead of OpenAI/Anthropic
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=phi3:mini

# Or if using llama3.2:
# OPENAI_MODEL=llama3.2:3b

PORT=18789
HOST=0.0.0.0
```

### Step 5: Start OpenClaw

```bash
cd ~/openclaw
npm start
```

### Step 6: Connect Dashboard

```bash
cd ~/OpenClaw-CyberDeck
python3 main_pi4b.py --url ws://localhost:18789
```

---

## 🚀 Option 2: Ollama on Windows PC (Better Performance)

Your Windows PC will have better performance for running LLMs.

### Step 1: Install Ollama on Windows

1. Download from: **https://ollama.com/download**
2. Install the Windows version
3. Ollama will run automatically

### Step 2: Pull a Model

Open PowerShell:

```powershell
# Pull a good model (8B is great for desktop)
ollama pull llama3.2:8b

# Or try the latest Llama 3.3:
ollama pull llama3.3:8b

# Test it
ollama run llama3.2:8b
```

### Step 3: Install OpenClaw on Windows

```powershell
# Install Node.js from https://nodejs.org/

# Clone OpenClaw
cd C:\
git clone https://github.com/openclawai/openclaw.git
cd openclaw

# Install dependencies
npm install
```

### Step 4: Configure OpenClaw for Ollama

Create `.env` file in `C:\openclaw\`:

```env
# Point OpenClaw to Ollama
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3.2:8b

PORT=18789
HOST=0.0.0.0
```

### Step 5: Start OpenClaw

```powershell
cd C:\openclaw
npm start
```

### Step 6: Find Your PC's IP

```powershell
ipconfig
```

Look for IPv4 Address (e.g., `192.168.1.100`)

### Step 7: Connect from Pi

```bash
# Replace with your PC's IP
python3 main_pi4b.py --url ws://192.168.1.100:18789
```

---

## 📊 Model Recommendations

| Model | Size | RAM Needed | Quality | Speed |
|-------|------|------------|---------|-------|
| `phi3:mini` | 2.3GB | 2GB+ | Basic | Fast |
| `llama3.2:3b` | 2GB | 4GB+ | Good | Fast |
| `llama3.2:8b` | 4.7GB | 8GB+ | Great | Medium |
| `llama3.3:8b` | 4.7GB | 8GB+ | Excellent | Medium |
| `qwen2.5:7b` | 4.7GB | 8GB+ | Excellent | Medium |

### For Raspberry Pi 4B:
- **2GB RAM**: Use `phi3:mini`
- **4GB RAM**: Use `llama3.2:3b`
- **8GB RAM**: Use `llama3.2:8b` or `llama3.3:8b`

### For Windows PC:
- **8GB+ RAM**: Use `llama3.3:8b` or `qwen2.5:7b`
- **16GB+ RAM**: Use `llama3.3:70b` (best quality)

---

## 🧪 Testing Ollama

### Test Ollama API

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test chat completion (OpenAI-compatible)
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3:mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## 🔧 Troubleshooting

### Ollama not starting

```bash
# Check status
sudo systemctl status ollama

# Restart
sudo systemctl restart ollama

# Check logs
journalctl -u ollama -f
```

### Model too slow on Pi

Try a smaller model:
```bash
ollama pull phi3:mini
```

Or run Ollama on your PC instead.

### OpenClaw can't connect to Ollama

Make sure:
1. Ollama is running: `curl http://localhost:11434/api/tags`
2. Model is pulled: `ollama list`
3. `.env` has correct `OPENAI_API_BASE`

---

## 💡 Why This is Better

✅ **100% Free** - No API costs ever  
✅ **Private** - Your data never leaves your device  
✅ **Offline** - Works without internet  
✅ **Fast** - No network latency  
✅ **No Rate Limits** - Use as much as you want  

---

## 🎯 Quick Start Summary

**Easiest (All on Pi):**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini

# Configure OpenClaw
cd ~/openclaw
echo "OPENAI_API_BASE=http://localhost:11434/v1" > .env
echo "OPENAI_API_KEY=ollama" >> .env
echo "OPENAI_MODEL=phi3:mini" >> .env
npm start

# Run dashboard
cd ~/OpenClaw-CyberDeck
python3 main_pi4b.py --url ws://localhost:18789
```

**Best Performance (Ollama on PC, Dashboard on Pi):**
1. Install Ollama on Windows
2. Pull `llama3.2:8b`
3. Install OpenClaw on Windows with Ollama config
4. Connect Pi to PC's IP

---

## 📚 Resources

- **Ollama**: https://ollama.com/
- **Model Library**: https://ollama.com/library
- **Ollama GitHub**: https://github.com/ollama/ollama

**No API keys. No costs. Just free AI!** 🎉

