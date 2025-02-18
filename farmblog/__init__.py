from flask import Flask
import os
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager, login_required
from authlib.integrations.flask_client import OAuth

# Create the SQLAlchemy instance globally (only once)
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
oauth = OAuth()
mail = Mail()

def create_app():
    app = Flask(__name__)
    login_manager.login_view = 'login'
    migrate = Migrate(app, db)

    '''oauth.register("google",
                    client_id=app.config.get('OAUTH_CLIENT_ID'),
                    client_secret=app.config.get('OAUTH_CLIENT_SECRET'),
                    server_metadata_url=app.config.get('OAUTH_SERVER_METADATA_URL'),
                    client_kwargs={
                        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read",
                    }
                 )
    app.register_blueprint(google_blueprint, url_prefix="/login") '''

    # App configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI_2 = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agriculture.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
    app.config['OAUTH2_CLIENT_SECRET'] =os.environ.get('CLIENT_SECRET')
    app.config['OAUTH2_CLIENT_ID'] = os.environ.get('SECRET_ID')
    app.config['OAUTH2_META_URL'] = "https://accounts.google.com/well-known/openid-configuration"
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('USER_EMAIL')
    app.config['MAIL_PASSWORD'] = os.environ.get('USER_PASSWORD')
    
    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)

    # Import models after the app and db are initialized
    with app.app_context():
        from .models import Products, User, Message, Post
        from farmblog import routes

    # Create tables if they do not exist
    with app.app_context():
        db.create_all()

    return app

''' from flask import Flask, session, redirect, url_for
import os
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

# Initialize extensions globally
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
oauth = OAuth()  # OAuth instance created globally

def create_app():
    app = Flask(__name__)
    
    # App configurations
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agriculture.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    oauth.init_app(app)  # Initialize OAuth with app

    # Register Google OAuth provider
    oauth.register(
        'google',
        client_id=os.environ.get('OAUTH_CLIENT_ID'),
        client_secret=os.environ.get('OAUTH_CLIENT_SECRET'),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read",
        }
    )

    # Import models and routes
    with app.app_context():
        from .models import Products, User, Message, Post
        from . import routes

    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()

    return app

# Instantiate the app
app = create_app() '''