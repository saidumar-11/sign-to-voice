import argparse
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from config import SUPPORTED_LANGUAGES, DEFAULT_LANG

def main():
    parser = argparse.ArgumentParser(description="Train Random Forest Classifier for Sign Language")
    parser.add_argument('--lang', type=str, default=DEFAULT_LANG, choices=list(SUPPORTED_LANGUAGES.keys()), help="Target language for output model mapping")
    parser.add_argument('--out', type=str, default='', help="Override default output model path")
    parser.add_argument('--data', type=str, default='./data.pickle', help="Input data.pickle file")
    args = parser.parse_args()

    try:
        data_dict = pickle.load(open(args.data, 'rb'))
    except FileNotFoundError:
        print(f"Error: {args.data} not found. Run createDataset.py first.")
        return

    data = np.asarray(data_dict['data'])
    labels = np.asarray(data_dict['labels'])

    try:
        x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)
    except Exception as e:
        print(f"Warning: train_test_split with stratify failed ({e}). Retrying without stratify...")
        x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True)
        
    print("Initializing model...")
    model = RandomForestClassifier()
    print("Fitting model...")
    model.fit(x_train, y_train)
    print("Predicting...")
    y_predict = model.predict(x_test)
    print("Calculating accuracy...")
    score = accuracy_score(y_predict, y_test)

    print('{:.2f}% of samples were classified correctly!'.format(score * 100))

    out_path = args.out
    if not out_path:
        out_path = SUPPORTED_LANGUAGES[args.lang]["model_path"]

    print("Saving model...")
    with open(out_path, 'wb') as f:
        pickle.dump({'model': model}, f)

    print(f"Model successfully saved to {out_path}")

if __name__ == "__main__":
    main()
