import random
import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('../../instance/fitness_app.db')
cursor = conn.cursor()

# Get all lifts and targeted area 
cursor.execute("SELECT name, targeted_area FROM Lifts")
lifts_data = cursor.fetchall()

# Organize the lifts by target area
exercises = {
    "Legs": [],
    "Chest": [],
    "Arms": [],
    "Back": [],
    "Full Body": []
}

# Loop through the data and organize by target area before closing connection
for lift_name, target_area in lifts_data:
    if target_area in exercises:
        exercises[target_area].append(lift_name)

# Close the connection
conn.close()

# Rep ranges based on the goal - low range for strenght with higher weight and high range with hypertrophy
rep_ranges = {
    1: (4, 6), # Strength
    0: (8, 14), # Hypertrophy
}

def generate_synthetic_data(num_samples):
    data = []
    
    for _ in range(num_samples):
        while True:  # Repeat until valid data is generated
            # Randomly choosing strength or hypertrophy and other body parts being targeted
            goal = random.choice([0, 1])
            legs = random.choice([0, 1])
            chest = random.choice([0, 1])
            arms = random.choice([0, 1])
            back = random.choice([0, 1])
            full_body = random.choice([0, 1])

            # Ensure at least one body part is targeted
            if legs or chest or arms or back or full_body:
                break

        # Set the rep range based on the goal
        rep_min, rep_max = rep_ranges[goal]
        
        # Collecting exercises based on the input - ensuring correct targeting
        lifts = []
        selected_lifts = set()
        
        target_groups = {
            "Legs": legs,
            "Chest": chest,
            "Arms": arms,
            "Back": back,
            "Full Body": full_body
        }
        
        for group, is_targeted in target_groups.items():
            if is_targeted and group in exercises:
                lift = random.choice(exercises[group])
                lifts.append(lift)
                selected_lifts.add(lift)

        # Ensure at least 6 exercises are selected and avoid duplicates
        while 6< len(lifts) <9:
            available_groups = [group for group, is_targeted in target_groups.items() if is_targeted and group in exercises]
            if not available_groups:
                break
            group_choice = random.choice(available_groups)
            new_lift = random.choice(exercises[group_choice])
            
            # Avoid duplicates
            if new_lift not in selected_lifts:
                lifts.append(new_lift)
                selected_lifts.add(new_lift)

        # Reps for the exercises
        reps = random.randint(rep_min, rep_max)
        
        # Create the record for this sample (input and output)
        record = {
            "Goal": goal,
            "Legs": legs,
            "Chest": chest,
            "Arms": arms,
            "Back": back,
            "Full Body": full_body,
            "Lifts": ";".join(lifts),
            "Reps": reps
        }
        
        data.append(record)

    # Convert to dataframe and create csv file
    df = pd.DataFrame(data)
    df.to_csv("../data/Synthetic_data_FF.csv", index=False)
    print(f"Generated {len(data)} samples of synthetic data.")

# Running script
generate_synthetic_data(1000)