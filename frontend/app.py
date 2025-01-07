from datetime import datetime
from functools import wraps
from flask import Flask, render_template, redirect, session, url_for, flash, request
from calendar_creation import generate_calendar, get_month_name, generate_dashboard_calendar
import requests
import sys
import os
from config import Config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.forms import LoginForm, RegisterForm


app = Flask(__name__)
app.config.from_object(Config)

# Backend API base URL
BACKEND_URL = "http://127.0.0.1:5001/api"

# Functions
# Get user id in session func
def get_id():
    user_id = session.get('user_id')
    return user_id

# Ensure user is logged in for according app routes func
def login_required(f):
    @wraps(f) #preserves original functions name and data
    def decorated_function(*args, **kwargs):  #wrapper intercepts request and enforces login check, returns original functions response if logged in - or redirect if not
        if not session.get("user_id"):
            flash("You must be logged in to view this page.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs) #if user is logged in continues with original funciton
    return decorated_function


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

# Index.html page
@app.route('/')
def index():
    calendar_data = generate_calendar() #calendar display - gathering data, this calander is for general guests displaying the current day
    return render_template(
        "index.html",
        year=calendar_data["year"],
        month=calendar_data["month"],
        day=calendar_data["day"],
        cal=calendar_data["calendar"],
        calendar_month_name=get_month_name()
    )

# Aboutus.html page
@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")


# Dashboard.html page
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = get_id()
    response = requests.get(f"{BACKEND_URL}/get-name/{user_id}")
    if response.status_code==200:
        user_firstname = response.json().get('firstname')
    else:
        user_firstname = response.json().get('error', 'An error occured')
        print("An error occured")
    now = datetime.now()
    year, month = now.year, now.month

    try:
        # Call the backend API to get tracked dates
        response = requests.get(f"{BACKEND_URL}/tracked-dates", params={"user_id": user_id, "year": year, "month": month})
        response.raise_for_status()  # Raise an error for non-200 responses
        tracked_dates = response.json().get("tracked_dates", [])
        tracked_days = [datetime.strptime(date, "%Y-%m-%d").day for date in tracked_dates]  # Extract day numbers
    except Exception as e:
        print(f"Error fetching tracked dates: {str(e)}")
        flash("Could not load tracked lift dates from the backend.", "danger")
        tracked_days = []

    # Generate calendar for the current month
    calendar_data = generate_dashboard_calendar(year=year, month=month)

    return render_template(
        "dashboard.html",
        year=calendar_data["year"],
        month=calendar_data["month"],
        cal=calendar_data["calendar"],
        calendar_month_name=get_month_name(),
        tracked_days=tracked_days,
        user_firstname = user_firstname
    )


# Login.html page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_data = {
            "username": form.username.data,
            "password": form.password.data,
        }
        response = requests.post(f"{BACKEND_URL}/login", json=login_data)

        if response.status_code == 200:
            # Extract user_id from the API response
            user = response.json().get("user", {})
            session["user_id"] = user.get("id")
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            # Display error message from backend
            flash(response.json().get("error", "Login failed. Please try again."), "danger")

    return render_template('login.html', form=form)


