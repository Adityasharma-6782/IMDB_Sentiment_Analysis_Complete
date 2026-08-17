# ReelTake

A movie-review sentiment analyzer: paste a review, get a verdict (positive/negative)
and a confidence score, styled as a printed cinema ticket stub. Built with Flask,
scikit-learn (TF-IDF + Logistic Regression), and MongoDB for accounts.

## Features

- Email/username + password signup and login (passwords hashed with Werkzeug)
- Forgot password / reset password flow (token-based, expires after 30 min)
- Profile page with bio, favorite genre, and your analysis history/stats
- Edit profile (username, email, bio, password change)
- The analyzer itself: paste a review, get a styled "ticket stub" verdict,
  with your last 8 results saved to your account
- About page that explains exactly how the model works and its accuracy
- CSRF protection on every form, session-based auth, MongoDB indexes for
  unique emails/usernames

## 1. Prerequisites

- Python 3.10+
- A MongoDB instance — either:
  - **Local**: install MongoDB Community Server and run `mongod`, or
  - **Free cloud option**: create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) and grab its connection string

## 2. Setup

```bash
cd sentiment-app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env: set SECRET_KEY to a random string, and MONGO_URI to your
# MongoDB connection string (the local default already works if you have
# `mongod` running on localhost:27017)
```

The trained model is already included in `models/` (trained on 25,000 IMDB
reviews, ~87.6% test accuracy), so you don't have to retrain anything to run
the app. If you want to retrain on your own data:

```bash
python train_model.py path/to/your_reviews.csv   # needs "text" and "sentiment" columns
```

## 3. Run it

```bash
python app.py
```

Visit **http://localhost:5000**.

## 4. Forgot-password flow without an email server

By default there's no SMTP server configured, so "forgot password" runs in
**dev mode**: instead of emailing a link, the app shows the reset link
directly on the page (and logs it) so you can test the whole flow locally.
To send real emails, fill in `MAIL_SERVER` / `MAIL_USERNAME` / `MAIL_PASSWORD`
in `.env`.

## 5. Running the tests

The test suite uses `mongomock` (an in-memory MongoDB stand-in) so you don't
need a real database running to test the app:

```bash
pip install mongomock
python tests/test_smoke.py
```

## Project layout

```
app.py                 App factory / entry point
config.py               Env-based configuration
extensions.py            MongoDB connection + indexes
auth_utils.py             Password hashing, login_required, CSRF, reset tokens
ml.py                      Loads the trained model and exposes predict_sentiment()
train_model.py              Script to (re)train the model from a CSV
nlp/text_clean.py            Shared text-cleaning pipeline (used by training + app)
blueprints/auth.py            signup / login / logout / forgot & reset password
blueprints/main.py             landing / analyzer / about / profile / edit profile
templates/                      Jinja templates
static/css/style.css             Design system (cinema ticket-stub theme)
static/js/main.js                 Small UI interactions
models/                            Saved vectorizer.pkl + model.pkl
nltk_data/                          Bundled NLTK data (stopwords, tokenizer)
tests/test_smoke.py                  End-to-end route test using mongomock
```

## Notes on security

This is a learning/portfolio project, not a hardened production app. Before
deploying anywhere public, at minimum: set a strong random `SECRET_KEY`,
serve over HTTPS, add rate limiting on login/signup/forgot-password, and
consider a proper CSRF library (Flask-WTF) and account lockout after repeated
failed logins.
