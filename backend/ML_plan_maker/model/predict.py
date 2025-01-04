import pickle
import os
from .decision_tree import DecisionTreeModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
MODEL_PATH = os.path.join(BASE_DIR,  '..', 'saved_models', 'decision_tree_model.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, '..', 'saved_models', 'label_encoder.pkl')

# Load the model
dt_model = DecisionTreeModel()
dt_model.load_model(MODEL_PATH)
print("Model loaded successfully.")

# Load the label encoder
with open(ENCODER_PATH, 'rb') as file:
    label_encoder = pickle.load(file)
print("Label encoder loaded successfully.")

def predict(input_goal, input_body_parts):
    inputs = [input_goal] + input_body_parts
    prediction = dt_model.predict([inputs])[0]
    return prediction
