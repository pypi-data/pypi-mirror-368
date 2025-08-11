from horseracepredictor import HorseRacePredictor

predictor = HorseRacePredictor()
predictor.load_data('2019_Jan_Mar-4.csv')
predictor.linear_regression()
predictor.train_model()
predictions = predictor.predict(threshold=0.35)
results = predictor.evaluate(predictions)

print("Results:", results)
