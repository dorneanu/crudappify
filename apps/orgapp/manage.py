# Set the path
import os, sys
import csv
import pandas as pd
import json
from flask import Flask, current_app, jsonify
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager, prompt_bool
from werkzeug.serving import run_simple
from app import app, register_blueprints

# Factory app
def create_app(config=None):
    if config:
        app.config.from_object("config." + config)
    else:
        app.config.from_object("config.default")
    return app

# Add sub-managers
db_manager = Manager(app=app, help="DB Manager")

# Create app 
manager = Manager(create_app)
manager.add_option('-c', '--config', help='Configuration')
manager.add_command("db", db_manager)


# DB Manager ------------------------------------------------------------------
@db_manager.command
def drop():
    """ Drops database tables """
    from app.database import db_session as db, Base, engine
    import app.models

    if prompt_bool("[?] Are you sure you want to lose all your data"):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        db.commit()
        db.close()

@db_manager.command
def create():
    """ Creates database tables from sqlalchemy models and import samples """
    from app.database import db_session as db, Base, engine
    from utils.db import populate_from_samples
    import app.models

    Base.metadata.create_all(engine)
    populate_from_samples()

@db_manager.command
def recreate():
    """ Recreates database tables (same as issuing 'drop' and then 'create') """
    drop()
    create()

@db_manager.command
def populate():
    """ Populate database with default data (samples folder) """ 
    from utils.db import populate_from_samples
    populate_from_samples()

@db_manager.command
def init():
    """ Initialize db (calls recreate)"""
    recreate()
    print("[!] DB was successfully initialized!")

@db_manager.option('-o', '--output', help='Specify folder where to export JSON files')
def export(output=None):
    """ Export all tables to JSON files """
    from utils.db import export_tables

    try:
        export_tables(output)
    finally:
        print("[!] DB tables successfully exported to %s as JSON!" % output)

@db_manager.option('-t', '--table', dest='table', help='Table where to insert data', required=True)
@db_manager.option('-f', '--file', dest='jsonfile', help='JSON file to be imported', required=True)
def insert(table, jsonfile):
    """ Insert data from JSON file into table """
    from utils.db import insert_data
    
    try:
        insert_data(table, jsonfile)
    finally:
        print("[!] Imported data from <%s> into <%s> table!" % (jsonfile, table))

    
# Manager ---------------------------------------------------------------------
@manager.command
def run():
    # Register blueprints
    register_blueprints(app)

    # Run WSGI application
    run_simple(
        app.config['HOST'], 
        app.config['PORT'], 
        app, 
        use_reloader=app.config['RELOAD'],
        use_debugger=app.config['DEBUG']
    )

if __name__ == "__main__":
    manager.run()
