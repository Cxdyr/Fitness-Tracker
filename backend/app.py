from datetime import datetime
from flask_bcrypt import Bcrypt
from flask import Flask, jsonify, request
import sys
import os
from sqlalchemy import func
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.ML_plan_maker.model import predict
from config import Config
from models import LiftPerformance, db, bcrypt, User, Lift, Plan, PlanLift

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def index():
    return "Backend is running!"


def populate_lifts():
    predefined_lifts = [
        {"name": "Barbell Bench Press"},
        {"name": "Barbell Bench Incline Press"},
        {"name": "Dumbbell Flat Press"},
        {"name": "Dumbbell Incline Press"},
        {"name": "Machine Chest Press"},
        {"name": "Squat"},
        {"name": "High Bar Squat"},
        {"name": "Low Bar Squat"},
        {"name": "Box Squat"},
        {"name": "Pin Press Squat"},
        {"name": "Deadlift"},
        {"name": "Sumo Deadlift"},
        {"name": "Bench Press"},
        {"name": "Shoulder Dumbbell Press"},
        {"name": "Shoulder Barbell Press"},
        {"name": "Shoulder Machine Press"},
        {"name": "Barbell Row"},
        {"name": "Dumbbell Row"},
        {"name": "Cable Row"},
        {"name": "T-Bar Row"},
        {"name": "Pull-Ups"},
        {"name": "Push-Ups"},
        {"name": "Dumbbell Curl"},
        {"name": "Barbell Curl"},
        {"name": "Hammer Curl"},
        {"name": "Spider Curl"},
        {"name": "Machine Curl"},
        {"name": "Cable Curl"},
        {"name": "Overhead Tricep Press"},
        {"name": "Overhead Tricep Extensions"},
        {"name": "Single Arm Tricep Extensions"},
        {"name": "Tricep Extension"},
        {"name": "Skull Crushers"},
        {"name": "Tricep Pushdowns"},
        {"name": "Lat Pull Downs"},
        {"name": "Lat Pull Overs"},
        {"name": "Lat Raises"},
        {"name": "Front Raises"},
        {"name": "Rear Delt Flies"},
        {"name": "Pec Deck"},
        {"name": "Cable Chest Press"},
        {"name": "Chest Flies (DB or Cable)"},
        {"name": "Lunges"},
        {"name": "Weighted Dips"},
        {"name": "Plank"},
        {"name": "Leg Press"},
        {"name": "Leg Extensions"},
        {"name": "Hamstring Curls"},
        {"name": "Hip Abductors"},
        {"name": "Hip Adductors"},
        {"name": "Hip Thrust"},
        {"name": "Calf Raise"},
        {"name": "Russian Twist"},
        {"name": "Upright Row"},
        {"name": "Standing Overhead Press"},
        {"name": "Romanian Deadlift"},
        {"name": "Bulgarian Split Squats"},
    ]
    for lift_data in predefined_lifts:
        existing_lift = Lift.query.filter_by(name=lift_data["name"]).first()
        if not existing_lift:
            new_lift = Lift(name=lift_data["name"])
            db.session.add(new_lift)
    db.session.commit()

# End point for getting user tracked dates for calander display on dashboard
@app.route('/api/tracked-dates', methods=['GET'])
def get_tracked_dates_api():
    try:
        user_id = request.args.get('user_id', type=int)
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        if not year or not month:
            return jsonify({"error": "Year and Month are required"}), 400

        tracked_dates = db.session.query(LiftPerformance.date).join(
            PlanLift, LiftPerformance.plan_lift_id == PlanLift.id
        ).join(
            Plan, PlanLift.plan_id == Plan.id
        ).filter(
            Plan.user_id == user_id,  # Filter by user_id
            func.extract('year', LiftPerformance.date) == year,  
            func.extract('month', LiftPerformance.date) == month 
        ).distinct().all()  # Use distinct to remove duplicates

        unique_dates = set(date[0].date() for date in tracked_dates)  #Get unique dates
        tracked_dates_list = [date.strftime("%Y-%m-%d") for date in sorted(unique_dates)]  
        return jsonify({"tracked_dates": tracked_dates_list}), 200

    except Exception as e:
        print(f"Error in /tracked-dates API: {str(e)}")
        return jsonify({"error": str(e)}), 500

    
