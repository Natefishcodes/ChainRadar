import os

class Config:
    # Secret key for securely signing session cookies
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")

    # Database connection string (SQLite for now, but can be upgraded to PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///site.db")

    # Turn off the SQLAlchemy event system to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bot tokens (replace with your actual tokens)
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "your_discord_bot_token")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your_telegram_bot_token")
