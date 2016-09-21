"""
Microservice endpoints.
"""

import os
import time
import json

import isodate
import pandas as pd
from flask import Response, render_template, request, abort

from app import app, maps, conn

from utils import bbox


# helpers

def build_where_clause(criteria):
    '''
    Build a SQL where clause from a list of criteria.

    Example:
        build_where_clause([('foo', '=', 'bar'), ('x', '>', 42)])
        -> ' WHERE foo=bar AND x>42'
    '''

    result = ''
    if any(criteria):
        result += ' WHERE '
    result += ' AND '.join(['%s%s%s' % (k, op, json.dumps(v)) for (k, op, v) in criteria if v is not None])
    return result


# desired API endpoint

@app.route('/data', methods=['POST'])
def post_data():
    """
    Post vehicle data and store into a database.

    Test using curl like this:

    curl -X POST "http://localhost:5000/data" --data "uid=76b1b23a-9763-41e8-9727-a63955cb5daf&type=car&timestamp=1472716308.602317&longitude=13.383333&lattitude=52.516667&heading=123"
    """

    data = {k: request.form[k] for k in request.form.keys()}

    cmd = "INSERT INTO traffic VALUES (?, ?, ?, ?, ?, ?)"
    vals = (
        data['uid'], 
        data['type'], 
        data['timestamp'], 
        data['longitude'],
        data['lattitude'],
        data['heading']
    )
    cursor = conn.cursor()
    cursor.execute(cmd, vals)
    conn.commit()
    return 'saved'


# additional endpoints

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/simple')
def get_simple():
    # This is only for benchmarking the simplest GET endpoint. 

    return 'done'


@app.route('/num_data')
def get_num_data():
    '''
    Return number of data points
    '''

    cursor = conn.cursor()
    cmd = "SELECT count(*) FROM traffic"
    cursor.execute(cmd)
    row = cursor.fetchone()
    return str(row[0])


@app.route('/data.csv')
def get_data_csv():
    '''
    Download traffic data from matching some criteria, as a CSV file.

    Duration is supposed to be in ISO8601 format (PT1H means a time
    period of one hour).

    Examples:
        /data.csv
        /data.csv?type=car&duration=PT1H
        /data.csv?uid=687a7ec8-6fa8-11e6-b897-442a60f31a14
    '''

    args = request.args
    where_args = []

    uid = args.get('uid', None)
    if uid:
        where_args.append(('uid', '=', uid))
    
    typ = args.get('type', None)
    allowed_types = ['bus', 'car', 'taxi', 'train']
    if typ:
        assert typ in allowed_types
        where_args.append(('type', '=', typ))

    timestamp = None
    if args.get('duration', None):
        value = args['duration']
        try:
            dur = isodate.parse_duration(value)
        except:
            msg = "'%s' is an invalid ISO 8601 duration string. " % value
            msg += 'See https://en.wikipedia.org/wiki/ISO_8601#Durations'
            abort(404, msg)
        timestamp = time.time() - dur.total_seconds()
        where_args.append(('timestamp', '>=', timestamp))

    # using pandas to run the SQL query and convert rows to CSV
    cmd = "SELECT * FROM traffic "
    where_clause = build_where_clause(where_args)
    cmd += where_clause
    df = pd.read_sql_query(cmd, conn)
    csv = df.to_csv()
    return Response(csv, mimetype='text/csv')


@app.route('/map/traffic')
def get_map_traffic():
    '''
    Show a map with all locations of all (or only one) vehicles in Snowdonia.

    You can map only one vehicle by adding ?uid=<UID> as query parameter.
    '''

    cursor = conn.cursor()
    cmd = "SELECT * FROM traffic "
    args = request.args
    uid = args.get('uid', None)
    if uid:
        cmd += ' WHERE uid="%s"' % uid
    df = pd.read_sql_query(cmd, conn)
    data = list(zip(df.longitude, df.lattitude))

    plt = maps.make_map_traffic(data)
    plt.savefig('geo/map_traffic.png')
    return Response(open('geo/map_traffic.png', 'rb').read(), mimetype='image/png')


# additional, undocumented maps

@app.route('/map/world', methods=['GET'])
def get_map_world():
    '''
    Show a world map.
    '''

    plt = maps.make_map_world()
    plt.savefig('geo/map_world.png')
    return Response(open('geo/map_world.png', 'rb').read(), mimetype='image/png')


@app.route('/map/berlin/bvg')
def get_map_berlin_bvg():
    '''
    Show a Berlin map with BVG stops.
    '''

    plt = maps.make_map_berlin_bvg()
    plt.savefig('geo/map_berlin.png')
    return Response(open('geo/map_berlin.png', 'rb').read(), mimetype='image/png')
