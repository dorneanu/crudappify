import json
import pandas as pd
from flask import Blueprint, request, redirect, render_template, url_for, jsonify
from flask.views import MethodView
from app.models import App, Connection, Tag, AppType, Target
from app.database import db_session, Base, engine

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
        conns = Connection.query.all()

        # Generate json data
        raw_data = [
            {'url' : c.url, 'port' : c.port, 'answer' : c.answer}
            for c in conns
        ]
        json_data = json.dumps(raw_data)

        return render_template('charts/connection.html', json_data=json_data)
    else:
        return "<p>ERROR</p>"

@apps.route("/get/targets")
def targets():
    """ Returns targets """
    tags = [t.name for t in Tag.query.all()]
    tags_count = {}

    targets = db_session.query(Target)
    # Return tags count for all targets
    for t in tags:
        count = targets.filter(Target.tags.any(Tag.name.startswith(t))).count()
        tags_count[t] = count
        
    # Transform to JSON
    df = pd.DataFrame(pd.Series(tags_count))
    df = df.reset_index()
    df.columns=['label', 'value']
    json_obj = df.to_dict(outtype="records")
    json_dict = { "tags": json_obj, "discrete": [{ "key": "Cumulative Return", "values": json_obj }]}

    return jsonify(json_dict)
 