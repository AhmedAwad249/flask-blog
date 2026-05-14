"""
WSGI entry point for production servers (gunicorn, waitress, etc.).

Usage:
    gunicorn wsgi:app              (Linux/Mac)
    waitress-serve --port=8000 wsgi:app   (Windows alternative)

This uses ProductionConfig by default (debug=False, secure cookies).
"""

from blog_pro import create_app

app = create_app()  # defaults to 'config.ProductionConfig'
