from datetime import datetime
from dotenv import load_dotenv
from flask_bcrypt import bcrypt
from flask import Flask, abort, jsonify, request
from sqlalchemy import func
from models import LiftPerformance, db, bcrypt, User, Lift, Plan, PlanLift
from predict import predict_lifts
from recommend_weight import true_math
from config import Config
from email_validator import validate_email


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

load_dotenv()


#  validate API key
@app.before_request
def validate_api_key():
    """
    Middleware: Validates the API key in the 'X-API-KEY' request header from frontend or other call locations
    """
    api_key = request.headers.get('X-API-KEY') #From frontend to retrieve api key from headers
    if api_key != Config.API_KEY: #if api key is wrong, we cannot perform api requests
        abort(403, "Invalid API Key") 


# backend health check 
@app.route('/')
def index():
    """
    Health check for the backend

    """
    return "Backend is running!"


#-------- BASIC ENDPOINTS --------------

# Get id endpoint
@app.route('/api/get-id/<string:username>', methods=['GET'])
def get_id(username):
    """
    GET /api/get-id/{username}
    ---
    Retrieves the user ID that is associated with the provided username.

    """
    user = User.query.filter_by(username=username).first()
    if user and user.id:
        return jsonify({"id": user.id}), 200
    elif user:
        return jsonify({"error": "ID not found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404
    

# Get-name endpoint
@app.route('/api/get-name/<int:user_id>', methods=['GET'])
def get_name(user_id):
    """
    GET /api/get-name/{user_id}
    ---
    Returns the first name of the user associated with the provided user ID.
    """
    user = User.query.filter_by(id=user_id).first()
    if user and user.first_name:
        return jsonify({"firstname": user.first_name}), 200
    elif user:
        return jsonify({"error": "First name not found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404
    

# Delete user endpoint
@app.route('/api/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    DELETE /api/users/delete/{user_id}
    ---
    Deletes a user from the database based on their unique ID.
    """
    try:
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": f"User {user.username} has been deleted successfully"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occured: {str(e)}"}),500



# End point for changing user email 
@app.route('/api/change-email', methods=['POST'])
def change_email():
    """
    POST /api/change-email
    ---
    Changes a user's email after validating the input, ensuring the email does not already exist in database, then updating the user's record.
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        new_email = data.get("email")
  

        if not new_email:
            return jsonify({"error": "New email is required"}), 400 # If no input
        
        if not validate_email(new_email):
            return jsonify({"error": "Email format is incorrect"}), 400 # If incorrect format
        
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user:
            return jsonify({"error": "User with existing email already exists, please try a different email"}), 409 # If user email exists attached to other user
        
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}),404
        
        user.email = new_email
        db.session.commit()
        return jsonify({"message": "Successfully updated email"}), 200 # Successfully changed user email 
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occured: {str(e)}"}),500


# End point for getting user tracked dates for calander display on dashboard
@app.route('/api/tracked-dates', methods=['GET'])
def get_tracked_dates_api():
    """
    GET /api/tracked-dates
    ---
    Retrieves the dates a user has tracked performance for a specific year and month for calendar display
    """
    try: # Gets user id, year, and month info
        user_id = request.args.get('user_id', type=int)
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400 # User id auth error 
        if not year or not month:
            return jsonify({"error": "Year and Month are required"}), 400 # Unable to populate calander information error

        tracked_dates = db.session.query(LiftPerformance.date).join( # Gathering all dates that user liftperformance entries have been created (days users tracked lifts)
            PlanLift, LiftPerformance.plan_lift_id == PlanLift.id
        ).join(
            Plan, PlanLift.plan_id == Plan.id
        ).filter(
            Plan.user_id == user_id,  # Filter by user_id
            func.extract('year', LiftPerformance.date) == year,  
            func.extract('month', LiftPerformance.date) == month 
        ).distinct().all()  # Use distinct to remove duplicates

        unique_dates = set(date[0].date() for date in tracked_dates)  #Get unique dates - a user can track multiple times in one day and this will prevent issues with this
        tracked_dates_list = [date.strftime("%Y-%m-%d") for date in sorted(unique_dates)]  # Sorting dates into order
        return jsonify({"tracked_dates": tracked_dates_list}), 200

    except Exception as e:
        print(f"Error in /tracked-dates API: {str(e)}")
        return jsonify({"error": str(e)}), 500

    


# ----- BASIC AUTH ENDPOINTS (REGISTER/LOGIN) --------



# End point for user registration
@app.route('/api/register', methods=['POST'])
def api_register():
    """
    Ensures user input username doesn't exist, creates new user with user input information user(username, password, first_name, last_name, email, goal)
    and adds to users db.
    """
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
            password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8'), # hasing user password before commit to db
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


# End point for user login
@app.route('/api/login', methods=['POST'])
def api_login():
    """
    Checks user input username/password with database username/password post hash for authentication.
    """
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password are required"}), 400

        user = User.query.filter_by(username=data['username']).first() # Finding user in users table by unique username
        if not user or not bcrypt.check_password_hash(user.password_hash, data['password']): # Validating password
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


# End point for reset password
@app.route('/api/reset-password', methods=['POST'])
def check_reset_pw():
    """
    Checks user input (email and dob) to make sure both match a database record - if so we return success which is handled in frontend,
    if wrong return error code that prevents user from changing password
    """
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('desired_password'):
            return jsonify({"error": "Missing data"}), 400
        
        #finding the user by email
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({"error": "Invalid email"}),401
        
        
        password_hash = bcrypt.generate_password_hash(data['desired_password']).decode('utf-8')
        user.password_hash = password_hash

        db.session.commit()
        return jsonify({"message": "Success, your password has been reset"}), 200
    
    
    except Exception as e:
        return jsonify({"error":str(e)}), 500
    

# End point for recieving user data for settings
@app.route('/api/settings/user-info/<int:user_id>', methods=['GET'])
def get_settings_info(user_id):

    user = db.session.get(User, user_id)
    if user:
        user_info = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "date_of_birth": user.date_of_birth,
            "email": user.email,
            "creation_date": user.creation_date,
            "goal": user.goal
        }
        return jsonify(user_info), 200
    else:
        return jsonify({"error": "User not found"}), 404
    

# ----- PLAN CREATION AND VIEWING ENDPOINTS  --------

# Create plan endpoint
@app.route('/api/plans', methods=['POST'])
def create_plan():
    """
    Create plan for user based on json data retrieved from frontend.
    """
    try:
        data = request.get_json() #Retrieve json data from frontend
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400


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
        db.session.add(new_plan) # Add the plan to plan db
        db.session.flush()  # Get the plan ID without committing

        # Add lifts to the Plan
        for lift in lifts_data:
            plan_lift = PlanLift(
                plan_id=new_plan.id,
                lift_id=lift['lift_id'],
                sets=lift.get('sets', 3),
                reps=lift.get('reps', 10),
            )
            db.session.add(plan_lift) # Add plan lift to the planlift db

        db.session.commit()
        return jsonify({"message": "Plan created successfully", "plan_id": new_plan.id}), 201

    except Exception as e:
        app.logger.error(f"Error creating plan: {e}")
        return jsonify({"error": f"Server error: {e}"}), 500


# Retrieve plans endpoint 
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
                        "reps": pl.reps
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
    

# Get all existing lifts endpoint
@app.route('/api/lifts', methods=['GET'])
def get_lifts():
    """
    Get all predefined lifts from lifts db.
    """
    lifts = Lift.query.all() # retrieves all lifts
    lifts_data = [{"id": lift.id, "name": lift.name} for lift in lifts] #formatting data into json 
    return jsonify(lifts_data), 200


# -----TRACKING ENDPOINTS  --------

#Track workout endpoint
@app.route('/api/plans/<int:plan_id>/lifts/<int:lift_id>/track', methods=['POST'])
def track_lift_performance(plan_id, lift_id):
    """
    Track the performance of a specific lift in a plan. First ensures plan and planlift exist, then retreives data from user input information 
    (reps performed, weight performed, reps in reserve, soon to be added notes). Populates LiftPerformance record and adds to db.
    """
    try:
        # Validate the existence of the plan and lift
        plan = db.session.get(Plan, plan_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404
        

        # Validate the existence of the lift
        lift = db.session.get(Lift, lift_id)
        if not lift:
            return jsonify({"error": "Lift not found"}), 404

        plan_lift = PlanLift.query.filter_by(plan_id=plan_id, lift_id=lift_id).first()
        if not plan_lift:
            return jsonify({"error": "Lift not found in the specified plan"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400


        user_id = data.get('user_id')
        reps_performed = data.get('reps_performed')
        weight_performed = data.get('weight_performed')
        reps_in_reserve = data.get('reps_in_reserve')
        additional_notes = data.get('additional_notes')
        recommended_weight = true_math(weight_performed,reps_in_reserve)

        # Validate inputs
        if reps_performed is None or weight_performed is None or reps_in_reserve is None:
            return jsonify({"error": "Missing required fields"}), 400
        # Validate data types
        if not isinstance(reps_performed, int) or not isinstance(weight_performed, (int, float)) or not isinstance(reps_in_reserve, int):
            return jsonify({"error": "Invalid data types"}), 400

        # Create a new LiftPerformance record
        performance = LiftPerformance(
            plan_lift_id=plan_lift.id,
            lift_id = lift.id,
            user_id = user_id,
            reps_performed=reps_performed,
            weight_performed=weight_performed,
            reps_in_reserve=reps_in_reserve,
            additional_notes=additional_notes,
            recommended_weight=recommended_weight
        )

        db.session.add(performance) #Adding new record to LiftPerformance db
        db.session.commit()

        return jsonify({
            "message": "Lift performance tracked successfully",
            "performance_id": performance.id
        }), 201

    except Exception as e:
        app.logger.error(f"Error tracking lift performance: {str(e)}")
        return jsonify({"error": "Server error"}), 500
    

#Retrive tracking data for display purposes
@app.route('/api/plans/<int:plan_id>/lifts/<int:lift_id>/track', methods=['GET'])
def get_lift_performance(plan_id, lift_id):
    """
    Retrieve tracking data for a specific lift in a plan. Ensures Plan exists, then ensures PlanLift exists (both by id), and retrieves all performances in order by descending date.
    Puts data into json format and returns list of performance data for frontend display
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
                "reps_in_reserve": perf.reps_in_reserve,
                "additional_notes":perf.additional_notes,
                "future_recommended_weight":perf.future_recommended_weight
            })

        return jsonify(performances_data), 200

    except Exception as e:
        app.logger.error(f"Error retrieving lift performance: {str(e)}")
        return jsonify({"error": "Server error"}), 500
    
    
# Retreive all tracking data for a specific user endpoint
@app.route('/api/users/<int:user_id>/trackings', methods=['GET'])
def get_user_trackings(user_id):
    """
    Retrieve all tracking data for a specific user. Retreives user id, finds all plans that belong to user, searches through all plans and planlift records to find lift_performance records,
    which are then stored into the trackings list in json format to be returned to the frontend for display
    """
    try:
        user = db.session.get(User, user_id) # Getting user id
        if not user:
            return jsonify({"error": "User not found"}), 404

        plans = Plan.query.filter_by(user_id=user_id).all() # Getting plan id
        if not plans:
            return jsonify([]), 200

        trackings = [] #All PlanLift performance records
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
                        "reps_in_reserve": perf.reps_in_reserve,
                        "additional_notes":perf.additional_notes,
                        "recommended_weight":perf.recommended_weight
                    })
                           
        return jsonify(trackings), 200

    except Exception as e:
        app.logger.error(f"Error retrieving user trackings: {str(e)}")
        return jsonify({"error": "Server error"}), 500
    

# Get all performance data for a specific user and lift
@app.route('/api/users/<int:user_id>/lifts/<string:lift_name>/performance', methods=['GET'])
def get_performance_data(user_id, lift_name):
    """
    Get performance data for a specific user and lift.
    """
    # Get the lift ID from the name
    lift = Lift.query.filter_by(name=lift_name).first()
    if not lift:
        return jsonify({"error": "Lift not found"}), 404

    # Look through performance data by user and lift, to find all tracked logs of this lift for this user
    performance_data = LiftPerformance.query.filter_by(user_id=user_id, lift_id=lift.id).all()

    if not performance_data:
        return jsonify({"performance_data": []}), 205 #if user has no tracked logs for this lift

    # Format the data to include only the necessary fields
    performance_data_formatted = [
        {
            "date": record.date.strftime('%Y-%m-%d'),  # date as string
            "weight_performed": record.weight_performed,
            "reps_performed": record.reps_performed
        }
        for record in performance_data
    ]

    return jsonify({"performance_data": performance_data_formatted}), 200 #Success 


#---------GENERATE/REMOVE PLAN ENDPOINTS ------------

# Generate plan using decision tree model endpoint
@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    """
    Generates user plan based on user input and decision tree model. First retrieves user inputed data in json form, creates plan name based on selected user input (target body parts),
    and ensures no existing plan of identical name exists. Calls our prediction model with features (user input), returning our target information (lifts and reps). These predictions are then
    seperated into individual lifts and added to the new Plan, PlanLift information before being sent to the database.
    """
    try:
        data = request.get_json() # recieving json information from frontend
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        user_id = data.get('user_id') 
        goal = data.get('goal')  # "hypertrophy" or "strength" selection
        body_parts = data.get('body_parts')  # List of body parts to focus on for prediction model

        if not user_id or not goal or not body_parts:
            return jsonify({"error": "user_id, goal, and body_parts are required"}), 400

        # Generate plan name, if 1 body part targeted - __ workout, if 2 - __ and __ workout, if more so on
        if len(body_parts) == 1:
            plan_name = f"{body_parts[0]} workout"
        elif len(body_parts) == 2:
            plan_name = f"{body_parts[0]} and {body_parts[1]} workout"
        else:
            plan_name = f"{', '.join(body_parts[:-1])}, and {body_parts[-1]} workout"

        # Check if a plan with the same name already exists for the user, if it does - do not make new plan
        existing_plan = Plan.query.filter_by(user_id=user_id, plan_name=plan_name).first()
        if existing_plan:
            return jsonify({"error": f"A plan named '{plan_name}' already exists."}), 400

        # Predict lifts and reps using the model
        predictions = predict_lifts(goal, body_parts)

        # Create the Plan
        new_plan = Plan(
            user_id=user_id,
            plan_name=plan_name,
            plan_type=goal,
            plan_duration="50"  # Default duration for now
        )
        db.session.add(new_plan) #adding new plan to database
        db.session.flush()  # Get the plan ID without committing

        # Add lifts to the Plan
        for prediction in predictions:
            lift_names = prediction.get('lift_name').split(';')  # Split semicolon-separated lifts
            for lift_name in lift_names:
                lift_name = lift_name.strip()  # Clean up whitespace
                lift = Lift.query.filter_by(name=lift_name).first() # finding lifts in database based on name

                if not lift:
                    continue

                plan_lift = PlanLift( #Create plan lift with lift, plan_id, 
                    plan_id=new_plan.id,
                    lift_id=lift.id,
                    sets=3,
                    reps=prediction.get('reps', 10), #predicted reps
                )
                db.session.add(plan_lift) # Adding to database

        db.session.commit() 

        return jsonify({"message": "Plan generated successfully", "plan_name": plan_name}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {e}"}), 500


# Remove existing plan endpoint
@app.route('/api/delete-plan', methods=['POST'])
def delete_plan():
    """
    Delete plan by plan id, first retreives json data of selected plan to delete, finds and deletes plan from Plans DB and other relational tables
    """
    try:
        if request.is_json:
            data = request.get_json()
            plan_id = data.get('plan_id')
        else:
            plan_id = request.form.get('plan_id')

        if not plan_id:
            return jsonify({"error": "Plan ID is required"}), 400

        # Find plan in the database
        plan = Plan.query.get(plan_id)
        if not plan:
            return jsonify({"error": f"Plan with ID {plan_id} not found"}), 404

        # Deleting related PlanLift records manually incase cascade delete fails - models.py
        PlanLift.query.filter_by(plan_id=plan_id).delete()

        # Delete plan
        db.session.delete(plan)
        db.session.commit()

        return jsonify({"message": f"Plan {plan_id} deleted successfully"}), 200

    except Exception as e:
        app.logger.error(f"Error deleting plan: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while deleting the plan"}), 500
    


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
