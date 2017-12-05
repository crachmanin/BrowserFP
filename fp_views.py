import os
import MySQLdb
import logging
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
                   fingerprint VARCHAR(20),
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
                   cpu_cores VARCHAR(20),
                   using_adblocker VARCHAR(20),
                   html_canvas_data VARCHAR(20),
                   web_gl_vendor VARCHAR(20),
                   web_gl_renderer VARCHAR(20),
                   audio_sample_rate VARCHAR(20),
                   fonts_available VARCHAR(20),
                   logged_in_to VARCHAR(20)); """)

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


@app.route('/dbput')
def db_put():
    db = connect_to_cloudsql()
    cursor = db.cursor()

    create_db_and_table(cursor)

    result = []
    for r in cursor.fetchall():
        result.append(str(r))

    return "\n".join(result)


if __name__ == "__main__":
    handler = RotatingFileHandler('fp.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True, port=5000)
