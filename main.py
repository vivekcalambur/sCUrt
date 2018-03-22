import os
import MySQLdb
from flask import Flask, render_template, request

# environment variables from app.yaml
PROJECT_ID = os.environ.get('PROJECT_ID')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_DB = os.environ.get('CLOUDSQL_DB')
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')


# local
#
#   run:
#   ./cloud_sql_proxy -instances="scurt-198704:us-central1:mysql-1"=tcp:3307
#   dev_appserver.py app.yaml
#
#   address: 
#   http://localhost:8080

# app engine
#
#   run:
#   gcloud app deploy
#
#   address: 
#   https://scurt-198704.appspot.com   


# function to establish local/app engine connection to cloud SQL
def connect_to_cloudsql():
    # app engine connection
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        cloudsql_unix_socket = os.path.join('/cloudsql', 
            CLOUDSQL_CONNECTION_NAME)
        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            db=CLOUDSQL_DB)

    # local connection
    else:
        db = MySQLdb.connect(
            host='127.0.0.1',
            port=3307, 
            user=CLOUDSQL_USER,
            db=CLOUDSQL_DB)

    return db

db = connect_to_cloudsql()
cursor = db.cursor()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

# @app.route("/signup", method=['POST'])
# def signup():
#     username = request.

