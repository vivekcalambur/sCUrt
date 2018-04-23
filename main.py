import os
import datetime
import MySQLdb
from flask import Flask, render_template, request, session, redirect, url_for
from nlp import run_content_analysis
#from maps_api import get_distance_duration

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

    cars_sql = "INSERT INTO Cars (state, license_plate, odometer, mpg, make, model, year, owner_id) "\
          "VALUES (\'%s\', \'%s\', %d, %d, \'%s\', \'%s\', %d, %d)"\
          % (state, lic_plate, odometer, mpg, make, model, year, session['user_id'])
    cursor.execute(cars_sql)

    ratings_sql = "INSERT INTO RATINGS VALUES (\'%s\', \'%s\', %f, %f, %f, %f, %d)"\
        % (state, lic_plate, 7.0, 7.0, 7.0, 7.0, 0)
    cursor.execute(ratings_sql)

    db.commit()

    return redirect(url_for('add_car'))


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

    for i in range(0, len(lic_plates)):
        if start_dates[i] != '' and start_times[i] != '' and end_dates[i] != '' and end_times[i] != '':
            start_date_time = start_dates[i] + ' ' + start_times[i]
            end_date_time = end_dates[i] + ' ' + end_times[i]
            sql = "INSERT INTO Availability VALUES (\'%s\', \'%s\', \'%s\', \'%s\')"\
                % (states[i], lic_plates[i], start_date_time, end_date_time)
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

@app.route("/rent_car")
def rent_car():
    sql = "SELECT Bookings.state, Bookings.license_plate, make, model, DATE(start_date_time), "\
        "TIME(start_date_time), DATE(end_date_time), TIME(end_date_time) "\
        "FROM Bookings, Cars WHERE renter_id=%d and Bookings.state=Cars.state "\
        "and Bookings.license_plate=Cars.license_plate" % (session['user_id'])
    cursor.execute(sql)
    current_rentals = []
    if cursor.rowcount:
        current_rentals = cursor.fetchall()

    return render_template('rent_car.html', current_rentals=current_rentals)

@app.route("/search_cars", methods=['POST'])
def search_cars():
    start_date = request.form['start_date']
    start_time = request.form['start_time']
    end_date = request.form['end_date']
    end_time = request.form['end_time']
    start_date_time = start_date + ' ' + start_time
    end_date_time = end_date + ' ' + end_time

    available_sql = "SELECT state, license_plate FROM Availability "\
        "WHERE start_date_time <= \'%s\' and end_date_time >= \'%s\'" % (start_date_time, end_date_time)
    cursor.execute(available_sql)
    available_cars = []
    if cursor.rowcount:
        available_cars = cursor.fetchall()

    booking_sql = "SELECT state, license_plate FROM Bookings "\
        "WHERE start_date_time <= \'%s\' and end_date_time >= \'%s\'" % (start_date_time, end_date_time)
    cursor.execute(booking_sql)
    booked_cars = []
    if cursor.rowcount:
        booked_cars = cursor.fetchall()

    available_cars = [x for x in available_cars if x not in booked_cars]
    available_cars_info = []
    for car in available_cars:
        sql = "SELECT Cars.state, Cars.license_plate, make, model, overall_rating FROM Cars, Ratings "\
            "WHERE Cars.state=Ratings.state and Cars.license_plate=Ratings.license_plate and "\
            "Cars.state=\'%s\' and Cars.license_plate=\'%s\'" % (car[0], car[1])
        cursor.execute(sql)
        if cursor.rowcount:
            temp = list(cursor.fetchone())
            temp.extend((start_date, start_time, end_date, end_time))
            temp = tuple(temp)
            available_cars_info.append(temp)

    rented_sql = "SELECT Bookings.state, Bookings.license_plate, make, model, DATE(start_date_time), "\
        "TIME(start_date_time), DATE(end_date_time), TIME(end_date_time) "\
        "FROM Bookings, Cars WHERE renter_id=%d and Bookings.state=Cars.state "\
        "and Bookings.license_plate=Cars.license_plate" % (session['user_id'])
    cursor.execute(rented_sql)
    current_rentals = []
    if cursor.rowcount:
        current_rentals = cursor.fetchall()

    return render_template('rent_car_new.html', current_rentals=current_rentals, available_cars=available_cars_info)

@app.route("/submit_rent_car", methods=['POST'])
def submit_rent_car():
    states = request.form.getlist('state')
    lic_plates = request.form.getlist('license_plate')
    start_dates = request.form.getlist('start_date')
    start_times = request.form.getlist('start_time')
    end_dates = request.form.getlist('end_date')
    end_times = request.form.getlist('end_time')
    books = request.form.getlist('book')

    print request.form

    for i in range(0, len(lic_plates)):
        if books[i] == 'yes':
            start_date_time = start_dates[i] + ' ' + start_times[i]
            end_date_time = end_dates[i] + ' ' + end_times[i]
            sql = "INSERT INTO Bookings VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')"\
                % (session['user_id'], states[i], lic_plates[i], start_date_time, end_date_time)
            print(sql)
            cursor.execute(sql)

    db.commit()

    return redirect(url_for('rent_car'))

@app.route("/update_rentals", methods=['POST'])
def update_rentals():
    states = request.form.getlist('state')
    lic_plates = request.form.getlist('license_plate')
    start_dates = request.form.getlist('start_date')
    start_times = request.form.getlist('start_time')
    end_dates = request.form.getlist('end_date')
    end_times = request.form.getlist('end_time')
    deletes = request.form.getlist('delete')

    for i in range(0, len(lic_plates)):
        if deletes[i] == 'yes':
            start_date_time = start_dates[i] + ' ' + start_times[i]
            end_date_time = end_dates[i] + ' ' + end_times[i]
            sql = "DELETE FROM Bookings WHERE state=\'%s\' and license_plate=\'%s\' "\
                "and start_date_time=\'%s\' and end_date_time=\'%s\'" % (states[i], lic_plates[i], start_date_time, end_date_time)
            cursor.execute(sql)

    db.commit()

    return redirect(url_for('rent_car'))


@app.route("/submit_review", methods=['POST'])
def submit_review():
    state = request.form['state'].upper()
    lic_plate = request.form['license_plate'].replace(' ', '').upper()
    review = request.form['text1'].upper()

    get_review_data_sql = "SELECT overall_rating,number_of_reviews,cleanliness,cosmetics,reliability"\
        "FROM Reviews"\
        "WHERE state=\'%s\' and license_plate=\'%s\'" % (state, lic_plate)

    cursor.execute(get_review_data_sql)
    if cursor.rowcount:
        current_numbers = cursor.fetchone()

    values = run_content_analysis(review, current_numbers)

    sql = "UPDATE Reviews SET overall_rating=%d, number_of_reviews=%d, cleanliness=%d, cosmetics=%d,reliability=%d, WHERE state=\'%s\' and license_plate=\'%s\'"\
          % (int(values[0]),int(values[1]),float(values[2]),float(values[3]),float(values[4]), state, lic_plate)

    cursor.execute(sql)

    return redirect(url_for('login_landing'))
@app.route("/trip_planner")
def trip_planner():
    return render_template('trip_planner.html')

@app.route("/submit_trip_planner", methods=['POST'])
def submit_trip_planner():
    origin = request.form['origin']
    destination = request.form['destination']
