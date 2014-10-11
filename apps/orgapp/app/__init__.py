from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Define the WSGI application object
app = Flask(__name__)

# Configurations
# TODO: Add several environments/configurations
app.config.from_object('config')


def register_blueprints(app):
    # Add (fake) admin blueprint 
    from app.admin.views import admin

    # Add the main app
    from app.main.views import apps
    app.register_blueprint(apps)


# Register blueprint(s)
register_blueprints(app)

