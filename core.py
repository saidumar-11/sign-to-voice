import pickle
import numpy as np
import time
import threading
import pyttsx3
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    SUPPORTED_LANGUAGES, DEFAULT_LANG, STABILIZATION_BUFFER_SIZE, 
    REGISTRATION_THRESHOLD, REGISTRATION_DELAY_SEC
)

class HandDetector:
    def __init__(self, model_asset_path='hand_landmarker.task'):
        try:
            base_options = python.BaseOptions(model_asset_path=model_asset_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=1,
                min_hand_detection_confidence=0.5
            )
            self.detector = vision.HandLandmarker.create_from_options(options)
            self.is_valid = True
        except Exception as e:
            print(f"Failed to initialize HandLandmarker: {e}")
            self.detector = None
            self.is_valid = False

    def detect(self, np_image):
        if not self.is_valid: 
            return None
        # MediaPipe expects ImageFormat.SRGB
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_image)
        return self.detector.detect(mp_image)


class SignLanguageModel:
    def __init__(self, language_name=DEFAULT_LANG):
        self.language_name = language_name
        self.model = None
        self.labels_dict = {}
        
        self.stabilization_buffer = []
        self.last_registered_time = time.time()
        self.stable_char = None
        
        self.load_model(language_name)

    def load_model(self, language_name):
        self.language_name = language_name
        config = SUPPORTED_LANGUAGES.get(language_name, SUPPORTED_LANGUAGES[DEFAULT_LANG])
        self.labels_dict = config["labels"]
        model_path = config["model_path"]
        
        try:
            with open(model_path, 'rb') as f:
                model_dict = pickle.load(f)
                self.model = model_dict['model']
            return True, "Model loaded successfully."
        except Exception as e:
            print(f"Error loading model {model_path} for {language_name}: {e}")
            self.model = None
            return False, f"Model file not found: {model_path}"

    def predict(self, features):
        if self.model is None or not features:
            return "?"
        try:
            prediction = self.model.predict([np.asarray(features)])
            return self.labels_dict.get(int(prediction[0]), "?")
        except Exception as e:
            print(f"Prediction Error: {e}")
            return "?"

    def process_prediction_with_stabilization(self, predicted_char):
        if predicted_char == "?":
            return predicted_char, None, 0.0
            
        self.stabilization_buffer.append(predicted_char)
        if len(self.stabilization_buffer) > STABILIZATION_BUFFER_SIZE:
            self.stabilization_buffer.pop(0)

        count = self.stabilization_buffer.count(predicted_char)
        progress = min(1.0, count / REGISTRATION_THRESHOLD)

        # Check if the character has been recognized enough times in the buffer
        if count >= REGISTRATION_THRESHOLD:
            current_time = time.time()
            if current_time - self.last_registered_time > REGISTRATION_DELAY_SEC:
                self.stable_char = predicted_char
                self.last_registered_time = current_time
                self.stabilization_buffer.clear() # Clear buffer to prevent spamming
                return predicted_char, self.stable_char, 1.0
                
        return predicted_char, None, progress
        
    def reset_stabilization(self):
        self.stabilization_buffer = []
        self.stable_char = None


class SentenceBuilder:
    def __init__(self):
        self.word_buffer = ""
        self.sentence = ""
        self.engine = pyttsx3.init()
        # Voice fallback setup can be dynamic
        
    def set_voice(self, lang_code):
        # Optional enhancement to select a voice matching the language code (uz, en, ru)
        pass

    def process_character(self, char):
        if not char: 
            return False
            
        updated = False
        if char == ' ':
            if self.word_buffer.strip():
                self.sentence += self.word_buffer + " "
                updated = True
            elif self.sentence and not self.sentence.endswith(" "):
                self.sentence += " "
                updated = True
            self.word_buffer = ""
        elif char == '.':
            if self.word_buffer.strip():
                self.sentence += self.word_buffer + ". "
                updated = True
            elif self.sentence and not self.sentence.endswith(". "):
                self.sentence = self.sentence.rstrip() + ". "
                updated = True
            self.word_buffer = ""
        else:
            self.word_buffer += char
            updated = True
            
        return updated

    def get_current_word(self):
        return self.word_buffer if self.word_buffer else "N/A"
        
    def get_current_sentence(self):
        return self.sentence.strip() if self.sentence.strip() else "N/A"

    def reset(self):
        self.word_buffer = ""
        self.sentence = ""

    def speak(self):
        text = self.sentence.strip()
        if not text or text == "N/A": 
            return
            
        def tts_thread():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print("TTS Error:", e)
                
        threading.Thread(target=tts_thread, daemon=True).start()
