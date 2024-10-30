from flask import Flask
import os
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required

# Create the SQLAlchemy instance globally (only once)
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    login_manager.login_view = 'login'
    migrate = Migrate(app, db)

    # App configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI_2 = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agriculture.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app)

    # Import models after the app and db are initialized
    with app.app_context():
        from .models import Products, User, Message, Post
        from farmblog import routes

    # Create tables if they do not exist
    with app.app_context():
        db.create_all()

    return app
