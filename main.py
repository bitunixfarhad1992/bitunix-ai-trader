from bitunix_api import BitunixAPI
from analyzer import Analyzer
from predictor import LSTMPredictor
import pandas as pd

# API KEY ها
API_KEY = "67a81a5d771221a450cb1730b90dad61"
API_SECRET = "52cdd54e7d843e897cc2418ff356050f"

client = BitunixAPI(API_KEY, API_SECRET)
predictor = LSTMPredictor()

symbol = "BTCUSDT"
quantity_in_usdt = 50
leverage = 10

# گرفتن آخرین 50 کندل 5 دقیقه‌ای
data = client.get_kline(symbol=symbol, interval="5m", limit=50)
kline_data = pd.DataFrame(data['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
kline_data['timestamp'] = pd.to_datetime(kline_data['timestamp'], unit='ms')
kline_data.set_index('timestamp', inplace=True)
kline_data = kline_data.astype(float)

# اجرای تحلیل تکنیکال
analyzer = Analyzer(kline_data)
analyzer.calculate_indicators()
entry_score = analyzer.check_entry()

# پیش‌بینی قیمت آینده با LSTM
predicted_price = predictor.predict_next_price(kline_data)
last_price = kline_data['close'].iloc[-1]

print("Entry Score:", entry_score)
print("Predicted price:", predicted_price)

# شرط ورود به معامله:
if entry_score >= 4 and predicted_price > last_price * 1.002:
    print("✅ سیگنال لانگ")
    price = client.get_market_price(symbol)
    qty = round(quantity_in_usdt / price, 4)
    response = client.place_order(symbol, side=1, price=price, quantity=qty, position_side="LONG", leverage=leverage)
    print(response)

elif entry_score >= 4 and predicted_price < last_price * 0.998:
    print("✅ سیگنال شورت")
    price = client.get_market_price(symbol)
    qty = round(quantity_in_usdt / price, 4)
    response = client.place_order(symbol, side=2, price=price, quantity=qty, position_side="SHORT", leverage=leverage)
    print(response)

else:
    print("❌ سیگنال ورود داده نشد")
