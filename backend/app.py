from datetime import datetime
from flask_bcrypt import Bcrypt
from flask import Flask, jsonify, request
from models import User, db, Lift
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
from config import Config


app = Flask(__name__)
bcrypt = Bcrypt(app)

#App configuration
app.config.from_object(Config)
db.init_app(app)


@app.route('/')
def index():
    return "Backend is running!"

#Register endpoint, ensures format is correct - username is unique - email is unique - and commits new user to table if satisfied redirecting to login page
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data format"}), 400

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "Username already exists"}), 400
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered"}), 400

    try:
        date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        new_user = User(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            username=data.get('username'),
            email=data.get('email'),
            date_of_birth=date_of_birth,
            goal=data.get('goal'),
            password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Server error: {e}"}), 500


#Login endpoint,  makes sure that fields are filled - username exists - and hashed password matches hashed password - then redirects user to dashboard if satisfied
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


#Get users endpoint, fetches all users and full information omitting the hashed password
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_data = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "date_of_birth": user.date_of_birth.strftime('%Y-%m-%d'),
            "goal": user.goal,
            "creation_time": user.creation_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        for user in users
    ]
    return jsonify(users_data)


#Function for prepopulating the lift database table - choices for user day - in user plan -  in future
def populate_lifts():
    predefined_lifts = [
        {"name": "Bench Press", "sets": 3, "reps": 10},
        {"name": "Squat", "sets": 4, "reps": 8},
        {"name": "Deadlift", "sets": 3, "reps": 5},
        {"name": "Overhead Press", "sets": 3, "reps": 8},
        {"name": "Barbell Row", "sets": 3, "reps": 10},
        {"name": "Pull-Ups", "sets": 3, "reps": 8},
        {"name": "Push-Ups", "sets": 3, "reps": 12},
        {"name": "Dumbbell Curl", "sets": 3, "reps": 10},
        {"name": "Tricep Extension", "sets": 3, "reps": 12},
        {"name": "Lunges", "sets": 3, "reps": 10},
    ]
    for lift in predefined_lifts:
        existing_lift = Lift.query.filter_by(name=lift["name"]).first()
        if not existing_lift:
            new_lift = Lift(name=lift["name"], sets=lift["sets"], reps=lift["reps"])
            db.session.add(new_lift)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        populate_lifts()  # Populate the database with predefined lifts
    app.run(debug=True, host='0.0.0.0', port=5001)
