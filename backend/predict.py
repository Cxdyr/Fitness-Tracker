import pickle
import os
from ML_plan_maker.model.decision_tree import DecisionTreeModel
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
MODEL_PATH = os.path.join(BASE_DIR, 'ML_plan_maker', 'saved_models', 'decision_tree_model.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'ML_plan_maker', 'saved_models', 'label_encoder.pkl')

# Load the model
dt_model = DecisionTreeModel()
dt_model.load_model(MODEL_PATH)
print("Model loaded successfully.")

# Load the label encoder
with open(ENCODER_PATH, 'rb') as file:
    label_encoder = pickle.load(file)
print("Label encoder loaded successfully.")

# Load the label encoder
with open(ENCODER_PATH, 'rb') as file:
    label_encoder = pickle.load(file)
print("Label encoder loaded successfully.")

def predict_lifts(goal, body_parts):
    """
    Predict lifts and reps based on the goal and body parts.
    """
    # Map body parts to one-hot encoding, binary 1 if yes 0 if no
    body_parts_mapping = ['Legs', 'Chest', 'Arms', 'Back', 'Full Body']
    body_parts_input = [1 if part in body_parts else 0 for part in body_parts_mapping]

    # Prepare input data for the model
    input_data = pd.DataFrame([{
        'Goal': 1 if goal == "strength" else 0,
        'Legs': body_parts_input[0],
        'Chest': body_parts_input[1],
        'Arms': body_parts_input[2],
        'Back': body_parts_input[3],
        'Full Body': body_parts_input[4],
    }])

    # Predict using the preloaded model based on user inpuut
    predictions = dt_model.predict(input_data)
    predicted_lifts_encoded = predictions[:, 0].astype(int)
    predicted_reps = predictions[:, 1]

    # Decoding lift names
    predicted_lifts = label_encoder.inverse_transform(predicted_lifts_encoded)

    # Format predictions for API compatibility
    formatted_predictions = [
        {
            "lift_name": lift,
            "reps": int(reps),  # Predicted reps
        }
        for lift, reps in zip(predicted_lifts, predicted_reps)
    ]

    return formatted_predictions # Returning our finalized predictions



