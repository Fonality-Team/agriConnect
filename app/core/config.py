from dotenv import load_dotenv
import os


class Config:
    """Configuration class to manage environment variables."""

    def __init__(self):
        load_dotenv()  # Load environment variables from .env file


    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///default.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
