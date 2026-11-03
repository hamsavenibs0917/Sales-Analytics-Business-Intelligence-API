import os
from app import create_app
from app.extensions import db
from app.models.sale import Sale
from scripts.seed_db import seed_database

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

# Auto-create tables and auto-seed if database is fresh / empty
with app.app_context():
    db.create_all()
    try:
        if Sale.query.count() == 0:
            print("Empty database detected: auto-seeding with master data and sample sales...")
            seed_database(app)
    except Exception as e:
        print(f"Notice: Auto-seed check: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = env == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
