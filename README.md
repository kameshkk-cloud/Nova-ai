# ⬡ NOVA — Neural Operative Virtual Assistant v2.0

> *"Your personal JARVIS, built from scratch."*
> Built for: **KK Sir** | Production Build — Voice + Automation + Intelligence + Plugins

---

## 🚀 Quick Start

```bash
# Step 1: Install all dependencies
python install.py

# Step 2: Configure your LLM (pick ONE)
#   Option A — Groq (free, cloud): Get key from https://console.groq.com
#   Option B — OpenAI (paid, cloud): Get key from https://platform.openai.com
#   Option C — Ollama (free, offline): Install from https://ollama.ai
copy .env.example .env        # then edit .env with your API key

# Step 3: Run NOVA!
python main.py
```

---

## 📁 Architecture

```
NOVA AI/
├── main.py                 ← 🚀 Entry point
├── install.py              ← 📦 Dependency installer
├── dashboard.py            ← 📊 Live system dashboard
├── .env.example            ← ⚙️ Config template
│
├── nova/
│   ├── config/
│   │   └── settings.py     ← All configuration (.env aware)
│   │
│   ├── core/
│   │   ├── orchestrator.py ← Central lifecycle manager
│   │   └── events.py       ← Pub/sub event bus
│   │
│   ├── voice/
│   │   ├── tts.py          ← 🎙 Adaptive text-to-speech (multi-voice)
│   │   ├── stt.py          ← 🎤 Speech recognition with retry
│   │   └── wake_word.py    ← Wake word detection with debounce
│   │
│   ├── brain/
│   │   ├── intent.py       ← 🧠 Intent classifier (pattern + LLM)
│   │   ├── llm.py          ← 🤖 Multi-provider LLM (Groq/OpenAI/Ollama)
│   │   ├── router.py       ← Intent → command dispatcher
│   │   └── prompts.py      ← System prompt templates
│   │
│   ├── memory/
│   │   ├── short_term.py   ← Session ring buffer (20 turns)
│   │   ├── long_term.py    ← Persistent JSON (profile, notes, history)
│   │   └── manager.py      ← Unified memory interface
│   │
│   ├── commands/
│   │   ├── registry.py     ← @command decorator & auto-discovery
│   │   ├── system_info.py  ← CPU, RAM, battery, disk, network
│   │   ├── app_control.py  ← Open/close apps, volume, screenshot
│   │   ├── power.py        ← Shutdown, restart, lock
│   │   ├── file_ops.py     ← Organise, summarise, find files
│   │   ├── productivity.py ← Activity tracking & daily reports
│   │   └── assistant.py    ← Time, help, reminders, notes, exit
│   │
│   ├── monitoring/
│   │   ├── health_monitor.py ← Background daemon with event-bus alerts
│   │   └── alerts.py        ← Cooldown manager (no alert spam)
│   │
│   ├── plugins/
│   │   └── loader.py       ← 🔌 Auto-discover plugins from data/plugins/
│   │
│   └── utils/
│       ├── logger.py       ← Rotating file + Rich console logging
│       ├── retry.py        ← @retry decorator with backoff
│       └── text.py         ← Sanitise, extract paths/URLs/numbers
│
└── data/
    ├── memory/             ← Conversation & profile storage
    ├── logs/               ← nova.log + activity tracking
    └── plugins/            ← Drop .py files here to extend NOVA
```

---

## 🎙 Voice Commands

| Say this...                     | NOVA does this...             |
|---------------------------------|-------------------------------|
| "Hey NOVA"                      | Activates NOVA                |
| "What time is it?"              | Tells current time            |
| "CPU status"                    | Reports CPU usage             |
| "Battery"                       | Battery % and status          |
| "System report"                 | Full health report            |
| "Open Chrome"                   | Launches Chrome               |
| "Search Python tutorials"       | Google search                 |
| "Shutdown"                      | Shuts down in 10 seconds      |
| "Volume up / down"              | Adjusts system volume         |
| "Screenshot"                    | Saves a screenshot            |
| "Organise C:\\Downloads"        | Sorts files by type           |
| "Summarize C:\\notes.txt"       | Reads and summarises file     |
| "Remind me to study at 6pm"     | Saves a reminder              |
| "Note: important idea"          | Saves a quick note            |
| "Daily report"                  | Productivity summary          |
| "Help"                          | Lists all capabilities        |
| "Stop" / "Exit"                 | Shuts down NOVA               |
| *Anything else*                 | LLM-powered conversation      |

