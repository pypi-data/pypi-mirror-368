# # horseracepredictor/predictor.py
#
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import statsmodels.api as sm
# from sklearn.linear_model import LinearRegression
#
# class HorseRacePredictor:
#     def __init__(self):
#         self.weights = None
#         self.biases = None
#         self.model = None
#         self.learning_rate = 0.02
#         self.iterations = 20
#
#     def load_data(self, csv_path):
#         self.data = pd.read_csv(csv_path)
#         self.x = self.data[['saddle', 'decimalPrice', 'runners', 'weight']]
#         self.y = self.data['Winner']
#
#     def linear_regression(self):
#         reg = LinearRegression()
#         reg.fit(self.x, self.y)
#         self.model = reg
#         return reg.coef_, reg.intercept_
#
#     def logistic_regression(self):
#         log_model = sm.Logit(self.y, self.x)
#         result = log_model.fit(disp=0)
#         self.model = result
#         return result.summary()
#
#     def compute_targets(self):
#         self.targets = (
#             -0.00044618449 * self.x['saddle']
#             + 0.963206007 * self.x['decimalPrice']
#             + 0.000387599664 * self.x['runners']
#             - 0.0000333688539 * self.x['weight']
#             - 0.014001054804715737
#         ).values.reshape(-1, 1)
#         return self.targets
#
#     def init_weights(self):
#         self.weights = np.random.uniform(0, 0.1, size=(4, 1))
#         self.biases = np.random.uniform(0, 0.1, size=1)
#
#     def train_model(self):
#         observations = self.x.shape[0]
#         self.init_weights()
#         targets_2d = self.compute_targets()
#
#         for _ in range(self.iterations):
#             outputs = np.dot(self.x, self.weights) + self.biases
#             deltas = outputs - targets_2d
#             loss = np.sum(deltas ** 2) / (2 * observations)
#
#             deltas_scaled = deltas / observations
#             self.weights -= self.learning_rate * np.dot(self.x.T, deltas_scaled)
#             self.biases -= self.learning_rate * np.sum(deltas_scaled)
#
#         return self.weights, self.biases
#
#     def predict(self, threshold=0.35):
#         outputs = np.dot(self.x, self.weights) + self.biases
#         predicted = (outputs.flatten() >= threshold).astype(int)
#         return predicted
#
#     def evaluate(self, predicted):
#         actual = self.y[:len(predicted)].astype(int)
#         correct = (predicted == actual).sum()
#         return {
#             "total": len(predicted),
#             "correct": correct,
#             "accuracy": correct / len(predicted)
#         }






# horseracepredictor/predictor.py

# horseracepredictor/predictor.py

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

class HorseRacePredictor:
    def __init__(self, feature_cols=None, target_col=None):
        self.feature_cols = feature_cols or ['saddle', 'decimalPrice', 'runners', 'weight']
        self.target_col = target_col or 'Winner'
        self.weights = None
        self.biases = None
        self.model = None
        self.learning_rate = 0.02
        self.iterations = 20
        self.data = None
        self.x = None
        self.y = None

    def load_data(self, csv_path):
        """Load CSV data into the model"""
        self.data = pd.read_csv(csv_path)
        self.x = self.data[self.feature_cols]
        self.y = self.data[self.target_col]

    def linear_regression(self):
        """Train using sklearn Linear Regression"""
        reg = LinearRegression()
        reg.fit(self.x, self.y)
        self.model = reg
        return reg.coef_, reg.intercept_

    def logistic_regression(self):
        """Train using statsmodels Logistic Regression"""
        log_model = sm.Logit(self.y, self.x)
        result = log_model.fit(disp=0)
        self.model = result
        return result.summary()

    def compute_targets(self):
        """Custom target computation formula"""
        self.targets = (
            -0.00044618449 * self.x['saddle']
            + 0.963206007 * self.x['decimalPrice']
            + 0.000387599664 * self.x['runners']
            - 0.0000333688539 * self.x['weight']
            - 0.014001054804715737
        ).values.reshape(-1, 1)
        return self.targets

    def init_weights(self):
        """Initialize weights and biases randomly"""
        self.weights = np.random.uniform(0, 0.1, size=(len(self.feature_cols), 1))
        self.biases = np.random.uniform(0, 0.1, size=1)

    def train_model(self):
        """Custom gradient descent training"""
        observations = self.x.shape[0]
        self.init_weights()
        targets_2d = self.compute_targets()

        for _ in range(self.iterations):
            outputs = np.dot(self.x, self.weights) + self.biases
            deltas = outputs - targets_2d
            # Mean squared error loss
            loss = np.sum(deltas ** 2) / (2 * observations)

            # Update weights and biases
            deltas_scaled = deltas / observations
            self.weights -= self.learning_rate * np.dot(self.x.T, deltas_scaled)
            self.biases -= self.learning_rate * np.sum(deltas_scaled)

        return self.weights, self.biases

    def predict(self, threshold=0.35):
        """Predict winners based on trained weights"""
        outputs = np.dot(self.x, self.weights) + self.biases
        predicted = (outputs.flatten() >= threshold).astype(int)
        return predicted

    def evaluate(self, predicted):
        """Return accuracy statistics"""
        actual = self.y[:len(predicted)].astype(int)
        correct = (predicted == actual).sum()
        accuracy = correct / len(predicted)
        return {
            "total": len(predicted),
            "correct": correct,
            "accuracy": accuracy
        }

    def summary(self, threshold=0.35, save_csv=False):
        """Train → Predict → Show summary automatically"""
        predicted = self.predict(threshold=threshold)

        # Store predictions
        self.data['Predicted_Winner'] = predicted

        # Accuracy metrics
        acc = accuracy_score(self.y, predicted)
        cm = confusion_matrix(self.y, predicted)
        cr = classification_report(self.y, predicted)

        print("===== Prediction Summary =====")
        print(f"Total Records: {len(predicted)}")
        print(f"Correct Predictions: {(predicted == self.y).sum()}")
        print(f"Accuracy: {acc * 100:.2f}%")
        print("\nConfusion Matrix:")
        print(cm)
        print("\nClassification Report:")
        print(cr)

        if save_csv:
            self.data.to_csv("prediction_results.csv", index=False)
            print("\nResults saved to 'prediction_results.csv'")
