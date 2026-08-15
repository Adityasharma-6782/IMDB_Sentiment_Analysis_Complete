"""
Trains the sentiment model used by the web app and saves it to models/.

Usage:
    python train_model.py path/to/reviews.csv

The CSV must have two columns: "text" and "sentiment" (values "pos"/"neg").
Re-run this any time you want to retrain on new data.
"""
import pickle
import sys
import time
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from nlp.text_clean import clean_text

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"


def main(csv_path: str):
    print(f"Loading {csv_path} ...")
    df = pd.read_csv(csv_path)
    if not {"text", "sentiment"}.issubset(df.columns):
        raise ValueError("CSV must have 'text' and 'sentiment' columns")

    print("Cleaning text (this takes a minute on ~25k rows)...")
    t0 = time.time()
    df["clean_text"] = df["text"].astype(str).apply(clean_text)
    print(f"  done in {time.time() - t0:.1f}s")

    df["label"] = df["sentiment"].map({"pos": 1, "neg": 0})
    df = df.dropna(subset=["label"])

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    print("Vectorizing (TF-IDF)...")
    vectorizer = TfidfVectorizer(max_features=3000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training Logistic Regression...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    preds = model.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    print(f"\nTest accuracy: {acc:.4f}\n")
    print(classification_report(y_test, preds, target_names=["neg", "pos"]))

    MODELS_DIR.mkdir(exist_ok=True)
    with open(MODELS_DIR / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open(MODELS_DIR / "model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(MODELS_DIR / "metrics.pkl", "wb") as f:
        pickle.dump({"accuracy": acc, "n_train": len(X_train), "n_test": len(X_test)}, f)

    print(f"Saved model + vectorizer to {MODELS_DIR}/")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python train_model.py path/to/reviews.csv")
        sys.exit(1)
    main(sys.argv[1])
