from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()
app.config.from_pyfile('config.py')
db.init_app(app)

with app.app_context():
    result = db.engine.execute('show tables;')
    rows = result.fetchall()
    print rows[0][0]

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    email = request.form['email']
    site = request.form['site_url']
    comments = request.form['comments']

    return render_template(
        'submitted_form.html',
        name=rows,
        email=email,
        site=site,
        comments=comments)