import os
import sys
from flask import Flask, render_template, redirect, url_for, flash, request
import requests
from calendar_creation import generate_calendar, get_month_name
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.forms import LoginForm, RegisterForm
from config import Config 

app = Flask(__name__)
app.config.from_object(Config)

# Backend API base URL
BACKEND_URL = "http://127.0.0.1:5001/api"

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

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

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

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
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            error_message = response.json().get('error', 'Login failed. Please try again.')
            flash(error_message, "danger")
    return render_template('login.html', form=form)

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



@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if request.method == 'POST':
        user_id = 1  # Replace with session user_id in production

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


@app.route('/my_plans')
def my_plans():
    """
    Fetches all plans for user=1, then displays them.
    """
    user_id = 1  # Replace with session user_id in production
    resp = requests.get(f"{BACKEND_URL}/users/{user_id}/plans")

    if resp.status_code == 200:
        plans = resp.json()
        app.logger.info(f"Plans retrieved: {plans}")
    else:
        plans = []
        flash("Could not load plans from backend.", "danger")

    return render_template('my_plans.html', plans=plans)




@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    user_id = 1  # or from session

    if request.method == 'POST':
        plan_id = request.form.get('plan_id')
        if not plan_id:
            flash("No plan selected to track.", "danger")
            return redirect(url_for('tracker'))

        total_lifts = int(request.form.get('total_lifts', 0))
        lifts_data = []
        for i in range(total_lifts):
            plan_lift_id_str = request.form.get(f"plan_lift_id_{i}")
            if plan_lift_id_str:
                actual_sets_str = request.form.get(f"actual_sets_{i}", '0')
                actual_reps_str = request.form.get(f"actual_reps_{i}", '0')
                actual_weight_str = request.form.get(f"actual_weight_{i}", '0')
                lifts_data.append({
                    "plan_lift_id": int(plan_lift_id_str),
                    "actual_sets": int(actual_sets_str),
                    "actual_reps": int(actual_reps_str),
                    "actual_weight": float(actual_weight_str)
                })

        payload = {
            "user_id": user_id,
            "lifts": lifts_data
        }
        track_url = f"{BACKEND_URL}/plans/{plan_id}/track"
        r = requests.post(track_url, json=payload)
        if r.status_code == 200:
            flash("Workout logged successfully!", "success")
        else:
            flash("Error logging workout.", "danger")
        return redirect(url_for('tracker'))

    else:
        plan_id = request.args.get('plan_id')
        plans_resp = requests.get(f"{BACKEND_URL}/users/{user_id}/plans")
        if plans_resp.status_code == 200:
            user_plans = plans_resp.json()
        else:
            user_plans = []
            flash("Could not load user plans.", "danger")

        selected_plan = None
        if plan_id:
            detail_resp = requests.get(f"{BACKEND_URL}/plans/{plan_id}")
            if detail_resp.status_code == 200:
                selected_plan = detail_resp.json()

        return render_template('tracker.html', user_plans=user_plans, selected_plan=selected_plan)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
