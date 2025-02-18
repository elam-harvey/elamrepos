from flask import Flask, render_template, request, redirect, url_for, flash
from flask import current_app as app
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_admin import Admin
import os

# Initialize your database and login manager
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
admin = Admin(name="Admin Panel", template_mode='bootstrap4')

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bnb.db'
    app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY2')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    admin.init_app(app)

     # Import models after the app and db are initialized
    with app.app_context():
        from .models import  User, Room, Payments, Bookings
        from KILIFI import routes
        # adding Models to admin site
        admin.add_view(AdminModelView(Room, db.session))
        admin.add_view(AdminModelView(Payments, db.session))
        admin.add_view(AdminModelView(User, db.session))
        admin.add_view(AdminModelView(Bookings, db.session))

    # Create tables if they do not exist
    with app.app_context():
        migrate = Migrate(app, db)
        db.create_all()

    return app