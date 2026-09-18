import os
import time
import tempfile
import threading
import ctypes
import tkinter as tk
from google import genai
from PIL import Image
import mss
import keyboard

# get monitor size
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# place Gemini api key here, get one for free at aistudio.google.com
API_KEYS = [
    "AQ.Ab8RN6example_APIkey1",  #keep track of which account has which key
    "AQ.Ab8RN6example_APIkey2",  #Exampleaccount123
    "AQ.Ab8RN6example_APIkey3"   #TestAccount456
]

current_key_index = 0

def get_client(index):
    return genai.Client(api_key=API_KEYS[index])

temp_dir = tempfile.gettempdir()
screenshot_path = os.path.join(temp_dir, "sara_screenshot.png")

# overlay
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000  # Window will NEVER steal focus when shown
WS_EX_TRANSPARENT = 0x00000020  # Mouse clicks pass directly through

class FullScreenGlow:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        self.top.attributes("-alpha", 0.0)

        # Dynamic screen resolution fit
        sw = self.top.winfo_screenwidth()
        sh = self.top.winfo_screenheight()
        self.top.geometry(f"{sw}x{sh}+0+0")

        # Transparent color key to make the inside hollow and click-through
        TRANSPARENT_COLOR = "#000001"
        self.top.config(bg=TRANSPARENT_COLOR)
        self.top.attributes("-transparentcolor", TRANSPARENT_COLOR)

        # Canvas to draw the glowing border around the entire screen edges
        self.canvas = tk.Canvas(self.top, bg=TRANSPARENT_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        colors = ["#9988ff", "#8877ee", "#7766dd"]
        for i, color in enumerate(colors):
            offset = i * 6
            width = 18 - (i * 5)
            self.canvas.create_rectangle(
                offset, offset, sw - offset, sh - offset, 
                outline=color, width=max(2, width)
            )
        
        self.top.update()
        hwnd = ctypes.windll.user32.GetParent(self.top.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TRANSPARENT)

        self.top.withdraw()

    def flash(self):
        """Trigger the smooth fade-in and extended fade-out aura effect."""
        self.top.attributes("-alpha", 0.0)
        self.top.deiconify()
        self._fade_in(0.0)

    def _fade_in(self, alpha):
        if alpha < 0.9:
            alpha += 0.1
            self.top.attributes("-alpha", min(0.9, alpha))
            self.top.after(30, lambda: self._fade_in(alpha))
        else:

            self.top.after(1000, lambda: self._fade_out(alpha))

    def _fade_out(self, alpha):
        if alpha > 0.0:
            alpha -= 0.08
            self.top.attributes("-alpha", max(0.0, alpha))
            self.top.after(35, lambda: self._fade_out(alpha))
        else:
            self.top.withdraw()


class StealthOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9)
        self.root.withdraw()

        sw = self.root.winfo_screenwidth()
        overlay_width = max(400, min(560, int(sw * 0.32)))
        overlay_height = 280
        x_pos = max(10, sw - overlay_width - 30)
        y_pos = 40
        self.root.geometry(f"{overlay_width}x{overlay_height}+{x_pos}+{y_pos}")

        frame = tk.Frame(self.root, bg="#18181b", padx=16, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)

        header_lbl = tk.Label(
            frame,
            text="S.A.R.A",
            fg="#8877ff",
            bg="#18181b",
            font=("Arial", 10, "bold"),
        )
        header_lbl.pack(anchor="w", pady=(0, 8))

        self.text_box = tk.Text(
            frame,
            wrap=tk.WORD,
            bg="#27272a",
            fg="#f4f4f5",
            insertbackground="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            height=8,
        )
        self.text_box.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        # Apply Windows API flags to prevent focus stealing & make click-through
        self.root.update()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TRANSPARENT)

        # Corner smoothing
        hrgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, overlay_width, overlay_height, 20, 20)
        ctypes.windll.user32.SetWindowRgn(hwnd, hrgn, True)

        self.dismiss_timer = None
        self.glow_overlay = FullScreenGlow(self.root)

    def start_processing(self):
        """Thread-safe call to refresh textbox, set text, and flash screen glow."""
        self.root.after(0, self._show_processing_ui)

    def _show_processing_ui(self):
        if self.dismiss_timer:
            self.root.after_cancel(self.dismiss_timer)

        # Refresh textbox and set processing message
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, "processing, this might take 10s")
        self.text_box.config(state=tk.DISABLED)

        self.root.deiconify()
        self.glow_overlay.flash()

    def display_text(self, answer_text):
        """Thread-safe call to update overlay text with final results."""
        self.root.after(0, self._update_ui, answer_text)

    def _update_ui(self, answer_text):
        if self.dismiss_timer:
            self.root.after_cancel(self.dismiss_timer)

        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, answer_text)
        self.text_box.config(state=tk.DISABLED)
        self.root.deiconify()
        self.dismiss_timer = self.root.after(8000, self.root.withdraw)


# Initialize overlay instance on main thread
overlay = StealthOverlay()

def solve_quiz():
    global current_key_index
    print("\n[+] Hotkey pressed! Capturing screen...")
    try:
        time.sleep(0.2)

        with mss.MSS() as sct:
            sct.shot(output=screenshot_path)
        overlay.start_processing()
        img = Image.open(screenshot_path)

        # Instructions to ask gemini
        prompt = (
            "Look at this screenshot of a quiz question. "
            "Give me ONLY the correct answer option and a brief 1-sentence explanation. "
            "Do NOT use markdown headers, do NOT list out wrong options, and keep it extremely short and clean."
        )

        attempts = 0
        max_attempts = len(API_KEYS)
        answer = None

        while attempts < max_attempts:
            active_client = get_client(current_key_index)
            try:
                print(f"[+] Asking Gemini (using Key #{current_key_index + 1})...")
                response = active_client.models.generate_content(
                    model="gemini-3.6-flash", contents=[img, prompt]
                )
                answer = response.text.strip()
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                break
                
            except Exception as e:
                print(f"[!] Key #{current_key_index + 1} failed: {e}")
                attempts += 1
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                if attempts >= max_attempts:
                    raise Exception("All provided API keys have failed.")

        print("\n--- Success! ---")
        print(answer)

        overlay.display_text(answer)

    except Exception as e:
        print(f"[ERROR]: {e}")
        overlay.display_text(f"[ERROR]: {e}")

print("==================================================")
print(" S.A.R.A  1.5  is running in the background.")
print(" Press [F9] to capture & solve.")
print(" Press [Ctrl + Shift + Q] to quit.")
print("==================================================")

keyboard.add_hotkey("f9", lambda: threading.Thread(target=solve_quiz, daemon=True).start())

# Run Tkinter main event loop on the main thread
def check_exit():
    if keyboard.is_pressed("ctrl+shift+q"):
        overlay.root.destroy()
        os._exit(0)
    overlay.root.after(100, check_exit)

overlay.root.after(100, check_exit)
overlay.root.mainloop()