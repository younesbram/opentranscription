import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
import pyaudio
import wave
import threading
import tempfile
import os
import webbrowser
from openai import OpenAI
import whisper
import keyboard

class OverlayWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.7)
        self.geometry("400x100+200+200")

        self.text_widget = scrolledtext.ScrolledText(self, wrap=tk.WORD, bg="black", fg="white")
        self.text_widget.pack(expand=True, fill='both', padx=10, pady=10)
        self.text_widget.config(state=tk.DISABLED)

        self.bind("<Control-Button-1>", self.start_move)
        self.bind("<Control-B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def update_text(self, text):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text + " ")
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self.adjust_size()

    def adjust_size(self):
        content_height = self.text_widget.count('1.0', tk.END, 'displaylines')[0]
        new_height = min(max(100, content_height * 20), 400)  # Min 100px, Max 400px
        self.geometry(f"400x{new_height}")

class LiveTranscriptionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Live Transcription Settings")
        self.master.geometry("400x550")

        self.overlay = None
        self.is_transcribing = False
        self.openai_client = None
        self.local_model = None
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.master, text="OpenAI API Key:").pack(pady=5)
        self.api_key_entry = tk.Entry(self.master, show="*")
        self.api_key_entry.pack(pady=5)

        self.use_local_model = tk.BooleanVar()
        self.local_model_check = tk.Checkbutton(self.master, text="Use Local Model", variable=self.use_local_model)
        self.local_model_check.pack(pady=5)
        self.create_tooltip(self.local_model_check, "Uses local Whisper model if checked, OpenAI API otherwise.")

        self.auto_translate = tk.BooleanVar()
        tk.Checkbutton(self.master, text="Auto-translate to English", variable=self.auto_translate).pack(pady=5)

        self.save_session = tk.BooleanVar()
        tk.Checkbutton(self.master, text="Save session to file", variable=self.save_session).pack(pady=5)

        tk.Label(self.master, text="Font Size:").pack(pady=5)
        self.font_size_slider = ttk.Scale(self.master, from_=8, to=24, orient="horizontal")
        self.font_size_slider.set(12)
        self.font_size_slider.pack(pady=5)

        tk.Label(self.master, text="Overlay Opacity:").pack(pady=5)
        self.opacity_slider = ttk.Scale(self.master, from_=0.1, to=1.0, orient="horizontal")
        self.opacity_slider.set(0.7)
        self.opacity_slider.pack(pady=5)

        tk.Label(self.master, text="Toggle Overlay Hotkey:").pack(pady=5)
        self.hotkey_entry = tk.Entry(self.master)
        self.hotkey_entry.insert(0, "ctrl+shift+h")
        self.hotkey_entry.pack(pady=5)

        self.start_button = tk.Button(self.master, text="Start Live Transcription", command=self.toggle_transcription)
        self.start_button.pack(pady=10)

        twitter_link = tk.Label(self.master, text="Report bugs on Twitter", fg="blue", cursor="hand2")
        twitter_link.pack(pady=5)
        twitter_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://x.com/didntdrinkwater"))

        project_link = tk.Label(self.master, text="View Project on GitHub", fg="blue", cursor="hand2")
        project_link.pack(pady=5)
        project_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/younesbram/opentranscription"))

    def create_tooltip(self, widget, text):
        def enter(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1).pack()
            widget.tooltip = tooltip

        def leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def toggle_transcription(self):
        if self.is_transcribing:
            self.stop_transcription()
        else:
            self.start_transcription()

    def start_transcription(self):
        if self.use_local_model.get():
            try:
                self.local_model = whisper.load_model("base")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load local model: {e}")
                return
        else:
            api_key = self.api_key_entry.get()
            if not api_key:
                messagebox.showerror("Error", "Please enter your OpenAI API key.")
                return
            os.environ["OPENAI_API_KEY"] = api_key
            self.openai_client = OpenAI()

        self.overlay = OverlayWindow(self.master)
        font_size = int(self.font_size_slider.get())
        self.overlay.text_widget.config(font=("Arial", font_size))
        opacity = self.opacity_slider.get()
        self.overlay.attributes("-alpha", opacity)

        self.is_transcribing = True
        self.start_button.config(text="Stop Live Transcription")
        self.master.iconify()

        hotkey = self.hotkey_entry.get()
        keyboard.add_hotkey(hotkey, self.toggle_overlay_visibility)

        if self.save_session.get():
            self.session_file = open("transcription_session.txt", "w", encoding="utf-8")

        threading.Thread(target=self.transcribe_audio, daemon=True).start()

    def stop_transcription(self):
        self.is_transcribing = False
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        self.start_button.config(text="Start Live Transcription")
        self.master.deiconify()

        hotkey = self.hotkey_entry.get()
        keyboard.remove_hotkey(hotkey)

        if hasattr(self, 'session_file'):
            self.session_file.close()

    def toggle_overlay_visibility(self):
        if self.overlay:
            if self.overlay.winfo_viewable():
                self.overlay.withdraw()
            else:
                self.overlay.deiconify()

    def transcribe_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = 2  # Reduced for more frequent updates

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        while self.is_transcribing:
            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
                wf = wave.open(temp_audio_file.name, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

            try:
                if self.local_model:
                    if self.auto_translate.get():
                        result = self.local_model.transcribe(temp_audio_file.name, task="translate")
                    else:
                        result = self.local_model.transcribe(temp_audio_file.name)
                    transcription = result["text"]
                else:
                    with open(temp_audio_file.name, "rb") as audio_file:
                        if self.auto_translate.get():
                            transcription = self.openai_client.audio.translations.create(
                                model="whisper-1", 
                                file=audio_file
                            ).text
                        else:
                            transcription = self.openai_client.audio.transcriptions.create(
                                model="whisper-1", 
                                file=audio_file
                            ).text

                if self.overlay:
                    self.overlay.update_text(transcription)

                if self.save_session.get():
                    self.session_file.write(transcription + "\n")
                    self.session_file.flush()

            except Exception as e:
                print(f"Transcription error: {e}")
                if self.local_model:
                    messagebox.showerror("Error", f"Local model failed: {e}\nSwitching to OpenAI API.")
                    self.local_model = None
                    self.use_local_model.set(False)

            os.unlink(temp_audio_file.name)

        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveTranscriptionApp(root)
    root.mainloop()
