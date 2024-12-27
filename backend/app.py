from datetime import datetime
from flask_bcrypt import Bcrypt
from flask import Flask, jsonify, request
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config
from models import db, bcrypt, User, Lift, Plan, PlanLift

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def index():
    return "Backend is running!"


def populate_lifts():
    predefined_lifts = [
        {"name": "Bench Press"},
        {"name": "Squat"},
        {"name": "Deadlift"},
        {"name": "Overhead Press"},
        {"name": "Barbell Row"},
        {"name": "Pull-Ups"},
        {"name": "Push-Ups"},
        {"name": "Dumbbell Curl"},
        {"name": "Tricep Extension"},
        {"name": "Lunges"},
        {"name": "Plank"},
        {"name": "Shoulder Fly"},
        {"name": "Lat Pull-Down"},
        {"name": "Leg Press"},
        {"name": "Calf Raise"},
        {"name": "Incline Bench Press"},
        {"name": "Russian Twist"},
        {"name": "Leg Extension"},
        {"name": "Leg Curl"},
        {"name": "Upright Row"},
    ]
    for lift_data in predefined_lifts:
        existing_lift = Lift.query.filter_by(name=lift_data["name"]).first()
        if not existing_lift:
            new_lift = Lift(name=lift_data["name"])
            db.session.add(new_lift)
    db.session.commit()


# -------------- BASIC AUTH ENDPOINTS (REGISTER/LOGIN) --------------

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug incoming data
        if not data:
            return jsonify({"error": "Invalid data format"}), 400

        # Validation checks
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({"error": "Username already exists"}), 400
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({"error": "Email already registered"}), 400

        # Create user
        date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        new_user = User(
            username=data['username'],
            password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            date_of_birth=date_of_birth,
            goal=data.get('goal')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        print(f"Error in /api/register: {e}")  # Log error
        return jsonify({"error": "Server error. Please try again later."}), 500


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Invalid data"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    if not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful", "user": {"id": user.id, "username": user.username}}), 200



@app.route('/api/plans', methods=['POST'])
def create_plan():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        # Log incoming data
        app.logger.info(f"Received data: {data}")

        user_id = data.get('user_id')
        plan_name = data.get('plan_name')
        plan_type = data.get('plan_type')
        plan_duration = data.get('plan_duration')
        lifts_data = data.get('lifts', [])

        if not user_id or not plan_name:
            return jsonify({"error": "user_id and plan_name are required"}), 400

        # Create the Plan
        new_plan = Plan(
            user_id=user_id,
            plan_name=plan_name,
            plan_type=plan_type,
            plan_duration=plan_duration
        )
        db.session.add(new_plan)
        db.session.flush()  # Get the plan ID without committing

        # Add lifts to the Plan
        for lift in lifts_data:
            plan_lift = PlanLift(
                plan_id=new_plan.id,
                lift_id=lift['lift_id'],
                sets=lift.get('sets', 3),
                reps=lift.get('reps', 10),
                weight_lifted=lift.get('weight_lifted')
            )
            db.session.add(plan_lift)

        db.session.commit()
        return jsonify({"message": "Plan created successfully", "plan_id": new_plan.id}), 201

    except Exception as e:
        app.logger.error(f"Error creating plan: {e}")
        return jsonify({"error": f"Server error: {e}"}), 500



@app.route('/api/users/<int:user_id>/plans', methods=['GET'])
def get_user_plans(user_id):
    """
    Fetch all plans for a specific user.
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            app.logger.error(f"User {user_id} not found.")
            return jsonify({"error": "User not found"}), 404

        # Fetch plans for the user
        plans = Plan.query.filter_by(user_id=user_id).all()
        if not plans:
            app.logger.info(f"No plans found for user {user_id}.")
            return jsonify([]), 200  # No plans for the user

        # Format the response
        plans_data = []
        for plan in plans:
            lifts_list = []
            for pl in plan.plan_lifts:
                lift_obj = db.session.get(Lift, pl.lift_id)
                if lift_obj:
                    lifts_list.append({
                        "lift_id": pl.lift_id,
                        "lift_name": lift_obj.name,
                        "sets": pl.sets,
                        "reps": pl.reps,
                        "weight_lifted": pl.weight_lifted
                    })

            plans_data.append({
                "plan_id": plan.id,
                "plan_name": plan.plan_name,
                "plan_type": plan.plan_type,
                "plan_duration": plan.plan_duration,
                "creation_date": plan.creation_date.isoformat() if plan.creation_date else None,
                "lifts": lifts_list
            })

        app.logger.info(f"Plans for user {user_id}: {plans_data}")
        return jsonify(plans_data), 200

    except Exception as e:
        app.logger.error(f"Error fetching plans for user {user_id}: {str(e)}")
        return jsonify({"error": "Server error"}), 500



@app.route('/api/lifts', methods=['GET'])
def get_lifts():
    """
    Fetch all predefined lifts.
    """
    lifts = Lift.query.all()
    lifts_data = [{"id": lift.id, "name": lift.name} for lift in lifts]
    return jsonify(lifts_data), 200



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        populate_lifts()

    app.run(debug=True, host='0.0.0.0', port=5001)
