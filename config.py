PROJECT_ID = 'your-project-id'

CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'your-cloudsql-password'
CLOUDSQL_DATABASE = 'bookshelf'
# Set this value to the Cloud SQL connection name, e.g.
#   "project:region:cloudsql-instance".
# You must also update the value in app.yaml.
CLOUDSQL_CONNECTION_NAME = 'your-cloudsql-connection-name'

SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{user}:{password}@localhost/{database}'
    '?unix_socket=/cloudsql/{connection_name}').format(
        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
        database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)