# ----- BASIC AUTH ENDPOINTS (REGISTER/LOGIN) --------

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
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password are required"}), 400

        user = User.query.filter_by(username=data['username']).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
            return jsonify({"error": "Invalid username or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username
            }
        }), 200

    except Exception as e:
        app.logger.error(f"Error in /api/login: {str(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500



# ----- PLAN CREATION AND VIEWING ENDPOINTS  --------

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
    Get all plans for a specific user.
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
    Get all predefined lifts.
    """
    lifts = Lift.query.all()
    lifts_data = [{"id": lift.id, "name": lift.name} for lift in lifts]
    return jsonify(lifts_data), 200


# -----TRACKING ENDPOINTS  --------

@app.route('/api/plans/<int:plan_id>/lifts/<int:lift_id>/track', methods=['POST'])
def track_lift_performance(plan_id, lift_id):
    """
    Track the performance of a specific lift in a plan.
    """
    try:
        # Validate the existence of the plan and lift
        plan = db.session.get(Plan, plan_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404

        plan_lift = PlanLift.query.filter_by(plan_id=plan_id, lift_id=lift_id).first()
        if not plan_lift:
            return jsonify({"error": "Lift not found in the specified plan"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        reps_performed = data.get('reps_performed')
        weight_performed = data.get('weight_performed')
        reps_in_reserve = data.get('reps_in_reserve')

        # Validate input 
        if reps_performed is None or weight_performed is None or reps_in_reserve is None:
            return jsonify({"error": "Missing required fields"}), 400

        if not isinstance(reps_performed, int) or not isinstance(weight_performed, (int, float)) or not isinstance(reps_in_reserve, int):
            return jsonify({"error": "Invalid data types"}), 400

        # Create a new LiftPerformance record
        performance = LiftPerformance(
            plan_lift_id=plan_lift.id,
            reps_performed=reps_performed,
            weight_performed=weight_performed,
            reps_in_reserve=reps_in_reserve
        )

        db.session.add(performance)
        db.session.commit()

        return jsonify({
            "message": "Lift performance tracked successfully",
            "performance_id": performance.id
        }), 201

    except Exception as e:
        app.logger.error(f"Error tracking lift performance: {str(e)}")
        return jsonify({"error": "Server error"}), 500



@app.route('/api/plans/<int:plan_id>/lifts/<int:lift_id>/track', methods=['GET'])
def get_lift_performance(plan_id, lift_id):
    """
    Retrieve tracking data for a specific lift in a plan.
    """
    try:
        # Validate the existence of the plan and lift
        plan = Plan.query.get(plan_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404

        plan_lift = PlanLift.query.filter_by(plan_id=plan_id, lift_id=lift_id).first()
        if not plan_lift:
            return jsonify({"error": "Lift not found in the specified plan"}), 404

        performances = LiftPerformance.query.filter_by(plan_lift_id=plan_lift.id).order_by(LiftPerformance.date.desc()).all()

        performances_data = []
        for perf in performances:
            performances_data.append({
                "performance_id": perf.id,
                "date": perf.date.isoformat(),
                "reps_performed": perf.reps_performed,
                "weight_performed": perf.weight_performed,
                "reps_in_reserve": perf.reps_in_reserve
            })

        return jsonify(performances_data), 200

    except Exception as e:
        app.logger.error(f"Error retrieving lift performance: {str(e)}")
        return jsonify({"error": "Server error"}), 500
    

@app.route('/api/users/<int:user_id>/trackings', methods=['GET'])
def get_user_trackings(user_id):
    """
    Retrieve all tracking data for a specific user.
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        plans = Plan.query.filter_by(user_id=user_id).all()
        if not plans:
            return jsonify([]), 200

        trackings = []
        for plan in plans:
            for plan_lift in plan.plan_lifts:
                for perf in plan_lift.performances:
                    trackings.append({
                        "plan_id": plan.id,
                        "plan_name": plan.plan_name,
                        "lift_id": plan_lift.lift_id,
                        "lift_name": plan_lift.lift.name,
                        "performance_id": perf.id,
                        "date": perf.date.date().isoformat(),
                        "reps_performed": perf.reps_performed,
                        "weight_performed": perf.weight_performed,
                        "reps_in_reserve": perf.reps_in_reserve
                    })
                           
        return jsonify(trackings), 200

    except Exception as e:
        app.logger.error(f"Error retrieving user trackings: {str(e)}")
        return jsonify({"error": "Server error"}), 500
    
@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    return None  #place holder



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        populate_lifts()

    app.run(debug=True, host='0.0.0.0', port=5001)
