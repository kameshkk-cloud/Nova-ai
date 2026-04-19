# 🐧 NOVA AI — Linux Setup Guide

## Complete step-by-step commands to clone and run NOVA on Linux.

---

## Step 1: Install System Dependencies

Open your terminal and run **one** of these based on your distro:

### Ubuntu / Debian
```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv python3-dev \
    espeak espeak-data portaudio19-dev \
    libxcb-xinerama0 libxcb-cursor0 libxkbcommon0 \
    pulseaudio-utils xdg-utils
```

### Fedora / RHEL
```bash
sudo dnf install -y git python3 python3-pip python3-devel \
    espeak portaudio-devel \
    libxcb xcb-util-cursor libxkbcommon \
    pulseaudio-utils xdg-utils
```

### Arch Linux
```bash
sudo pacman -S git python python-pip espeak-ng portaudio \
    xcb-util-cursor libxkbcommon \
    libpulse xdg-utils
```

### Verify Python is installed
```bash
python3 --version
# Should show: Python 3.10.x or higher
```

---

## Step 2: Clone from GitHub

```bash
# Clone the repo to your home directory
git clone https://github.com/kameshkk-cloud/Nova-ai.git ~/Nova-ai

# Go into the project folder
cd ~/Nova-ai
```

---

## Step 3: Create Virtual Environment & Install Packages

```bash
# Create virtual environment (only needed once)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all Python packages
pip install -r requirements.txt
```

### If PyAudio fails to install:
```bash
# Make sure portaudio is installed
sudo apt install portaudio19-dev    # Ubuntu/Debian
sudo dnf install portaudio-devel    # Fedora
sudo pacman -S portaudio            # Arch

# Then retry
pip install pyaudio
```

> **Can't install PyAudio?** NOVA still works — it falls back to keyboard input mode automatically.

---

## Step 4: Configure Your API Key

```bash
# Copy the example config
cp .env.example .env

# Edit it with nano
nano .env
```

Inside nano, set these values:
```
NOVA_LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key_here
NOVA_USER_NAME=KK Sir
NOVA_WAKE_WORD=hey nova
NOVA_VOICE_GENDER=male
```

**Get a FREE Groq API key:** https://console.groq.com

Save and exit nano: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## Step 5: Run NOVA

### GUI Mode (Recommended)
```bash
python nova_gui.py
```

### CLI Mode (Terminal only, no GUI)
```bash
python main.py
```

---

## 📌 Every Time You Open a New Terminal

You only need these 3 commands:

```bash
cd ~/Nova-ai
source venv/bin/activate
python nova_gui.py
```

> **Tip:** The system dependencies (Step 1) and pip packages (Step 3) only need to be installed **once**. After that, it's just the 3 commands above.

---

## 🔊 Test Voice (Optional)

```bash
# Test espeak directly
espeak "Hello, I am NOVA"

# Test NOVA's voice engine
cd ~/Nova-ai
source venv/bin/activate
python -c "
from nova.voice.tts import VoiceEngine
v = VoiceEngine()
v.speak('Hello sir. All systems online. NOVA is at your service.', block=True)
v.shutdown()
"
```

---

## ⚠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `espeak: command not found` | `sudo apt install espeak espeak-data` |
| `PyAudio failed to install` | `sudo apt install portaudio19-dev` then `pip install pyaudio` |
| GUI crashes with Qt plugin error | `sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon0` |
| Wayland display issues | Run `export QT_QPA_PLATFORM=xcb` before launching |
| No sound output | Check PulseAudio: `pactl info` |
| Volume commands don't work | `sudo apt install pulseaudio-utils` |
| Lock screen doesn't work | `sudo apt install xdg-utils` |
| `python3: command not found` | `sudo apt install python3` |
| `git: command not found` | `sudo apt install git` |
| Permission denied on shutdown | Use `sudo` or configure polkit rules |

### Quick Fix — Install Everything at Once (Ubuntu/Debian)
```bash
sudo apt install -y git python3 python3-pip python3-venv python3-dev \
    espeak espeak-data portaudio19-dev \
    libxcb-xinerama0 libxcb-cursor0 libxkbcommon0 \
    pulseaudio-utils xdg-utils
```

---

## 🔄 Updating NOVA (Pull Latest Changes)

```bash
cd ~/Nova-ai
source venv/bin/activate
git pull origin main
pip install -r requirements.txt   # in case new packages were added
python nova_gui.py
```

---

## 📁 Optional: Create a Desktop Shortcut

```bash
cat > ~/.local/share/applications/nova-ai.desktop << 'EOF'
[Desktop Entry]
Name=NOVA AI
Comment=JARVIS-style AI Assistant
Exec=bash -c "cd ~/Nova-ai && source venv/bin/activate && python nova_gui.py"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;
EOF

# Make it executable
chmod +x ~/.local/share/applications/nova-ai.desktop
```

Now NOVA will appear in your application menu!

---

## 📁 Optional: Create a Quick Launch Alias

Add this to your `~/.bashrc` or `~/.zshrc`:

```bash
echo 'alias nova="cd ~/Nova-ai && source venv/bin/activate && python nova_gui.py"' >> ~/.bashrc
source ~/.bashrc
```

Now you can just type `nova` in any terminal to launch!
