import cv2
import os
import glob
import numpy as np
import tkinter as tk
from tkinter import ttk, StringVar, messagebox, filedialog
from PIL import Image, ImageTk
import warnings

from core import HandDetector, SignLanguageModel, SentenceBuilder
from utils import extract_hand_features
from config import SUPPORTED_LANGUAGES, DEFAULT_LANG, HAND_CONNECTIONS

warnings.filterwarnings("ignore", category=UserWarning)

class PhotoAppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Language Photo Analyzer")
        self.root.geometry("1400x800")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        self.detector = HandDetector()
        self.sl_model = SignLanguageModel(DEFAULT_LANG)
        self.builder = SentenceBuilder()

        self.image_list = []
        self.current_image_index = 0

        self.setup_ui()
        self.on_language_change()

    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="Sign Language Photo Analyzer", font=("Segoe UI", 32, "bold"), fg="#cdd6f4", bg="#1e1e2e")
        header.grid(row=0, column=0, columnspan=2, pady=(15, 5))

        # Main Layout container
        main_container = tk.Frame(self.root, bg="#1e1e2e")
        main_container.grid(row=1, column=0, columnspan=2, padx=40, pady=5, sticky="nsew")
        self.root.columnconfigure(0, weight=1)

        # Video/Image Frame (Left)
        video_bg = tk.Frame(main_container, bg="#313244", bd=0, relief="flat", width=640, height=480)
        video_bg.pack(side=tk.LEFT, padx=(0, 30), pady=10)
        video_bg.pack_propagate(False)
        self.video_label = tk.Label(video_bg, bg="#11111b", text="No Image Loaded", fg="#6c7086", font=("Segoe UI", 16))
        self.video_label.pack(expand=True, fill="both", padx=5, pady=5)

        # Content Frame (Right)
        content_frame = tk.Frame(main_container, bg="#181825", bd=0, highlightbackground="#313244", highlightthickness=2)
        content_frame.pack(side=tk.RIGHT, fill="both", expand=True, pady=10)

        # Language Selector
        lang_frame = tk.Frame(content_frame, bg="#181825")
        lang_frame.pack(fill="x", padx=30, pady=(20, 15))
        tk.Label(lang_frame, text="Translation Language Model:", font=("Segoe UI", 16, "bold"), fg="#bac2de", bg="#181825").pack(anchor="w", pady=(0, 5))
        
        self.lang_var = StringVar(value=DEFAULT_LANG)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground="#313244", background="#45475a", foreground="#cdd6f4", font=("Segoe UI", 14), padding=5)
        
        self.lang_dropdown = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=list(SUPPORTED_LANGUAGES.keys()), state="readonly", font=("Segoe UI", 14), width=30)
        self.lang_dropdown.pack(anchor="w")
        self.lang_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)

        # Image Counter
        self.lbl_counter = tk.Label(lang_frame, text="0 / 0 Images", font=("Segoe UI", 12), fg="#f9e2af", bg="#181825")
        self.lbl_counter.pack(anchor="w", pady=(10, 0))

        # Text Displays
        disp_frame = tk.Frame(content_frame, bg="#181825")
        disp_frame.pack(fill="both", expand=True, padx=30, pady=5)

        tk.Label(disp_frame, text="Detected Character", font=("Segoe UI", 14), fg="#bac2de", bg="#181825").pack(anchor="w")
        self.lbl_alphabet = tk.Label(disp_frame, text="Ready", font=("Segoe UI", 36, "bold"), fg="#89b4fa", bg="#181825")
        self.lbl_alphabet.pack(anchor="w", pady=(0, 15))

        tk.Label(disp_frame, text="Constructed Word", font=("Segoe UI", 14), fg="#bac2de", bg="#181825").pack(anchor="w")
        self.lbl_word = tk.Label(disp_frame, text="N/A", font=("Segoe UI", 24, "bold"), fg="#fab387", bg="#181825", wraplength=500, justify="left")
        self.lbl_word.pack(anchor="w", pady=(0, 15))

        tk.Label(disp_frame, text="Formed Sentence", font=("Segoe UI", 14), fg="#bac2de", bg="#181825").pack(anchor="w")
        self.lbl_sentence = tk.Label(disp_frame, text="N/A", font=("Segoe UI", 20, "italic"), fg="#a6e3a1", bg="#181825", wraplength=500, justify="left")
        self.lbl_sentence.pack(anchor="w", pady=(0, 15))

        # Action Buttons
        btn_action_frame = tk.Frame(content_frame, bg="#181825")
        btn_action_frame.pack(fill="x", padx=30, pady=(5, 10))

        self.btn_reset = tk.Button(btn_action_frame, text="Reset Text", font=("Segoe UI", 12, "bold"), bg="#f38ba8", fg="#11111b", relief="flat", command=self.action_reset, width=12)
        self.btn_reset.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_speak = tk.Button(btn_action_frame, text="Speak Text", font=("Segoe UI", 12, "bold"), bg="#a6e3a1", fg="#11111b", relief="flat", command=self.action_speak, width=12)
        self.btn_speak.pack(side=tk.LEFT, padx=(0, 10))

        # Navigation & Load Buttons (Bottom spanning)
        nav_container = tk.Frame(self.root, bg="#1e1e2e")
        nav_container.grid(row=2, column=0, columnspan=2, pady=10)

        nav_buttons = [
            ("Load Single Image", self.load_single_image, "#89b4fa"),
            ("Load Directory", self.load_images, "#cba6f7"),
            ("← Previous", self.previous_image, "#585b70"),
            ("Next →", self.next_image, "#585b70")
        ]

        for text, cmd, color in nav_buttons:
            tk.Button(nav_container, text=text, font=("Segoe UI", 14, "bold"), bg=color, fg="#11111b" if color != "#585b70" else "#cdd6f4", relief="flat", command=cmd, width=15, pady=8).pack(side=tk.LEFT, padx=15)

    def on_language_change(self, event=None):
        new_lang = self.lang_var.get()
        success, msg = self.sl_model.load_model(new_lang)
        if not success:
            self.lbl_alphabet.config(text="Model Missing", fg="#f38ba8")
            messagebox.showwarning("Model Not Found", f"The model file for {new_lang} was not found.")
        else:
            self.lbl_alphabet.config(text="Ready", fg="#89b4fa")
        
        # Reprocess current image with new model if available
        if self.image_list:
            # We don't want to re-add to the sentence, just show the detection for the current image
            self.process_current_image(update_sentence=False)

    def action_reset(self):
        self.builder.reset()
        self.update_labels()
        self.lbl_alphabet.config(text="Ready")

    def action_speak(self):
        self.builder.speak()

    def update_labels(self):
        self.lbl_word.config(text=self.builder.get_current_word())
        self.lbl_sentence.config(text=self.builder.get_current_sentence())

    def update_counter(self):
        if not self.image_list:
            self.lbl_counter.config(text="0 / 0 Images")
        else:
            self.lbl_counter.config(text=f"{self.current_image_index + 1} / {len(self.image_list)} Images")

    def load_images(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Sign Language Images")
        if folder_path:
            exts = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.PNG']
            self.image_list = []
            for ext in exts:
                self.image_list.extend(glob.glob(os.path.join(folder_path, ext)))
            self.image_list.sort()
            
            if self.image_list:
                self.current_image_index = 0
                self.process_current_image()
            else:
                messagebox.showinfo("No Images", "No images found in the selected folder.")
            self.update_counter()

    def load_single_image(self):
        file_path = filedialog.askopenfilename(title="Select Sign Language Image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.image_list = [file_path]
            self.current_image_index = 0
            self.process_current_image()
            self.update_counter()

    def next_image(self):
        if self.image_list and self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.process_current_image()
            self.update_counter()

    def previous_image(self):
        if self.image_list and self.current_image_index > 0:
            self.current_image_index -= 1
            self.process_current_image()
            self.update_counter()

    def process_current_image(self, update_sentence=True):
        if not self.image_list: return
        
        image_path = self.image_list[self.current_image_index]
        frame = cv2.imread(image_path)
        if frame is None:
            self.lbl_alphabet.config(text="Load Error")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detection_result = self.detector.detect(frame_rgb)
        
        detected_char = None
        
        if detection_result and detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                features = extract_hand_features(hand_landmarks)
                detected_char = self.sl_model.predict(features)
                
                # Draw on frame
                h, w, _ = frame.shape
                for conn in HAND_CONNECTIONS:
                    p1 = hand_landmarks[conn[0]]
                    p2 = hand_landmarks[conn[1]]
                    cv2.line(frame, (int(p1.x * w), int(p1.y * h)), (int(p2.x * w), int(p2.y * h)), (166, 227, 161), 2)
                for lm in hand_landmarks:
                    cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 6, (137, 180, 250), cv2.FILLED)

        # UI updates
        if detected_char and detected_char != "?":
            disp_char = "[Space]" if detected_char == ' ' else ("[Period]" if detected_char == '.' else detected_char)
            self.lbl_alphabet.config(text=disp_char, fg="#89b4fa")
            
            if update_sentence:
                if self.builder.process_character(detected_char):
                    self.update_labels()
        else:
            self.lbl_alphabet.config(text="No Hand", fg="#f38ba8")

        cv2.putText(frame, f"Model: {self.lang_var.get()}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (205, 214, 244), 2)
        if detected_char:
            cv2.putText(frame, f"Det: {detected_char}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (137, 180, 250), 2)

        # Scale and render image dynamically
        target_w, target_h = 640, 480
        h, w = frame.shape[:2]
        scale = min(target_w/w, target_h/h)
        new_w, new_h = int(w*scale), int(h*scale)
        resized = cv2.resize(frame, (new_w, new_h))
        
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        canvas.fill(17) # #11111b Background
        y_off = (target_h - new_h) // 2
        x_off = (target_w - new_w) // 2
        canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
        
        img_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk, text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoAppUI(root)
    root.mainloop()

