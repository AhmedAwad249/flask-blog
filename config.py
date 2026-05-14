"""
Configuration classes for the Flask Blog application.

Usage:
    - DevelopmentConfig  → used by run.py (local development)
    - ProductionConfig   → used by wsgi.py and deployment platforms
    - TestingConfig      → used for automated tests (future)

All sensitive values are loaded from environment variables.
A .env file is supported for local development via python-dotenv.
"""

import os
from dotenv import load_dotenv

# Load .env file (only affects local dev — on platforms like Render
# the env vars are set directly in the dashboard)
load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    # --- Flask Core ---
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-CHANGE-ME-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Cloudinary ---
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

    # --- Security ---
    SESSION_COOKIE_HTTPONLY = True       # JS cannot read session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'     # Prevent CSRF via cross-site requests
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    # --- Upload validation ---
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
