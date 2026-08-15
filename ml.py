import pickle
from pathlib import Path

from nlp.text_clean import clean_text

MODELS_DIR = Path(__file__).resolve().parent / "models"

_vectorizer = None
_model = None
_metrics = None


class ModelNotTrainedError(RuntimeError):
    pass


def load_artifacts():
    global _vectorizer, _model, _metrics
    if _vectorizer is not None and _model is not None:
        return

    vec_path = MODELS_DIR / "vectorizer.pkl"
    model_path = MODELS_DIR / "model.pkl"
    metrics_path = MODELS_DIR / "metrics.pkl"

    if not vec_path.exists() or not model_path.exists():
        raise ModelNotTrainedError(
            "No trained model found in models/. Run `python train_model.py <csv>` first."
        )

    with open(vec_path, "rb") as f:
        _vectorizer = pickle.load(f)
    with open(model_path, "rb") as f:
        _model = pickle.load(f)
    if metrics_path.exists():
        with open(metrics_path, "rb") as f:
            _metrics = pickle.load(f)
    else:
        _metrics = {}


def get_metrics() -> dict:
    load_artifacts()
    return _metrics or {}


def predict_sentiment(raw_text: str) -> dict:
    """Returns {'label': 'pos'|'neg', 'confidence': float, 'clean_text': str}"""
    load_artifacts()

    cleaned = clean_text(raw_text)
    vec = _vectorizer.transform([cleaned])
    pred = int(_model.predict(vec)[0])
    proba = _model.predict_proba(vec)[0]
    confidence = float(max(proba))

    return {
        "label": "pos" if pred == 1 else "neg",
        "confidence": round(confidence * 100, 1),
        "clean_text": cleaned,
    }
