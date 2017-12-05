import os
import MySQLdb
import logging
import json
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask import request, render_template

app = Flask(__name__)

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')


def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db


def create_db_and_table(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS fp_db;")

    cursor.execute(""" CREATE TABLE IF NOT EXISTS fp_db.fp_table(
                   fingerprint VARCHAR(20) PRIMARY KEY,
                   user_agent VARCHAR(20),
                   accept VARCHAR(20),
                   accept_encoding VARCHAR(20),
                   accept_language VARCHAR(20),
                   plugins VARCHAR(20),
                   timezone_offset VARCHAR(20),
                   screen_resolution VARCHAR(20),
                   do_not_track VARCHAR(20),
                   cookies_enabled VARCHAR(20),
                   platform VARCHAR(20),
                   hardware_concurrency VARCHAR(20),
                   cpu_cores VARCHAR(20),
                   adblocker_present VARCHAR(20),
                   html_canvas_data VARCHAR(20),
                   webgl_vendor VARCHAR(20),
                   webgl_renderer VARCHAR(20),
                   audio_sample_rate VARCHAR(20),
                   audio_base_latency VARCHAR(20),
                   fonts_available VARCHAR(20),
                   logged_in_to VARCHAR(20)); """)


def insert_fp(cursor, fp_dict):
    vals = ["\'" + val + "\'" for val in fp_dict.values()]
    columns = "(" + ", ".join(fp_dict.keys()) + ")"
    values = "(" + ", ".join(vals) + ")"
    query_string = "INSERT IGNORE INTO fp_db.fp_table %s VALUES %s;" % (columns, values)
    app.logger.info(query_string)
    cursor.execute(query_string)


@app.route('/')
def hello_world():
    headers = request.headers
    return render_template("index.html", headers=dict(headers),
                           ip=request.remote_addr)


@app.route('/social.html')
def social():
    headers = request.headers
    return render_template("social.html", headers=dict(headers),
                           ip=request.remote_addr)


@app.route('/plot.html')
def plot():
    return render_template("plot.html")


@app.route('/stats')
def stats():
    db = connect_to_cloudsql()
    cursor = db.cursor()

    create_db_and_table(cursor)
    db.commit()

    query_string = """SELECT
                   COUNT(DISTINCT fingerprint) AS fingerprint_count ,
                   COUNT(DISTINCT user_agent) AS user_agent_count ,
                   COUNT(DISTINCT accept) AS accept_count ,
                   COUNT(DISTINCT accept_encoding) AS accept_encoding_count ,
                   COUNT(DISTINCT accept_language) AS accept_language_count ,
                   COUNT(DISTINCT plugins) AS plugins_count ,
                   COUNT(DISTINCT screen_resolution) AS screen_resolution_count ,
                   COUNT(DISTINCT platform) AS platform_count ,
                   COUNT(DISTINCT hardware_concurrency) AS hardware_concurrency_count ,
                   COUNT(DISTINCT html_canvas_data) AS html_canvas_data_count ,
                   COUNT(DISTINCT webgl_vendor) AS webgl_vendor_count ,
                   COUNT(DISTINCT webgl_renderer) AS webgl_renderer_count ,
                   COUNT(DISTINCT audio_sample_rate) AS audio_sample_rate_count ,
                   COUNT(DISTINCT audio_base_latency) AS audio_base_latency_count ,
                   COUNT(DISTINCT fonts_available) AS fonts_available_count ,
                   COUNT(DISTINCT logged_in_to) AS logged_in_to_count
                   FROM fp_db.fp_table; """

    cursor.execute(query_string)

    result = []
    for r in cursor.fetchall():
        result.append(r)

    return json.dumps(result[0])


@app.route('/dbput', methods=["POST"])
def db_put():
    db = connect_to_cloudsql()
    cursor = db.cursor()

    create_db_and_table(cursor)

    # get json object of fingerprint from request
    fp_dict = json.loads(request.data, encoding="utf-8")
    insert_fp(cursor, fp_dict)

    result = []
    for r in cursor.fetchall():
        result.append(str(r))

    db.commit()

    return "\n".join(result)


if __name__ == "__main__":
    handler = RotatingFileHandler('fp.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True, port=5000)
