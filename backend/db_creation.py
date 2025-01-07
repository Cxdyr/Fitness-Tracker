from app import app
from models import db, Lift

def populate_lifts():
    predefined_lifts = [
        {"name": "Bench Press", "targeted_area": "Chest"},
        {"name": "Barbell Bench Press", "targeted_area": "Chest"},
        {"name": "Barbell Bench Incline Press", "targeted_area": "Chest"},
        {"name": "Dumbbell Flat Press", "targeted_area": "Chest"},
        {"name": "Dumbbell Incline Press", "targeted_area": "Chest"},
        {"name": "Machine Chest Press", "targeted_area": "Chest"},
        {"name": "Squat", "targeted_area": "Legs"},
        {"name": "High Bar Squat", "targeted_area": "Legs"},
        {"name": "Low Bar Squat", "targeted_area": "Legs"},
        {"name": "Box Squat", "targeted_area": "Legs"},
        {"name": "Pin Press Squat", "targeted_area": "Legs"},
        {"name": "Deadlift", "targeted_area": "Back"},
        {"name": "Sumo Deadlift", "targeted_area": "Back"},
        {"name": "Shoulder Dumbbell Press", "targeted_area": "Arms"},
        {"name": "Shoulder Barbell Press", "targeted_area": "Arms"},
        {"name": "Shoulder Machine Press", "targeted_area": "Arms"},
        {"name": "Barbell Row", "targeted_area": "Back"},
        {"name": "Dumbbell Row", "targeted_area": "Back"},
        {"name": "Cable Row", "targeted_area": "Back"},
        {"name": "T-Bar Row", "targeted_area": "Back"},
        {"name": "Pull-Ups", "targeted_area": "Full Body"},
        {"name": "Push-Ups", "targeted_area": "Full Body"},
        {"name": "Dumbbell Curl", "targeted_area": "Arms"},
        {"name": "Barbell Curl", "targeted_area": "Arms"},
        {"name": "Hammer Curl", "targeted_area": "Arms"},
        {"name": "Spider Curl", "targeted_area": "Arms"},
        {"name": "Machine Curl", "targeted_area": "Arms"},
        {"name": "Cable Curl", "targeted_area": "Arms"},
        {"name": "Overhead Tricep Press", "targeted_area": "Arms"},
        {"name": "Overhead Tricep Extensions", "targeted_area": "Arms"},
        {"name": "Single Arm Tricep Extensions", "targeted_area": "Arms"},
        {"name": "Tricep Extension", "targeted_area": "Arms"},
        {"name": "Skull Crushers", "targeted_area": "Arms"},
        {"name": "Tricep Pushdowns", "targeted_area": "Arms"},
        {"name": "Lat Pull Downs", "targeted_area": "Back"},
        {"name": "Lat Pull Overs", "targeted_area": "Back"},
        {"name": "Lat Raises", "targeted_area": "Arms"},
        {"name": "Front Raises", "targeted_area": "Arms"},
        {"name": "Rear Delt Flies", "targeted_area": "Back"},
        {"name": "Pec Deck", "targeted_area": "Chest"},
        {"name": "Cable Chest Press", "targeted_area": "Chest"},
        {"name": "Chest Flies (DB or Cable)", "targeted_area": "Chest"},
        {"name": "Lunges", "targeted_area": "Legs"},
        {"name": "Weighted Dips", "targeted_area": "Full Body"},
        {"name": "Plank", "targeted_area": "Full Body"},
        {"name": "Leg Press", "targeted_area": "Legs"},
        {"name": "Leg Extensions", "targeted_area": "Legs"},
        {"name": "Hamstring Curls", "targeted_area": "Legs"},
        {"name": "Hip Abductors", "targeted_area": "Legs"},
        {"name": "Hip Adductors", "targeted_area": "Legs"},
        {"name": "Hip Thrust", "targeted_area": "Full Body"},
        {"name": "Calf Raise", "targeted_area": "Legs"},
        {"name": "Russian Twist", "targeted_area": "Full Body"},
        {"name": "Upright Row", "targeted_area": "Back"},
        {"name": "Standing Overhead Press", "targeted_area": "Full Body"},
        {"name": "Romanian Deadlift", "targeted_area": "Legs"},
        {"name": "Bulgarian Split Squats", "targeted_area": "Legs"},
    ]

    with app.app_context():
        for lift_data in predefined_lifts:
            existing_lift = Lift.query.filter_by(name=lift_data["name"]).first()
            if not existing_lift:
                new_lift = Lift(name=lift_data["name"], targeted_area = lift_data["targeted_area"])
                db.session.add(new_lift)
                print(f"Added lift: {new_lift.name}")
        db.session.commit()
        print("Lifts populated successfully!")

if __name__ == "__main__":
    with app.app_context():
     db.create_all()
     populate_lifts()
