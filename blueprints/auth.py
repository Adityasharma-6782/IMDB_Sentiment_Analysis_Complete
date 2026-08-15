from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from auth_utils import (
    csrf_protect,
    hash_password,
    make_reset_token,
    password_strength_error,
    read_reset_token,
    valid_email,
    valid_username,
    verify_password,
)

bp = Blueprint("auth", __name__)


@bp.route("/signup", methods=["GET", "POST"])
@csrf_protect
def signup():
    if session.get("user_id"):
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        error = None
        if not valid_username(username):
            error = "Usernames are 3-20 characters: letters, numbers, dot or underscore."
        elif not valid_email(email):
            error = "That email address doesn't look right."
        elif password != confirm:
            error = "Passwords don't match."
        else:
            error = password_strength_error(password)

        if error is None:
            db = current_app.db
            if db.users.find_one({"email": email}):
                error = "An account with that email already exists."
            elif db.users.find_one({"username": username}):
                error = "That username is taken."

        if error:
            flash(error, "error")
            return render_template("signup.html", username=username, email=email)

        db = current_app.db
        result = db.users.insert_one(
            {
                "username": username,
                "email": email,
                "password_hash": hash_password(password),
                "bio": "",
                "favorite_genre": "",
                "created_at": datetime.now(timezone.utc),
            }
        )
        session.clear()
        session["user_id"] = str(result.inserted_id)
        flash(f"Welcome, {username} — your account is ready.", "success")
        return redirect(url_for("main.home"))

    return render_template("signup.html")


@bp.route("/login", methods=["GET", "POST"])
@csrf_protect
def login():
    if session.get("user_id"):
        return redirect(url_for("main.home"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")

        db = current_app.db
        user = db.users.find_one(
            {"$or": [{"email": identifier}, {"username": identifier}]}
        )

        if user and verify_password(user["password_hash"], password):
            session.clear()
            session["user_id"] = str(user["_id"])
            flash(f"Good to see you, {user['username']}.", "success")
            next_url = request.args.get("next") or url_for("main.home")
            return redirect(next_url)

        flash("That email/username and password don't match.", "error")
        return render_template("login.html", identifier=identifier)

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You've been signed out.", "info")
    return redirect(url_for("main.landing"))


@bp.route("/forgot-password", methods=["GET", "POST"])
@csrf_protect
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        db = current_app.db
        user = db.users.find_one({"email": email})

        # Always show the same message, whether or not the account exists —
        # this avoids leaking which emails are registered.
        generic_msg = "If that email is registered, a reset link has been sent."

        if user:
            token = make_reset_token(user["_id"])
            db.reset_tokens.insert_one(
                {
                    "user_id": user["_id"],
                    "token": token,
                    "created_at": datetime.now(timezone.utc),
                    "expires_at": datetime.now(timezone.utc)
                    + timedelta(seconds=current_app.config["RESET_TOKEN_MAX_AGE"]),
                }
            )
            reset_url = url_for("auth.reset_password", token=token, _external=True)

            if current_app.config.get("MAIL_SERVER") and current_app.config.get("MAIL_USERNAME"):
                _send_reset_email(email, reset_url)
            else:
                # Dev mode: no SMTP configured, so surface the link directly
                # instead of silently doing nothing.
                current_app.logger.info("[password reset link] %s -> %s", email, reset_url)
                flash(generic_msg, "info")
                flash(f"Dev mode (no email server configured): {reset_url}", "dev")
                return render_template("forgot_password.html")

        flash(generic_msg, "info")
        return render_template("forgot_password.html")

    return render_template("forgot_password.html")


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
@csrf_protect
def reset_password(token):
    db = current_app.db
    max_age = current_app.config["RESET_TOKEN_MAX_AGE"]
    uid, err = read_reset_token(token, max_age)

    record = db.reset_tokens.find_one({"token": token})
    if err or not record:
        flash("That reset link is invalid or has expired. Request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        error = None
        if password != confirm:
            error = "Passwords don't match."
        else:
            error = password_strength_error(password)

        if error:
            flash(error, "error")
            return render_template("reset_password.html", token=token)

        from bson import ObjectId

        db.users.update_one(
            {"_id": ObjectId(uid)}, {"$set": {"password_hash": hash_password(password)}}
        )
        db.reset_tokens.delete_one({"token": token})
        flash("Password updated. Sign in with your new password.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)


def _send_reset_email(to_email: str, reset_url: str):
    """Minimal SMTP send, only used if MAIL_* env vars are set."""
    import smtplib
    from email.mime.text import MIMEText

    cfg = current_app.config
    msg = MIMEText(
        f"Someone requested a password reset for this email.\n\n"
        f"Reset your password: {reset_url}\n\n"
        f"If this wasn't you, you can ignore this email."
    )
    msg["Subject"] = "Reset your ReelTake password"
    msg["From"] = cfg["MAIL_SENDER"]
    msg["To"] = to_email

    with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"]) as server:
        server.starttls()
        server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
        server.send_message(msg)
