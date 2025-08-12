
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from mpl_toolkits.mplot3d import Axes3D


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
        self.processed_x = None  # for expanded feature set with dummies
        self.processed_weights = None
        self.processed_biases = None

    def load_data(self, csv_path):
        """Load CSV data into the model"""
        self.data = pd.read_csv(csv_path)
        self.x = self.data[self.feature_cols]
        self.y = self.data[self.target_col]


    def linear_regression(self):
        reg = LinearRegression()
        reg.fit(self.x, self.y)
        self.model = reg
        return reg.coef_, reg.intercept_

    def logistic_regression(self):
        log_model = sm.Logit(self.y, self.x)
        result = log_model.fit(disp=0)
        self.model = result
        return result.summary()

    def compute_targets(self):
        self.targets = (
            -0.00044618449 * self.x['saddle']
            + 0.963206007 * self.x['decimalPrice']
            + 0.000387599664 * self.x['runners']
            - 0.0000333688539 * self.x['weight']
            - 0.014001054804715737
        ).values.reshape(-1, 1)
        return self.targets

    def init_weights(self):
        self.weights = np.random.uniform(0, 0.1, size=(len(self.feature_cols), 1))
        self.biases = np.random.uniform(0, 0.1, size=1)

    def train_model(self):
        observations = self.x.shape[0]
        self.init_weights()
        targets_2d = self.compute_targets()

        for _ in range(self.iterations):
            outputs = np.dot(self.x, self.weights) + self.biases
            deltas = outputs - targets_2d
            loss = np.sum(deltas ** 2) / (2 * observations)
            deltas_scaled = deltas / observations
            self.weights -= self.learning_rate * np.dot(self.x.T, deltas_scaled)
            self.biases -= self.learning_rate * np.sum(deltas_scaled)

        return self.weights, self.biases

    def predict(self, threshold=0.35):
        outputs = np.dot(self.x, self.weights) + self.biases
        predicted = (outputs.flatten() >= threshold).astype(int)
        return predicted

    def evaluate(self, predicted):
        winners_mask = (self.y == 1)
        actual_winners = self.y[winners_mask].astype(int)
        predicted_winners = predicted[winners_mask]
        correct = (predicted_winners == actual_winners).sum()
        accuracy = correct / len(actual_winners) if len(actual_winners) > 0 else 0

        return {
            "total_winners": len(actual_winners),
            "correct": correct,
            "accuracy": accuracy
        }

    def summary(self, threshold=0.35, save_csv=False):
        predicted = self.predict(threshold=threshold)
        self.data['Predicted_Winner'] = predicted

        total_records = len(self.data)
        winners_mask = (self.y == 1)
        actual_winners = self.y[winners_mask]
        predicted_winners = predicted[winners_mask]

        acc = accuracy_score(actual_winners, predicted_winners)
        cm = confusion_matrix(actual_winners, predicted_winners)
        cr = classification_report(actual_winners, predicted_winners)

        print("Prediction Summary")
        print(f"Total Records: {total_records}")
        print(f"Total Winners: {len(actual_winners)}")
        print(f"Correct Predictions: {(predicted_winners == actual_winners).sum()}")
        print(f"Accuracy: {acc * 100:.2f}%")
        print("\nConfusion Matrix:")
        print(cm)
        print("\nClassification Report:")
        print(cr)

        if save_csv:
            self.data.to_csv("prediction_results.csv", index=False)
            print("\nResults saved to 'prediction_results.csv'")


    def prepare_features_with_dummies(self, all_columns):
        """
        Prepares the full feature matrix with categorical variables converted to dummies.
        all_columns: list of columns to include in features, including categorical
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        # Take all required columns from data
        df = self.data[all_columns].copy()
        # Drop rows with missing values
        df.dropna(inplace=True)
        # Separate features and target
        self.y = self.data[self.target_col].loc[df.index]
        # Convert categorical variables to dummies
        self.processed_x = pd.get_dummies(df.drop(columns=[self.target_col], errors='ignore'), drop_first=True)
        print(f"Feature shape: {self.processed_x.shape}")

    def train_with_gradient_descent(self, iterations=26, learning_rate=0.02):
        """
        Manual gradient descent training with expanded feature set (processed_x)
        """
        if self.processed_x is None or self.y is None:
            raise ValueError("Features not prepared. Call prepare_features_with_dummies() first.")
        X_np = self.processed_x.to_numpy()
        targets = self.y.to_numpy().reshape(-1, 1)

        # Initialize weights and biases
        init_range = 0.1
        weights = np.random.uniform(low=-init_range, high=init_range, size=(X_np.shape[1], 1))
        biases = np.random.uniform(low=-init_range, high=init_range, size=1)

        for i in range(iterations):
            outputs = np.dot(X_np, weights) + biases
            deltas = outputs - targets
            loss = np.sum(deltas ** 2) / 2
            print(f"Iteration {i + 1} Loss: {loss:.6f}")

            deltas_scaled = deltas
            weights -= learning_rate * np.dot(X_np.T, deltas_scaled)
            biases -= learning_rate * np.sum(deltas_scaled)

        self.processed_weights = weights
        self.processed_biases = biases
        print("Training completed.")

    def plot_3d_features_vs_prediction(self, feature_x, feature_y):
        """
        3D plot for two features vs predicted targets.
        feature_x, feature_y: column names from processed_x dataframe.
        """
        if self.processed_x is None or self.processed_weights is None or self.processed_biases is None:
            raise ValueError("Model not trained on processed features yet.")

        if feature_x not in self.processed_x.columns or feature_y not in self.processed_x.columns:
            raise ValueError("feature_x and feature_y must be in processed features.")

        X_np = self.processed_x.to_numpy()
        preds = np.dot(X_np, self.processed_weights) + self.processed_biases

        x_vals = self.processed_x[feature_x]
        y_vals = self.processed_x[feature_y]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(x_vals, y_vals, preds.flatten(), marker='o')
        ax.set_xlabel(feature_x)
        ax.set_ylabel(feature_y)
        ax.set_zlabel('Predicted Target')
        ax.view_init(azim=100)
        plt.title("3D Plot: Features vs Predicted Target")
        plt.show()

    def plot_predicted_vs_actual(self):
        """
        Plot predicted outputs vs actual targets for processed features and manual GD model.
        """
        if self.processed_x is None or self.processed_weights is None or self.processed_biases is None:
            raise ValueError("Model not trained on processed features yet.")

        X_np = self.processed_x.to_numpy()
        preds = np.dot(X_np, self.processed_weights) + self.processed_biases
        targets = self.y.to_numpy()

        plt.figure(figsize=(8,6))
        plt.scatter(preds, targets, alpha=0.5)
        plt.xlabel('Predicted Outputs')
        plt.ylabel('Actual Targets')
        plt.title('Predicted vs Actual Targets')
        plt.grid(True)
        plt.show()
