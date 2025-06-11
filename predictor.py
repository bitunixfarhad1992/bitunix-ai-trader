import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib

class LSTMPredictor:
    def __init__(self, model_path="model_lstm_bitunix.h5", scaler_path="scaler_lstm.save"):
        self.model = load_model(model_path, compile=False)
        self.scaler = joblib.load(scaler_path)

    def predict_next_price(self, df):
        close_data = df['close'].values.reshape(-1, 1)
        scaled = self.scaler.transform(close_data)

        X_input = scaled[-50:]
        X_input = X_input.reshape(1, 50, 1)

        predicted_scaled = self.model.predict(X_input)
        predicted_price = self.scaler.inverse_transform(predicted_scaled)

        return predicted_price[0][0]
