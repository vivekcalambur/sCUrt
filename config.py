import os

PROJECT_ID = 'scurt-198704'

CLOUDSQL_USER = 'root'
CLOUDSQL_DATABASE = 'sCUrt_db'
# Set this value to the Cloud SQL connection name, e.g.
#   "project:region:cloudsql-instance".
# You must also update the value in app.yaml.
CLOUDSQL_CONNECTION_NAME = "scurt-198704:us-central1:mysql-1"


# Alternatively, you could use a local MySQL instance for testing.
LOCAL_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{user}@127.0.0.1:3307/{database}').format(
        user=CLOUDSQL_USER, database=CLOUDSQL_DATABASE)

# When running on App Engine a unix socket is used to connect to the cloudsql
# instance.
LIVE_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{user}@localhost/{database}'
    '?unix_socket=/cloudsql/{connection_name}').format(
        user=CLOUDSQL_USER, database=CLOUDSQL_DATABASE, 
        connection_name=CLOUDSQL_CONNECTION_NAME)

if os.environ.get('GAE_INSTANCE'):
    SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
else:
    SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI
