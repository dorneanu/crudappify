# Set the path
import os, sys
import csv
from flask import Flask
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager, Server
from app import app

manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    port = '5000',
    host = '127.0.0.1')
)

@manager.command
def initdb():
    """  Read data from CSV files and init DB """
    from app.database import db_session, Base, engine
    from app.models import App, AppType, Organization, Department, Tag, Connection

    # Create new DB
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def get_csv_data(file_path):
        """ Returns the header and the row data """
        reader = csv.reader(open(file_path))
        header = next(reader)

        return (header,reader)

    # Tags
    for row in get_csv_data('samples/tags.csv')[1]:
        tag = Tag(name=row[0])
        db_session.add(tag)
        db_session.commit()

    # Organizations
    for row in get_csv_data('samples/organizations.csv')[1]:
        org = Organization(desc=row[0])
        db_session.add(org)
        db_session.commit()

    # Departments
    for row in get_csv_data('samples/departments.csv')[1]:
        org = db_session.query(Organization).filter_by(desc=row[0]).one()
        dpt = Department(desc=row[1], org=org)

        db_session.add(dpt)
        db_session.commit()

    # Application types
    for row in get_csv_data('samples/apptypes.csv')[1]:
        apptype = AppType(desc=row[0])
        db_session.add(apptype)
        db_session.commit()

    # Applications
    for row in get_csv_data('samples/applications.csv')[1]:
        apptype = db_session.query(AppType).filter_by(desc=row[1]).one()
        dpt = db_session.query(Department).join(Organization).\
              filter(Department.desc==row[2]).\
              filter(Organization.desc==row[3]).\
              one()
        app = App(desc=row[0], app_type=apptype, department=dpt)

        db_session.add(app)
        db_session.commit()

    # Connections
    for row in get_csv_data('samples/connections.csv')[1]:
        conn = Connection(url=row[0], port=row[1], answer=row[2], header=row[3], value=row[4])
        db_session.add(conn)
        db_session.commit()


    print("DB was successfully initialized!")
    db_session.close()

if __name__ == "__main__":
    manager.run()