# Logout button
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# Register.html page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_data = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "username": form.username.data,
            "email": form.email.data,
            "date_of_birth": form.date_of_birth.data.strftime('%Y-%m-%d'),
            "goal": form.goal.data,
            "password": form.password.data,
        }
        response = requests.post(f"{BACKEND_URL}/register", json=user_data)

        try:
            response_data = response.json()  # Try to parse JSON response
        except requests.exceptions.JSONDecodeError:
            flash("Unexpected server error. Please try again.", "danger")
            return render_template("register.html", form=form)

        if response.status_code == 201:
            flash("Your account has been created! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            error_message = response_data.get('error', 'Registration failed. Please try again.')
            flash(error_message, "danger")
    return render_template("register.html", form=form)


# Plan.html page
@app.route('/plan', methods=['GET', 'POST'])
@login_required
def plan():
    if request.method == 'POST':
        user_id = get_id()

        # Gather plan details from form
        plan_name = request.form.get('plan_name')
        plan_type = request.form.get('plan_type')
        plan_duration = request.form.get('plan_duration')

        # Build a list of selected exercises
        lifts_array = []
        for i in range(1, 9):  # up to 8 slots
            selected_id_str = request.form.get(f"exercise_{i}")
            if selected_id_str:
                sets_str = request.form.get(f"sets_{i}", '3')
                reps_str = request.form.get(f"reps_{i}", '10')

                try:
                    lifts_array.append({
                        "lift_id": int(selected_id_str),
                        "sets": int(sets_str),
                        "reps": int(reps_str)
                    })
                except ValueError:
                    flash(f"Invalid input for exercise {i}. Please enter numeric values.", "danger")
                    return redirect(url_for('plan'))

        payload = {
            "user_id": user_id,
            "plan_name": plan_name,
            "plan_type": plan_type,
            "plan_duration": plan_duration,
            "lifts": lifts_array
        }

        # Post to the backend to create the plan
        response = requests.post(f"{BACKEND_URL}/plans", json=payload)
        if response.status_code == 201:
            flash("Plan created successfully!", "success")
            return redirect(url_for('my_plans'))
        else:
            error_message = response.json().get('error', 'Error creating plan.')
            flash(error_message, "danger")
            return redirect(url_for('plan'))

    else:
        # GET request: render the plan creation form
        lifts_resp = requests.get(f"{BACKEND_URL}/lifts")
        if lifts_resp.status_code == 200:
            lifts = lifts_resp.json()
        else:
            lifts = []
            flash("Could not load exercises from backend.", "danger")

        return render_template('plan.html', lifts=lifts)


# My_plans.html page
@app.route('/my_plans')
@login_required
def my_plans():
    user_id = get_id()

    resp = requests.get(f"{BACKEND_URL}/users/{user_id}/plans")

    response = requests.get(f"{BACKEND_URL}/get-name/{user_id}")
    if response.status_code==200:
        user_firstname = response.json().get('firstname')
    else:
        user_firstname = response.json().get('error', 'An error occured')
        print("An error occured")

    if resp.status_code == 200:
        plans = resp.json()
        app.logger.info(f"Plans retrieved: {plans}")
    else:
        plans = []
        flash("Could not load plans from backend.", "danger")

    return render_template('my_plans.html', plans=plans, user_firstname = user_firstname)


# Delete_plan.html page
@app.route('/delete-plan', methods=['GET', 'POST'])
@login_required
def delete_plan():
    user_id = get_id()
    if not user_id:
        flash("You must be logged in to delete a plan.", "danger")
        return redirect(url_for('login'))  

    if request.method == 'POST':
        plan_id = request.form.get('plan_id')
        if not plan_id:
            flash("Please select a plan to delete.", "danger")
            return redirect(url_for('delete_plan'))

        # Call the backend delete-plan API
        delete_url = f"{BACKEND_URL}/delete-plan"
        response = requests.post(delete_url, json={"plan_id": plan_id})

        if response.status_code == 200:
            flash("Plan deleted successfully.", "success")
        else:
            error_message = response.json().get("error", "An error occurred.")
            flash(f"Error: {error_message}", "danger")
        return redirect(url_for('my_plans'))  

    # Fetch the plans for dropdown menu
    plans_resp = requests.get(f"{BACKEND_URL}/users/{user_id}/plans")
    if plans_resp.status_code == 200:
        plans = plans_resp.json()
    else:
        plans = []
        flash("Could not load plans", "danger")

    return render_template('delete_plan.html', plans=plans)


# Tracker.html page
@app.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    """
    Allows users to track their workout performance for each lift in a selected plan.
    """
    user_id = get_id()

    if request.method == 'POST':
        plan_id = request.form.get('plan_id')
        if not plan_id:
            flash("No plan selected to track.", "danger")
            return redirect(url_for('tracker'))

        # Fetch the selected plan's details
        plan_resp = requests.get(f"{BACKEND_URL}/users/{user_id}/plans")
        if plan_resp.status_code != 200:
            flash("Could not load plan details from backend.", "danger")
            return redirect(url_for('tracker'))

        plans = plan_resp.json()
        selected_plan = next((plan for plan in plans if str(plan['plan_id']) == plan_id), None)
        if not selected_plan:
            flash("Selected plan not found.", "danger")
            return redirect(url_for('tracker'))

        # Iterate over each lift in the selected plan and send tracking data
        tracking_success = True
        for lift in selected_plan['lifts']:
            lift_id = lift['lift_id']
            reps_performed_str = request.form.get(f"reps_performed_{lift_id}", '0')
            weight_performed_str = request.form.get(f"weight_performed_{lift_id}", '0')
            reps_in_reserve_str = request.form.get(f"reps_in_reserve_{lift_id}", '0')

            try:
                reps_performed = int(reps_performed_str)
                weight_performed = float(weight_performed_str)
                reps_in_reserve = int(reps_in_reserve_str)
            except ValueError:
                flash(f"Invalid input for lift '{lift['lift_name']}'. Please enter numeric values.", "danger")
                tracking_success = False
                continue

            # Send POST request to track performance
            track_url = f"{BACKEND_URL}/plans/{plan_id}/lifts/{lift_id}/track"
            payload = {
                "reps_performed": reps_performed,
                "weight_performed": weight_performed,
                "reps_in_reserve": reps_in_reserve
            }
            response = requests.post(track_url, json=payload)

            if response.status_code != 201:
                error_message = response.json().get('error', 'Error tracking performance.')
                flash(f"Failed to track lift '{lift['lift_name']}': {error_message}", "danger")
                tracking_success = False

        if tracking_success:
            flash("Workout logged successfully!", "success")
        else:
            flash("Some lifts could not be tracked. Please review the errors above.", "danger")

        return redirect(url_for('tracker'))

    else:
        # GET request: render the tracking form
        plans_resp = requests.get(f"{BACKEND_URL}/users/{user_id}/plans")
        if plans_resp.status_code == 200:
            user_plans = plans_resp.json()
        else:
            user_plans = []
            flash("Could not load user plans.", "danger")

        selected_plan = None
        plan_id = request.args.get('plan_id')
        if plan_id:
            # Fetch detailed plan information if plan_id is provided
            plan_resp = requests.get(f"{BACKEND_URL}/users/{user_id}/plans")
            if plan_resp.status_code == 200:
                plans = plan_resp.json()
                selected_plan = next((plan for plan in plans if str(plan['plan_id']) == plan_id), None)
            else:
                flash("Could not load plan details.", "danger")

        return render_template('tracker.html', user_plans=user_plans, selected_plan=selected_plan)



# Tracking_history.html page
@app.route('/tracking_history')
@login_required
def tracking_history():
    """
    Displays all tracking data for the user.
    """
    user_id = get_id() # Get user id
    resp = requests.get(f"{BACKEND_URL}/users/{user_id}/trackings") #call trackings api endpoint to recieve tracking history json info

    if resp.status_code == 200:
        trackings = resp.json()
    else:
        trackings = []
        flash("Could not load tracking data from backend.", "danger")

    return render_template('tracking_history.html', trackings=trackings)


# Generate_plan.html page
@app.route('/generate_plan', methods=['GET', 'POST'])
@login_required
def generate_plan():
    user_id = get_id()# Get user id

    if request.method == 'POST':
        goal = request.form.get('goal')
        body_parts = request.form.getlist('body_parts')  # Collect all selected body parts from html

        if not goal or not body_parts:
            flash("Please select a goal and at least one body part.", "danger")
            return redirect(url_for('generate_plan'))

        payload = { #getting json payload ready for generate plan endpoint
            "user_id": user_id,
            "goal": goal,
            "body_parts": body_parts
        }

        # Make a POST request to the backend API endpoint generate_plan
        response = requests.post(f"{BACKEND_URL}/generate_plan", json=payload)
        if response.status_code == 201:
            flash("Plan generated successfully!", "success")
            return redirect(url_for('my_plans')) # Redirect the user to my_plans page to view plans
        else:
            error_message = response.json().get("error", "An error occurred while generating the plan.")
            flash(error_message, "danger")

    return render_template("generate_plan.html")





if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
