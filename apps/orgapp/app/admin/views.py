from flask import Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.base import MenuLink
from flask.ext.admin.babel import gettext, ngettext, lazy_gettext
from flask.ext.admin.form import Select2TagsWidget, Select2Field, Select2TagsField, rules
from flask.ext.admin.actions import action
from wtforms import validators, fields

from app import app
from app.database import db_session
from app.models import AppType, App, AppBundle, Target, Organization, Department, Connection, Header, Tag
from app.models import conn_tags_table


class AppTypeAdmin(sqla.ModelView):
    list_template = "list.html"
    column_display_pk = False
    form_columns= ['desc']


class AppAdmin(sqla.ModelView):
    list_template = "list.html"
    column_display_pk = False

    # Allow only pre-defined values
    form_overrides = dict(severity=fields.SelectField)
    form_args = dict(
        severity = dict(
            choices = [('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]
    ))

    form_columns = [
        'app_name', 'desc', 'app_type', 'bundle',
        'version', 'environment', 'platform',
        'department', 'contact',
        'date_added',
        'status', 'last_scan', 'reported_to_dpt', 'open_issues',
        'severity', 'tags', 'url', 'comments'
    ]

    # Add here list of columns where to search
    column_searchable_list = ('desc', 'url', 'version', 'environment', 'platform', 'contact', AppBundle.name, Tag.name)

    # Define here filters
    column_filters = ('desc', 'app_name', 'department', 'app_type', 'url', 'app_id', 'version', 'environment', 'platform', 'date_added', 'tags', 'severity')

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
        },
        'bundle':   {
            'fields': (AppBundle.name, AppBundle.desc,)
        }
    }

    # Group fields
    form_create_rules = [
        rules.FieldSet(('app_name', 'desc', 'app_type', 'bundle', 'url', 'severity', 'tags', 'comments'), 'Application'),
        rules.FieldSet(('version', 'environment', 'platform', 'status'), 'Technical details'),
        rules.FieldSet(('contact', 'department'), 'Contact'),
        rules.FieldSet(('open_issues', 'last_scan', 'reported_to_dpt'), 'Audit details'),
    ]
    # Use same rule set for editing pages
    form_edit_rules = form_create_rules

    def __init__(self, session):
        # Just call parent class with predefined model
        super(AppAdmin, self).__init__(App, session)


class AppBundleAdmin(sqla.ModelView):
    list_template = "list.html"


class TargetAdmin(sqla.ModelView):
    list_template = "list.html"
    column_display_pk = False

    # Allow only pre-defined values
    form_overrides = dict(priority=fields.SelectField)
    form_args = dict(
        priority = dict(
            choices = [('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]
    ))

    column_filters = ('scheme', 'user', 'password', 'netloc', 'port', 'path', 'params', 'query', 'fragment', 'priority', 'comments')
    column_searchable_list = ('scheme', 'user', 'password', 'netloc', 'path', 'params', 'query', 'fragment', 'priority', 'comments', Tag.name)

    form_ajax_refs = {
        'tags': {
            'fields': (Tag.name,)
        }
    }

    # Group fields
    form_create_rules = [
        rules.FieldSet(('scheme', 'user', 'password', 'netloc', 'port', 'path', 'query', 'fragment'), 'URL Info'),
        rules.FieldSet(('priority', 'tags', 'comments', 'connection'), 'Audit details')
    ]
    # Use same rule set for editing pages
    form_edit_rules = form_create_rules

    @expose("/export")
    def action_export(self):
        return '<p>Not implemented yet</p>'

    @action('scan', 'Scan')
    def action_scan(self, ids):
        import json
        from utils.connection import send_request
        t = []
        data = []
        for id in ids:
            headers = []
            target = db_session.query(Target).filter_by(id=id).one()
            t.append(target.to_string())

            # Connect to target
            response = send_request(target.to_string(), t)

            # Collect headers
            for r in response.headers:
                headers.append({'header': r, 'value': response.headers[r]})

            data.append({'id': id, 'data': headers})

        return json.dumps(data, indent=2)


    def __init__(self, session):
        super(TargetAdmin, self).__init__(Target, session)


class OrgAdmin(sqla.ModelView):
    # list_template = "list.html"
    column_display_pk = True



class DepartmentAdmin(sqla.ModelView):
    list_template = "list.html"
    column_display_pk = False
    form_columns = ['org', 'desc', 'contact']
    column_searchable_list = ('desc', Organization.desc)
    column_filters = ('desc', 'org')

    form_args = dict(
        text=dict(label='Big Text', validators=[validators.required()])
    )

    form_ajax_refs = {
        'org': {
            'fields': (Organization.desc,)
        }
    }

    def __init__(self, session):
        # Just call parent class with predefined model
        super(DepartmentAdmin, self).__init__(Department, session)


class ConnectionAdmin(sqla.ModelView):
    list_template = "list.html"
    column_display_pk = False
    form_columns = ['conn_type', 'url', 'port', 'answer', 'redirect', 'tags']
    column_searchable_list = ('conn_type', 'url', 'answer', 'redirect', 'ip', Tag.name)
    column_filters = ('conn_type', 'url', 'port', 'answer', 'redirect', 'ip', Tag.name)

    # Define which fields should be preloaded by Ajax
    form_ajax_refs = {
        'tags': {
            'fields': (Tag.name,)
        }
    }


class HeaderAdmin(sqla.ModelView):
    list_template = "list.html"
    form_columns = ['conn_id', 'header', 'value']


# Add admin functionality
admin = Admin(app, name="Admin App Survey", url="/admin", base_template="layout-admin.html", template_mode="bootstrap3")

# Add models views
admin.add_view(AppTypeAdmin(AppType, db_session))
admin.add_view(sqla.ModelView(Tag, db_session))
admin.add_view(AppAdmin(db_session))
admin.add_view(AppBundleAdmin(AppBundle, db_session))
admin.add_view(ConnectionAdmin(Connection, db_session))
admin.add_view(HeaderAdmin(Header, db_session))
admin.add_view(OrgAdmin(Organization, db_session))
admin.add_view(DepartmentAdmin(db_session))
admin.add_view(TargetAdmin(db_session))

