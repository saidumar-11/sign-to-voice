import os
import argparse
import cv2
from config import SUPPORTED_LANGUAGES, DEFAULT_LANG

def main():
    parser = argparse.ArgumentParser(description="Collect images for sign language dataset.")
    # Show user the available shorthand or full names
    langs = list(SUPPORTED_LANGUAGES.keys())
    parser.add_argument('--lang', type=str, default=DEFAULT_LANG, choices=langs,
                        help=f"Language to collect data for. Options: {langs}")
    parser.add_argument('--dataset_size', type=int, default=100, help="Number of images per class")
    args = parser.parse_args()

    active_lang = args.lang
    dataset_size = args.dataset_size

    labels_dict = SUPPORTED_LANGUAGES[active_lang]["labels"]
    number_of_classes = len(labels_dict)

    DATA_DIR = './data'
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    cap = cv2.VideoCapture(0)
    
    # We iterate over the sorted keys to guarantee deterministic ordering
    for j in sorted(labels_dict.keys()):
        class_dir = os.path.join(DATA_DIR, str(j))
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)

        label_name = labels_dict[j]
        print(f'Collecting data for class {j} - {label_name} ({active_lang})')

        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            cv2.putText(frame, f'Target >> {label_name} <<', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, 'Press "Q" to start collecting!', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('frame', frame)
            
            if cv2.waitKey(25) == ord('q'):
                break

        counter = 0
        while counter < dataset_size:
            ret, frame = cap.read()
            if not ret:
                continue
                
            cv2.imshow('frame', frame)
            cv2.waitKey(25)
            cv2.imwrite(os.path.join(class_dir, f'{counter}.jpg'), frame)
            counter += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
