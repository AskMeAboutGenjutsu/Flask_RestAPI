from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_api.config import Config


jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    @app.teardown_appcontext
    def shutdown_session(exeption=None):
        db.session.remove()

    from flask_api.User_app.views import user_app_bp
    from flask_api.Car_app.views import car_app_bp

    app.register_blueprint(user_app_bp)
    app.register_blueprint(car_app_bp)

    return app
