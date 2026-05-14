"""
Local development entry point.

Run with:  python run.py
This uses DevelopmentConfig (debug=True, reads .env file).
"""

from blog_pro import create_app, db

app = create_app('config.DevelopmentConfig')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)