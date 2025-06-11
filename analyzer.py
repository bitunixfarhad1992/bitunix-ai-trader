import pandas as pd
import numpy as np

class Analyzer:

    def __init__(self, df):
        self.df = df

    def calculate_indicators(self):
        df = self.df

        # EMA
        df['EMA9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # Bollinger Bands
        df['Middle_Band'] = df['close'].rolling(window=20).mean()
        df['Upper_Band'] = df['Middle_Band'] + 2 * df['close'].rolling(window=20).std()
        df['Lower_Band'] = df['Middle_Band'] - 2 * df['close'].rolling(window=20).std()

        # ADX
        high = df['high']
        low = df['low']
        close = df['close']
        plus_dm = high.diff()
        minus_dm = low.diff()
        tr1 = abs(high - low)
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
        dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
        df['ADX'] = dx.rolling(window=14).mean()

        # Stochastic RSI
        min_val = df['RSI'].rolling(window=14).min()
        max_val = df['RSI'].rolling(window=14).max()
        df['StochRSI'] = (df['RSI'] - min_val) / (max_val - min_val)

        self.df = df

    def check_entry(self):
        df = self.df
        latest = df.iloc[-1]

        score = 0

        if latest['EMA9'] > latest['EMA21']:
            score += 1
        if latest['RSI'] < 30:
            score += 1
        if latest['MACD'] > latest['Signal_Line']:
            score += 1
        if latest['close'] < latest['Lower_Band']:
            score += 1
        if latest['ADX'] > 20:
            score += 1
        if latest['StochRSI'] < 0.2:
            score += 1

        return score

