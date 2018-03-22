import os
import MySQLdb
from flask import Flask


# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_DB = os.environ.get('CLOUDSQL_DB')

def connect_to_cloudsql():
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        cloudsql_unix_socket = os.path.join('/cloudsql', 
            CLOUDSQL_CONNECTION_NAME)
        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            db=CLOUDSQL_DB)
    else:
        db = MySQLdb.connect(
            host='127.0.0.1',
            port=3307, 
            user=CLOUDSQL_USER,
            db=CLOUDSQL_DB)

    return db

app = Flask(__name__)
@app.route("/")
def hello():
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    temp = cursor.fetchone()
    return temp

