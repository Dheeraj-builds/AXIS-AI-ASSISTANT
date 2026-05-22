<div align="center">

<img src="AXIS_AI.png" alt="AXIS Logo" width="150"/>

# A.X.I.S.
### Artificial eXecution & Intelligence System

**A JARVIS-style personal AI assistant built with Python**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA%203.3-orange?style=for-the-badge)](https://console.groq.com)
[![ElevenLabs](https://img.shields.io/badge/Voice-ElevenLabs-purple?style=for-the-badge)](https://elevenlabs.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*Built by a 15-year-old developer from Hyderabad, India 🇮🇳*

</div>

---

## 🤖 What is AXIS?

AXIS is a fully functional JARVIS-style AI assistant built entirely in Python. It features a futuristic full-screen GUI, a deep AI voice powered by ElevenLabs, and a powerful brain powered by Groq's LLaMA 3.3 70B model.

Think Tony Stark's JARVIS — but running on your Windows PC. Right now.

---

## ✨ Features

### 🧠 AI & Intelligence
- Powered by **Groq LLaMA 3.3 70B** — fast, free, and never expires
- Answers general knowledge, sports, health, science, and coding questions
- Writes, debugs, and explains code in any language
- Math & science calculator with step-by-step solutions
- Context-aware responses using recent chat history

### 🎙️ Voice
- Deep, calm, futuristic male voice via **ElevenLabs TTS**
- Automatic fallback to pyttsx3 if ElevenLabs quota runs out
- Optional microphone input — works perfectly with just typing too

### 💾 Memory System
- Remembers your name, preferences, subjects, location and more
- **AES encrypted** storage — your data never leaves your PC
- Persistent chat history across sessions
- Greets you by name and recalls your last project on startup

### 🖥️ Desktop Control
- Open any app, folder, or file by voice or text
- Volume control, screenshot, lock screen, sleep, shutdown, restart
- Open 20+ websites instantly — YouTube, Google, GitHub, Gmail and more
- Auto-start toggle — tell AXIS to start with Windows or go back to manual

### 📁 File Handling
- Attach PDFs, Word docs, images, and code files
- Summarize and analyze any document
- **Convert PDF → Word** and **Word → PDF**
- Convert images between formats (PNG, JPG, BMP)
- Read and improve code files

### 🗺️ Maps & Navigation
- Show maps of any location
- Get directions from A to B
- Find nearby places
- Open Street View

### 🖼️ Images
- **AI image generation** via Pollinations AI (free, no key needed)
  - "Generate image of a futuristic city"
- **Real web image search** via Google Images
  - "Show me images of Iron Man suit"

### 🎨 GUI
- Full-screen JARVIS-style dark blue interface
- Left HUD panel with animated rings, wave bars, and system stats
- Right chat panel with persistent scrollable history
- Timestamps on every message
- File attachment bar
- Quick command hints
- Live clock in top bar
- Pulsing online status indicator

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (primary support)

### Installation

**Step 1 — Clone the repository**
```bash
git clone https://github.com/Dheeraj-builds/AXIS-AI-Assistant.git
cd AXIS-AI-Assistant
```

**Step 2 — Install dependencies**
```bash
pip install groq elevenlabs speechrecognition pyaudio
pip install pillow requests cryptography pymupdf python-docx pdf2docx
```

**Step 3 — Get your API keys (both free)**

| Key | Where to get |
|-----|-------------|
| Groq API Key | [console.groq.com](https://console.groq.com) → API Keys → Create |
| ElevenLabs API Key | [elevenlabs.io](https://elevenlabs.io) → Profile → API Keys |

**Step 4 — Add your keys**

Open `axis_assistant.py` and edit lines 26-27:
```python
GROQ_API_KEY       = "your_groq_key_here"
ELEVENLABS_API_KEY = "your_elevenlabs_key_here"
```

**Step 5 — Add your name as creator (optional)**

Edit line 35:
```python
CREATOR_NAME = "Dheeraj"
```

**Step 6 — Run AXIS**
```bash
python axis_assistant.py
```

**Step 7 — Create desktop icon (run once)**
```bash
python install_axis.py
```
After this, just double-click the AXIS icon on your Desktop forever — no terminal needed!

---

## 💬 Example Commands

```
"Open YouTube"
"What time is it?"
"Remember my name is Dheeraj"
"Search for latest AI news"
"Generate image of a futuristic city"
"Show me images of Iron Man"
"Convert PDF to Word"
"Show map of Hyderabad"
"Open Downloads folder"
"Write a Python script to sort a list"
"What is the capital of Japan?"
"Enable auto start"
"Lock my screen"
"Exit AXIS"
```

---

## 📁 Project Structure

```
AXIS-AI-Assistant/
│
├── axis_assistant.py    ← Main application (GUI + AI + all features)
├── install_axis.py      ← Desktop installer (run once)
├── AXIS_AI.png          ← App icon (planet/orbit logo)
└── README.md            ← This file
```

---

## 🛣️ Roadmap

- [x] Futuristic JARVIS-style GUI
- [x] Groq LLaMA 3.3 AI brain
- [x] ElevenLabs voice
- [x] Encrypted memory
- [x] Persistent chat history
- [x] Desktop control
- [x] File conversion
- [x] Image generation + web image search
- [x] Maps & navigation
- [ ] Offline mode (Ollama local AI)
- [ ] IoT home appliance control
- [ ] Mobile companion app
- [ ] Wake word detection ("Hey AXIS")

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.8+ |
| GUI | Tkinter |
| AI Brain | Groq LLaMA 3.3 70B |
| Voice Output | ElevenLabs TTS |
| Voice Input | Google Speech Recognition |
| Memory Encryption | Cryptography (Fernet AES) |
| Image Generation | Pollinations AI |
| PDF Processing | PyMuPDF |
| Word Processing | python-docx |

---

## 👨‍💻 About the Developer

Built by a 15-year-old self-taught developer from Hyderabad, India — 
still learning, but building anyway.
I built AXIS because I wanted my own JARVIS — a personal AI assistant that actually works the way I want it to. No subscriptions, no limits, fully mine.

If you like this project, please ⭐ star it — it means a lot!

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and build on it.

---

<div align="center">

**Built with 🤖 by [Dheeraj-builds](https://github.com/Dheeraj-builds)**

*"I am not building just a project. I am building my future."*

</div>
