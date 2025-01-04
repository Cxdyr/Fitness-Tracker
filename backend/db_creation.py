from app import app
from models import db, Lift

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

    with app.app_context():
        for lift_data in predefined_lifts:
            existing_lift = Lift.query.filter_by(name=lift_data["name"]).first()
            if not existing_lift:
                new_lift = Lift(name=lift_data["name"])
                db.session.add(new_lift)
                print(f"Added lift: {new_lift.name}")
        db.session.commit()
        print("Lifts populated successfully!")

if __name__ == "__main__":
    populate_lifts()
