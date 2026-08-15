from datetime import datetime

from flask import Flask

from auth_utils import csrf_token, current_user
from config import Config
from extensions import init_mongo


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_mongo(app)

    from blueprints.auth import bp as auth_bp
    from blueprints.main import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_globals():
        return {
            "csrf_token": csrf_token,
            "current_user": current_user(),
            "current_year": datetime.utcnow().year,
        }

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template

        return render_template("errors.html", code=404, message="This reel doesn't exist."), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template

        return render_template("errors.html", code=500, message="Something jammed in the projector."), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
