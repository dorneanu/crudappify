# Flask stuff
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin
from flask.ext.admin.contrib import sqla

# SQLAlchemy stuff
import sqlalchemy as sql
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

# Own DB
from app.database import Base
from app.database import db_session as db

# Create additional tables
app_tags_table = sql.Table('app_tags', Base.metadata,
                 sql.Column('app_id', sql.Integer, ForeignKey('app.app_id')),
                 sql.Column('tag_id', sql.Integer, ForeignKey('tag.id'))
)

target_tags_table  = sql.Table('target_tags', Base.metadata,
                sql.Column('target_id', sql.Integer, ForeignKey('target.id')),
                sql.Column('tag_id', sql.Integer, ForeignKey('tag.id'))
)

conn_tags_table = sql.Table('conn_tags', Base.metadata,
                 sql.Column('conn_id', sql.Integer, ForeignKey('connection.id')),
                 sql.Column('tag_id', sql.Integer, ForeignKey('tag.id'))
)

apps_bundles_table = sql.Table('apps_bundles', Base.metadata,
                sql.Column('bundle_id', sql.Integer, ForeignKey('appbundle.id')),
                sql.Column('app_id', sql.Integer, ForeignKey('app.app_id'))
)


class AppType(Base):
    """ Application types """
    __tablename__ = 'apptype'

    id = sql.Column(sql.Integer, primary_key=True)
    desc = sql.Column(sql.String(50), unique=True)

    def __unicode__(self):
        return self.desc

    def __str__(self):
        return self.desc


class App(Base):
    """ Table of applications """
    __tablename__ = "app"

    app_id = sql.Column(sql.Integer, primary_key=True)
    app_name = sql.Column(sql.Text)
    type_id = sql.Column(sql.Integer, sql.ForeignKey('apptype.id'))
    url = sql.Column(sql.Text)
    desc = sql.Column(sql.String(100))
    date_added = sql.Column(sql.Text)
    comments = sql.Column(sql.Text)

    # Contact details
    department_id = sql.Column(sql.Integer, sql.ForeignKey('department.id'))
    contact = sql.Column(sql.Text)

    # Target <-> Application mapping
    target_id = sql.Column(sql.Integer, sql.ForeignKey('target.id'))

    # Technical info
    version = sql.Column(sql.Text)
    environment = sql.Column(sql.Text)
    platform = sql.Column(sql.Text)

    # Scan details
    status = sql.Column(sql.Text)
    last_scan = sql.Column(sql.Text)
    reported_to_dpt = sql.Column(sql.Text)
    open_issues = sql.Column(sql.Text)

    # Define relationships
    app_type = relationship('AppType', backref='applications')
    department = relationship('Department', backref='applications')
    tags = relationship('Tag', secondary=app_tags_table)
    target = relationship('Target', backref='application')
    bundle = relationship('AppBundle', secondary=apps_bundles_table, backref="apps")

    def __unicode__(self):
        return self.desc

    def __str__(self):
        return self.desc


class AppBundle(Base):
    """ App bundles """
    __tablename__ = "appbundle"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.Text, unique=True)
    desc = sql.Column(sql.Text)
    contact = sql.Column(sql.Text)

    # Define relationships
    #apps = relationship('App', secondary=apps_bundles_table, backref="bundle")

    def __unicode__(self):
        #return "%d -> %s" % (self.id, self.name)
        return self.name

    def __str__(self):
        #return "%d -> %s" % (self.id, self.name)
        return self.name


class Target(Base):
    """ Table of targets """
    __tablename__ = "target"
    __table_args__ = (sql.UniqueConstraint('scheme', 'user', 'password', 'netloc', 'port', 'path', name='unique_target'),)

    id = sql.Column(sql.Integer, primary_key=True)
    scheme = sql.Column(sql.Text)
    user = sql.Column(sql.Text)
    password = sql.Column(sql.Text)
    netloc = sql.Column(sql.Text)
    port = sql.Column(sql.Integer)
    path = sql.Column(sql.Text)
    params = sql.Column(sql.Text)
    query = sql.Column(sql.Text)
    fragment = sql.Column(sql.Text)
    comments = sql.Column(sql.Text)

    # Add connection
    connection_id = sql.Column(sql.Integer, sql.ForeignKey('connection.id'))
    connection = relationship('Connection', backref="target")

    tags = relationship('Tag', secondary=target_tags_table)

    def to_string(self):
        """ Return object as string """
        url = self.scheme

        # Add user/password (if any)
        if self.user:
            if self.password:
                url += "://%s@%s" % (self.user, self.password)
        else:
            url += "://"

        # Add netloc
        url += self.netloc

        # Add port
        if self.port:
            url += ":%d" % self.port
        else:
            url += ":80"        # default port

        # Add path,
        url += "%s" % self.path

        return url

    def __unicode__(self):
        return self.netloc

    def __str__(self):
        return self.id


class Department(Base):
    """ Table of departments """
    __tablename__ = "department"
    __table_args__ = (sql.UniqueConstraint('org_id', 'desc', name='unique_org_department'),)

    id = sql.Column(sql.Integer, primary_key=True)
    org_id = sql.Column(sql.Integer, sql.ForeignKey("organization.id"))
    org = relationship('Organization', backref="departments")
    desc = sql.Column(sql.String(50))
    contact = sql.Column(sql.Text)

    def __unicode__(self):
        return "%s -> %s" % (self.org.desc, self.desc)

    def __str__(self):
        return "%s -> %s" % (self.org.desc, self.desc)


class Organization(Base):
    """ Table of organizations """
    __tablename__ = "organization"

    id = sql.Column(sql.Integer, primary_key=True)
    desc = sql.Column(sql.Text, unique=True)

    def __unicode__(self):
        return self.desc

    def __str__(self):
        return self.desc


class Connection(Base):
    """ Connection tables """
    __tablename__ = "connection"
    #__table_args__ = (sql.UniqueConstraint('url', 'port', name='unique_url_port'),)

    id = sql.Column(sql.Integer, primary_key=True)
    conn_type = sql.Column(sql.String(30))
    url = sql.Column(sql.Text)
    ip = sql.Column(sql.Text)
    port = sql.Column(sql.Integer)
    answer = sql.Column(sql.String(50))
    redirect = sql.Column(sql.Text)
    tags = relationship('Tag', secondary=lambda: conn_tags_table)



    tag_list = association_proxy('tags', 'name')

    def __unicode__(self):
        return "%d -> %s" % (self.id, self.url)

    def __str__(self):
        return "%d -> %s -> %d" % (self.id, self.url, self.port)


class Header(Base):
    __tablename__ = "header"

    id = sql.Column(sql.Integer, primary_key=True)
    conn_id = sql.Column(sql.Integer, ForeignKey('connection.id'))
    conn = relationship('Connection', backref="headers")
    header = sql.Column(sql.Text)
    value = sql.Column(sql.Text)


class DNS(Base):
    __tablename__  = "dns"

    id = sql.Column(sql.Integer, primary_key=True)
    domain = sql.Column(sql.Text)
    record = sql.Column(sql.Text)
    value = sql.Column(sql.Text)


class Tag(Base):
    """ Table for tags """
    __tablename__ = "tag"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.Text, unique=True)
    desc = sql.Column(sql.Text)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name
