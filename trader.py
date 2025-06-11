import time
import pandas as pd
from bitunix_api import BitunixAPI
from analyzer import Analyzer
from predictor import LSTMPredictor

class AutoTrader:
    def __init__(self, api_key, api_secret, symbol="BTCUSDT", quantity_usdt=50, leverage=10):
        self.client = BitunixAPI(api_key, api_secret)
        self.predictor = LSTMPredictor()
        self.symbol = symbol
        self.quantity_usdt = quantity_usdt
        self.leverage = leverage
        self.position = None  # برای ثبت وضعیت پوزیشن باز

    def get_kline_data(self):
        data = self.client.get_kline(symbol=self.symbol, interval="5m", limit=50)
        df = pd.DataFrame(data['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df.astype(float)
        return df

    def analyze_market(self, df):
        analyzer = Analyzer(df)
        analyzer.calculate_indicators()
        score = analyzer.check_entry()
        prediction = self.predictor.predict_next_price(df)
        last_price = df['close'].iloc[-1]
        return score, prediction, last_price

    def open_position(self, direction, price):
        qty = round(self.quantity_usdt / price, 4)
        side = 1 if direction == "LONG" else 2
        pos_side = "LONG" if direction == "LONG" else "SHORT"
        response = self.client.place_order(self.symbol, side, price, qty, pos_side, self.leverage)
        print("Order response:", response)
        if response.get('code') == 0:
            self.position = {
                'direction': direction,
                'entry_price': price,
                'quantity': qty
            }

    def close_position(self, direction):
        price = self.client.get_market_price(self.symbol)
        qty = self.position['quantity']
        side = 2 if direction == "LONG" else 1
        pos_side = "LONG" if direction == "LONG" else "SHORT"
        response = self.client.place_order(self.symbol, side, price, qty, pos_side, self.leverage)
        print("Closing position:", response)
        self.position = None

    def run(self):
        while True:
            try:
                df = self.get_kline_data()
                score, prediction, last_price = self.analyze_market(df)
                price = self.client.get_market_price(self.symbol)

                if self.position is None:
                    if score >= 4 and prediction > last_price * 1.002:
                        print("✅ Open LONG")
                        self.open_position("LONG", price)

                    elif score >= 4 and prediction < last_price * 0.998:
                        print("✅ Open SHORT")
                        self.open_position("SHORT", price)

                    else:
                        print("🔎 No signal... waiting")

                else:
                    entry = self.position['entry_price']
                    direction = self.position['direction']

                    if direction == "LONG":
                        tp = entry * 1.015
                        sl = entry * 0.99
                        if price >= tp or price <= sl:
                            print("📈 Take Profit or Stop Loss hit (LONG)")
                            self.close_position(direction)

                    elif direction == "SHORT":
                        tp = entry * 0.985
                        sl = entry * 1.01
                        if price <= tp or price >= sl:
                            print("📉 Take Profit or Stop Loss hit (SHORT)")
                            self.close_position(direction)

                time.sleep(60)  # هر دقیقه بررسی می‌کند

            except Exception as e:
                print("Error:", e)
                time.sleep(60)
