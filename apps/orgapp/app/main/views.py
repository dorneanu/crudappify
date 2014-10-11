from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from app.models import App, Connection, Tag, AppType

apps = Blueprint('apps', __name__,)


@apps.route("/")
def index():
    return render_template("index.html")
    
@apps.route("/list/<table>")
def list(table=None):
    """ List specified table """
    if table == "apps":
        apps = App.query.all()
        return render_template('list/app.html', apps=apps)

    elif table == "apptypes":
        apptypes = AppType.query.all()
        return render_template('list/apptype.html', types=apptypes)

    elif table == "connections":
        conns = Connection.query.all()
        return render_template('list/connection.html', connections=conns)

    elif table == "tags":
        tags = Tag.query.all()
        return render_template('list/tag.html', tags=tags)

    else:
        return "<p>ERROR</p>"

@apps.route("/charts/<table>")
def charts(table=None):
    """ Create some table specific charts """
    if table == "apps":
        apps = App.query.all()
        return render_template('charts/app.html', apps=apps)

    elif table == "connections":
        import json
        conns = Connection.query.all()

        # Generate json data
        raw_data = [
            {'url' : c.url, 'port' : c.port, 'answer' : c.answer, 'header': c.header} 
            for c in conns
        ]
        json_data = json.dumps(raw_data)

        return render_template('charts/connection.html', json_data=json_data)

    else:
        return "<p>ERROR</p>"

