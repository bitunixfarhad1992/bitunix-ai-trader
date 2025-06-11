import time
import hmac
import hashlib
import requests
import json

class BitunixAPI:
    def __init__(self, api_key, api_secret):
        self.base_url = "https://api.bitunix.com"
        self.api_key = api_key
        self.api_secret = api_secret

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, method, endpoint, timestamp, query_string="", body=""):
        message = f"{timestamp}{method}{endpoint}{query_string}{body}"
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _send_request(self, method, endpoint, params=None, data=None, private=False):
        url = self.base_url + endpoint
        timestamp = self._get_timestamp()
        query_string = ""
        body = ""

        headers = {
            "Content-Type": "application/json"
        }

        if params:
            query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            url += query_string

        if data:
            body = json.dumps(data)

        if private:
            signature = self._sign(method, endpoint, timestamp, query_string, body)
            headers.update({
                "ApiKey": self.api_key,
                "Request-Time": timestamp,
                "Signature": signature
            })

        response = requests.request(method, url, headers=headers, data=body)
        return response.json()

    def get_kline(self, symbol="BTCUSDT", interval="5m", limit=100):
        endpoint = "/v1/market/kline"
        params = {"symbol": symbol,"interval": interval,"limit": limit}
        return self._send_request("GET", endpoint, params=params)

    def get_market_price(self, symbol="BTCUSDT"):
        endpoint = "/v1/market/ticker"
        params = {"symbol": symbol}
        response = self._send_request("GET", endpoint, params=params)
        return float(response['data'][0]['lastPrice'])

    def place_order(self, symbol, side, price, quantity, position_side="LONG", leverage=10):
        endpoint = "/v1/private/order/create"
        data = {
            "symbol": symbol,
            "price": str(price),
            "vol": str(quantity),
            "side": side,
            "leverage": leverage,
            "positionSide": position_side,
            "orderType": 1,
            "tradeType": 1,
            "openType": 1,
            "externalOid": str(int(time.time() * 1000))
        }
        return self._send_request("POST", endpoint, data=data, private=True)
