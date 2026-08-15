"""
Not part of the shipped app — a throwaway harness to exercise every route
with an in-memory Mongo (mongomock) since this sandbox can't run a real
mongod. Run with: python _smoke_test.py
"""
import re
import sys

import mongomock
import pymongo

# Patch MongoClient BEFORE importing the app so extensions.py picks up the mock.
pymongo.MongoClient = mongomock.MongoClient

import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa: E402
import app as app_module  # noqa: E402

flask_app = app_module.app
flask_app.config["TESTING"] = True


def get_csrf(html):
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, "no csrf token found in page"
    return m.group(1)


def main():
    client = flask_app.test_client()
    failures = []

    def check(name, cond):
        status = "OK" if cond else "FAIL"
        print(f"[{status}] {name}")
        if not cond:
            failures.append(name)

    # 1. Landing page
    r = client.get("/")
    check("GET / (landing) -> 200", r.status_code == 200)
    check("landing shows Get a ticket CTA", b"Get a ticket" in r.data or b"Get your ticket" in r.data)

    # 2. About page
    r = client.get("/about")
    check("GET /about -> 200", r.status_code == 200)

    # 3. Signup page renders
    r = client.get("/signup")
    check("GET /signup -> 200", r.status_code == 200)
    token = get_csrf(r.data.decode())

    # 4. Signup with bad confirm password
    r = client.post("/signup", data={
        "csrf_token": token, "username": "critic_dev", "email": "critic@example.com",
        "password": "MoviePass1", "confirm_password": "wrong",
    })
    check("signup mismatched passwords rejected", b"don&#39;t match" in r.data or b"don't match" in r.data)

    # 5. Successful signup
    token = get_csrf(r.data.decode())
    r = client.post("/signup", data={
        "csrf_token": token, "username": "critic_dev", "email": "critic@example.com",
        "password": "MoviePass1", "confirm_password": "MoviePass1",
    }, follow_redirects=True)
    check("signup succeeds -> analyzer page", b"Paste a review" in r.data)

    # 6. Logout
    r = client.get("/logout", follow_redirects=True)
    check("logout redirects to landing", b"Every review" in r.data)

    # 7. Login with wrong password
    r = client.get("/login")
    token = get_csrf(r.data.decode())
    r = client.post("/login", data={"csrf_token": token, "identifier": "critic@example.com", "password": "wrong"})
    check("login wrong password rejected", b"don&#39;t match" in r.data or b"don't match" in r.data)

    # 8. Login correctly
    token = get_csrf(r.data.decode())
    r = client.post("/login", data={"csrf_token": token, "identifier": "critic@example.com", "password": "MoviePass1"}, follow_redirects=True)
    check("login succeeds -> analyzer page", b"Paste a review" in r.data)

    # 9. Run a prediction (positive-leaning review)
    r = client.get("/home")
    token = get_csrf(r.data.decode())
    r = client.post("/home", data={
        "csrf_token": token,
        "review_text": "This was an absolutely brilliant film, the acting was phenomenal and I loved every minute of it.",
    })
    check("positive review -> POSITIVE stub", b"POSITIVE" in r.data)
    check("prediction shows a confidence number", b"CONFIDENCE" in r.data)

    # 10. Run a prediction (negative-leaning review)
    token = get_csrf(r.data.decode())
    r = client.post("/home", data={
        "csrf_token": token,
        "review_text": "Awful movie, boring plot, terrible acting, complete waste of time and money.",
    })
    check("negative review -> NEGATIVE stub", b"NEGATIVE" in r.data)

    # 11. History shows up
    check("history list shows recent stub", b"history-item" in r.data)

    # 12. Profile page
    r = client.get("/profile")
    check("GET /profile -> 200", r.status_code == 200)
    check("profile shows 2 analyzed reviews", b">2<" in r.data)

    # 13. Edit profile
    r = client.get("/profile/edit")
    token = get_csrf(r.data.decode())
    r = client.post("/profile/edit", data={
        "csrf_token": token, "username": "critic_dev", "email": "critic@example.com",
        "bio": "Big fan of slow-burn thrillers.", "favorite_genre": "Neo-noir",
        "current_password": "", "new_password": "",
    }, follow_redirects=True)
    check("edit profile succeeds", b"Profile updated" in r.data or r.status_code == 200)

    r = client.get("/profile")
    check("bio shows on profile after edit", b"slow-burn thrillers" in r.data)

    # 14. Wrong-CSRF POST is rejected
    r = client.post("/profile/edit", data={"csrf_token": "bogus", "username": "x", "email": "x@x.com"})
    check("bad csrf token -> 400", r.status_code == 400)

    # 15. Access control: logout then try protected page
    client.get("/logout")
    r = client.get("/home", follow_redirects=True)
    check("logged-out user redirected away from /home", b"Sign in" in r.data or b"sign in" in r.data.lower())

    # 16. Forgot password (dev mode link shown)
    r = client.get("/forgot-password")
    token = get_csrf(r.data.decode())
    r = client.post("/forgot-password", data={"csrf_token": token, "email": "critic@example.com"})
    check("forgot-password shows dev reset link", b"reset-password" in r.data)

    m = re.search(rb'/reset-password/([\w\-\.]+)', r.data)
    check("could extract reset token from dev link", bool(m))
    if m:
        reset_path = "/reset-password/" + m.group(1).decode()
        r = client.get(reset_path)
        check("GET reset-password page -> 200", r.status_code == 200)
        token = get_csrf(r.data.decode())
        r = client.post(reset_path, data={
            "csrf_token": token, "password": "NewPassword2", "confirm_password": "NewPassword2",
        }, follow_redirects=True)
        check("password reset succeeds -> login page", b"Password updated" in r.data or b"Sign in" in r.data)

        # log in with new password
        r = client.get("/login")
        token = get_csrf(r.data.decode())
        r = client.post("/login", data={"csrf_token": token, "identifier": "critic_dev", "password": "NewPassword2"}, follow_redirects=True)
        check("login with new password works", b"Paste a review" in r.data)

    # 17. 404 page
    r = client.get("/this-page-does-not-exist")
    check("unknown route -> 404", r.status_code == 404)

    print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}"))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
