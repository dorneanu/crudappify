import csv
import json

from app.database import db_session, Base, engine
from app.models import App, Target, AppType, Organization, Department, Tag, Connection, Header
from app.serializer import \
        TagSerializer, ConnectionSerializer, HeaderSerializer,\
        AppTypeSerializer, OrganizationSerializer, AppSerializer,\
        DepartmentSerializer, TargetSerializer
from utils.insert import AppTypeInsert, AppInsert, TargetInsert, DepartmentInsert,\
        OrganizationInsert, TagInsert, ConnectionInsert, HeaderInsert

# Create table <-> models mapping:
#   table -> (<model>, <serializer>, <insert>)
table_models_map = { 
    'apptype':      {
        'model': AppType, 
        'serializer': AppTypeSerializer,
        'insert': AppTypeInsert
    },
    'application':  {
        'model': App, 
        'serializer': AppSerializer,
        'insert': AppInsert
    },
    'organization': {
        'model': Organization, 
        'serializer': OrganizationSerializer,
        'insert': OrganizationInsert
    },
    'department':   {
        'model': Department, 
        'serializer': DepartmentSerializer,
        'insert': DepartmentInsert
    },
    'tag':          {
        'model': Tag, 
        'serializer': TagSerializer, 
        'insert': TagInsert
    },
    'connection':   {
        'model': Connection, 
        'serializer': ConnectionSerializer, 
        'insert': ConnectionInsert
    },
    'header':       {
        'model': Header, 
        'serializer': HeaderSerializer,
        'insert': HeaderInsert
    },
    'target':       {
        'model': Target,
        'serializer': TargetSerializer,
        'insert': TargetInsert
    }
}

def get_csv_data(file_path):
    """ Returns the CSV data as dictionary """
    reader = csv.DictReader(open(file_path), delimiter="\t")
    result = []
    for row in reader:
        result.append(row)

    return result

def populate_from_samples():
    """  Read data from CSV files and init DB """

    # Tags
    try:
        for row in get_csv_data('samples/tags.csv'):
            tag = Tag(name=row['Name'], desc=row['Description'])
            db_session.add(tag)
    finally:
        db_session.commit()

    # Organizations
    try:
        for row in get_csv_data('samples/organizations.csv'):
            org = Organization(desc=row['Name'])
            db_session.add(org)
    finally:
        db_session.commit()

    # Departments
    try:   
        for row in get_csv_data('samples/departments.csv'):
            org = db_session.query(Organization).filter_by(desc=row['Organization']).one()
            dpt = Department(desc=row['Department'], org=org)

            db_session.add(dpt)
    finally:
        db_session.commit()

    # Application types
    try:
        for row in get_csv_data('samples/apptypes.csv'):
            apptype = AppType(desc=row['Name'])
            db_session.add(apptype)
    finally:
        db_session.commit()

    # Applications
    try:
        for row in get_csv_data('samples/applications.csv'):
            apptype = db_session.query(AppType).filter_by(desc=row['AppType']).one()
            dpt = db_session.query(Department).join(Organization).\
                  filter(Department.desc==row['Department']).\
                  filter(Organization.desc==row['Organization']).\
                  one()

            app = App(desc=row['Application'], 
                      app_type=apptype, 
                      department=dpt,
                      version=row['Version'],
                      environment=row['Environment'],
                      platform=row['Platform']
            )

            db_session.add(app)
    finally:
        db_session.commit()

    # Connections and Headers
    try:
        for row in get_csv_data('samples/connections.csv'):
            conn = Connection(conn_type=row['Type'], url=row['URL'], port=row['Port'], answer=row['Answer'])
            header = Header(conn_id=conn.id, header=row['Header'], value=row['Value'], conn=conn)

            db_session.add(conn)
            db_session.add(header)
    finally:
        db_session.commit()

def export_tables(output=None):
    """ Export all tables to JSON files """
    # Get list of tables
    tables = Base.metadata.tables

    if output:
        # Export tables to JSON
        tables = table_models_map.keys()
        for t in tables:
            print("Exporting %s ..." % t)
            
            result = [i for i in db_session.query(table_models_map[t]['model']).all()]
            serialized = table_models_map[t]['serializer'](result, many=True)

            # Write to JSON file
            with open(output + "/" + t + ".json", 'w') as outfile:
                json.dump(serialized.data, outfile, sort_keys=True, indent=2)

    else:
        print("[!] output folder not specified. Aborted.")

def insert_data(table, jsonfile):
    """ Insert data into table from jsonfile """
    with open(jsonfile) as infile:
        data = json.load(infile)
        table_models_map[table]['insert'](data)