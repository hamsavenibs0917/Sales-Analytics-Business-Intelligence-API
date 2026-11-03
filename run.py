import os
from app import create_app
from app.extensions import db

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

# Auto-create tables for local development convenience
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = env == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
