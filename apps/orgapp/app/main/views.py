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

    # Return priorities
    elif mode == "priority":
        from sqlalchemy import func
        colors = {'high': '#FD0000', 'medium': '#FF8000', 'low': '#ffff00', 'none': '#eeeeee'}
        json_prio = []
        # Return priority count for all targets
        priorities = db_session.query(Target.priority, func.count(Target.priority)).group_by(Target.priority).all()
        for p in priorities:
            if p[0]:
                json_prio.append({'label': p[0], 'value': p[1], 'color': colors[p[0].lower()]})
            else:
                json_prio.append({'label': 'None', 'value': p[1], 'color': colors['none']})


        # Build dict
        json_dict = {
            "priorities": json_prio,
            "discrete": [{ "key": "Cumulative Return", "values": json_prio }]
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

    # Return severities
    elif mode == "severity":
        from sqlalchemy import func
        json_severity = []
        colors = {'high': '#FD0000', 'medium': '#FF8000', 'low': '#ffff00', 'none': '#eeeeee'}

        # Return severity count for all apps
        severities = db_session.query(App.severity, func.count(App.severity)).group_by(App.severity).all()
        for s in severities:
            if s[0]:
                json_severity.append({'label': s[0], 'value': s[1], 'color': colors[s[0].lower()]})
            else:
                json_severity.append({'label': 'None', 'value': s[1], 'color': colors['none']})


        # Build dict
        json_dict = {
            "severities": json_severity,
            "discrete": [{ "key": "Cumulative Return", "values": json_severity }]
        }

        return jsonify(json_dict)

    # No mode specified
    else:
        return 'No mode specified'

@apps.route('/api/get/selected-tags', methods = ['POST'])
def selected_tags():
    tags = request.json
    groups = []

    for t in tags:
        # Look for first group
        apps = db_session.query(App).filter(App.tags.any(Tag.name.in_(t['main'])))

        # Look for sub-groups
        for m in t['main']:
            for g in t['sub']:
                c = apps.filter(App.tags.any(Tag.name.in_([g]))).count()
                groups.append({'group': m, 'label':g, 'value':c})

    return json.dumps(groups)
