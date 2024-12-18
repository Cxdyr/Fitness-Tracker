import os
import sys 
from flask import Flask, render_template, redirect, url_for, flash
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #for config file path
from config import Config 
from backend.forms import LoginForm, RegisterForm
from calendar_creation import generate_calendar, get_month_name


app = Flask(__name__)
app.config.from_object(Config)

#back-end api access variable    add /endpoint     for each endpoint
BACKEND_URL = "http://127.0.0.1:5001/api"


#Landing page, index.html app route
@app.route('/')
def index():
    calendar_data = generate_calendar() #calendar display - gathering data
    return render_template(
        "index.html",
        year=calendar_data["year"],
        month=calendar_data["month"],
        day=calendar_data["day"],
        cal=calendar_data["calendar"],
        calendar_month_name=get_month_name()
    )

#Home page, dashboard.html app route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

#Login page, login.html app route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_data = {
            "username": form.username.data,
            "password": form.password.data,
        }
        response = requests.post(f"{BACKEND_URL}/login", json=login_data)  #Calling login endpoint, getting response

        if response.status_code == 200:
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            error_message = response.json().get('error', 'Login failed. Please try again.')
            flash(error_message, "danger")
    return render_template('login.html', form=form)


#Register page, register.html app route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():  #Only basic client-side checks
        user_data = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "username": form.username.data,
            "email": form.email.data,
            "date_of_birth": form.date_of_birth.data.strftime('%Y-%m-%d'),
            "goal": form.goal.data,
            "password": form.password.data,
        }
        response = requests.post(f"{BACKEND_URL}/register", json=user_data) #Calling register endpoint, getting response

        if response.status_code == 201:
            flash("Your account has been created! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            error_message = response.json().get('error', 'Registration failed. Please try again.')
            flash(error_message, "danger")
    return render_template("register.html", form=form)


#Tracker page, tracker.html app route
@app.route('/tracker')
def tracker():
    return render_template('tracker.html')

#Plan page, page.html app route
@app.route('/plan')
def plan():
    return render_template('plan.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)