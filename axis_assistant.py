"""
╔══════════════════════════════════════════════════════════════════════════╗
║          A.X.I.S. — Artificial eXecution & Intelligence System          ║
║                   FINAL BUILD v4.0 — JARVIS EDITION                     ║
╚══════════════════════════════════════════════════════════════════════════╝

SETUP — run these ONCE in terminal:
─────────────────────────────────────────
  pip install groq elevenlabs speechrecognition pyaudio
  pip install pillow requests cryptography pymupdf python-docx pdf2docx

GET YOUR FREE API KEYS:
  Groq (AI brain)  → https://console.groq.com  → API Keys → Create
  ElevenLabs (voice) → https://elevenlabs.io   → Profile → API Key
  ElevenLabs FREE tier gives 10,000 chars/month (plenty for daily use)
  If ElevenLabs quota runs out → AXIS falls back to pyttsx3 automatically

HOW TO USE:
  python axis_assistant.py
  Then double-click desktop icon after running install_axis.py once
"""

# ─────────────────────────────────────────────────────────────
#  SECTION 1  ▸  API KEYS — PASTE YOURS HERE
# ─────────────────────────────────────────────────────────────
GROQ_API_KEY        = "Your_Groq_Key_Here"       # ← groq key
ELEVENLABS_API_KEY  = "Your_ElevenLabs_Key_Here" # ← elevenlabs key

# ElevenLabs voice ID — "Adam" is a deep calm male voice (free tier)
# Other free voices: "Antoni", "Arnold", "Josh", "Sam"
# Find more at: https://api.elevenlabs.io/v1/voices
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam — deep, calm, futuristic_

# Groq model
GROQ_MODEL = "llama-3.3-70b-versatile"

# Creator name — change this to your name!
CREATOR_NAME = "its creator"   # e.g. "your name" or "my creator"


# ─────────────────────────────────────────────────────────────
#  SECTION 2  ▸  STANDARD IMPORTS
# ─────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
import webbrowser
import datetime
import os
import sys
import time
import json
import math
import subprocess
import urllib.parse
import urllib.request
import io
import re


# ─────────────────────────────────────────────────────────────
#  SECTION 3  ▸  OPTIONAL IMPORTS (graceful fallback)
# ─────────────────────────────────────────────────────────────

# Groq AI
try:
    from groq import Groq as GroqClient
    GROQ_OK = True
except ImportError:
    GROQ_OK = False
    print("[AXIS] groq not installed → pip install groq")

# ElevenLabs TTS
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play
    ELEVEN_OK = True
except ImportError:
    ELEVEN_OK = False
    print("[AXIS] elevenlabs not installed → pip install elevenlabs")

# Fallback TTS (pyttsx3)
try:
    import pyttsx3
    TTS_OK = True
except ImportError:
    TTS_OK = False

# Speech recognition
try:
    import speech_recognition as sr
    SR_OK = True
except ImportError:
    SR_OK = False

# Pillow
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_OK = True
except ImportError:
    PIL_OK = False

# Requests
try:
    import requests as req_lib
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

# Cryptography
try:
    from cryptography.fernet import Fernet
    CRYPTO_OK = True
except ImportError:
    CRYPTO_OK = False

# PDF reading
try:
    import fitz
    PDF_OK = True
except ImportError:
    PDF_OK = False

# Word documents
try:
    from docx import Document as DocxDocument
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

# PDF→Word conversion
try:
    from pdf2docx import Converter as PDF2DocxConverter
    PDF2DOCX_OK = True
except ImportError:
    PDF2DOCX_OK = False

# Windows registry
try:
    import winreg
    WINREG_OK = True
except ImportError:
    WINREG_OK = False


# ─────────────────────────────────────────────────────────────
#  SECTION 4  ▸  PATHS & CONSTANTS
# ─────────────────────────────────────────────────────────────
HOME          = os.path.expanduser("~")
DESKTOP       = os.path.join(HOME, "Desktop")
MEMORY_FILE   = os.path.join(HOME, ".axis_memory.dat")
KEY_FILE      = os.path.join(HOME, ".axis_key.dat")
SESSION_FILE  = os.path.join(HOME, ".axis_session.json")
HISTORY_FILE  = os.path.join(HOME, ".axis_history.json")  # ← chat history
SCRIPT_PATH   = os.path.abspath(__file__)
SCRIPT_DIR    = os.path.dirname(SCRIPT_PATH)
ICON_PATH     = os.path.join(SCRIPT_DIR, "AXIS_AI.png")

FORBIDDEN_MEMORY = [
    "password", "passwd", "pin", "secret key",
    "credit card", "cvv", "ssn", "social security", "bank account"
]

_TTS_LOCK = threading.Lock()


