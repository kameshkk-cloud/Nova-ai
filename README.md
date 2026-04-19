<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Linux-Ubuntu%2FDebian%2FFedora%2FArch-FCC624?style=for-the-badge&logo=linux&logoColor=black" />
  <img src="https://img.shields.io/badge/Windows-Also%20Supported-0078D6?style=for-the-badge&logo=windows&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white" />
  <img src="https://img.shields.io/badge/Voice-JARVIS%20Style-ff6f00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Version-2.0-cyan?style=for-the-badge" />
</p>

<h1 align="center">🤖 NOVA AI — Neural Operative Virtual Assistant</h1>

<p align="center">
  <strong>A JARVIS-inspired AI desktop assistant with a futuristic PyQt6 GUI,<br>
  voice interaction, system monitoring, and multi-LLM support.<br>
  Built for Linux. Also works on Windows.</strong>
</p>

---

## 📋 Table of Contents

- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Quick Start (5 Minutes)](#-quick-start-5-minutes)
- [Detailed Setup Guide](#-detailed-setup-guide)
  - [Step 1: Install System Dependencies](#step-1-install-system-dependencies)
  - [Step 2: Get the Project](#step-2-get-the-project)
  - [Step 3: Create Virtual Environment](#step-3-create-virtual-environment)
  - [Step 4: Install Python Dependencies](#step-4-install-python-dependencies)
  - [Step 5: Configure Environment](#step-5-configure-environment)
  - [Step 6: Run NOVA](#step-6-run-nova)
- [Setting Up on Another Computer](#-setting-up-on-another-computer)
- [LLM Provider Setup](#-llm-provider-setup)
- [Voice Configuration](#-voice-configuration)
- [GUI Overview](#-gui-overview)
- [Available Commands](#-available-commands)
- [Project Architecture](#-project-architecture)
- [Troubleshooting](#-troubleshooting)
- [Windows Setup](#-windows-setup)
- [FAQ](#-faq)

---

## ✨ Features

| Category | Details |
|----------|---------|
| 🎙️ **JARVIS Voice** | Smooth, authoritative male voice — espeak (Linux) / SAPI5 (Windows) |
| 🖥️ **Futuristic GUI** | Iron Man-style interface with animated AI orb, real-time system gauges, chat panel |
| 🧠 **Multi-LLM Brain** | Supports Groq (free), OpenAI, and Ollama (offline) for smart conversations |
| 📊 **System Monitoring** | Live CPU, RAM, Disk, Battery, Network stats with automatic alerts |
| 🎤 **Voice Control** | Wake word ("Hey NOVA"), speech recognition, hands-free operation |
| ⚡ **Quick Actions** | One-click buttons for Chrome, Terminal, Screenshot, Volume, Lock, Shutdown |
| 🧩 **Plugin System** | Extensible command architecture — add new skills easily |
| 💾 **Memory System** | Short-term conversation context + long-term persistent memory |
| 📁 **File Operations** | Organize files, search, manage downloads |
| ⏱️ **Productivity** | Command tracking, session logging, usage analytics |
| 🐧 **Cross-Platform** | Full support for Linux (Ubuntu, Debian, Fedora, Arch) and Windows |

---

## 💻 System Requirements

| Requirement | Details |
|-------------|---------|
| **Operating System** | Linux (Ubuntu 20.04+, Debian 11+, Fedora 36+, Arch) or Windows 10/11 |
| **Python** | 3.10 or higher (3.11 or 3.12 recommended) |
| **RAM** | 4 GB minimum, 8 GB recommended |
| **Disk Space** | ~500 MB (including Python packages) |
| **TTS Engine** | `espeak` (installed in Step 1) |
| **Microphone** | Optional — NOVA falls back to keyboard input if no mic is available |
| **Internet** | Required for Groq/OpenAI LLMs; optional with Ollama (offline) |
| **Display** | X11 or Wayland |

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    espeak espeak-data portaudio19-dev python3-pyaudio \
    libxcb-xinerama0 libxcb-cursor0 libxkbcommon0

# 2. Navigate to the project folder
cd ~/NOVA-AI

# 3. Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Copy the example env file and configure
cp .env.example .env
nano .env
# → Set your GROQ_API_KEY (get free key at https://console.groq.com)

# 6. Launch NOVA
python nova_gui.py
```

> **That's it!** NOVA will boot up with the JARVIS voice and futuristic interface.

---

## 📖 Detailed Setup Guide

### Step 1: Install System Dependencies

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    espeak espeak-data portaudio19-dev python3-pyaudio \
    libxcb-xinerama0 libxcb-cursor0 libxkbcommon0 \
    pulseaudio-utils xdg-utils
```

**Fedora / RHEL:**
```bash
sudo dnf install -y python3 python3-pip python3-devel \
    espeak portaudio-devel \
    libxcb xcb-util-cursor libxkbcommon \
    pulseaudio-utils xdg-utils
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip espeak-ng portaudio \
    xcb-util-cursor libxkbcommon \
    libpulse xdg-utils
```

**Verify Python:**
```bash
python3 --version
# Should show: Python 3.10.x or higher
```

---

### Step 2: Get the Project

**Option A: Clone from Git (if available)**
```bash
git clone <your-repo-url> ~/NOVA-AI
cd ~/NOVA-AI
```

**Option B: Copy the folder**
- Copy the entire `NOVA AI` folder to your preferred location (e.g., `~/NOVA-AI`)
```bash
cd ~/NOVA-AI
```

---

### Step 3: Create Virtual Environment

A virtual environment keeps NOVA's packages separate from your system Python.

```bash
# Create the virtual environment (only needed once)
python3 -m venv venv

# Activate it (needed every time you open a new terminal)
source venv/bin/activate
```

> You'll see `(venv)` at the beginning of your prompt when activated.

---

### Step 4: Install Python Dependencies

With the virtual environment activated:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

#### 🔧 PyAudio Troubleshooting

If PyAudio fails to install:

```bash
# Make sure portaudio dev package is installed
sudo apt install portaudio19-dev   # Ubuntu/Debian
sudo dnf install portaudio-devel   # Fedora
sudo pacman -S portaudio           # Arch

# Then retry
pip install pyaudio
```

**Can't install PyAudio at all?** NOVA still works! It automatically falls back to keyboard input mode — you just won't be able to use voice commands.

#### Verify Installation

```bash
python -c "import PyQt6; import pyttsx3; import psutil; print('All core dependencies OK!')"
```

---

### Step 5: Configure Environment

1. **Copy the example config:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the config file:**
   ```bash
   nano .env
   ```

3. **Fill in your settings:**
   ```env
   # ── LLM Provider (choose one: groq | openai | ollama) ────
   NOVA_LLM_PROVIDER=groq

   # ── Groq API Key (FREE) ──────────────────────────────────
   # Get yours at: https://console.groq.com
   GROQ_API_KEY=gsk_your_key_here

   # ── Personalisation ──────────────────────────────────────
   NOVA_USER_NAME=Your Name
   NOVA_WAKE_WORD=hey nova
   NOVA_VOICE_GENDER=male
   ```

4. Save and exit: `Ctrl+O` → Enter → `Ctrl+X`

> 💡 **Minimum required:** Just set `GROQ_API_KEY` for smart AI responses. Everything else has sensible defaults.

---

### Step 6: Run NOVA

**GUI Mode (Recommended):**
```bash
python nova_gui.py
```

**CLI Mode (Terminal only, no GUI):**
```bash
python main.py
```

> On first launch, NOVA will:
> 1. Initialize the JARVIS voice engine (espeak)
> 2. Load all command modules
> 3. Connect to your LLM provider
> 4. Start system monitoring
> 5. Greet you by name!

#### Test Voice Separately (Optional)

```bash
# Test espeak directly
espeak "Hello, I am NOVA"

# Test NOVA's TTS engine
python -c "
from nova.voice.tts import VoiceEngine
v = VoiceEngine()
v.speak('Hello sir. All systems are online. NOVA is at your service.', block=True)
v.shutdown()
"
```

---

## 🔄 Setting Up on Another Computer

### Prerequisites Checklist

- [ ] Linux (Ubuntu 20.04+, Debian 11+, Fedora 36+, Arch) or Windows
- [ ] Internet connection (for downloading packages)
- [ ] Python 3.10+ installed

### Step-by-Step (Linux)

```bash
# ═══════════════════════════════════════════════════════════════
# STEP 1: Install system dependencies
# ═══════════════════════════════════════════════════════════════
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    espeak espeak-data portaudio19-dev python3-pyaudio \
    libxcb-xinerama0 libxcb-cursor0 libxkbcommon0

# ═══════════════════════════════════════════════════════════════
# STEP 2: Copy the NOVA AI folder to the new computer
#         Use USB drive, SCP, rsync, cloud storage, or git clone
#         Do NOT copy the venv/ folder — recreate it fresh
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# STEP 3: Navigate to the project
# ═══════════════════════════════════════════════════════════════
cd ~/NOVA-AI

# ═══════════════════════════════════════════════════════════════
# STEP 4: Create & activate virtual environment
# ═══════════════════════════════════════════════════════════════
python3 -m venv venv
source venv/bin/activate

# ═══════════════════════════════════════════════════════════════
# STEP 5: Install all dependencies
# ═══════════════════════════════════════════════════════════════
pip install --upgrade pip
pip install -r requirements.txt

# ═══════════════════════════════════════════════════════════════
# STEP 6: Create your .env file
# ═══════════════════════════════════════════════════════════════
cp .env.example .env
nano .env
# → Add your GROQ_API_KEY and personal settings

# ═══════════════════════════════════════════════════════════════
# STEP 7: Launch NOVA!
# ═══════════════════════════════════════════════════════════════
python nova_gui.py
```

### What to Transfer to the New Computer

| What | Where | Transfer? |
|------|-------|-----------|
| Entire `NOVA AI` folder | Any location (e.g., `~/NOVA-AI`) | ✅ Yes |
| `.env` file | Inside project root | ✅ Yes (contains your API keys) |
| `data/` folder | Inside project root | Optional (contains memory/logs) |
| `venv/` folder | **DO NOT COPY** | ❌ No — recreate on new machine |

> ⚠️ **Never copy the `venv/` folder** between machines. Always create a fresh virtual environment on each computer.

---

## 🧠 LLM Provider Setup

NOVA supports three LLM backends. You only need **one**.

### Option 1: Groq (Recommended — FREE)

1. Go to **https://console.groq.com**
2. Sign up (free account)
3. Go to **API Keys** → Create new key
4. Add to your `.env`:
   ```env
   NOVA_LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
   ```

### Option 2: OpenAI (Paid)

1. Go to **https://platform.openai.com**
2. Create an API key and add billing
3. Add to your `.env`:
   ```env
   NOVA_LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
   ```
4. Install the package:
   ```bash
   pip install openai
   ```

### Option 3: Ollama (Fully Offline — FREE)

1. Install Ollama on Linux:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```
2. Pull a model and start:
   ```bash
   ollama pull llama3
   ollama serve
   ```
3. Add to your `.env`:
   ```env
   NOVA_LLM_PROVIDER=ollama
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```

### No LLM Provider?

NOVA works without any LLM! System commands (CPU check, battery, screenshots, etc.) work fully offline. Only the "smart conversation" feature requires an LLM.

---

## 🎙️ Voice Configuration

### JARVIS Voice

On Linux, NOVA uses **espeak** as the TTS engine with tuned settings for JARVIS-like delivery:

- **Rate: 165 words/min** — smooth, deliberate delivery
- **Volume: 100%** — confident and clear
- **Profiles:** JARVIS (default), Calm, Energetic, Alert

### Customisation

In your `.env` file:
```env
# Voice speed (words per minute). Lower = slower
NOVA_VOICE_RATE=165

# Volume: 0.0 to 1.0
NOVA_VOICE_VOLUME=1.0

# Gender: male or female
NOVA_VOICE_GENDER=male
```

### Installing Better Voices (Optional)

For more natural-sounding voices on Linux:

```bash
# Install mbrola voices (significantly better quality)
sudo apt install mbrola mbrola-en1

# Or install espeak-ng for improved quality
sudo apt install espeak-ng

# List all available voices
espeak --voices=en
```

---

## 🖥️ GUI Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  ⬡ NOVA AI  v2.0                         ● ONLINE    ─ □ ✕   │
├──────────┬──────────────────────────────────┬───────────────────┤
│ SYSTEM   │         ┌──────────┐             │   ⚙ SETTINGS     │
│ STATUS   │         │    AI    │             │   Wake Word  [ON] │
│          │         │   ORB    │             │   Voice: JARVIS   │
│ CPU [██] │         │  ◉◉◉    │             │   LLM: GROQ       │
│ RAM [██] │         └──────────┘             │   User: KK Sir    │
│ Disk  75%│         🎙 READY                │                   │
│ Bat  85% │                                  │   📋 ACTIVITY LOG │
│ Net   ✓  │  ◈ COMMAND INTERFACE            │   15:30 ▶ CMD...  │
│          │  ┌──────────────────────────┐    │   15:30 ◀ RSP...  │
│ ⚡ QUICK │  │ Chat messages appear     │    │   15:31 ● System  │
│ ACTIONS  │  │ here with typing effect  │    │                   │
│ 🌐 📂 📸│  └──────────────────────────┘    │                   │
│ 📊 🔊 🔇│  [Type a command...        ] [▶] │                   │
│ 🔒 ⏻   │                                  │                   │
└──────────┴──────────────────────────────────┴───────────────────┘
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+M` | Toggle microphone |
| `Escape` | Minimize window |
| `Ctrl+Q` | Quit NOVA |
| `Enter` | Send typed command |

---

## 🗣️ Available Commands

### System
| Command | What it does |
|---------|-------------|
| `system report` | Full CPU/RAM/Battery/Disk report |
| `check cpu` | CPU usage percentage |
| `check ram` | RAM usage details |
| `check battery` | Battery level and status |
| `check disk` | Disk space info |
| `check network` | Internet connectivity status |
| `top processes` | List top running processes |

### App Control
| Command | What it does |
|---------|-------------|
| `open chrome` | Launch Google Chrome (`google-chrome`) |
| `open firefox` | Launch Firefox |
| `open terminal` | Open GNOME Terminal |
| `open vlc` | Launch VLC media player |
| `open vs code` | Open Visual Studio Code |
| `screenshot` | Take a screenshot (requires `pyautogui`) |

### Volume & Power
| Command | What it does | How (Linux) |
|---------|-------------|-------------|
| `volume up` | Increase volume | `pactl` / `amixer` |
| `volume down` | Decrease volume | `pactl` / `amixer` |
| `mute` | Toggle mute | `pactl` / `amixer` |
| `lock screen` | Lock computer | `loginctl` / `xdg-screensaver` |
| `shutdown` | Shut down PC | `shutdown -h` |
| `restart` | Reboot PC | `reboot` |

### Conversation
| Command | What it does |
|---------|-------------|
| *Any natural language* | Chat with NOVA using your configured LLM |
| `help` | List all available commands |

---

## 🏗️ Project Architecture

```
NOVA-AI/
├── nova_gui.py              ← GUI entry point (run this)
├── main.py                  ← CLI entry point (terminal mode)
├── requirements.txt         ← Python dependencies (cross-platform)
├── .env.example             ← Template for configuration
├── .env                     ← Your actual config (git-ignored)
│
├── nova/                    ← Core backend package
│   ├── brain/               ← AI/LLM integration
│   │   ├── intent.py        ← Intent classifier
│   │   ├── llm.py           ← Multi-provider LLM client
│   │   ├── prompts.py       ← System prompts
│   │   └── router.py        ← Command routing logic
│   │
│   ├── commands/            ← Command handlers (cross-platform)
│   │   ├── registry.py      ← Self-registering command system
│   │   ├── system_info.py   ← CPU/RAM/Battery/Network
│   │   ├── app_control.py   ← Launch apps (Linux + Windows maps)
│   │   ├── power.py         ← Shutdown/restart/lock (Linux + Windows)
│   │   ├── file_ops.py      ← File management
│   │   ├── assistant.py     ← Greetings, help, time
│   │   └── productivity.py  ← Session tracking
│   │
│   ├── config/
│   │   └── settings.py      ← All configuration constants
│   │
│   ├── core/
│   │   ├── orchestrator.py  ← Main lifecycle manager
│   │   └── events.py        ← Pub/sub event bus
│   │
│   ├── memory/              ← Conversation memory
│   │   ├── manager.py       ← Memory facade
│   │   ├── short_term.py    ← In-session context
│   │   └── long_term.py     ← Persistent JSON storage
│   │
│   ├── monitoring/
│   │   ├── health_monitor.py ← Background health checks
│   │   └── alerts.py        ← Alert threshold logic
│   │
│   ├── plugins/
│   │   └── loader.py        ← Plugin auto-loader
│   │
│   ├── utils/
│   │   ├── logger.py        ← Centralized logging
│   │   ├── retry.py         ← Retry decorator
│   │   └── text.py          ← Text utilities
│   │
│   └── voice/               ← Voice I/O (cross-platform)
│       ├── tts.py           ← JARVIS TTS (espeak / SAPI5 / nsss)
│       ├── stt.py           ← Speech recognition
│       └── wake_word.py     ← Wake word detector
│
├── ui/                      ← PyQt6 GUI (cross-platform)
│   ├── main_window.py       ← Main window assembly
│   ├── bridge.py            ← GUI ↔ Backend bridge
│   ├── components/
│   │   ├── ai_orb.py        ← Animated NOVA orb
│   │   ├── chat_panel.py    ← Chat interface
│   │   ├── voice_control.py ← Mic button + status
│   │   ├── status_panel.py  ← System gauges
│   │   ├── settings_panel.py← Settings sidebar
│   │   ├── quick_actions.py ← Action button grid
│   │   ├── activity_log.py  ← Event log
│   │   └── notification_bar.py ← Toast notifications
│   └── styles/
│       └── theme.py         ← Color palette + QSS
│
└── data/                    ← Runtime data (auto-created)
    ├── memory/              ← Conversation history
    └── logs/                ← Application logs
```

---

## 🔧 Troubleshooting

### Voice Issues

| Issue | Solution |
|-------|----------|
| **No voice / espeak not found** | `sudo apt install espeak espeak-data` |
| **Voice sounds robotic** | Install mbrola: `sudo apt install mbrola mbrola-en1` |
| **No sound output** | Check PulseAudio: `pactl info` |
| **Volume commands don't work** | `sudo apt install pulseaudio-utils` |

### GUI Issues

| Issue | Solution |
|-------|----------|
| **Qt platform plugin error** | `sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon0` |
| **`Could not load "xcb"` error** | Install all xcb libs: see command below |
| **Wayland display issues** | `export QT_QPA_PLATFORM=xcb` before running |
| **GUI crashes on launch** | `pip install PyQt6` |

### Package Issues

| Issue | Solution |
|-------|----------|
| **PyAudio install fails** | `sudo apt install portaudio19-dev && pip install pyaudio` |
| **`python3` not found** | `sudo apt install python3 python3-pip` |
| **No LLM backend available** | Set `GROQ_API_KEY` in `.env` or install Ollama |

### Quick Fix — Install All Dependencies at Once

```bash
# Ubuntu/Debian — one command to install everything
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    espeak espeak-data portaudio19-dev python3-pyaudio \
    libxcb-xinerama0 libxcb-cursor0 libxkbcommon0 \
    pulseaudio-utils xdg-utils
```

```bash
# If GUI still crashes with platform plugin error
export QT_QPA_PLATFORM=xcb
python nova_gui.py
```

### Permission Issues

```bash
# If shutdown/restart requires root
# Option 1: Run with sudo (not recommended for GUI)
# Option 2: Configure polkit for passwordless shutdown
sudo nano /etc/polkit-1/localauthority/50-local.d/allow-shutdown.pkla
```

---

## 🪟 Windows Setup

<details>
<summary>Click to expand Windows instructions</summary>

### Quick Start (Windows)

```powershell
cd "C:\NOVA AI"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
# → Add your GROQ_API_KEY
python nova_gui.py
```

### Windows-Specific Notes

- **Python**: Download from https://www.python.org — check **"Add to PATH"** during install
- **Voice**: Uses Microsoft David (SAPI5) — no extra software needed
- **PyAudio fails?** Run: `pip install pipwin && pipwin install pyaudio`
- **Execution Policy error?** Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Windows-only packages** (`comtypes`, `pywin32`) are auto-installed from `requirements.txt`

</details>

---

## ❓ FAQ

**Q: Is NOVA free to use?**
A: Yes! NOVA is completely free. Groq's API is also free-tier. Only OpenAI requires paid credits.

**Q: Can I use NOVA without internet?**
A: Yes! System commands work fully offline. For AI conversations, use Ollama (offline LLM).

**Q: Does NOVA work on Windows too?**
A: Yes! Full Windows 10/11 support. See the [Windows Setup](#-windows-setup) section.

**Q: How do I add new commands?**
A: Create a new file in `nova/commands/`, write a function decorated with `@command(intents=[...])`, and NOVA auto-discovers it on next boot.

**Q: Where are logs stored?**
A: In `data/logs/nova.log` — useful for debugging.

**Q: How do I change the wake word?**
A: In `.env`: `NOVA_WAKE_WORD=hey jarvis` (or anything you prefer).

**Q: Does the GUI work on Wayland?**
A: PyQt6 supports Wayland, but if you see display issues, run: `export QT_QPA_PLATFORM=xcb`

**Q: How do I get better voice quality on Linux?**
A: Install mbrola voices: `sudo apt install mbrola mbrola-en1`

---

## 📄 License

This project is for personal/educational use.

---

<p align="center">
  Built with ❤️ by KK Sir<br>
  <em>"I am NOVA, your Neural Operative Virtual Assistant."</em>
</p>
