import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import joblib

# دریافت داده
df = pd.read_csv("historical_data.csv")  # فایل CSV شامل حداقل 500 کندل

# فقط ستون Close
close_prices = df['close'].values.reshape(-1, 1)

# نرمال‌سازی داده
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(close_prices)

# ذخیره Scaler
joblib.dump(scaler, "scaler_lstm.save")

# ایجاد sequence‌ها
X = []
y = []
sequence_length = 50

for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i - sequence_length:i])
    y.append(scaled_data[i])

X, y = np.array(X), np.array(y)

# ساخت مدل
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(64, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mse')
model.fit(X, y, epochs=30, batch_size=32)

# ذخیره مدل
model.save("model_lstm_bitunix.h5")
