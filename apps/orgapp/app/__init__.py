import os

from flask import Flask, current_app, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Define the WSGI application object
# The app will be configured later.
app = Flask(__name__)

def register_blueprints(app):
    # Add (fake) admin blueprint 
    from app.admin.views import admin

    # Add the main app
    from app.main.views import apps
    app.register_blueprint(apps)