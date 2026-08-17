# ReelTake — Movie Review Sentiment Analyzer

A web app where you paste a movie review and it tells you whether the sentiment is **positive** or **negative**, along with a confidence score — shown as a styled cinema "ticket stub." Built with Flask, MongoDB, and a machine learning model (TF-IDF + Logistic Regression).

---

## 📌 Project Attribution & Transparency Note

- **Backend** — Built independently by me: Flask app structure, MongoDB integration, authentication (signup/login/logout/forgot password), CSRF protection, session handling, and the full machine learning pipeline (text cleaning, TF-IDF vectorization, Logistic Regression model training).
- **Frontend** — Built with AI assistance (Claude): HTML templates, CSS design (cinema ticket-stub theme), and JavaScript interactions, based on my requirements (sign in/signup, login, about, profile, edit profile, forgot password, logout).

This note exists purely for transparency about which parts were self-written vs. AI-assisted.

---

## ✅ Features

- Sign up / Login / Logout with secure password hashing
- Forgot password → Reset password flow (works even without an email server — shows a dev-mode reset link)
- Profile page with bio, favorite genre, and analysis history
- Edit profile (change username, email, password)
- Movie review sentiment analyzer with confidence score
- About page explaining how the model works
- CSRF protection on all forms

---

## 🛠️ Prerequisites

Before running this project, make sure you have:

1. **Python 3.10, 3.11, or 3.12** installed (avoid very new versions like 3.13+ for now, since some ML libraries don't have ready-made installers for them yet)
2. **MongoDB** — either:
   - Install MongoDB Community Server on your own PC and run it locally, **or**
   - Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) (no local install needed, works over internet)
3. **pip** (comes with Python)

To check your Python version, run:
```
python --version
```

---

## 🚀 Step-by-Step Setup

### Step 1: Extract the project
Unzip the project folder anywhere on your system, then open a terminal/command prompt inside the `sentiment-app` folder.

```
cd sentiment-app
```

### Step 2: Create a virtual environment
This keeps this project's packages separate from your other Python projects.

```
python -m venv venv
```

Activate it:

- **Windows:**
  ```
  venv\Scripts\activate
  ```
- **Mac/Linux:**
  ```
  source venv/bin/activate
  ```

You'll know it worked if you see `(venv)` at the start of your terminal line.

### Step 3: Install dependencies

```
pip install -r requirements.txt
```

This installs Flask, MongoDB driver (pymongo), scikit-learn, nltk, pandas, and everything else needed. This may take 2-5 minutes.

**⚠️ If you get a build/compiler error on Windows** (common with scikit-learn), try:
```
pip install --upgrade pip
pip install scikit-learn --only-binary :all:
pip install -r requirements.txt
```
This forces pip to use pre-built packages instead of trying to compile from source.

### Step 4: Set up MongoDB

**Option A — Local MongoDB:**
Install MongoDB Community Server, then run `mongod` in a separate terminal window. Leave that terminal open while using the app.

**Option B — MongoDB Atlas (easier, no install):**
1. Sign up at MongoDB Atlas (free tier)
2. Create a free cluster
3. Under "Database Access," create a username/password
4. Under "Network Access," allow access from anywhere (0.0.0.0/0) for testing
5. Click "Connect" → "Connect your application" → copy the connection string

### Step 5: Create your `.env` file

Copy `.env.example` and rename the copy to `.env`:

```
copy .env.example .env      (Windows)
cp .env.example .env        (Mac/Linux)
```

Open `.env` in any text editor and fill in:
- `SECRET_KEY` → any random long string (e.g., mash your keyboard)
- `MONGO_URI` →
  - If using local MongoDB: leave as `mongodb://localhost:27017`
  - If using Atlas: paste your connection string here

### Step 6: Run the app

```
python app.py
```

You should see something like:
```
Running on http://127.0.0.1:5000
```

Open your browser and go to:
```
http://localhost:5000
```

---

## 🎬 How to Use the App

1. Click **"Get a ticket"** to sign up with a username, email, and password
2. You'll be logged in automatically and taken to the **Analyzer** page
3. Paste any movie review text into the box and click **"Print my stub"**
4. You'll see a verdict (POSITIVE/NEGATIVE) with a confidence percentage
5. Check your **Profile** to see your stats and history
6. Try **Edit Profile** to update your bio or change your password
7. Try **Logout**, then **Forgot Password** to test the reset flow (since there's no email server configured, the reset link will appear directly on the page)

---

## 🧪 Running Tests (Optional)

To verify everything works without needing a real MongoDB connection:

```
pip install mongomock
python tests/test_smoke.py
```

This runs 25 automated checks covering signup, login, predictions, profile edits, and more.

---

## 📁 Project Structure

```
sentiment-app/
├── app.py                       → Main entry point
├── config.py                    → Configuration settings
├── extensions.py                → MongoDB connection setup
├── auth_utils.py                → Authentication helper functions
├── ml.py                        → Loads the ML model
├── train_model.py               → Script to retrain the model (optional)
├── nlp/text_clean.py            → Text cleaning logic
├── blueprints/auth.py           → Login/signup/logout routes
├── blueprints/main.py           → Analyzer/profile/about routes
├── templates/                   → HTML pages
├── static/css/style.css         → Styling
├── static/js/main.js            → Frontend interactions
├── models/                      → Saved trained ML model
├── requirements.txt             → Python dependencies
├── .env.example                 → Environment variable template
└── tests/test_smoke.py          → Automated tests
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Make sure your virtual environment is activated and you ran `pip install -r requirements.txt` |
| MongoDB connection error | Check that `mongod` is running (local) or your Atlas connection string is correct in `.env` |
| Port 5000 already in use | Close other apps using that port, or change the port in `app.py` |
| scikit-learn build error (Windows) | Use `pip install scikit-learn --only-binary :all:` before installing requirements |

---