---

## 🧠 How It Works

```
User Input (Voice / Keyboard)
         ↓
   Orchestrator (core/orchestrator.py)
         ↓
   Intent Classifier (brain/intent.py)  ←── Pattern matching
         ↓
   ┌─ Command Registry ──────────────────────────┐
   │  system_info  app_control  power  file_ops   │
   │  productivity  assistant   + plugins          │
   └──────────────────────────────────────────────┘
         ↓ (no match)
   LLM Client (brain/llm.py)  ←── Groq / OpenAI / Ollama
         ↓
   Voice Engine (voice/tts.py)  ←── Adaptive profile
         ↓
   Memory Manager  ←── Short-term (session) + Long-term (JSON)
```

---

## 🎨 Adaptive Voice

NOVA automatically adjusts its voice based on context:

| Profile     | Rate | Volume | Used when...                    |
|-------------|------|--------|---------------------------------|
| `calm`      | 140  | 75%    | Late night (11pm–6am)           |
| `default`   | 175  | 100%   | Normal hours                    |
| `energetic` | 210  | 100%   | Morning (6am–10am) / excitement |
| `alert`     | 195  | 100%   | Critical system alerts          |

---

## 🔌 Plugin System

Create a `.py` file in `data/plugins/` — it's auto-loaded at boot:

```python
# data/plugins/joke.py
from nova.commands.registry import command, CommandResult

@command(intents=["tell_joke"], description="Tell a joke", category="fun")
def cmd_joke(arg, memory):
    return CommandResult(response="Why do programmers prefer dark mode? Light attracts bugs!")

def register(registry):
    pass  # @command handles registration
```

---

## ⚙️ Configuration

All settings live in `nova/config/settings.py` and can be overridden via `.env`:

| Environment Variable   | Default        | Description                |
|------------------------|----------------|----------------------------|
| `NOVA_USER_NAME`       | KK Sir         | What NOVA calls you        |
| `NOVA_WAKE_WORD`       | hey nova       | Activation phrase          |
| `NOVA_LLM_PROVIDER`   | groq           | groq / openai / ollama     |
| `GROQ_API_KEY`         | (empty)        | Groq API key               |
| `OPENAI_API_KEY`       | (empty)        | OpenAI API key             |
| `OLLAMA_MODEL`         | llama3         | Ollama model name          |
| `NOVA_VOICE_GENDER`    | male           | male / female              |
| `NOVA_MONITOR_INTERVAL`| 30             | Health check seconds       |
| `NOVA_ALERT_COOLDOWN`  | 300            | Alert repeat cooldown (s)  |
| `NOVA_LOG_LEVEL`       | DEBUG          | Logging verbosity          |

---

## 📦 Dependencies

| Package           | Purpose                | Required |
|-------------------|------------------------|----------|
| pyttsx3           | Text-to-Speech         | ✓        |
| SpeechRecognition | Voice input            | ✓        |
| psutil            | System monitoring      | ✓        |
| rich              | Terminal UI            | ✓        |
| groq              | Groq LLM API          | ✓        |
| openai            | OpenAI LLM API        | ✓        |
| python-dotenv     | .env file loading      | ✓        |
| pyautogui         | Screenshots            | ✓        |
| pyaudio           | Microphone access      | Optional |

---

## 🗺 Roadmap

| Phase | Feature                           | Status       |
|-------|-----------------------------------|--------------|
| 1     | Voice + Automation + Memory       | ✅ Complete   |
| 2     | Multi-LLM (Groq/OpenAI/Ollama)   | ✅ Complete   |
| 2     | Plugin System                     | ✅ Complete   |
| 2     | Adaptive Voice Profiles           | ✅ Complete   |
| 2     | Event Bus + Alert Cooldowns       | ✅ Complete   |
| 3     | Mobile App (Flutter)              | 🔜 Planned   |
| 3     | AWS Cloud Integration             | 🔜 Planned   |
| 4     | Gesture Control (OpenCV)          | 🔜 Future    |

---

*Built with ❤️ for KK Sir — from prototype to production, one module at a time.*
