import os
import pickle
from sklearn.tree import DecisionTreeClassifier  

path = 'saved_models/decision_tree_model.pkl'

class DecisionTreeModel:
    def __init__(self):
        self.model = DecisionTreeClassifier()  

    def train(self, X, y):  #trains the model with data x, targets y
        self.model.fit(X, y)

    def predict(self, X): #trained model for making predictions on input data x
        return self.model.predict(X)

    def save_model(self, path): #save the model in our saved_models directory
        os.makedirs(os.path.dirname(path),exist_ok=True)
        with open(path, 'wb') as file:
            pickle.dump(self.model, file)

    def load_model(self, path): #loads model
        with open(path, 'rb') as file:
            self.model = pickle.load(file)
