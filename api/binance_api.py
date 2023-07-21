import hashlib
import hmac
from urllib.parse import urlencode
import requests
import time
import pandas
from typing import NoReturn


def get_timestamp() -> int:
    return int(time.time() * 1000)


class BinanceAPI:
    API_KEY = ""
    API_SECRET = ""
    base_url = "https://fapi.binance.com"
    last_orders_id = {}

    def __init__(self, api_key: str, api_secret: str):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.header = {
            "X-MBX-APIKEY": self.API_KEY
        }

    def make_signature(self, body: dict) -> str:
        hashed_sign = hmac.new(self.API_SECRET.encode('utf-8'), urlencode(body).encode('utf-8'),
                               hashlib.sha256).hexdigest()

        return hashed_sign

    def get_account(self) -> dict | None:
        params = {
            "timestamp": get_timestamp()
        }
        params["signature"] = self.make_signature(params)
        print(self.API_KEY)
        response = requests.get(
            self.base_url + "/fapi/v2/account",
            params=params,
            headers=self.header
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def set_dual_position(self, value: bool) -> dict:
        params = {
            "dualSidePosition": "true" if value else "false",
            "timestamp": get_timestamp()
        }
        params["signature"] = self.make_signature(params)
        return requests.post(
            "https://fapi.binance.com/fapi/v1/positionSide/dual",
            params=params,
            headers=self.header
        ).json()

    def get_candles(self, currency_pair: str, interval: str, start_time: int = None,
                    end_time: int = None, limit: int = 500) -> pandas.DataFrame | NoReturn:  # time in ms
        params = {
            "symbol": currency_pair,
            "interval": interval,
            "limit": limit,
        }
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        response = requests.get(
            self.base_url + "/fapi/v1/klines",
            params=params
        )
        if response.status_code == 200:
            data = []

            for elem in response.json():
                data.append(
                    [int(elem[0]), float(elem[1]), float(elem[2]), float(elem[3]), float(elem[4]), float(elem[5]),
                     int(elem[6]), float(elem[7]), int(elem[8]), float(elem[9]), float(elem[10]), float(elem[11])]
                )
        else:
            raise Exception("Bad request :(")

        data_frame = pandas.DataFrame(data)
        data_frame = data_frame.drop(columns=[9, 10, 11])
        data_frame.columns = ["open_time", "open_price", "high_price", "low_price", "close_price",
                              "volume", "close_time", "quote_asset_volume", "number_of_trades"]

        return data_frame

    def make_order(self, currency_pair: str, side: str, order_type: str, position_side: str,
                   quantity: float, price: float, leverage: int, stop_price: int = None) -> dict:
        params = {
            "symbol": currency_pair,
            "leverage": str(leverage),
            "timestamp": get_timestamp()
        }
        params["signature"] = self.make_signature(params)

        leverage_response = requests.post(
            self.base_url + "/fapi/v1/leverage",
            params=params,
            headers=self.header
        )

        if leverage_response.status_code != 200:
            print("vse ploho", leverage_response.json())

        params = {
            "symbol": currency_pair,
            "side": side,
            "positionSide": position_side,
            "type": order_type,
            "stopPrice": str(stop_price),
            "quantity": str(quantity),
            "price": str(price),
            "close_position": "true",
            "timeInForce": "GTC",
            "timestamp": get_timestamp()
        }
        params["signature"] = self.make_signature(params)
        response = requests.post(
            self.base_url + "/fapi/v1/order",
            params=params,
            headers=self.header
        )

        if response.status_code == 200:
            self.last_orders_id[currency_pair] = response["clientOrderId"]

        return response.json()

    def cancel_last_order(self, currency_pair: str) -> dict | None:
        if self.last_orders_id:
            params = {
                "symbol": currency_pair,
                "origClientOrderId": self.last_orders_id[currency_pair],
                "timestamp": get_timestamp()
            }
            params["signature"] = self.make_signature(params)
            response = requests.post(
                self.base_url + "/fapi/v1/order",
                params=params,
                headers=self.header
            )

            return response.json()

        return None


if __name__ == "__main__":
    api = BinanceAPI(
        "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
        "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    )

    # print(api.make_order("DOGEUSDT", "BUY", "LIMIT", "LONG", 100, 0.06145, 10))