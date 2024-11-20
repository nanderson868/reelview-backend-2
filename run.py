# run.py
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig


def get_config_class():
    """Determine config class from environment variable"""
    config_type = os.getenv("FLASK_CONFIG", "development").lower()
    print(f"Config type: {config_type.capitalize()}")
    if config_type == "production" or config_type == "staging":
        return ProductionConfig
    elif config_type == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig


app = create_app(get_config_class())

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=5001)
