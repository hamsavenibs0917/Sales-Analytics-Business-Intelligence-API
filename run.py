import os
from app import create_app
from app.extensions import db
from app.models.sale import Sale
from scripts.seed_db import seed_database

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

# Safely ensure database tables exist without crashing multi-worker Gunicorn boot
try:
    with app.app_context():
        db.create_all()
except Exception as err:
    app.logger.warning(f"Database table verification notice: {err}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = env == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
