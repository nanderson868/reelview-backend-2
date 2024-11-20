# __init__.py
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from .routes import routes_blueprint
from .extensions import db, limiter
from config import DevelopmentConfig


def create_app(config_class=DevelopmentConfig):

    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": config_class.allowed_origins()}})

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)

    # Initialize migration engine
    Migrate(app, db)

    # Register blueprints
    with app.app_context():
        app.register_blueprint(routes_blueprint)

    return app
