# app/config.py
import os

class Config:
    """Configuration class for Flask application."""
    
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev_secret_change_in_production")
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL") or "sqlite:///marketing.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Connection pool settings for better stability
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 300,    # Recycle connections every 5 minutes
        "pool_size": 10,        # Maximum number of connections
        "max_overflow": 20      # Maximum overflow connections
    }
    
    # === Open Graph defaults ===
    OG_SITE_NAME = os.getenv("OG_SITE_NAME", "Andrii-IT")
    OG_TITLE = os.getenv("OG_TITLE", "Marketing Agent - KI-gestützte Marketing Automation")
    OG_DESCRIPTION = os.getenv("OG_DESCRIPTION", "Erstellen und veröffentlichen Sie professionelle Social-Media-Inhalte automatisch auf Telegram, Facebook, Instagram und LinkedIn mit OpenAI-Technologie.")
    OG_IMAGE_ABS = os.getenv("OG_IMAGE_ABS", "")  # повний https-URL (рекомендовано). Якщо пусто — зберемо з request.url_root
    OG_LOCALE = os.getenv("OG_LOCALE", "de_DE")
    
    # === Meta Pixel ===
    META_PIXEL_ID = os.getenv("META_PIXEL_ID", "")
    
    # === Stripe ===
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
