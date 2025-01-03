import pandas as pd
import pickle
from decision_tree import DecisionTreeModel

# Load the model
dt_model = DecisionTreeModel()
dt_model.load_model('../saved_models/decision_tree_model.pkl')
print("Model loaded successfully.")

# Load the label encoder
with open('../saved_models/label_encoder.pkl', 'rb') as file:
    label_encoder = pickle.load(file)

def predict(input_goal, input_body_parts):
    inputs = [input_goal] + input_body_parts
    prediction = dt_model.predict([inputs])[0]
    return prediction