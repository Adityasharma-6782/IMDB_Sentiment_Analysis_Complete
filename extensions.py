from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

_client = None
_db = None


def init_mongo(app):
    """Connect to MongoDB using the app config. Attaches `app.db` for
    convenience and returns the database handle."""
    global _client, _db

    _client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=5000)
    _db = _client[app.config["MONGO_DBNAME"]]

    try:
        _client.admin.command("ping")
        # Helpful indexes — safe to call every startup, MongoDB no-ops if they exist.
        _db.users.create_index("email", unique=True)
        _db.users.create_index("username", unique=True)
        _db.reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    except (ConnectionFailure, Exception) as exc:  # noqa: BLE001 - we want to start regardless
        app.logger.warning(
            "Could not reach MongoDB at %s (%s). The app will still start "
            "(e.g. you can view the landing/about pages), but any page that "
            "touches the database will error out until MongoDB is running.",
            app.config["MONGO_URI"],
            exc,
        )

    app.db = _db
    return _db


def get_db():
    if _db is None:
        raise RuntimeError("MongoDB has not been initialized yet. Call init_mongo(app) first.")
    return _db
