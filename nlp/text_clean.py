"""
Text cleaning pipeline shared by the training script and the Flask app.
Keeping this in one place guarantees that a review typed into the website
goes through EXACTLY the same preprocessing as the reviews the model was
trained on.
"""
import os
import re
import string

import nltk

# Point NLTK at the data bundled with this project so the app works
# offline / without needing every machine to run nltk.download() by hand.
_BUNDLED_NLTK_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nltk_data")
if os.path.isdir(_BUNDLED_NLTK_DATA) and _BUNDLED_NLTK_DATA not in nltk.data.path:
    nltk.data.path.insert(0, _BUNDLED_NLTK_DATA)


def _ensure_nltk_data():
    for pkg, path in [("stopwords", "corpora/stopwords"), ("punkt_tab", "tokenizers/punkt_tab")]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)


_ensure_nltk_data()

from nltk.corpus import stopwords  # noqa: E402
from nltk.stem.porter import PorterStemmer  # noqa: E402
from nltk.tokenize import word_tokenize  # noqa: E402

STOPWORDS = set(stopwords.words("english"))
_PUNCT_RE = re.compile("[%s]" % re.escape(string.punctuation))
_HTML_RE = re.compile("<.*?>")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_STEMMER = PorterStemmer()


def remove_html_tags(txt: str) -> str:
    return _HTML_RE.sub("", txt)


def remove_urls(txt: str) -> str:
    return _URL_RE.sub("", txt)


def remove_punctuation(txt: str) -> str:
    return _PUNCT_RE.sub("", txt)


def remove_stopwords(txt: str) -> str:
    return " ".join(w for w in txt.split() if w not in STOPWORDS)


def stem_tokens(tokens) -> str:
    return " ".join(_STEMMER.stem(t) for t in tokens)


def clean_text(raw_text: str) -> str:
    """Full pipeline: lowercase -> strip html/urls/punctuation -> drop
    stopwords -> tokenize -> stem. Returns a single cleaned string ready
    for the TF-IDF vectorizer."""
    txt = raw_text.lower()
    txt = remove_html_tags(txt)
    txt = remove_urls(txt)
    txt = remove_punctuation(txt)
    txt = remove_stopwords(txt)
    tokens = word_tokenize(txt)
    return stem_tokens(tokens)
