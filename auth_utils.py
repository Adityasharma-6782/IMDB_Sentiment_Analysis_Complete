import re
import secrets
from functools import wraps

from flask import abort, current_app, flash, redirect, request, session, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.]{3,20}$")


# ---------- passwords ----------

def hash_password(raw: str) -> str:
    return generate_password_hash(raw)


def verify_password(hashed: str, raw: str) -> bool:
    return check_password_hash(hashed, raw)


def password_strength_error(pwd: str) -> str | None:
    if len(pwd) < 8:
        return "Password needs to be at least 8 characters."
    if not re.search(r"[A-Za-z]", pwd):
        return "Password needs at least one letter."
    if not re.search(r"[0-9]", pwd):
        return "Password needs at least one number."
    return None


def valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def valid_username(username: str) -> bool:
    return bool(USERNAME_RE.match(username or ""))


# ---------- session / login ----------

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return current_app.db.users.find_one({"_id": _to_object_id(uid)})


def _to_object_id(uid):
    from bson import ObjectId

    try:
        return ObjectId(uid)
    except Exception:
        return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to continue.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


# ---------- CSRF (lightweight, no extra dependency) ----------

def csrf_token() -> str:
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(16)
    return session["_csrf_token"]


def validate_csrf(form_token: str) -> bool:
    real = session.get("_csrf_token")
    return bool(real) and bool(form_token) and secrets.compare_digest(real, form_token)


def csrf_protect(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if request.method == "POST":
            token = request.form.get("csrf_token", "")
            if not validate_csrf(token):
                abort(400, description="Your session expired, please try again.")
        return view(*args, **kwargs)

    return wrapped


# ---------- password reset tokens ----------

def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="password-reset")


def make_reset_token(user_id: str) -> str:
    return _serializer().dumps({"uid": str(user_id)})


def read_reset_token(token: str, max_age: int):
    try:
        data = _serializer().loads(token, max_age=max_age)
    except SignatureExpired:
        return None, "expired"
    except BadSignature:
        return None, "invalid"
    return data.get("uid"), None
