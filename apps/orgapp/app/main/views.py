import json
import pandas as pd
import app.serializer as srlz
from flask import Blueprint, request, redirect, render_template, url_for, jsonify
from flask.views import MethodView
from app.models import App, Connection, Tag, AppType, Target
from app.database import db_session, Base, engine


apps = Blueprint('apps', __name__,)


@apps.route("/")
def index():
    return render_template("index.html")

@apps.route("/analysis/<table>")
def analysis(table=None):
    """ Create some table specific charts """
    if table == "apps":
        apps = App.query.all()
        return render_template('analysis/app.html')

    elif table == "targets":
        return render_template('analysis/target.html')
    else:
        return "<p>ERROR</p>"

@apps.route('/api/get/targets/<mode>')
def targets(mode=None):
    """ Returns targets """
    tags = [t.name for t in Tag.query.all()]
    tags_count = {}


    targets = db_session.query(Target)

    # Return tags
    if mode == "tags":
        # Return tags count for all targets
        for t in tags:
            count = targets.filter(Target.tags.any(Tag.name.startswith(t))).count()
            tags_count[t] = count

        # Transform to JSON
        df = pd.DataFrame(pd.Series(tags_count))
        df = df.reset_index()
        df.columns=['label', 'value']
        json_obj = df.to_dict(outtype="records")

        # Build dict
        json_dict = {
            "tags": json_obj,
            "discrete": [{ "key": "Cumulative Return", "values": json_obj }]
        }

        return jsonify(json_dict)

    # Return records
    elif mode == "table":
        serialized = srlz.TargetSerializer(targets.all(), many=True);
        json_dict = { "data" : serialized.data}

        return jsonify(json_dict)

    # No mode specified
    else:
        return 'No mode specified'


@apps.route('/api/get/apps/<mode>')
def applications(mode=None):
    """ Returns apps """
    applications = db_session.query(App)

    # Return tags
    if mode == "table":
        serialized = srlz.AppSerializer(applications.all(), many=True);
        json_dict = {'data': serialized.data}

        return jsonify(json_dict)

    # No mode specified
    else:
        return 'No mode specified'






