# Set the path
import os, sys
import csv
import json
from flask import Flask, current_app, jsonify
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager, prompt_bool, Command, Option
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

# Gunicorn -------------------------------------------------------------------
class GunicornServer(Command):

    description = 'Run the app within Gunicorn'

    def __init__(self, host='0.0.0.0', port=int(os.environ.get("PORT", 33507)), workers=4):
        self.port = port
        self.host = host
        self.workers = workers

    def get_options(self):
        return [
            Option('-t', '--host', dest='host', default=self.host),
            Option('-p', '--port', dest='port', type=int, default=self.port),
            Option('-w', '--workers', dest='workers', type=int, default=self.workers),
        ]

    def run(self, *args, **kwargs):
        from gunicorn.app.base import Application
        host = kwargs['host']
        port = kwargs['port']
        workers = kwargs['workers']

        # Register blueprints
        register_blueprints(app)

        print("Starting gunicorn server on %s:%d ...\n " % (host, port))
        class FlaskApplication(Application):
            def init(self, parser, opts, args):
                return {
                    'bind': '{0}:{1}'.format(host, port),
                    'workers': workers
                }

            def load(self):
                return app

        FlaskApplication().run()

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

@db_manager.option('-t', '--table', dest='table', help='Table where to insert data')
@db_manager.option('-f', '--file', dest='jsonfile', help='JSON file to be imported')
@db_manager.option('-d', '--directory', dest="directory", help="Insert all JSON files from directory.")
def insert(table=None, jsonfile=None, directory=None):
    """ Insert data from JSON file into table """
    from utils.db import insert_data
    from os import walk
    from os.path import basename, splitext, join

    # Use file names as table names
    if directory:
        for (dirpath, dirnames, filenames) in walk(directory):
            for f in filenames:
                file_path = join(dirpath, f)
                (table, suffix) = splitext(basename(file_path))

                # Regard only JSON files
                if suffix == ".json":
                    insert_data(table, file_path)


    # Insert file
    elif jsonfile and table:
        insert_data(table, jsonfile)
        print("[!] Imported data from <%s> into <%s> table!" % (jsonfile, table))

    else:
        print("[!] Error! See --help")


# Manager ---------------------------------------------------------------------
@manager.command
def devrun():
    """ Run debugable web server """
    # Register blueprints
    register_blueprints(app)

    run_simple(
        app.config['HOST'],
        app.config['PORT'],
        app,
        use_reloader=app.config['RELOAD'],
        use_debugger=app.config['DEBUG']
    )

# Add gunicorn command to the manager
manager.add_command("gunicorn", GunicornServer())

if __name__ == "__main__":
    manager.run()
