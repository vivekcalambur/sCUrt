import os
import datetime
import MySQLdb
from flask import Flask, render_template, request, session, redirect, url_for
from nlp import run_content_analysis

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
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# home page
@app.route("/")
def index():
    return render_template('index.html')

# sign up submit
@app.route("/signup", methods=['POST'])
def signup():
    email = request.form['email'].lower()
    pw = request.form['password']
    fname = request.form['first_name'].title()
    lname = request.form['last_name'].title()
    age = int(request.form['age'])
    address = request.form['address'].title()
    phone = request.form['phone']

    sql = "INSERT INTO Users (email, password, first_name, last_name, age, address, phone) "\
          "VALUES (\'%s\', \'%s\', \'%s\', \'%s\', %d, \'%s\', \'%s\')"\
          % (email, pw, fname, lname, age, address, phone)
    cursor.execute(sql)
    db.commit()

    return render_template('index.html')

# landing page after login
@app.route("/login_landing")
def login_landing():
    return render_template('login.html')

# login submit
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
        session['user_id'] = record[0]
        session['user_name'] = record[1] + ' ' + record[2]

    return render_template('login.html')

# clear session and go back to home page
@app.route("/signout")
def signout():
    session.clear()
    return redirect('/')


# populate edit user
@app.route("/edit_user")
def edit_user():
    return render_template('edit_user.html')

# submit edit user
@app.route("/submit_edit_user")
def submit_edit_user():
    return redirect(url_for('login_landing'))


# add car landing
@app.route("/add_car")
def add_car():
    return render_template('add_car.html')

# submit add car
@app.route("/submit_add_car", methods=['POST'])
def submit_add_car():
    state = request.form['state'].upper()
    lic_plate = request.form['license_plate'].replace(' ', '').upper()
    odometer = int(request.form['odometer'])
    mpg = int(request.form['mpg'])
    make = request.form['make'].title()
    model = request.form['model'].title()
    year = int(request.form['year'])

    sql = "INSERT INTO Cars (state, license_plate, odometer, mpg, make, model, year, owner_id) "\
          "VALUES (\'%s\', \'%s\', %d, %d, \'%s\', \'%s\', %d, %d)"\
          % (state, lic_plate, odometer, mpg, make, model, year, session['user_id'])
    cursor.execute(sql)
    db.commit()

    return redirect(url_for('login_landing'))


# populate update car
@app.route("/update_car")
def update_car():
    sql = "SELECT state, license_plate, make, model, odometer FROM Cars "\
          "WHERE owner_id=%d" % (session['user_id'])
    cursor.execute(sql)

    if not cursor.rowcount:
        return render_template('update_car.html')
    else:
        cars = cursor.fetchall()

    return render_template('update_car.html', cars=cars)

# submit update car
@app.route("/submit_update_car", methods=['POST'])
def submit_update_car():
    states = request.form.getlist('state')
    lic_plates = request.form.getlist('license_plate')
    odometers = request.form.getlist('odometer')
    deletes = request.form.getlist('delete')

    for i in range(0, len(lic_plates)):
        sql = "UPDATE Cars SET odometer=%d WHERE state=\'%s\' and license_plate=\'%s\'"\
              % (int(odometers[i]), states[i], lic_plates[i])
        cursor.execute(sql)

        if deletes[i] == 'yes':
            sql = "DELETE FROM Cars WHERE state=\'%s\' and license_plate=\'%s\'"\
                  % (states[i], lic_plates[i])
            cursor.execute(sql)

    db.commit()

    return redirect(url_for('update_car'))


@app.route("/schedule_car")
def schedule_car():
    all_cars_sql = "SELECT state, license_plate, make, model FROM Cars "\
          "WHERE owner_id=%d" % (session['user_id'])
    cursor.execute(all_cars_sql)

    all_cars = []
    if cursor.rowcount:
        all_cars = cursor.fetchall()

    scheduled_cars = []
    unscheduled_cars = []
    for car in all_cars:
        scheduled_cars_sql = "SELECT Cars.state, Cars.license_plate, make, model, start_date_time, end_date_time "\
            "FROM Availability, Cars "\
            "WHERE Cars.state=Availability.state and Cars.license_plate=Availability.license_plate "\
            "and Availability.state=\'%s\' and Availability.license_plate=\'%s\'" % (car[0], car[1])
        cursor.execute(scheduled_cars_sql)

        if cursor.rowcount:
            orig = cursor.fetchone()
            start_date = orig[4].strftime('%m/%d/%y')
            start_time = orig[4].strftime('%I:%M %p')
            end_date = orig[5].strftime('%m/%d/%y')
            end_time = orig[5].strftime('%I:%M %p')

            formatted = (orig[0], orig[1], orig[2], orig[3], start_date, start_time, end_date, end_time)
            scheduled_cars.append(formatted)
        else:
            unscheduled_cars.append((car[0], car[1], car[2], car[3]))

    return render_template('schedule_car.html', unscheduled=unscheduled_cars, scheduled=scheduled_cars)

@app.route("/submit_schedule_car", methods=['POST'])
def submit_schedule_car():
    states = request.form.getlist('state')
    lic_plates = request.form.getlist('license_plate')
    start_dates = request.form.getlist('start_date')
    start_times = request.form.getlist('start_time')
    end_dates = request.form.getlist('end_date')
    end_times = request.form.getlist('end_time')

    print end_times
    for i in range(0, len(lic_plates)):
        print end_times[i]
        if start_dates[i] != '' and start_times[i] != '' and end_dates[i] != '' and end_times[i] != '':
            start_date_time = start_dates[i] + ' ' + start_times[i]
            end_date_time = end_dates[i] + ' ' + end_times[i]

            sql = "INSERT INTO Availability VALUES (\'%s\', \'%s\', \'%s\', \'%s\')"\
                % (states[i], lic_plates[i], start_date_time, end_date_time)
            print(sql)
            cursor.execute(sql)
            db.commit()

    return redirect(url_for('schedule_car'))

@app.route("/delete_scheduled_car", methods=['POST'])
def delete_scheduled_car():
    states = request.form.getlist('state')
    lic_plates = request.form.getlist('license_plate')
    deletes = request.form.getlist('delete')

    for i in range(0, len(lic_plates)):
        if deletes[i] == 'yes':
            sql = "DELETE FROM Availability WHERE state=\'%s\' and license_plate=\'%s\'"\
                  % (states[i], lic_plates[i])
            cursor.execute(sql)

    db.commit()

    return redirect(url_for('schedule_car'))

@app.route("/submit_review", methods=['POST'])
def submit_review():
    state = request.form['state'].upper()
    lic_plate = request.form['license_plate'].replace(' ', '').upper()
    review = request.form['text1'].upper()
    values = run_content_analysis(review)
    
