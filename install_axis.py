"""
╔══════════════════════════════════════════════════════════════════════════╗
║              A.X.I.S. — Desktop Installer                               ║
║         Run this ONCE to create your desktop icon                       ║
╚══════════════════════════════════════════════════════════════════════════╝

HOW TO USE:
  1. Place this file in the SAME folder as axis_assistant.py and AXIS_AI.png
  2. Run:  python install_axis.py
  3. Done! Double-click the AXIS icon on your Desktop forever.
"""

import os
import sys
import subprocess

HOME       = os.path.expanduser("~")
DESKTOP    = os.path.join(HOME, "Desktop")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_FILE  = os.path.join(SCRIPT_DIR, "axis_assistant.py")
ICON_PNG   = os.path.join(SCRIPT_DIR, "AXIS_AI.png")
ICON_ICO   = os.path.join(SCRIPT_DIR, "AXIS_AI.ico")


def install_packages():
    """Auto-install all required packages."""
    packages = [
        "speechrecognition", "pyttsx3", "pyaudio",
        "google-generativeai", "pillow", "requests",
        "cryptography", "pymupdf", "python-docx", "pdf2docx",
    ]
    print("\n[AXIS Installer] Installing required packages...\n")
    for pkg in packages:
        print(f"  Installing {pkg}...")
        subprocess.call(
            [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    print("\n  All packages installed!\n")


def convert_png_to_ico():
    """Convert AXIS_AI.png to AXIS_AI.ico for Windows shortcut icon."""
    if not os.path.exists(ICON_PNG):
        print(f"  [Warning] AXIS_AI.png not found at {ICON_PNG}")
        print("  Place AXIS_AI.png in the same folder for the custom icon.")
        return None
    try:
        from PIL import Image
        img = Image.open(ICON_PNG)
        # Create multi-size ICO (Windows needs multiple sizes)
        img.save(ICON_ICO, format="ICO",
                 sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
        print(f"  Icon converted: AXIS_AI.ico")
        return ICON_ICO
    except ImportError:
        print("  [Warning] Pillow not installed. pip install pillow")
        return None
    except Exception as e:
        print(f"  [Warning] Icon conversion failed: {e}")
        return None


def create_desktop_shortcut(ico_path):
    """Create a Windows .lnk shortcut on the Desktop."""
    try:
        import winreg
    except ImportError:
        print("  [Warning] winreg not available — Windows only feature.")
        return False

    try:
        # Use pythonw.exe so no terminal window flashes on launch
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pythonw):
            pythonw = sys.executable

        shortcut_path = os.path.join(DESKTOP, "A.X.I.S..lnk")

        # Use PowerShell to create the .lnk file
        ico_arg = f'$Shortcut.IconLocation = "{ico_path}"' if ico_path else ""
        ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{pythonw}"
$Shortcut.Arguments = '"{MAIN_FILE}"'
$Shortcut.WorkingDirectory = "{SCRIPT_DIR}"
$Shortcut.Description = "A.X.I.S. - Artificial eXecution and Intelligence System"
{ico_arg}
$Shortcut.Save()
"""
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  Desktop shortcut created: A.X.I.S..lnk")
            return True
        else:
            print(f"  [Warning] Shortcut creation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"  [Warning] Shortcut creation error: {e}")
        return False


def create_batch_launcher():
    """
    Create a .bat file as a backup launcher in case the .lnk fails.
    User can also pin this to taskbar.
    """
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    bat_path = os.path.join(DESKTOP, "Launch AXIS.bat")
    bat_content = f'@echo off\nstart "" "{pythonw}" "{MAIN_FILE}"\n'
    try:
        with open(bat_path, "w") as f:
            f.write(bat_content)
        print(f"  Batch launcher created: 'Launch AXIS.bat' on Desktop")
        return bat_path
    except Exception as e:
        print(f"  [Warning] Batch launcher failed: {e}")
        return None


def pin_to_taskbar_instructions():
    """Print instructions for taskbar pinning (can't be done programmatically)."""
    print("\n  HOW TO PIN TO TASKBAR:")
    print("  ─────────────────────────────────────────────────")
    print("  1. Find 'A.X.I.S.' shortcut on your Desktop")
    print("  2. Right-click it")
    print("  3. Click 'Pin to taskbar'")
    print("  That's it! AXIS will appear in your taskbar forever.")
    print("  ─────────────────────────────────────────────────\n")


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║        A.X.I.S. Desktop Installer               ║")
    print("╚══════════════════════════════════════════════════╝\n")

    if not os.path.exists(MAIN_FILE):
        print(f"  [ERROR] axis_assistant.py not found at:\n  {MAIN_FILE}")
        print("\n  Make sure install_axis.py and axis_assistant.py")
        print("  are in the SAME folder, then run again.")
        input("\n  Press Enter to exit...")
        return

    print(f"  Main script found: {MAIN_FILE}")
    print(f"  Installing to Desktop: {DESKTOP}\n")

    # Step 1 — Install packages
    answer = input("  Install/update all required Python packages? (y/n): ").strip().lower()
    if answer == "y":
        install_packages()

    # Step 2 — Convert icon
    print("\n[AXIS Installer] Converting icon...")
    ico_path = convert_png_to_ico()

    # Step 3 — Desktop shortcut
    print("\n[AXIS Installer] Creating desktop shortcut...")
    shortcut_ok = create_desktop_shortcut(ico_path)

    # Step 4 — Batch launcher backup
    print("\n[AXIS Installer] Creating batch launcher backup...")
    create_batch_launcher()

    # Step 5 — Taskbar instructions
    pin_to_taskbar_instructions()

    # Done!
    print("╔══════════════════════════════════════════════════╗")
    if shortcut_ok:
        print("║  ✅  Installation complete!                      ║")
        print("║                                                  ║")
        print("║  Double-click 'A.X.I.S.' on your Desktop        ║")
        print("║  to launch AXIS anytime — no terminal needed!   ║")
    else:
        print("║  ⚠️   Shortcut failed — use 'Launch AXIS.bat'    ║")
        print("║      on your Desktop to start AXIS instead.     ║")
    print("╚══════════════════════════════════════════════════╝\n")

    input("  Press Enter to exit the installer...")


if __name__ == "__main__":
    main()