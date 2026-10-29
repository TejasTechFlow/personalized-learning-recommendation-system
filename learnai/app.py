from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect

from config import Config
from models.database import db

def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update(overrides or {})
    db.init_app(app)
    CSRFProtect(app)

    from routes.pages import bp as pages
    from routes.api import bp as api
    app.register_blueprint(pages)
    app.register_blueprint(api, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", message="That page doesn't exist."), 404

    @app.errorhandler(Exception)
    def server_error(e):  # never show raw stack traces to users
        app.logger.exception(e)
        return render_template("error.html", message="Something went wrong. Please try again."), 500

    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    create_app().run(debug=True)
