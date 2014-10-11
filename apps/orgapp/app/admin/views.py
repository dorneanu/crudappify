from flask import Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin import Admin
from flask.ext.admin.base import MenuLink
from wtforms import validators

from app import app
from app.database import db_session
from app.models import AppType, App, Organization, Department, Connection, Tag


class CustomView(sqla.ModelView):
    """ Customized admin interface """
    list_template = "list.html"
    create_template = "create.html"
    edit_template = "edit.html"


class AppTypeAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns= ['id', 'desc']


class AppAdmin(sqla.ModelView):
    column_display_pk = False
    form_columns = ['desc', 'app_type', 'department', 'url', 'date_added', 'tags']

    # Add here list of columns where to search
    column_searchable_list = ('desc', 'url', Tag.name)

    # Define here filters
    column_filters = ('desc', 'department', 'app_type', 'url', 'app_id', 'date_added', 'tags')


    # Define which fields should be preloaded by Ajax
    form_ajax_refs = {
        'tags': {
            'fields': (Tag.name,)
        },
        'app_type': {
            'fields': (AppType.desc,)
        },
        'department': {
            'fields': (Department.desc,)
        }
    }

    def __init__(self, session):
        # Just call parent class with predefined model
        super(AppAdmin, self).__init__(App, session)


class OrgAdmin(sqla.ModelView):
    column_display_pk = True


class DepartmentAdmin(sqla.ModelView):
    column_display_pk = False
    form_columns = ['org_id', 'desc']
    column_searchable_list = ('desc', Organization.desc)
    column_filters = ('desc', 'org')

    form_args = dict(
        text=dict(label='Big Text', validators=[validators.required()])
    )

    def __init__(self, session):
        # Just call parent class with predefined model
        super(DepartmentAdmin, self).__init__(Department, session)


class ConnectionAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['conn_id', 'url', 'port', 'answer', 'header', 'value']
    column_searchable_list = ('url', 'answer', 'header', 'value')
    column_filters = ('url', 'port', 'answer', 'header', 'value')


# Add admin functionality
admin = Admin(app, name="Admin App Survey", url="/admin", base_template="layout-admin.html", template_mode="bootstrap3")
#admin = Admin(app, name="Admin App Survey", url="/admin")

# Add views
admin.add_view(AppTypeAdmin(AppType, db_session))
admin.add_view(sqla.ModelView(Tag, db_session))
admin.add_view(AppAdmin(db_session))
admin.add_view(ConnectionAdmin(Connection, db_session))
admin.add_view(OrgAdmin(Organization, db_session))
admin.add_view(DepartmentAdmin(db_session))
