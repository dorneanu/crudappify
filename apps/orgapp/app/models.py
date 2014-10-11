# Flask stuff
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin
from flask.ext.admin.contrib import sqla

# SQLAlchemy stuff
import sqlalchemy as sql
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

# Own DB
from app.database import Base
from app.database import db_session as db

# Create additional tables
app_tags_table = sql.Table('app_tags', Base.metadata,
                 sql.Column('app_id', sql.Integer, ForeignKey('app.app_id')),
                 sql.Column('tag_id', sql.Integer, ForeignKey('tag.id'))
)

conn_tags_table = sql.Table('conn_tags', Base.metadata,
                 sql.Column('conn_id', sql.Integer, ForeignKey('connection.id')),
                 sql.Column('tag_id', sql.Integer, ForeignKey('tag.id'))
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
    type_id = sql.Column(sql.Integer, sql.ForeignKey('apptype.id'))
    url = sql.Column(sql.Text)
    desc = sql.Column(sql.String(100))
    date_added = sql.Column(sql.Text)
    department_id = sql.Column(sql.Integer, sql.ForeignKey('department.id'))

    # Technical info
    version = sql.Column(sql.Text)
    environment = sql.Column(sql.Text)
    platform = sql.Column(sql.Text)

    # Define relationships
    app_type = relationship('AppType', backref='applications')
    department = relationship('Department', backref='applications')
    tags = relationship('Tag', secondary=app_tags_table)

    def __unicode__(self):
        return self.desc

    def __str__(self):
        return self.desc


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
    port = sql.Column(sql.Integer)
    answer = sql.Column(sql.String(50))
    redirect = sql.Column(sql.Text)
    tags = relationship('Tag', secondary=conn_tags_table)

    def __unicode__(self):
        return self.url

    def __str__(self):
        return "%s -> %d" % (self.url, self.port)


class Header(Base):
    __tablename__ = "header"

    id = sql.Column(sql.Integer, primary_key=True)
    conn_id = sql.Column(sql.Integer, ForeignKey('connection.id'))
    conn = relationship('Connection', backref="headers")
    header = sql.Column(sql.Text)
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
        