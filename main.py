import cv2
import tkinter as tk
from tkinter import ttk, StringVar, messagebox
from PIL import Image, ImageTk
import warnings

from core import HandDetector, SignLanguageModel, SentenceBuilder
from utils import extract_hand_features
from config import SUPPORTED_LANGUAGES, DEFAULT_LANG, HAND_CONNECTIONS

warnings.filterwarnings("ignore", category=UserWarning)

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Language to Speech Translator")
        self.root.geometry("1400x750")
        self.root.configure(bg="#1e1e2e")  # Base dark modern theme
        self.root.resizable(False, False)

        # backend components
        self.detector = HandDetector()
        self.sl_model = SignLanguageModel(DEFAULT_LANG)
        self.builder = SentenceBuilder()

        # State
        self.is_paused = False

        self.setup_ui()

        # Camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Start Processing
        self.on_language_change() # Trigger initial model validity check UI rendering
        self.process_frame()

    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="Sign Language Translator", font=("Segoe UI", 32, "bold"), fg="#cdd6f4", bg="#1e1e2e")
        header.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Main Layout container
        main_container = tk.Frame(self.root, bg="#1e1e2e")
        main_container.grid(row=1, column=0, columnspan=2, padx=40, pady=10, sticky="nsew")
        self.root.columnconfigure(0, weight=1)

        # Video Frame (Left side)
        video_bg = tk.Frame(main_container, bg="#313244", bd=0, relief="flat", width=640, height=480)
        video_bg.pack(side=tk.LEFT, padx=(0, 30), pady=10)
        video_bg.pack_propagate(False)
        self.video_label = tk.Label(video_bg, bg="#11111b")
        self.video_label.pack(expand=True, fill="both", padx=5, pady=5)

        # Content Frame (Right side)
        content_frame = tk.Frame(main_container, bg="#181825", bd=0, highlightbackground="#313244", highlightthickness=2)
        content_frame.pack(side=tk.RIGHT, fill="both", expand=True, pady=10)

        # Language Selector
        lang_frame = tk.Frame(content_frame, bg="#181825")
        lang_frame.pack(fill="x", padx=30, pady=(30, 20))
        tk.Label(lang_frame, text="Translation Language Model:", font=("Segoe UI", 16, "bold"), fg="#bac2de", bg="#181825").pack(anchor="w", pady=(0, 5))
        
        self.lang_var = StringVar(value=DEFAULT_LANG)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground="#313244", background="#45475a", foreground="#cdd6f4", font=("Segoe UI", 14), padding=5)
        
        self.lang_dropdown = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=list(SUPPORTED_LANGUAGES.keys()), state="readonly", font=("Segoe UI", 14), width=30)
        self.lang_dropdown.pack(anchor="w")
        self.lang_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)

        # Text Displays
        disp_frame = tk.Frame(content_frame, bg="#181825")
        disp_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Real-time Prediction and Progress
        rt_frame = tk.Frame(disp_frame, bg="#181825")
        rt_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(rt_frame, text="Live Prediction:", font=("Segoe UI", 12), fg="#a6adc8", bg="#181825").pack(side=tk.LEFT)
        self.lbl_live = tk.Label(rt_frame, text="-", font=("Segoe UI", 16, "bold"), fg="#f38ba8", bg="#181825")
        self.lbl_live.pack(side=tk.LEFT, padx=(10, 20))

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(rt_frame, variable=self.progress_var, maximum=1.0, length=200, style="TProgressbar")
        self.progress.pack(side=tk.LEFT, fill="none", pady=(2, 0))

        style.configure("TProgressbar", thickness=15, background="#a6e3a1", troughcolor="#313244", bordercolor="#181825", lightcolor="#a6e3a1", darkcolor="#a6e3a1")

        # Alphabet
        tk.Label(disp_frame, text="Registered Character:", font=("Segoe UI", 14), fg="#bac2de", bg="#181825").pack(anchor="w")
        self.lbl_alphabet = tk.Label(disp_frame, text="Ready", font=("Segoe UI", 48, "bold"), fg="#89b4fa", bg="#181825")
        self.lbl_alphabet.pack(anchor="w", pady=(0, 25))

        # Word
        tk.Label(disp_frame, text="Constructed Word", font=("Segoe UI", 14), fg="#bac2de", bg="#181825").pack(anchor="w")
        self.lbl_word = tk.Label(disp_frame, text="N/A", font=("Segoe UI", 26, "bold"), fg="#fab387", bg="#181825", wraplength=500, justify="left")
        self.lbl_word.pack(anchor="w", pady=(0, 25))

        # Sentence
        tk.Label(disp_frame, text="Formed Sentence", font=("Segoe UI", 14), fg="#bac2de", bg="#181825").pack(anchor="w")
        self.lbl_sentence = tk.Label(disp_frame, text="N/A", font=("Segoe UI", 22, "italic"), fg="#a6e3a1", bg="#181825", wraplength=500, justify="left")
        self.lbl_sentence.pack(anchor="w", pady=(0, 20))

        # Control Buttons
        btn_frame = tk.Frame(content_frame, bg="#181825")
        btn_frame.pack(fill="x", padx=30, pady=(10, 30))

        self.btn_reset = tk.Button(btn_frame, text="Reset Text", font=("Segoe UI", 14, "bold"), bg="#f38ba8", fg="#11111b", relief="flat", command=self.action_reset, width=12, pady=5)
        self.btn_reset.pack(side=tk.LEFT, padx=(0, 15))

        self.btn_pause = tk.Button(btn_frame, text="Pause Feed", font=("Segoe UI", 14, "bold"), bg="#89dceb", fg="#11111b", relief="flat", command=self.action_pause, width=12, pady=5)
        self.btn_pause.pack(side=tk.LEFT, padx=(0, 15))

        self.btn_speak = tk.Button(btn_frame, text="Speak Text", font=("Segoe UI", 14, "bold"), bg="#a6e3a1", fg="#11111b", relief="flat", command=self.action_speak, width=12, pady=5)
        self.btn_speak.pack(side=tk.LEFT, padx=(0, 15))

    def on_language_change(self, event=None):
        new_lang = self.lang_var.get()
        success, msg = self.sl_model.load_model(new_lang)
        self.builder.reset()
        self.update_labels()
        if not success:
            self.lbl_alphabet.config(text="Model Missing", fg="#f38ba8", font=("Segoe UI", 24, "bold"))
            messagebox.showwarning("Model Not Found", f"The model file for {new_lang} was not found. Please place it in the application directory or train a new model.")
        else:
            self.lbl_alphabet.config(text="Ready", fg="#89b4fa", font=("Segoe UI", 48, "bold"))

    def action_reset(self):
        self.builder.reset()
        self.sl_model.reset_stabilization()
        self.update_labels()
        self.lbl_alphabet.config(text="Ready")
        self.lbl_live.config(text="-")
        self.progress_var.set(0.0)

    def action_pause(self):
        self.is_paused = not self.is_paused
        self.btn_pause.config(text="Resume Feed" if self.is_paused else "Pause Feed", bg="#f9e2af" if self.is_paused else "#89dceb")

    def action_speak(self):
        self.builder.speak()

    def update_labels(self):
        self.lbl_word.config(text=self.builder.get_current_word())
        self.lbl_sentence.config(text=self.builder.get_current_sentence())

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.process_frame)
            return

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.is_paused:
            self.display_image(img_rgb)
            self.root.after(10, self.process_frame)
            return

        # Inference
        detection_result = self.detector.detect(img_rgb)
        
        current_live_char = "-"
        current_progress = 0.0

        if detection_result and detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                features = extract_hand_features(hand_landmarks)
                
                # Predict
                char = self.sl_model.predict(features)
                
                # Stabilize Buffer
                live_char, stable_char, progress = self.sl_model.process_prediction_with_stabilization(char)
                
                if live_char in [' ', '.']:
                    disp_live = "[Space]" if live_char == ' ' else "[Period]"
                else:
                    disp_live = live_char if live_char else "-"
                
                current_live_char = disp_live
                current_progress = progress

                self.lbl_live.config(text=disp_live, fg="#f38ba8" if progress < 1.0 else "#a6e3a1")
                self.progress_var.set(progress)

                if stable_char:
                    if stable_char in [' ', '.']:
                        disp_char = "[Space]" if stable_char == ' ' else "[Period]"
                        self.lbl_alphabet.config(text=disp_char, fg="#eba0ac")
                    else:
                        self.lbl_alphabet.config(text=stable_char, fg="#89b4fa")

                    if self.builder.process_character(stable_char):
                        self.update_labels()

                # Draw Hand Connections
                self.draw_hand(img_rgb, hand_landmarks)

        # Draw Overlay info
        cv2.putText(img_rgb, f"Model: {self.lang_var.get()}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (244, 214, 205), 2)
        
        if current_live_char != "-":
            cv2.putText(img_rgb, f"Predicting: {current_live_char}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (250, 180, 137), 2)
            # Draw a sleek progress bar on the video
            cv2.rectangle(img_rgb, (10, 85), (210, 100), (49, 50, 68), cv2.FILLED)
            if current_progress > 0:
                cv2.rectangle(img_rgb, (10, 85), (10 + int(200 * current_progress), 100), (161, 227, 166), cv2.FILLED)
            cv2.rectangle(img_rgb, (10, 85), (210, 100), (205, 214, 244), 2)
        else:
            self.lbl_live.config(text="-")
            self.progress_var.set(0.0)

        self.display_image(img_rgb)
        self.root.after(10, self.process_frame)

    def draw_hand(self, img, landmarks):
        h, w, _ = img.shape
        # Draw lines
        for conn in HAND_CONNECTIONS:
            p1 = landmarks[conn[0]]
            p2 = landmarks[conn[1]]
            cv2.line(img, (int(p1.x * w), int(p1.y * h)), (int(p2.x * w), int(p2.y * h)), (166, 227, 161), 2)
        # Draw points
        for lm in landmarks:
            cv2.circle(img, (int(lm.x * w), int(lm.y * h)), 6, (137, 180, 250), cv2.FILLED)
        
    def display_image(self, img_rgb):
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()
