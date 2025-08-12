# from horseracepredictor import HorseRacePredictor
#
# predictor = HorseRacePredictor(feature_cols=['saddle', 'decimalPrice', 'runners', 'weight'], target_col='Winner')
# predictor.load_data("2019_Jan_Mar-4.csv")
# predictor.train()
# # predictor.plot_predictions()


# from horseracepredictor import HorseRacePredictor
# from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
# import numpy as np
#
# predictor = HorseRacePredictor(
#     feature_cols=['saddle', 'decimalPrice', 'runners', 'weight'],
#     target_col='Winner'
# )
#
# predictor.load_data("2019_Jan_Mar-4.csv")
# predictor.train()
#
# # Get predictions
# predictions = predictor.predict()
#
# # Convert to class labels if needed
# if predictions.ndim > 1 and predictions.shape[1] == 2:
#     predictions = np.argmax(predictions, axis=1)
# elif np.issubdtype(predictions.dtype, np.floating):
#     predictions = (predictions >= 0.5).astype(int)
#
# # Store results
# predictor.data['Predicted_Winner'] = predictions
#
# # Calculate accuracy
# accuracy = accuracy_score(predictor.data['Winner'], predictor.data['Predicted_Winner'])
# correct_count = (predictor.data['Winner'] == predictor.data['Predicted_Winner']).sum()
# total_count = len(predictor.data)
#
# # Summary output
# print(f"Total Records: {total_count}")
# print(f"Correct Predictions: {correct_count}")
# print(f"Accuracy: {accuracy * 100:.2f}%")
# print("\nConfusion Matrix:")
# print(confusion_matrix(predictor.data['Winner'], predictor.data['Predicted_Winner']))
# print("\nClassification Report:")
# print(classification_report(predictor.data['Winner'], predictor.data['Predicted_Winner']))
#
# # Save results
# predictor.data.to_csv("prediction_results.csv", index=False)
# print("\nResults saved to 'prediction_results.csv'")





# # test_run.py
#
# from horseracepredictor import HorseRacePredictor
#
# # Create the predictor
# predictor = HorseRacePredictor(
# )
#
# # Step 1: Load the data
# predictor.load_data("2019_Jan_Mar-4.csv")
#
# # Step 2: Train the model
# weights, biases = predictor.train_model()
# print("Model trained with weights:", weights.flatten())
# print("Bias:", biases)
#
# # Step 3 & 4: Show summary (includes accuracy, confusion matrix, classification report)
# predictor.summary(threshold=0.35, save_csv=True)
#
# # Step 5 (optional): Get predictions explicitly if needed
# predicted = predictor.predict(threshold=0.35)
# print("Predicted classes:", predicted)
#
# # Optional: print all available methods and attributes if you want to explore
# # print(dir(predictor))


from horseracepredictor import HorseRacePredictor

predictor = HorseRacePredictor()

# Step 1: Load data
csv_file = "2019_Jan_Mar-4.csv"
predictor.load_data(csv_file)

# Step 2: Train using original feature set and gradient descent
print("\nTraining model with original features using gradient descent...")
weights, biases = predictor.train_model()
print("Training completed.")
print("Weights:", weights.flatten())
print("Bias:", biases)

# Step 3: Summary of original feature model (accuracy, confusion matrix, etc.)
print("\nSummary of predictions with feature set:")
predictor.summary(threshold=0.35, save_csv=True)

# Step 4: Prepare expanded features with dummies (include categorical columns)
expanded_features = [
    'ncond', 'class', 'saddle', 'decimalPrice', 'isFav',
    'positionL', 'dist', 'headGear', 'runners', 'weight'
]
print(f"\nPreparing expanded feature: {expanded_features}")
predictor.prepare_features_with_dummies(expanded_features)

# Step 5: Train on expanded features with manual gradient descent
print("\nTraining model with expanded features using manual gradient descent...")
predictor.train_with_gradient_descent(iterations=26, learning_rate=0.02)

# Step 6: Plot 3D visualization of two features vs predicted target
print("\nPlotting 3D features vs prediction...")
predictor.plot_3d_features_vs_prediction(feature_x='decimalPrice', feature_y='weight')

# Step 7: Plot predicted vs actual for expanded feature model (uncomment if needed)
# print("\nPlotting predicted vs actual targets for expanded features...")
# predictor.plot_predicted_vs_actual()
