"""
Flask Extensions Initialization.

Extensions are instantiated here without binding to a specific app instance,
allowing the application factory (create_app) to initialize them cleanly.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
