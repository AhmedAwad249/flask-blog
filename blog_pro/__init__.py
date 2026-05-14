"""
Blog Pro — Flask Application Factory
=====================================

This module creates and configures the Flask application.

Usage:
    from blog_pro import create_app
    app = create_app()                          # defaults to ProductionConfig
    app = create_app('config.DevelopmentConfig') # for local dev
"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import cloudinary
import cloudinary.uploader
import cloudinary.api

# ---------------------------------------------------------------------------
# Extensions (created once, initialized in create_app)
# ---------------------------------------------------------------------------
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config_class='config.ProductionConfig'):
    """
    Application factory.

    Args:
        config_class: dotted path to a config class (str).
                      Defaults to ProductionConfig (safe default).
                      Use 'config.DevelopmentConfig' for local dev.
    """
    app = Flask(__name__)

    # ── Load configuration ────────────────────────────────────────────
    app.config.from_object(config_class)

    # ── Fix Render/Railway DATABASE_URL (postgres:// → postgresql://) ─
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_url.startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
            'postgres://', 'postgresql://', 1
        )

    # ── Initialize extensions ─────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # ── Configure Cloudinary from environment variables ───────────────
    cloud_name = app.config.get('CLOUDINARY_CLOUD_NAME')
    api_key = app.config.get('CLOUDINARY_API_KEY')
    api_secret = app.config.get('CLOUDINARY_API_SECRET')

    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
    else:
        app.logger.warning(
            '⚠️  Cloudinary credentials not set! '
            'Image uploads will fail. '
            'Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, '
            'and CLOUDINARY_API_SECRET environment variables.'
        )

    # ── Security headers ──────────────────────────────────────────────
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # ── Register blueprints ───────────────────────────────────────────
    from blog_pro import routes
    from .routes import main_bp
    from .post.routes import post_bp
    from .auth.routes import auth_bp
    from .profile.routes import profile

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(profile)

    # ── CLI commands ──────────────────────────────────────────────────
    @app.cli.command('init-db')
    def init_db_command():
        """Create all database tables."""
        db.create_all()
        print('Database tables created successfully.')

    return app
