import os
import argparse
import pickle
import cv2
import warnings

from core import HandDetector
from utils import extract_hand_features

warnings.filterwarnings("ignore", category=UserWarning)

def main():
    parser = argparse.ArgumentParser(description="Extract hand features and save to a pickle file.")
    parser.add_argument('--dir', type=str, default='./data', help='Input directory containing categorical subdirectories with images.')
    parser.add_argument('--out', type=str, default='./data.pickle', help='Output pickle file to save features.')
    args = parser.parse_args()

    DATA_DIR = args.dir
    OUT_FILE = args.out

    if not os.path.exists(DATA_DIR):
        print(f"Data directory '{DATA_DIR}' not found. Please run collectImgs.py first.")
        return

    detector = HandDetector()
    if not detector.is_valid:
        print("Failed to load HandDetector. Ensure 'hand_landmarker.task' exists.")
        return

    data = []
    labels = []

    dirs = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    
    for dir_ in dirs:
        dir_path = os.path.join(DATA_DIR, dir_)
        print(f"Processing class: {dir_}")
        
        for img_path in os.listdir(dir_path):
            img = cv2.imread(os.path.join(dir_path, img_path))
            if img is None:
                continue
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = detector.detect(img_rgb)

            if results and results.hand_landmarks:
                for hand_landmarks in results.hand_landmarks:
                    # extract_hand_features returns exactly 42 normalized features
                    features = extract_hand_features(hand_landmarks)
                    data.append(features)
                    labels.append(dir_)
            else:
                pass # skipping output to avoid log spam
                # print(f"Skipped {img_path} in {dir_}: No hands detected.")

    if data:
        with open(OUT_FILE, 'wb') as f:
            pickle.dump({'data': data, 'labels': labels}, f)
        print(f"\nDataset saved successfully. Total samples mapped: {len(data)}")
    else:
        print("\nFailed to extract any hand features. Dataset is empty.")

if __name__ == "__main__":
    main()
