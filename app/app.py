from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

def create_app():
    app = Flask(__name__)

    # Set a secret key for session management
    app.config["SECRET_KEY"] = "6566c7c812959a3f34d1a24c902c5470261a2c87cb2177391cf2d16c9f1cea11"  # Replace with your generated key

    # Configure MongoDB
    app.config["MONGO_URI"] = "mongodb://localhost:27017/yourdatabase"  # Include your database name
    mongo = PyMongo(app)

    # Configure JWT
    app.config["JWT_SECRET_KEY"] = "6566c7c812959a3f34d1a24c902c5470261a2c87cb2177391cf2d16c9f1cea11"  # Replace with your generated key
    jwt = JWTManager(app)

    # Configure Bcrypt
    bcrypt = Bcrypt(app)

    # Register Blueprints
    from .routes import main  # Use relative import to avoid circular import
    app.register_blueprint(main)

    # Attach global objects to the app
    app.mongo = mongo
    app.bcrypt = bcrypt
    app.jwt = jwt

    return app
