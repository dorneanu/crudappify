# Set the path
import os, sys
import csv
import pandas as pd
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
    import pandas as pd
    import csv
    import json
    from app.database import db_session as db, Base, engine
    from app.models import App, AppType, Organization, Department, Tag, Connection, Header
    from app.serializer import \
        TagSerializer, ConnectionSerializer, HeaderSerializer,\
        AppTypeSerializer, OrganizationSerializer, AppSerializer,\
        DepartmentSerializer

    # Get list of tables
    tables = Base.metadata.tables

    # Create table <-> models mapping:
    #   table -> (<model>, <serializer>)
    table_models_map = { 
        'apptype':      (AppType, AppTypeSerializer),
        'application':  (App, AppSerializer),
        'organization': (Organization, OrganizationSerializer),
        'department':   (Department, DepartmentSerializer),
        'tag':          (Tag, TagSerializer),
        'connection':   (Connection, ConnectionSerializer),
        'header':       (Header, HeaderSerializer)
    }

    if output:
        # Export tables to JSON
        tables = ['department', 'organization', 'connection', 'tag', 'header', 'apptype', 'application']
        for t in tables:
            print("Exporting %s ..." % t)
            result = [i for i in table_models_map[t][0].query.all()]
            serialized = table_models_map[t][1](result, many=True)

            with open(output + "/" + t + ".json", 'w') as outfile:
                json.dump(serialized.data, outfile, sort_keys=True, indent=2)

        print("[!] DB tables successfully exported to %s as JSON!" % output)
    else:
        print("[!] output folder not specified. Aborted.")
    

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
