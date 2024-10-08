import base64
import hashlib
import hmac
import requests
import time
import json
import pandas


class KucoinAPI:
    base_url: str = "https://api-futures.kucoin.com"
    PASSPHRASE = ""
    API_SECRET = ""
    API_KEY = ""

    def set_api(self, api_key: str, api_secret: str, passphrase: str):
        self.PASSPHRASE: str = passphrase
        self.API_SECRET: str = api_secret
        self.API_KEY: str = api_key

    def make_header(self, method: str, endpoint: str, body: dict) -> dict:
        if not self.PASSPHRASE or not self.API_SECRET or not self.API_KEY:
            raise Exception("empty Kucoin API")

        now = int(time.time() * 1000)
        data_json = json.dumps(body)
        str_to_sign = str(now) + method + endpoint + data_json
        signature = base64.b64encode(
            hmac.new(self.API_SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
        passphrase = base64.b64encode(
            hmac.new(self.API_SECRET.encode('utf-8'), self.PASSPHRASE.encode('utf-8'), hashlib.sha256).digest())
        return {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": self.API_KEY,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
        }

    def get_candles(self, interval: str, currency_pair: str) -> list:
        response = requests.get(
            self.base_url + "/api/v1/market/candles",
            params={
                "symbol": currency_pair,
                "type": interval
            },
            headers=self.make_header("GET", "/api/v1/market/candles", {})
        )
        return response.json()["data"]

    def make_order(
            self, currency_pair: str, side: str,
            stop: str, stop_price: float, leverage: int, quantity: int, limit_price: float,
            type: str = "limit", stop_price_type: str = "TP") -> str:
        body: dict = {
            "clientOid": "test",
            "type": type,
            "stopPriceType": stop_price_type,
            "stop": stop,
            "symbol": currency_pair,
            "side": side,
            "stopPrice": str(stop_price),
            "size": str(quantity),
            "price": str(limit_price),
            "leverage": str(leverage)
        }
        response: requests.Response = requests.post(
            self.base_url + "/api/v1/orders",
            data=json.dumps(body),
            headers=self.make_header("POST", "/api/v1/orders", body)
        )
        print(response.json())
        return response.json()["data"]["orderId"]

    def get_candles(self, currency_pair: str, interval: str) -> pandas.DataFrame:  # doesn't work
        end_time = time.time() * 1000

        if interval == "1m":
            granularity = 1
        else:
            granularity = 15

        start_time = end_time - granularity * 6000 * 500
        response = requests.get(
            self.base_url + "/api/v1/kline/query",
            params={
                "symbol": currency_pair,
                "granularity": granularity,
                "from": start_time,
                "to": end_time
            }
        )
        print(response.json())
        # data = response.json()["data"]
        # print(data, len(data))

    def get_order(self, order_id: str) -> dict:
        params = {
            "order-id": order_id
        }
        return requests.get(
            self.base_url + "/api/v1/orders/" + order_id,
            headers=self.make_header("GET", "/api/v1/orders/" + order_id, {})
        ).json()


if __name__ == "__main__":
    api = KucoinAPI()
    api.set_api(
        "64816ce56152270001860c9f",
        "32f40af3-4599-4b42-9df4-7d68909c3842",
        "^r3*3rh!3JJk)9Lq-+"
    )
    # print(api.get_order(api.make_order("DOGEUSDTM", "buy", "up", 0.06145, 10, 100, 0.06145)))
    print(api.get_order("5bd6e9286d99522a52e458de"))