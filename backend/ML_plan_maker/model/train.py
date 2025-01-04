import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from .decision_tree import DecisionTreeModel

data_path = '../data/trainingdata.csv'

# Load the data
data = pd.read_csv(data_path)

# defining tne features (X) and labels (y)
X = data.iloc[:, :-2]  # All columns except the last two for training data
y_lifts = data['Lifts']  # Lifts are target 1
y_reps = data['Reps']  # Reps as target 2

# Encode the Lifts column because we cannot use strings
label_encoder = LabelEncoder()
y_lifts_encoded = label_encoder.fit_transform(y_lifts)

# Combining lifts and reps 
y = pd.DataFrame({'Lifts': y_lifts_encoded, 'Reps': y_reps})

# Featurs must be numeric
X = X.apply(pd.to_numeric, errors='coerce')

# Combine X and y to drop rows with missing values consistently
data_cleaned = pd.concat([X, y], axis=1).dropna()

# Split cleaned data
X = data_cleaned.iloc[:, :-2]
y = data_cleaned.iloc[:, -2:]

#Training model
dt_model = DecisionTreeModel()
dt_model.train(X, y)

model_path = '../saved_models/decision_tree_model.pkl'
dt_model.save_model(model_path)

encoder_path = '../saved_models/label_encoder.pkl'
with open(encoder_path, 'wb') as file:
    pickle.dump(label_encoder, file)

print(f"Model trained and saved as '{model_path}'.")
print(f"Label encoder saved as '{encoder_path}'.")
