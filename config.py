import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-CHANGE-ME-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')


    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url.startswith('postgresql') or _db_url.startswith('postgres://'):
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,      # Test connection before use (avoids stale connections)
            'pool_recycle': 300,        # Recycle connections every 5 minutes
            'pool_size': 5,             # Max persistent connections
            'max_overflow': 10,         # Extra connections allowed under load
        }

    SESSION_COOKIE_HTTPONLY = True       # JS cannot read session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'     # Prevent CSRF via cross-site requests
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


class DevelopmentConfig(Config):
    """Local development — debug ON, no HTTPS requirement."""
    DEBUG = True
    # SESSION_COOKIE_SECURE is False by default (OK for http://localhost)


class ProductionConfig(Config):
    """Production — debug OFF, HTTPS-only cookies."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Cookie only sent over HTTPS


class TestingConfig(Config):
    """Future: automated tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
