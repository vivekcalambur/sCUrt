PROJECT_ID = 'scurt-198704'

CLOUDSQL_USER = 'root'
CLOUDSQL_DATABASE = 'sCUrt_db'
# Set this value to the Cloud SQL connection name, e.g.
#   "project:region:cloudsql-instance".
# You must also update the value in app.yaml.
CLOUDSQL_CONNECTION_NAME = 'scurt-198704:us-central1:mysql-1'

SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{user}@localhost/{database}'
    '?unix_socket=/cloudsql/{connection_name}').format(
        user=CLOUDSQL_USER, database=CLOUDSQL_DATABASE, 
        connection_name=CLOUDSQL_CONNECTION_NAME)
