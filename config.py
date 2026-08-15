import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://adisharma8107_db_user:irR68zGzMbIUrhcw@cluster0.avpqqjj.mongodb.net")
    MONGO_DBNAME = os.environ.get("MONGO_DBNAME", "reeltake")

    # How long a "forgot password" link stays valid, in seconds.
    RESET_TOKEN_MAX_AGE = int(os.environ.get("RESET_TOKEN_MAX_AGE", 60 * 30))  # 30 min

    # If real SMTP creds are supplied, password-reset links are emailed for
    # real. Otherwise the app runs in "dev mode" and just shows the link
    # on screen / prints it to the console, so the whole flow still works
    # without needing an email provider configured.
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SENDER = os.environ.get("MAIL_SENDER", "no-reply@reeltake.local")
