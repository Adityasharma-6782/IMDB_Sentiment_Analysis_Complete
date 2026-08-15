from datetime import datetime, timezone

from bson import ObjectId
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

import ml
from auth_utils import (
    csrf_protect,
    current_user,
    hash_password,
    login_required,
    valid_email,
    valid_username,
    verify_password,
)

bp = Blueprint("main", __name__)


@bp.route("/")
def landing():
    if session.get("user_id"):
        return redirect(url_for("main.home"))
    metrics = ml.get_metrics()
    return render_template("landing.html", metrics=metrics)


@bp.route("/home", methods=["GET", "POST"])
@login_required
@csrf_protect
def home():
    user = current_user()
    result = None

    if request.method == "POST":
        review_text = request.form.get("review_text", "").strip()
        if len(review_text) < 5:
            flash("Give it at least a full sentence to work with.", "error")
        else:
            result = ml.predict_sentiment(review_text)
            current_app.db.predictions.insert_one(
                {
                    "user_id": user["_id"],
                    "text": review_text,
                    "label": result["label"],
                    "confidence": result["confidence"],
                    "created_at": datetime.now(timezone.utc),
                }
            )

    history = list(
        current_app.db.predictions.find({"user_id": user["_id"]}).sort("created_at", -1).limit(8)
    )
    return render_template("home.html", user=user, result=result, history=history)


@bp.route("/about")
def about():
    metrics = ml.get_metrics()
    return render_template("about.html", metrics=metrics)


@bp.route("/profile")
@login_required
def profile():
    user = current_user()
    total = current_app.db.predictions.count_documents({"user_id": user["_id"]})
    pos = current_app.db.predictions.count_documents({"user_id": user["_id"], "label": "pos"})
    neg = total - pos
    stats = {"total": total, "pos": pos, "neg": neg}
    return render_template("profile.html", user=user, stats=stats)


@bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
@csrf_protect
def edit_profile():
    user = current_user()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        bio = request.form.get("bio", "").strip()[:280]
        favorite_genre = request.form.get("favorite_genre", "").strip()[:40]
        new_password = request.form.get("new_password", "")
        current_password = request.form.get("current_password", "")

        db = current_app.db
        error = None

        if not valid_username(username):
            error = "Usernames are 3-20 characters: letters, numbers, dot or underscore."
        elif not valid_email(email):
            error = "That email address doesn't look right."
        elif username != user["username"] and db.users.find_one({"username": username}):
            error = "That username is taken."
        elif email != user["email"] and db.users.find_one({"email": email}):
            error = "An account with that email already exists."

        updates = {"username": username, "email": email, "bio": bio, "favorite_genre": favorite_genre}

        if new_password:
            if not verify_password(user["password_hash"], current_password):
                error = "Current password is incorrect."
            elif len(new_password) < 8:
                error = "New password needs to be at least 8 characters."
            else:
                updates["password_hash"] = hash_password(new_password)

        if error:
            flash(error, "error")
            return render_template("edit_profile.html", user={**user, **updates})

        db.users.update_one({"_id": user["_id"]}, {"$set": updates})
        flash("Profile updated.", "success")
        return redirect(url_for("main.profile"))

    return render_template("edit_profile.html", user=user)


@bp.route("/profile/delete-history-item/<item_id>", methods=["POST"])
@login_required
@csrf_protect
def delete_history_item(item_id):
    user = current_user()
    current_app.db.predictions.delete_one({"_id": ObjectId(item_id), "user_id": user["_id"]})
    flash("Removed from your history.", "info")
    return redirect(request.referrer or url_for("main.home"))