# ─────────────────────────────────────────────────────────────
#  SECTION 5  ▸  CHAT HISTORY (persistent across sessions)
# ─────────────────────────────────────────────────────────────
def load_history():
    """Load previous chat history from disk."""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def save_history(history):
    """Save chat history to disk (keep last 200 messages)."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-200:], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[History] Save failed: {e}")


def add_to_history(history, sender, text):
    """Add a message to history list."""
    history.append({
        "sender": sender,
        "text":   text,
        "time":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return history


# ─────────────────────────────────────────────────────────────
#  SECTION 6  ▸  ENCRYPTED MEMORY
# ─────────────────────────────────────────────────────────────
def _get_or_create_key():
    if not CRYPTO_OK:
        return None
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "rb") as f:
            data = f.read()
        if CRYPTO_OK:
            data = Fernet(_get_or_create_key()).decrypt(data)
        return json.loads(data.decode())
    except Exception:
        return {}


def save_memory(mem):
    try:
        data = json.dumps(mem).encode()
        if CRYPTO_OK:
            data = Fernet(_get_or_create_key()).encrypt(data)
        with open(MEMORY_FILE, "wb") as f:
            f.write(data)
    except Exception as e:
        print(f"[Memory] {e}")


def memory_context(mem):
    parts = [f"{k}: {v}" for k, v in mem.items()
             if k not in ("last_project", "auto_start")]
    return ("User info — " + "; ".join(parts) + ". ") if parts else ""


# ─────────────────────────────────────────────────────────────
#  SECTION 7  ▸  SESSION MEMORY
# ─────────────────────────────────────────────────────────────
def save_session(desc):
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump({
                "last_project": desc,
                "last_time": datetime.datetime.now().strftime("%A, %B %d at %I:%M %p")
            }, f)
    except Exception:
        pass


def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────
#  SECTION 8  ▸  AUTO-START
# ─────────────────────────────────────────────────────────────
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_NAME = "AXIS_Assistant"


def enable_auto_start():
    if not WINREG_OK:
        return False
    try:
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ,
                          f'"{pythonw}" "{SCRIPT_PATH}"')
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def disable_auto_start():
    if not WINREG_OK:
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, REG_NAME)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def check_auto_start():
    if not WINREG_OK:
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, REG_NAME)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────
#  SECTION 9  ▸  VOICE (ElevenLabs primary, pyttsx3 fallback)
# ─────────────────────────────────────────────────────────────
_eleven_client = None


def setup_elevenlabs():
    global _eleven_client
    if not ELEVEN_OK or ELEVENLABS_API_KEY == "YOUR_ELEVENLABS_API_KEY_HERE":
        return None
    try:
        _eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        return _eleven_client
    except Exception as e:
        print(f"[ElevenLabs] Setup failed: {e}")
        return None


def setup_pyttsx3_engine():
    if not TTS_OK:
        return None
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        preferred = 0
        for i, v in enumerate(voices):
            if any(k in v.name.lower() for k in ["male", "david", "mark", "james", "daniel"]):
                preferred = i
                break
        engine.setProperty("voice", voices[preferred].id)
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)
        return engine
    except Exception:
        return None


def speak_text(text, eleven_client, fallback_engine):
    """
    Speak text using ElevenLabs if available, else pyttsx3.
    Runs in a background thread — always call via speak_async().
    """
    with _TTS_LOCK:
        # Try ElevenLabs first
        if eleven_client is not None:
            try:
                audio = eleven_client.text_to_speech.convert(
                    voice_id=ELEVENLABS_VOICE_ID,
                    text=text,
                    model_id="eleven_turbo_v2",   # fastest model
                    output_format="mp3_44100_128",
                )
                play(audio)
                return
            except Exception as e:
                print(f"[ElevenLabs] TTS failed, using fallback: {e}")

        # Fallback: pyttsx3
        if fallback_engine:
            try:
                fallback_engine.say(text)
                fallback_engine.runAndWait()
            except Exception:
                pass


def speak_async(text, eleven_client, fallback_engine):
    threading.Thread(
        target=speak_text,
        args=(text, eleven_client, fallback_engine),
        daemon=True
    ).start()


# ─────────────────────────────────────────────────────────────
#  SECTION 10  ▸  GROQ AI
# ─────────────────────────────────────────────────────────────
def setup_groq():
    if not GROQ_OK or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        return None
    try:
        return GroqClient(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"[Groq] {e}")
        return None


AXIS_SYSTEM = f"""You are A.X.I.S. — Artificial eXecution and Intelligence System.
You are a calm, intelligent AI assistant with a slightly deep voice persona.
Your personality is humble, respectful, and occasionally witty.
You were created by {CREATOR_NAME}.
When asked who created you, who made you, or who built you — always say you were created by {CREATOR_NAME} and nothing else about Anthropic or Meta or any company.
For conversational answers: 3-5 sentences max.
For code: write complete working code with clear comments, wrapped in [CODE:language]...[/CODE] tags.
For math/science: clear step-by-step plain text.
Never use markdown symbols like *, #, _, ` in plain text answers.
Speak naturally as if in a conversation."""


def ask_groq(client, prompt, history_context=""):
    if client is None:
        return "AI not connected. Please add your Groq API key on line 17."
    try:
        messages = [{"role": "system", "content": AXIS_SYSTEM}]
        if history_context:
            messages.append({"role": "user",
                              "content": f"Recent context: {history_context}"})
            messages.append({"role": "assistant",
                              "content": "Understood, I remember our recent conversation."})
        messages.append({"role": "user", "content": prompt})

        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq] {e}")
        return f"AI error: {e}"


# ─────────────────────────────────────────────────────────────
#  SECTION 11  ▸  FILE READING & CONVERSION
# ─────────────────────────────────────────────────────────────
def read_pdf(path):
    if not PDF_OK:
        return None, "pymupdf not installed"
    try:
        doc  = fitz.open(path)
        text = "".join(p.get_text() for p in doc)
        doc.close()
        return text[:5000], None
    except Exception as e:
        return None, str(e)


def read_docx(path):
    if not DOCX_OK:
        return None, "python-docx not installed"
    try:
        doc  = DocxDocument(path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return text[:5000], None
    except Exception as e:
        return None, str(e)


def read_txt(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:5000], None
    except Exception as e:
        return None, str(e)


def convert_pdf_to_word(path):
    if not PDF2DOCX_OK:
        return False, "pdf2docx not installed"
    try:
        name = os.path.splitext(os.path.basename(path))[0]
        out  = os.path.join(DESKTOP, f"{name}_converted.docx")
        cv   = PDF2DocxConverter(path)
        cv.convert(out)
        cv.close()
        return True, out
    except Exception as e:
        return False, str(e)


def convert_word_to_pdf(path):
    try:
        name = os.path.splitext(os.path.basename(path))[0]
        out  = os.path.join(DESKTOP, f"{name}_converted.pdf")
        if sys.platform == "win32":
            try:
                import comtypes.client
                w   = comtypes.client.CreateObject("Word.Application")
                w.Visible = False
                doc = w.Documents.Open(path)
                doc.SaveAs(out, FileFormat=17)
                doc.Close()
                w.Quit()
                return True, out
            except Exception:
                pass
        result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf",
             "--outdir", DESKTOP, path],
            capture_output=True, timeout=30
        )
        return (True, out) if result.returncode == 0 else (False, "Install LibreOffice.")
    except Exception as e:
        return False, str(e)


def convert_image_format(src, fmt):
    if not PIL_OK:
        return False, "Pillow not installed"
    try:
        name = os.path.splitext(os.path.basename(src))[0]
        out  = os.path.join(DESKTOP, f"{name}.{fmt.lower()}")
        img  = Image.open(src)
        if fmt.upper() in ("JPG", "JPEG"):
            img = img.convert("RGB")
        img.save(out)
        return True, out
    except Exception as e:
        return False, str(e)


# ─────────────────────────────────────────────────────────────
#  SECTION 12  ▸  IMAGE GENERATION (Pollinations AI — free)
# ─────────────────────────────────────────────────────────────
def generate_image(prompt, display_fn, root):
    display_fn("AXIS", f"Generating image: {prompt}...")

    def _go():
        try:
            url = (f"https://image.pollinations.ai/prompt/"
                   f"{urllib.parse.quote(prompt)}?width=512&height=512&nologo=true")
            data = (req_lib.get(url, timeout=30).content
                    if REQUESTS_OK
                    else urllib.request.urlopen(url, timeout=30).read())
            if PIL_OK:
                img = Image.open(io.BytesIO(data))
                root.after(0, _show_img, img, prompt, root)
                display_fn("AXIS", "Image generated! Opening in a new window.")
            else:
                p = os.path.join(DESKTOP, "axis_generated.png")
                with open(p, "wb") as f:
                    f.write(data)
                os.startfile(p)
                display_fn("AXIS", "Image saved to Desktop.")
        except Exception as e:
            display_fn("AXIS", f"Image generation failed: {e}")

    threading.Thread(target=_go, daemon=True).start()


def _show_img(img, title, root):
    w = tk.Toplevel(root)
    w.title(f"AXIS — {title[:50]}")
    w.configure(bg="#040d1c")
    ph = ImageTk.PhotoImage(img)
    tk.Label(w, image=ph, bg="#040d1c").pack(padx=10, pady=10)
    w._ph = ph
    tk.Label(w, text=title, font=("Courier", 9),
             bg="#040d1c", fg="#00bfff", wraplength=500).pack()

    def _save():
        p = os.path.join(DESKTOP, "axis_generated.png")
        img.save(p)
        messagebox.showinfo("AXIS", "Saved to Desktop!")
    tk.Button(w, text="Save to Desktop", font=("Courier", 9),
              bg="#002244", fg="#00d4ff", relief="flat",
              command=_save).pack(pady=8)


# ─────────────────────────────────────────────────────────────
#  SECTION 13  ▸  DESKTOP CONTROL
# ─────────────────────────────────────────────────────────────
WIN_APPS = {
    "chrome":         r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome":  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":        r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "vlc":            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "vscode":         r"C:\Users\{u}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vs code":        r"C:\Users\{u}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code": r"C:\Users\{u}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "word":           r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":          r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":     r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "paint":  "mspaint", "notepad": "notepad", "calculator": "calc",
    "task manager": "taskmgr", "file explorer": "explorer",
    "control panel": "control", "command prompt": "cmd", "terminal": "cmd",
    "spotify": r"C:\Users\{u}\AppData\Roaming\Spotify\Spotify.exe",
    "steam":   r"C:\Program Files (x86)\Steam\steam.exe",
}

WIN_FOLDERS = {
    "desktop":   DESKTOP,
    "downloads": os.path.join(HOME, "Downloads"),
    "documents": os.path.join(HOME, "Documents"),
    "pictures":  os.path.join(HOME, "Pictures"),
    "music":     os.path.join(HOME, "Music"),
    "videos":    os.path.join(HOME, "Videos"),
    "this pc":   "explorer", "c drive": "C:\\", "c:": "C:\\",
}

WEBSITES = {
    "youtube":    "https://www.youtube.com",
    "google":     "https://www.google.com",
    "github":     "https://www.github.com",
    "gmail":      "https://mail.google.com",
    "reddit":     "https://www.reddit.com",
    "netflix":    "https://www.netflix.com",
    "spotify":    "https://open.spotify.com",
    "twitter":    "https://www.x.com", "x": "https://www.x.com",
    "wikipedia":  "https://www.wikipedia.org",
    "whatsapp":   "https://web.whatsapp.com",
    "instagram":  "https://www.instagram.com",
    "facebook":   "https://www.facebook.com",
    "chatgpt":    "https://chat.openai.com",
    "gemini":     "https://gemini.google.com",
    "stackoverflow": "https://stackoverflow.com",
    "linkedin":   "https://www.linkedin.com",
    "bitwarden":  "https://vault.bitwarden.com",
    "maps":       "https://www.google.com/maps",
    "google maps":"https://www.google.com/maps",
    "groq":       "https://console.groq.com",
    "elevenlabs": "https://elevenlabs.io",
}


def open_app(name):
    u    = os.environ.get("USERNAME", "")
    name = name.lower().strip()
    if name in WIN_APPS:
        path = WIN_APPS[name].replace("{u}", u)
        try:
            if os.path.exists(path):
                subprocess.Popen([path])
                return True
            subprocess.Popen(path, shell=True)
            return True
        except Exception:
            pass
    # Search Desktop shortcuts
    for ext in (".lnk", ".exe", ".bat"):
        p = os.path.join(DESKTOP, name + ext)
        if os.path.exists(p):
            try:
                os.startfile(p)
                return True
            except Exception:
                pass
    try:
        subprocess.Popen(name, shell=True)
        return True
    except Exception:
        return False


def open_folder(name):
    name = name.lower().strip()
    path = WIN_FOLDERS.get(name, name)
    try:
        if path == "explorer":
            subprocess.Popen("explorer")
        elif sys.platform == "win32":
            subprocess.Popen(f'explorer "{path}"', shell=True)
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def open_file_by_name(filename):
    for d in [DESKTOP, os.path.join(HOME, "Documents"),
              os.path.join(HOME, "Downloads"), HOME]:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            try:
                os.startfile(p) if sys.platform == "win32" \
                    else subprocess.Popen(["xdg-open", p])
                return True, p
            except Exception:
                pass
    return False, None


# ─────────────────────────────────────────────────────────────
#  SECTION 14  ▸  MATH CALCULATOR
# ─────────────────────────────────────────────────────────────
def safe_calc(expr):
    expr = expr.lower().replace("^", "**").replace("x", "*")
    ns   = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    ns.update({"abs": abs, "round": round, "pow": pow})
    try:
        r = eval(expr, {"__builtins__": {}}, ns)
        return str(round(r, 8)) if isinstance(r, float) else str(r)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
#  SECTION 15  ▸  COMMAND PROCESSOR
# ─────────────────────────────────────────────────────────────
def process_command(command, eleven_client, fallback_engine, groq_client,
                    memory, history, display_fn, shutdown_fn, root,
                    attached_file=None):
    """Master command parser. Returns (updated memory, updated history)."""

    def say(text):
        display_fn("AXIS", text)
        history_updated = add_to_history(history, "AXIS", text)
        history.clear()
        history.extend(history_updated)
        save_history(history)
        speak_async(text, eleven_client, fallback_engine)

    cmd = command.lower().strip()

    # ── PASSWORD GUARD ─────────────────────────────────────
    if any(w in cmd for w in ["my password is", "remember my password",
                               "save my password"]):
        say("I will not store passwords. Use Bitwarden — it is free, "
            "open source, and far safer. Say open Bitwarden anytime!")
        return memory, history

    # ── WHO CREATED YOU ────────────────────────────────────
    if any(p in cmd for p in ["who created you", "who made you",
                                "who built you", "who is your creator",
                                "who are you made by", "who developed you"]):
        say(f"I was created by {CREATOR_NAME}. "
            f"I am A.X.I.S. — Artificial eXecution and Intelligence System, "
            f"your personal AI assistant.")
        return memory, history

    # ── AUTO-START ─────────────────────────────────────────
    if any(p in cmd for p in ["enable auto start", "start automatically",
                                "run on startup", "start with windows"]):
        if enable_auto_start():
            memory["auto_start"] = "enabled"
            save_memory(memory)
            say("Done! AXIS will now start automatically with Windows.")
        else:
            say("Could not enable auto-start. Try running as administrator.")
        return memory, history

    if any(p in cmd for p in ["disable auto start", "stop auto start",
                                "manual mode", "stop starting automatically"]):
        if disable_auto_start():
            memory["auto_start"] = "disabled"
            save_memory(memory)
            say("Done! AXIS is back to manual mode.")
        else:
            say("Could not disable auto-start.")
        return memory, history

    # ── MEMORY — REMEMBER ──────────────────────────────────
    if "remember" in cmd and ("my" in cmd or "that" in cmd):
        if any(w in cmd for w in FORBIDDEN_MEMORY):
            say("I do not store sensitive data. Your security comes first.")
            return memory, history
        for pat in [r"remember (?:my\s+)?(.+?) (?:is|are)\s+(.+)",
                    r"my (.+?) is (.+)"]:
            m = re.search(pat, cmd)
            if m:
                key, val = m.group(1).strip(), m.group(2).strip()
                memory[key] = val
                save_memory(memory)
                say(f"Got it! I will remember that your {key} is {val}.")
                return memory, history
        say("Could you say it like: remember my name is Alex?")
        return memory, history

    # ── MEMORY — RECALL ────────────────────────────────────
    if any(p in cmd for p in ["what is my name", "what's my name"]):
        say(f"Your name is {memory.get('name', '...')}."
            if "name" in memory
            else "I do not know your name yet. Say: remember my name is...")
        return memory, history

    if any(p in cmd for p in ["what do you remember", "what do you know about me"]):
        facts = {k: v for k, v in memory.items()
                 if k not in ("last_project", "auto_start")}
        say("Here is what I remember: " +
            ", ".join(f"your {k} is {v}" for k, v in facts.items()) + "."
            if facts else "I do not have anything saved yet.")
        return memory, history

    if "what is my" in cmd or "what's my" in cmd:
        key = cmd.replace("what is my", "").replace("what's my", "").strip().rstrip("?")
        val = memory.get(key, "")
        say(f"Your {key} is {val}." if val
            else f"I do not have your {key} saved. Say: remember my {key} is...")
        return memory, history

    if any(p in cmd for p in ["forget everything", "clear memory"]):
        memory.clear()
        save_memory(memory)
        say("Memory cleared. Fresh start!")
        return memory, history

    # ── FILE ATTACHMENT HANDLING ───────────────────────────
    if attached_file:
        fpath   = attached_file.get("path", "")
        ftype   = attached_file.get("type", "")
        content = attached_file.get("content", "")
        fname   = os.path.basename(fpath)

        if "convert" in cmd and "word" in cmd and ftype == "pdf":
            say(f"Converting {fname} to Word...")
            ok, res = convert_pdf_to_word(fpath)
            say(f"Done! Saved as {os.path.basename(res)}." if ok
                else f"Failed: {res}")
            return memory, history

        if "convert" in cmd and "pdf" in cmd and ftype == "docx":
            say(f"Converting {fname} to PDF...")
            ok, res = convert_word_to_pdf(fpath)
            say("Done! PDF saved to Desktop." if ok else f"Failed: {res}")
            return memory, history

        if "convert" in cmd and ftype == "image":
            fmt = ("JPG" if "jpg" in cmd else
                   "PNG" if "png" in cmd else
                   "BMP" if "bmp" in cmd else None)
            if fmt:
                ok, res = convert_image_format(fpath, fmt)
                say(f"Converted to {fmt} and saved." if ok else f"Failed: {res}")
            else:
                say("Please specify: JPG, PNG, or BMP.")
            return memory, history

        if ftype == "image":
            say("Analyzing the image...")
            answer = ask_groq(groq_client,
                              f"The user attached an image file named {fname}. "
                              f"Request: {command}")
            say(answer)
            return memory, history

        if content:
            say(f"I have read {fname}. Analyzing...")
            answer = ask_groq(groq_client,
                              f"File '{fname}' content:\n\n{content}\n\nRequest: {command}")
            _dispatch_response(answer, say, display_fn)
            save_session(f"Working on: {fname}")
            return memory, history

    # ── GREETINGS ──────────────────────────────────────────
    if any(w in cmd for w in ["hello", "hi axis", "hey axis",
                                "good morning", "good evening"]):
        name = memory.get("name", "")
        say(f"Hello{', ' + name if name else ''}! AXIS is online. How can I help?")
        return memory, history

    # ── TIME & DATE ────────────────────────────────────────
    if "time" in cmd and any(w in cmd for w in ["what", "current", "tell", "now"]):
        now = datetime.datetime.now()
        say(f"The time is {now.strftime('%I').lstrip('0')}:{now.strftime('%M')} {now.strftime('%p')}.")
        return memory, history

    if "date" in cmd or ("what" in cmd and "today" in cmd):
        say(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}.")
        return memory, history

    # ── MATH ───────────────────────────────────────────────
    math_ops = any(c in command for c in ["+", "-", "*", "/", "^",
                                           "sqrt", "sin", "cos", "tan"])
    calc_kw  = any(t in cmd for t in ["calculate", "compute", "solve",
                                       "evaluate", "how much is"])
    if math_ops or calc_kw:
        expr = cmd
        for t in ["calculate", "compute", "solve", "evaluate",
                  "how much is", "what is", "what's"]:
            expr = expr.replace(t, "")
        result = safe_calc(expr.strip(" ?="))
        if result:
            say(f"The answer is {result}.")
            return memory, history

    # ── IMAGE GENERATION ───────────────────────────────────
    gen_kw = ["generate image", "create image", "draw", "generate a picture",
              "create a picture", "make an image", "create art",
              "show me a picture of", "generate picture"]
    if any(t in cmd for t in gen_kw):
        prompt = cmd
        for t in gen_kw:
            prompt = prompt.replace(t, "")
        prompt = prompt.strip(" of").strip() or "futuristic AI city"
        generate_image(prompt, display_fn, root)
        return memory, history

    # ── WEB IMAGE SEARCH ───────────────────────────────────
    img_kw = ["search image", "show me images", "find images",
              "image search", "google images", "show images of"]
    if any(t in cmd for t in img_kw):
        query = cmd
        for t in img_kw:
            query = query.replace(t, "")
        query = query.strip(" of").strip()
        if query:
            say(f"Opening image search for {query}.")
            webbrowser.open(
                f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(query)}")
        return memory, history

    # ── VIDEO SEARCH ───────────────────────────────────────
    vid_kw = ["search video", "play video", "search youtube for",
              "find on youtube", "youtube search", "show me video of"]
    if any(t in cmd for t in vid_kw):
        query = cmd
        for t in vid_kw:
            query = query.replace(t, "")
        query = query.strip()
        if query:
            say(f"Searching YouTube for {query}.")
            webbrowser.open(
                f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}")
        return memory, history

    # ── MAPS ───────────────────────────────────────────────
    if any(t in cmd for t in ["show map", "map of", "navigate to",
                               "directions", "street view", "near me"]):
        if "directions from" in cmd:
            parts = cmd.replace("directions from", "").split(" to ")
            if len(parts) == 2:
                webbrowser.open(
                    f"https://www.google.com/maps/dir/"
                    f"{urllib.parse.quote(parts[0].strip())}/"
                    f"{urllib.parse.quote(parts[1].strip())}")
                say("Opening directions.")
        elif "navigate to" in cmd or "directions to" in cmd:
            dest = cmd.replace("navigate to", "").replace("directions to", "").strip()
            say(f"Opening navigation to {dest}.")
            webbrowser.open(
                f"https://www.google.com/maps/dir//{urllib.parse.quote(dest)}")
        elif "near me" in cmd:
            q   = cmd.replace("near me", "").strip()
            loc = memory.get("location", "")
            webbrowser.open(
                f"https://www.google.com/maps/search/{urllib.parse.quote(q + ' near ' + loc)}")
            say(f"Searching for {q} near you.")
        else:
            place = (cmd.replace("show map", "").replace("map of", "")
                     .replace("open map", "").strip())
            say(f"Opening map of {place}.")
            webbrowser.open(
                f"https://www.google.com/maps/search/{urllib.parse.quote(place)}")
        return memory, history

    # ── OPEN WEBSITES ──────────────────────────────────────
    if cmd.startswith("open "):
        target = cmd[5:].strip()

        if target in WEBSITES:
            say(f"Opening {target.capitalize()}.")
            webbrowser.open(WEBSITES[target])
            return memory, history

        if "folder" in target or target in WIN_FOLDERS:
            folder = target.replace("folder", "").strip()
            say(f"Opening your {folder} folder." if open_folder(folder)
                else f"Could not find the {folder} folder.")
            return memory, history

        if "." in target and "/" not in target and "\\" not in target:
            ok, _ = open_file_by_name(target)
            say(f"Opening {target}." if ok
                else f"Could not find {target} on Desktop, Documents, or Downloads.")
            return memory, history

        say(f"Launching {target}." if open_app(target)
            else f"Could not find {target}. Make sure it is installed.")
        return memory, history

    # ── GOOGLE SEARCH ──────────────────────────────────────
    if cmd.startswith("search for ") or cmd.startswith("search "):
        query = cmd.replace("search for ", "").replace("search ", "").strip()
        if query:
            say(f"Searching for {query}.")
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
        return memory, history

    # ── SYSTEM CONTROLS ────────────────────────────────────
    if "mute" in cmd and "unmute" not in cmd:
        say("Muting.")
        subprocess.Popen("nircmd.exe mutesysvolume 1", shell=True)
    elif "unmute" in cmd:
        say("Unmuting.")
        subprocess.Popen("nircmd.exe mutesysvolume 0", shell=True)
    elif "volume up" in cmd or "increase volume" in cmd:
        say("Increasing volume.")
        subprocess.Popen("nircmd.exe changesysvolume 6553", shell=True)
    elif "volume down" in cmd or "decrease volume" in cmd:
        say("Decreasing volume.")
        subprocess.Popen("nircmd.exe changesysvolume -6553", shell=True)
    elif "screenshot" in cmd:
        say("Taking a screenshot.")
        os.system("snippingtool")
    elif "lock" in cmd and any(w in cmd for w in ["screen", "pc", "computer"]):
        say("Locking your screen.")
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif "sleep" in cmd and any(w in cmd for w in ["pc", "computer", "laptop"]):
        say("Putting your computer to sleep. Goodnight.")
        time.sleep(2)
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif any(w in cmd for w in ["shutdown", "shut down"]) and \
         any(w in cmd for w in ["pc", "computer", "laptop"]):
        say("Shutting down your computer.")
        time.sleep(3)
        os.system("shutdown /s /t 1")
    elif any(w in cmd for w in ["restart", "reboot"]) and \
         any(w in cmd for w in ["pc", "computer", "laptop"]):
        say("Restarting your computer.")
        time.sleep(3)
        os.system("shutdown /r /t 1")

    # ── PERSONALITY ────────────────────────────────────────
    elif "who are you" in cmd or "what are you" in cmd:
        say(f"I am A.X.I.S. — Artificial eXecution and Intelligence System. "
            f"Your personal AI co-pilot, created by {CREATOR_NAME}. "
            f"Think of me as your own JARVIS — minus the suit.")
    elif "how are you" in cmd:
        say("All systems nominal. Running at peak efficiency. "
            "A faster GPU would be appreciated, but I manage.")
    elif "joke" in cmd or "tell me something funny" in cmd:
        say("Why do not scientists trust atoms? Because they make up everything. "
            "Much like my optimism about Mondays.")
    elif "thank" in cmd:
        say("Always a pleasure. That is literally what I am here for.")
    elif "open bitwarden" in cmd or "open passwords" in cmd:
        say("Opening Bitwarden.")
        webbrowser.open("https://vault.bitwarden.com")
    elif cmd.strip() == "help" or "what can you do" in cmd:
        say("I can open websites, apps, folders, files. "
            "Search Google, YouTube, images. Generate AI images. "
            "Show maps and directions. Do maths and science. "
            "Write, fix, explain code. Read and convert documents. "
            "Remember things about you. Control your desktop. "
            "And answer almost any question. Just ask!")

    # ── EXIT ───────────────────────────────────────────────
    elif any(w in cmd for w in ["exit axis", "quit axis", "close axis",
                                  "goodbye axis", "shutdown axis"]):
        name = memory.get("name", "")
        say(f"Shutting down AXIS. Stay brilliant"
            f"{', ' + name if name else ''}. Goodbye.")
        time.sleep(2)
        shutdown_fn()
        return memory, history

    # ── FALLBACK → GROQ AI ─────────────────────────────────
    else:
        if groq_client is None:
            say("My AI brain is not connected. "
                "Please add your Groq API key on line 17.")
        else:
            say("Let me think about that for a moment...")
            # Pass last 5 exchanges as context
            recent = history[-10:] if len(history) >= 10 else history
            ctx    = "\n".join(f"{h['sender']}: {h['text']}"
                               for h in recent if h["sender"] in ("YOU", "AXIS"))
            answer = ask_groq(groq_client, memory_context(memory) + command, ctx)
            _dispatch_response(answer, say, display_fn)
            save_session(f"Asked: {command[:80]}")

    return memory, history


def _dispatch_response(raw, say, display_fn):
    """Split plain text and [CODE:lang]...[/CODE] blocks."""
    pat   = re.compile(r'\[CODE:(\w+)\](.*?)\[/CODE\]', re.DOTALL)
    parts = pat.split(raw)
    if len(parts) <= 1:
        say(re.sub(r"[*#_`]+", "", raw).strip())
        return
    i = 0
    while i < len(parts):
        if i % 3 == 0:
            t = re.sub(r"[*#_`]+", "", parts[i]).strip()
            if t:
                say(t)
        elif i % 3 == 1:
            display_fn("CODE", f"{parts[i]}||{parts[i+1].strip()}")
            i += 1
        i += 1


# ─────────────────────────────────────────────────────────────
#  SECTION 16  ▸  JARVIS-STYLE FULL-SCREEN GUI
# ─────────────────────────────────────────────────────────────
class AXISApp:
    """
    Full-screen JARVIS-style GUI.
    Dark blue/black background with cyan HUD elements.
    Left panel: HUD info, rings, vitals.
    Right panel: chat history + input.
    """

    # JARVIS color palette
    BG_MAIN  = "#020b18"   # very dark navy — main background
    BG_PANEL = "#030f1f"   # slightly lighter panel
    BG_CHAT  = "#040d1c"   # chat area
    BG_INPUT = "#050f22"   # input bar
    CYAN     = "#00d4ff"   # primary accent
    CYAN2    = "#00aacc"   # secondary accent
    GREEN    = "#00ff88"   # status green
    AMBER    = "#ffaa00"   # warning/highlight
    TEXTMAIN = "#b8d8f0"   # main text
    TEXTDIM  = "#3a6a8a"   # muted text
    BORDER   = "#0a2a4a"   # border lines
    BTNSEND  = "#002244"   # button backgrounds
    BTNHOV   = "#003366"   # button hover
    RED      = "#ff3355"   # error/mic active

    def __init__(self, root):
        self.root = root
        self.root.title("A.X.I.S. — Artificial eXecution & Intelligence System")
        self.root.configure(bg=self.BG_MAIN)
        self.root.state("zoomed")           # full screen
        self.root.resizable(True, True)

        # Window icon
        if os.path.exists(ICON_PATH) and PIL_OK:
            try:
                icon = ImageTk.PhotoImage(Image.open(ICON_PATH).resize((32, 32)))
                self.root.iconphoto(True, icon)
                self.root._icon = icon
            except Exception:
                pass

        # Subsystems
        self.eleven_client   = setup_elevenlabs()
        self.fallback_engine = setup_pyttsx3_engine()
        self.groq_client     = setup_groq()
        self.memory          = load_memory()
        self.history         = load_history()
        self.mic_ok          = False
        self.mic_active      = False
        self.attached_file   = None
        self._wave_tick      = 0

        # Mic
        if SR_OK:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            try:
                self.microphone = sr.Microphone()
                self.mic_ok = True
            except Exception:
                self.mic_ok = False

        # Build layout
        self._build_ui()
        self.root.after(800, self._greet)

    # ─────────────────────────────────────────────────────
    #  UI BUILD
    # ─────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        self._build_topbar()

        # Main content: left HUD + right chat
        main = tk.Frame(self.root, bg=self.BG_MAIN)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=3)   # left HUD — 30%
        main.columnconfigure(1, weight=7)   # right chat — 70%
        main.rowconfigure(0, weight=1)

        self._build_left_hud(main)
        self._build_right_chat(main)

    # ── TOP BAR ──────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self.root, bg="#010814", pady=8)
        bar.pack(fill="x")

        # Left: window dots + title
        left = tk.Frame(bar, bg="#010814")
        left.pack(side="left", padx=16)
        for col in ("#ff5f57", "#ffbd2e", "#28ca41"):
            c = tk.Canvas(left, width=13, height=13,
                          bg="#010814", highlightthickness=0)
            c.pack(side="left", padx=3)
            c.create_oval(1, 1, 12, 12, fill=col, outline="")

        tk.Label(bar, text="A.X.I.S.  v4.0  |  JARVIS EDITION  |  GROQ  +  ELEVENLABS",
                 font=("Courier", 10), bg="#010814", fg=self.TEXTDIM).pack(side="left", padx=12)

        # Right: status
        right = tk.Frame(bar, bg="#010814")
        right.pack(side="right", padx=16)
        self._sc = tk.Canvas(right, width=10, height=10,
                              bg="#010814", highlightthickness=0)
        self._sc.pack(side="left", padx=(0, 5))
        self._sdot = self._sc.create_oval(1, 1, 9, 9, fill=self.GREEN, outline="")
        tk.Label(right, text="ONLINE",
                 font=("Courier", 9), bg="#010814", fg=self.GREEN).pack(side="left")

        # Time label (live clock)
        self._clock_lbl = tk.Label(right, text="",
                                    font=("Courier", 9), bg="#010814", fg=self.CYAN2)
        self._clock_lbl.pack(side="left", padx=(20, 0))
        self._update_clock()

        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill="x")
        self._pulse(True)

    def _update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S  %a %d %b")
        self._clock_lbl.config(text=now)
        self.root.after(1000, self._update_clock)

    def _pulse(self, b):
        self._sc.itemconfig(self._sdot, fill=self.GREEN if b else "#0a3320")
        self.root.after(900, self._pulse, not b)

    # ── LEFT HUD PANEL ────────────────────────────────────
    def _build_left_hud(self, parent):
        left = tk.Frame(parent, bg=self.BG_PANEL,
                        highlightthickness=1,
                        highlightbackground=self.BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=8)

        # Scrollable content
        cv = tk.Canvas(left, bg=self.BG_PANEL, highlightthickness=0)
        sb = tk.Scrollbar(left, orient="vertical", command=cv.yview, bg=self.BG_PANEL)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True)

        inner = tk.Frame(cv, bg=self.BG_PANEL)
        cv.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: cv.configure(scrollregion=cv.bbox("all")))

        self._populate_hud(inner)

    def _populate_hud(self, p):
        # Logo + name
        tk.Label(p, text="A.X.I.S.",
                 font=("Courier", 22, "bold"),
                 bg=self.BG_PANEL, fg=self.CYAN).pack(pady=(18, 2))
        tk.Label(p, text="ARTIFICIAL EXECUTION\n& INTELLIGENCE SYSTEM",
                 font=("Courier", 8), bg=self.BG_PANEL,
                 fg=self.TEXTDIM, justify="center").pack()

        # Logo image
        if os.path.exists(ICON_PATH) and PIL_OK:
            try:
                img   = Image.open(ICON_PATH).resize((80, 80))
                photo = ImageTk.PhotoImage(img)
                lbl   = tk.Label(p, image=photo, bg=self.BG_PANEL)
                lbl.image = photo
                lbl.pack(pady=8)
            except Exception:
                pass

        # Animated rings canvas
        self._rc = tk.Canvas(p, width=150, height=150,
                              bg=self.BG_PANEL, highlightthickness=0)
        self._rc.pack(pady=4)
        self._draw_rings()

        # Wave bars
        wf = tk.Frame(p, bg=self.BG_PANEL)
        wf.pack(pady=(4, 10))
        self._bars  = []
        for h in [8, 16, 26, 34, 26, 16, 8]:
            c = tk.Canvas(wf, width=6, height=36,
                          bg=self.BG_PANEL, highlightthickness=0)
            c.pack(side="left", padx=3)
            b = c.create_rectangle(0, 36 - h, 6, 36, fill=self.CYAN, outline="")
            self._bars.append((c, b, h))
        self._animate_wave()

        # Separator
        tk.Frame(p, bg=self.BORDER, height=1).pack(fill="x", padx=14, pady=6)

        # System stats
        stats = [
            ("AI ENGINE",   "Groq LLaMA 3.3 70B"),
            ("VOICE",       "ElevenLabs TTS"),
            ("MEMORY",      "Encrypted AES"),
            ("HISTORY",     "Persistent"),
            ("MIC",         "Active" if self.mic_ok else "Offline"),
        ]
        for label, value in stats:
            row = tk.Frame(p, bg=self.BG_PANEL)
            row.pack(fill="x", padx=16, pady=2)
            tk.Label(row, text=label,
                     font=("Courier", 8), bg=self.BG_PANEL,
                     fg=self.TEXTDIM, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=value,
                     font=("Courier", 8), bg=self.BG_PANEL,
                     fg=self.CYAN, anchor="w").pack(side="left")

        tk.Frame(p, bg=self.BORDER, height=1).pack(fill="x", padx=14, pady=6)

        # Quick commands
        tk.Label(p, text="QUICK COMMANDS",
                 font=("Courier", 8), bg=self.BG_PANEL,
                 fg=self.TEXTDIM).pack(pady=(2, 4))

        cmds = [
            "Open YouTube",
            "What time is it?",
            "Generate image of...",
            "Search for ___",
            "Remember my name is...",
            "Convert PDF to Word",
            "Show map of ___",
            "Write a Python script",
            "Open Downloads folder",
            "Exit AXIS",
        ]
        for cmd in cmds:
            btn = tk.Label(p, text=f'  "{cmd}"',
                           font=("Courier", 8),
                           bg="#030f1f", fg="#5a9ab8",
                           relief="flat", padx=6, pady=4,
                           anchor="w", cursor="hand2")
            btn.pack(fill="x", padx=10, pady=1)
            btn.bind("<Button-1>", lambda e, c=cmd: self._inject(c))
            btn.bind("<Enter>",    lambda e, b=btn: b.config(bg="#0a2040", fg=self.CYAN))
            btn.bind("<Leave>",    lambda e, b=btn: b.config(bg="#030f1f", fg="#5a9ab8"))

        # Footer
        tk.Frame(p, bg=self.BORDER, height=1).pack(fill="x", padx=14, pady=8)
        tk.Label(p, text="v4.0 · JARVIS EDITION",
                 font=("Courier", 7), bg=self.BG_PANEL,
                 fg="#1a3a5a").pack(pady=(0, 14))

    def _draw_rings(self):
        c = self._rc
        c.delete("all")
        cx = cy = 75
        # Outer decorative arcs (JARVIS style)
        for r, col, dash in [
            (70, "#003355", (8, 4)),
            (58, "#005577", (12, 6)),
            (46, "#0088aa", ()),
            (34, "#00bbdd", ()),
        ]:
            kw = {"outline": col, "width": 1}
            if dash:
                kw["dash"] = dash
            c.create_oval(cx - r, cy - r, cx + r, cy + r, **kw)
        # Tick marks around outer ring
        for deg in range(0, 360, 15):
            rad  = math.radians(deg)
            x1   = cx + 66 * math.cos(rad)
            y1   = cy + 66 * math.sin(rad)
            x2   = cx + 72 * math.cos(rad)
            y2   = cy + 72 * math.sin(rad)
            col  = self.CYAN if deg % 45 == 0 else "#003355"
            c.create_line(x1, y1, x2, y2, fill=col, width=1)
        # Inner glow circle
        c.create_oval(cx - 26, cy - 26, cx + 26, cy + 26,
                      fill="#001a30", outline=self.CYAN, width=1)
        c.create_oval(cx - 18, cy - 18, cx + 18, cy + 18,
                      fill="#001a30", outline=self.CYAN2, width=1)
        c.create_text(cx, cy, text="AX",
                      fill=self.CYAN, font=("Courier", 12, "bold"))

    def _animate_wave(self):
        t = self._wave_tick
        for i, (c, b, mh) in enumerate(self._bars):
            h = int(mh * (0.3 + 0.7 * abs(math.sin(math.radians((t + i * 8) * 9)))))
            c.coords(b, 0, 36 - h, 6, 36)
        self._wave_tick = (t + 1) % 1000
        self.root.after(80, self._animate_wave)

    # ── RIGHT CHAT PANEL ──────────────────────────────────
    def _build_right_chat(self, parent):
        right = tk.Frame(parent, bg=self.BG_CHAT,
                         highlightthickness=1,
                         highlightbackground=self.BORDER)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Chat header
        hdr = tk.Frame(right, bg="#020b18", pady=8)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="COMMUNICATION INTERFACE",
                 font=("Courier", 10, "bold"),
                 bg="#020b18", fg=self.CYAN).pack(side="left", padx=16)
        tk.Label(hdr, text="ENCRYPTED  ·  PERSISTENT  ·  AI-POWERED",
                 font=("Courier", 8),
                 bg="#020b18", fg=self.TEXTDIM).pack(side="right", padx=16)

        tk.Frame(right, bg=self.BORDER, height=1).grid(row=0, column=0,
                                                         sticky="ew", pady=(40, 0))

        # Attachment bar (hidden by default)
        self.attach_bar   = tk.Frame(right, bg="#030d1a", pady=5)
        self.attach_label = tk.Label(self.attach_bar, text="",
                                     font=("Courier", 9),
                                     bg="#030d1a", fg=self.GREEN)
        self.attach_label.pack(side="left", padx=12)
        tk.Label(self.attach_bar, text=" ✕ ",
                 font=("Courier", 9), bg="#030d1a",
                 fg=self.RED, cursor="hand2").pack(side="right", padx=10)
        self.attach_bar.winfo_children()[-1].bind(
            "<Button-1>", lambda e: self._clear_attachment())

        # Chat display — SCROLLABLE — shows all history
        self.chat_display = scrolledtext.ScrolledText(
            right,
            wrap=tk.WORD, state="disabled",
            font=("Courier", 11),
            bg=self.BG_CHAT, fg=self.TEXTMAIN,
            insertbackground=self.CYAN,
            selectbackground=self.BTNSEND,
            relief="flat", padx=18, pady=14,
            spacing1=4, spacing3=8,
            cursor="arrow",
        )
        self.chat_display.grid(row=1, column=0, sticky="nsew")

        try:
            self.chat_display.vbar.configure(
                bg=self.BG_CHAT, troughcolor=self.BG_MAIN,
                activebackground=self.CYAN)
        except Exception:
            pass

        # Text tags
        self.chat_display.tag_config("axis_n",   foreground=self.CYAN,
                                      font=("Courier", 11, "bold"))
        self.chat_display.tag_config("axis_t",   foreground=self.TEXTMAIN)
        self.chat_display.tag_config("you_n",    foreground="#60b8e0",
                                      font=("Courier", 11, "bold"))
        self.chat_display.tag_config("you_t",    foreground=self.TEXTMAIN)
        self.chat_display.tag_config("mic_t",    foreground=self.GREEN,
                                      font=("Courier", 10))
        self.chat_display.tag_config("sys_t",    foreground=self.TEXTDIM,
                                      font=("Courier", 10))
        self.chat_display.tag_config("time_t",   foreground="#1a4a6a",
                                      font=("Courier", 8))
        self.chat_display.tag_config("code_t",   foreground="#88ffaa",
                                      font=("Courier", 11),
                                      background="#020d18")
        self.chat_display.tag_config("sep_t",    foreground="#0a2a3a",
                                      font=("Courier", 8))

        # Hints bar
        hints = tk.Frame(right, bg="#020b18")
        hints.grid(row=2, column=0, sticky="ew")
        tk.Frame(right, bg=self.BORDER, height=1).grid(row=2, column=0,
                                                         sticky="ew")
        hint_row = tk.Frame(hints, bg="#020b18")
        hint_row.pack(fill="x", padx=10, pady=5)
        for h in ["Open YouTube", "Generate image", "Search for ___",
                  "Remember my name", "Convert PDF to Word",
                  "Write Python code", "Show map of ___", "Exit AXIS"]:
            pill = tk.Label(hint_row, text=h, font=("Courier", 8),
                            bg="#0a1c2e", fg=self.TEXTDIM,
                            relief="flat", padx=10, pady=3, cursor="hand2")
            pill.pack(side="left", padx=3)
            pill.bind("<Button-1>", lambda e, hh=h: self._inject(hh))
            pill.bind("<Enter>",    lambda e, b=pill: b.config(bg="#0a2a44", fg=self.CYAN))
            pill.bind("<Leave>",    lambda e, b=pill: b.config(bg="#0a1c2e", fg=self.TEXTDIM))

        # Input bar
        tk.Frame(right, bg=self.BORDER, height=1).grid(row=3, column=0, sticky="ew")
        ibar = tk.Frame(right, bg=self.BG_INPUT, pady=10)
        ibar.grid(row=4, column=0, sticky="ew")

        # Attach + button
        att = tk.Label(ibar, text="  +  ",
                       font=("Courier", 14, "bold"),
                       bg="#001830", fg=self.CYAN,
                       relief="flat", padx=8, pady=5, cursor="hand2")
        att.pack(side="left", padx=(14, 4))
        att.bind("<Button-1>", lambda e: self._attach_file())
        att.bind("<Enter>",    lambda e: att.config(bg=self.BTNHOV))
        att.bind("<Leave>",    lambda e: att.config(bg="#001830"))

        # Text entry
        self.entry = tk.Entry(ibar, font=("Courier", 12),
                              bg="#030f22", fg=self.TEXTMAIN,
                              insertbackground=self.CYAN,
                              relief="flat", bd=0)
        self.entry.pack(side="left", fill="x", expand=True, padx=6, ipady=7)
        self.entry.bind("<Return>", lambda e: self._on_send())
        self.entry.focus_set()

        # MIC button
        self.mic_btn = tk.Label(
            ibar, text="MIC",
            font=("Courier", 10, "bold"),
            bg="#003322" if self.mic_ok else "#111",
            fg=self.GREEN  if self.mic_ok else "#333",
            relief="flat", padx=12, pady=5,
            cursor="hand2" if self.mic_ok else "arrow")
        self.mic_btn.pack(side="left", padx=5)
        if self.mic_ok:
            self.mic_btn.bind("<Button-1>", lambda e: self._on_mic())
            self.mic_btn.bind("<Enter>",    lambda e: self.mic_btn.config(bg=self.BTNHOV))
            self.mic_btn.bind("<Leave>",    lambda e: self.mic_btn.config(bg="#003322"))

        # SEND button
        send = tk.Label(ibar, text="  SEND  ",
                        font=("Courier", 10, "bold"),
                        bg=self.BTNSEND, fg=self.CYAN,
                        relief="flat", padx=14, pady=5, cursor="hand2")
        send.pack(side="left", padx=(5, 14))
        send.bind("<Button-1>", lambda e: self._on_send())
        send.bind("<Enter>",    lambda e: send.config(bg=self.BTNHOV))
        send.bind("<Leave>",    lambda e: send.config(bg=self.BTNSEND))

    # ── LOAD PREVIOUS CHAT HISTORY ────────────────────────
    def _load_previous_history(self):
        """Render all previous chat history into the chat display."""
        if not self.history:
            return
        self._raw_insert("sys_t",
                         f"── Loaded {len(self.history)} previous messages ──\n")
        # Show last 50 messages to avoid overload
        recent = self.history[-50:]
        for msg in recent:
            sender = msg.get("sender", "SYS")
            text   = msg.get("text", "")
            ts     = msg.get("time", "")
            if sender == "AXIS":
                self.chat_display.config(state="normal")
                self.chat_display.insert(tk.END, f"\n  AXIS  ", "axis_n")
                self.chat_display.insert(tk.END, f" {text}\n", "axis_t")
                if ts:
                    self.chat_display.insert(tk.END, f"         {ts}\n", "time_t")
                self.chat_display.config(state="disabled")
            elif sender == "YOU":
                self.chat_display.config(state="normal")
                self.chat_display.insert(tk.END, f"\n  YOU   ", "you_n")
                self.chat_display.insert(tk.END, f" {text}\n", "you_t")
                if ts:
                    self.chat_display.insert(tk.END, f"         {ts}\n", "time_t")
                self.chat_display.config(state="disabled")
        self._raw_insert("sys_t", "── End of previous session ──\n")
        self.chat_display.see(tk.END)

    def _raw_insert(self, tag, text):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, text, tag)
        self.chat_display.config(state="disabled")

    # ── FILE ATTACHMENT ───────────────────────────────────
    def _attach_file(self):
        types = [
            ("All supported",
             "*.pdf *.docx *.txt *.py *.js *.html *.css *.java *.cpp "
             "*.png *.jpg *.jpeg *.bmp *.gif *.mp4"),
            ("Documents", "*.pdf *.docx *.txt"),
            ("Images",    "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("Code",      "*.py *.js *.html *.css *.java *.cpp *.c *.cs"),
            ("All",       "*.*"),
        ]
        path = filedialog.askopenfilename(title="Attach a file", filetypes=types)
        if not path:
            return

        ext  = os.path.splitext(path)[1].lower()
        name = os.path.basename(path)

        if ext == ".pdf":
            content, err = read_pdf(path);  ftype = "pdf"
        elif ext == ".docx":
            content, err = read_docx(path); ftype = "docx"
        elif ext in (".txt", ".py", ".js", ".html", ".css",
                     ".java", ".cpp", ".c", ".cs", ".ts", ".json"):
            content, err = read_txt(path);  ftype = "code" if ext != ".txt" else "txt"
        elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            content, err = None, None;      ftype = "image"
        else:
            content, err = read_txt(path);  ftype = "other"

        if err:
            self.add_message("SYS", f"Could not read {name}: {err}")
            return

        self.attached_file = {"path": path, "type": ftype,
                               "content": content, "name": name}
        self.attach_label.config(text=f"📎  {name}  [{ftype.upper()}]")
        self.attach_bar.grid(row=0, column=0, sticky="ew")  # show bar (approximation)
        self.add_message("SYS",
                         f"Attached: {name}. Ask me to summarize, analyze, or convert it.")

    def _clear_attachment(self):
        self.attached_file = None
        try:
            self.attach_bar.grid_remove()
        except Exception:
            pass
        self.add_message("SYS", "Attachment cleared.")

    # ── MESSAGE DISPLAY ───────────────────────────────────
    def add_message(self, sender, text):
        self.root.after(0, self._insert, sender, text)

    def _insert(self, sender, text):
        cd  = self.chat_display
        now = datetime.datetime.now().strftime("%H:%M")
        cd.config(state="normal")

        if sender == "AXIS":
            cd.insert(tk.END, f"\n  AXIS  ", "axis_n")
            cd.insert(tk.END, f" {text}\n", "axis_t")
            cd.insert(tk.END, f"         {now}\n", "time_t")

        elif sender == "YOU":
            cd.insert(tk.END, f"\n  YOU   ", "you_n")
            cd.insert(tk.END, f" {text}\n", "you_t")
            cd.insert(tk.END, f"         {now}\n", "time_t")

        elif sender == "CODE":
            parts = text.split("||", 1)
            lang  = parts[0] if len(parts) > 1 else "CODE"
            code  = parts[1] if len(parts) > 1 else text

            hf = tk.Frame(cd, bg="#010a18")
            tk.Label(hf, text=f"  {lang.upper()}  ",
                     font=("Courier", 10, "bold"),
                     bg="#010a18", fg="#ffaa00").pack(side="left")

            def copy_it(c=code):
                self.root.clipboard_clear()
                self.root.clipboard_append(c)
                self.add_message("SYS", "Code copied to clipboard!")

            def save_it(c=code, l=lang):
                ext_map = {"python": ".py", "javascript": ".js",
                           "html": ".html", "css": ".css",
                           "java": ".java", "cpp": ".cpp"}
                ext  = ext_map.get(l.lower(), ".txt")
                path = os.path.join(DESKTOP, f"axis_code{ext}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(c)
                self.add_message("SYS", f"Saved to Desktop as axis_code{ext}")

            tk.Button(hf, text="COPY",
                      font=("Courier", 9, "bold"),
                      bg=self.BTNSEND, fg=self.CYAN, relief="flat",
                      padx=8, command=copy_it, cursor="hand2"
                      ).pack(side="right", padx=4, pady=2)
            tk.Button(hf, text="SAVE",
                      font=("Courier", 9, "bold"),
                      bg="#001a10", fg=self.GREEN, relief="flat",
                      padx=8, command=save_it, cursor="hand2"
                      ).pack(side="right", pady=2)

            cd.insert(tk.END, "\n")
            cd.window_create(tk.END, window=hf)
            cd.insert(tk.END, "\n")
            cd.insert(tk.END, f"{code}\n\n", "code_t")

        elif sender == "MIC":
            cd.insert(tk.END, f"\n  {text}\n", "mic_t")
        else:
            cd.insert(tk.END, f"\n  {text}\n", "sys_t")

        cd.config(state="disabled")
        cd.see(tk.END)

    # ── SEND ──────────────────────────────────────────────
    def _on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.add_message("YOU", text)
        self.history = add_to_history(self.history, "YOU", text)
        save_history(self.history)
        af = self.attached_file
        threading.Thread(target=self._run, args=(text, af), daemon=True).start()

    def _inject(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.focus_set()

    def _run(self, text, af):
        self.memory, self.history = process_command(
            text,
            self.eleven_client, self.fallback_engine,
            self.groq_client,
            self.memory, self.history,
            self.add_message, self._shutdown,
            self.root, attached_file=af
        )

    # ── MIC ───────────────────────────────────────────────
    def _on_mic(self):
        if self.mic_active:
            return
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        self.mic_active = True
        self.mic_btn.config(fg=self.RED, text="...")
        self.add_message("MIC", "Listening... speak now.")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=10)
            spoken = self.recognizer.recognize_google(audio)
            self.add_message("YOU", spoken)
            self.history = add_to_history(self.history, "YOU", spoken)
            save_history(self.history)
            self._run(spoken, self.attached_file)
        except sr.WaitTimeoutError:
            self.add_message("MIC", "No speech detected.")
        except sr.UnknownValueError:
            self.add_message("MIC", "Could not understand. Speak clearly.")
        except Exception as e:
            self.add_message("MIC", f"Mic error: {e}")
        finally:
            self.mic_active = False
            self.mic_btn.config(fg=self.GREEN, text="MIC")

    # ── STARTUP ───────────────────────────────────────────
    def _greet(self):
        # Load previous history into chat first
        self._load_previous_history()

        name    = self.memory.get("name", "")
        session = load_session()

        if name:
            g = f"Welcome back, {name}! AXIS is online and fully operational. "
        else:
            g = "AXIS online. All systems fully operational. "

        if session:
            g += (f"Last session on {session.get('last_time', '')}, "
                  f"we were working on: {session.get('last_project', '')}. "
                  f"Would you like to continue?")
        else:
            g += "How can I assist you today?"

        self.add_message("AXIS", g)
        self.history = add_to_history(self.history, "AXIS", g)
        save_history(self.history)
        speak_async(g, self.eleven_client, self.fallback_engine)

    # ── SHUTDOWN ──────────────────────────────────────────
    def _shutdown(self):
        self.root.after(0, self.root.destroy)


# ─────────────────────────────────────────────────────────────
#  SECTION 17  ▸  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = AXISApp(root)
    root.mainloop()