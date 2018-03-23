import os
import MySQLdb
from flask import Flask, render_template, request, g

# environment variables from app.yaml
PROJECT_ID = os.environ.get('PROJECT_ID')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_DB = os.environ.get('CLOUDSQL_DB')
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')

# local
#   run:
#   ./cloud_sql_proxy -instances="scurt-198704:us-central1:mysql-1"=tcp:3307
#   dev_appserver.py app.yaml
#
#   address:
#   http://localhost:8080

# app engine
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

# home page
@app.route("/")
def index():
    return render_template('index.html')

# sign up
@app.route("/signup", methods=['POST'])
def signup():
    email = request.form['email']
    pw = request.form['password']
    fname = request.form['first_name']
    lname = request.form['last_name']
    age = int(request.form['age'])
    address = request.form['address']
    phone = request.form['phone']

    sql = "INSERT INTO Users (email, password, first_name, last_name, age, address, phone) "\
          "VALUES (\'%s\', \'%s\', \'%s\', \'%s\', %d, \'%s\', \'%s\')"\
          % (email, pw, fname, lname, age, address, phone)

    cursor.execute(sql)
    db.commit()

    return render_template('index.html')

# login
@app.route("/login", methods=['POST'])
def login():
    email = request.form['email']
    pw = request.form['password']

    sql = "SELECT user_id, first_name, last_name from Users " \
          "WHERE email=\'%s\' AND password=\'%s\'"\
          % (email, pw)

    cursor.execute(sql)
    if not cursor.rowcount:
        return render_template('index.html')

    else:
        record = cursor.fetchone()
        g.user_id = record[0]
        g.user_name = record[1] + ' ' + record[2]

    return render_template('login.html')

@app.route("/add_car", methods=['POST'])
def add_car():
    sql = "INSERT INTO Car (state, license_plate, odometer, mpg, make, model, year, owner_id) "\
          "VALUES (\'%s\', \'%s\', %d, %d, \'%s\', \'%s\', %d, %d)"\
          % (request.form['state'], request.form['license_plate'], int(request.form['odometer']), int(request.form['mpg']), request.form['make'], request.form['model'], int(request.form['year']),int(g.user_id))
    cursor.execute(sql)
    db.commit()

    return render_template('login.html')


@app.route("/update_mileage", methods=['POST'])
def update_car():
    sql = "UPDATE Car SET odometer=odometer+%d"\
          "WHERE state=\'%s\' AND license_plate=\'%s\'"\
          % (int(request.form['miles'],request.form['state'], request.form['license_plate']))
    cursor.execute(sql)
    db.commit()

    return render_template('login.html')
