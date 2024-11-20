# config.py
import os
import logging
from app.models import *
from app.extensions import db


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = []

    @classmethod
    def init_app(cls, app):
        app.config["CORS_ORIGINS"] = cls.allowed_origins()
        cls.init_logging(app)

    @staticmethod
    def prepare_database_uri(env_var):
        uri = os.getenv(env_var, "")
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        return uri

    @staticmethod
    def init_logging(app):
        logging.basicConfig(
            level=app.config.get("LOG_LEVEL", logging.INFO),
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.info("Logging initialized")
        logging.info(f"Configuring app for: {app.config['CONFIG_NAME']}")

    @classmethod
    def allowed_origins(cls):
        return cls.CORS_ORIGINS


class ProductionConfig(Config):
    DEBUG = False
    CONFIG_NAME = "Production"
    LOG_LEVEL = logging.INFO
    CORS_ORIGINS = ["https://www.reelview.io", "https://reelview.io"]
    SQLALCHEMY_DATABASE_URI = Config.prepare_database_uri("DATABASE_URL_PRODUCTION")


class DevelopmentConfig(Config):
    DEBUG = True
    CONFIG_NAME = "Development"
    LOG_LEVEL = logging.DEBUG
    CORS_ORIGINS = [
        "http://localhost:3000",
        "https://editor.swagger.io",
    ]
    SQLALCHEMY_DATABASE_URI = Config.prepare_database_uri("DATABASE_URL_DEVELOPMENT")


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    CONFIF_NAME = "Testing"
    LOG_LEVEL = logging.CRITICAL
    CORS_ORIGINS = ["http://localhost:3000"]
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
