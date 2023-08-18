from dataclasses import dataclass
import hashlib
import hmac
from urllib.parse import urlencode
import requests
import time
import pandas
from utils import get_price_tick_size, get_precision, get_lot_tick_size
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed


def get_timestamp() -> int:
    return int(time.time() * 1000)


def process_get_candles_data(response: requests.Response) -> pandas.DataFrame:
    data = []
    for elem in response.json():
        data.append(
            [int(elem[0]), float(elem[1]), float(elem[2]), float(elem[3]), float(elem[4]), float(elem[5]),
             int(elem[6]), float(elem[7]), int(elem[8]), float(elem[9]), float(elem[10]), float(elem[11])]
        )

    data_frame = pandas.DataFrame(data)
    data_frame = data_frame.drop(columns=[9, 10, 11])
    data_frame.columns = ["open_time", "open_price", "high_price", "low_price", "close_price",
                          "volume", "close_time", "quote_asset_volume", "number_of_trades"]

    return data_frame


@dataclass
class GetCandlesRequest:
    currency_pair: str
    interval: str
    start_time: int = None
    end_time: int = None
    limit: int = 500


class BinanceAPI:
    API_KEY = ""
    API_SECRET = ""
    base_url = "https://fapi.binance.com"
    last_orders_id = {}
    header = {}

    def set_api(self, api_key: str, api_secret: str):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.header = {
            "X-MBX-APIKEY": self.API_KEY
        }

    def add_signature(self, body: dict) -> dict:
        hashed_sign = hmac.new(self.API_SECRET.encode('utf-8'), urlencode(body).encode('utf-8'),
                               hashlib.sha256).hexdigest()

        body["signature"] = hashed_sign
        return body

    def get_account(self) -> dict | None:
        params = {
            "timestamp": get_timestamp()
        }
        print(self.API_KEY)
        response = requests.get(
            self.base_url + "/fapi/v2/account",
            params=self.add_signature(params),
            headers=self.header
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(response.json())
            return None

    def set_dual_position(self, value: bool) -> dict:
        params = {
            "dualSidePosition": "true" if value else "false",
            "timestamp": get_timestamp()
        }
        return requests.post(
            self.base_url + "/fapi/v1/positionSide/dual",
            params=self.add_signature(params),
            headers=self.header
        ).json()

    def get_candles(self, currency_pair: str, interval: str, start_time: int = None,
                    end_time: int = None, limit: int = 500) -> pandas.DataFrame:  # time in ms
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
            return process_get_candles_data(response)
        else:
            raise Exception("Bad request :(")

    def get_a_lot_of_candles(self, requests_list: list[GetCandlesRequest]) -> pandas.DataFrame:
        result = pandas.DataFrame()
        futures = []

        with FuturesSession() as session:
            for get_candles_request in requests_list:
                params = {
                    "symbol": get_candles_request.currency_pair,
                    "interval": get_candles_request.interval,
                    "limit": get_candles_request.limit,
                }
                if get_candles_request.start_time is not None:
                    params["startTime"] = get_candles_request.start_time
                if get_candles_request.end_time is not None:
                    params["endTime"] = get_candles_request.end_time

                futures.append(session.get(
                    self.base_url + "/fapi/v1/klines",
                    params=params
                ))

        for future in as_completed(futures):
            if future.result().status_code == 200:
                result = pandas.concat([result, process_get_candles_data(future.result())])
            else:
                print(future.result())

        result = result.sort_values("open_time", ignore_index=True)

        return result

    def make_order(self, currency_pair: str, side: str, order_type: str, price: float, leverage: int, quantity: int,
                   stop_price: float = None, stop_price_type: str = None, position_side: str = "BOTH",
                   time_in_force: str = "FOK", reduce_only: bool = None) -> dict:
        params = {
            "symbol": currency_pair,
            "leverage": leverage,
            "timestamp": get_timestamp()
        }
        leverage_response = requests.post(
            self.base_url + "/fapi/v1/leverage",
            params=self.add_signature(params),
            headers=self.header
        )

        if leverage_response.status_code != 200:
            print("vse ploho", leverage_response.json())

        price_tick_size = get_precision(get_price_tick_size(currency_pair, self.get_exchange_info()))
        lot_tick_size = get_precision(
            get_lot_tick_size(currency_pair, self.get_exchange_info(), order_type == "MARKET")
        )
        print(price_tick_size, lot_tick_size)

        params = {
            "symbol": currency_pair,
            "side": side,
            "type": order_type,
            "price": str(round(price, price_tick_size)),
            "timeInForce": time_in_force,
            "timestamp": get_timestamp(),
            "quantity": str(round(quantity, lot_tick_size)),
            "positionSide": position_side
        }

        if stop_price is not None:
            params["stopPrice"] = str(round(stop_price, price_tick_size))
        if stop_price_type is not None:
            params["stopPriceType"] = stop_price_type
        if reduce_only is not None:
            params["reduceOnly"] = reduce_only

        print(params)

        response = requests.post(
            self.base_url + "/fapi/v1/order",
            params=self.add_signature(params),
            headers=self.header
        )

        return response.json()

    def cancel_order(self, currency_pair: str, client_order_id: str) -> dict | None:
        params = {
            "symbol": currency_pair,
            "origClientOrderId": client_order_id,
            "timestamp": get_timestamp()
        }
        response = requests.post(
            self.base_url + "/fapi/v1/order",
            params=self.add_signature(params),
            headers=self.header
        )

        return response.json()

    def get_order(self, currency_pair: str, client_order_id: str) -> dict:
        params = {
            "symbol": currency_pair,
            "origClientOrderId": client_order_id,
            "timestamp": get_timestamp()
        }
        response = requests.get(
            self.base_url + "/fapi/v1/order",
            params=self.add_signature(params),
            headers=self.header
        )
        return response.json()

    def get_exchange_info(self) -> dict:
        response = requests.get(
            self.base_url + "/fapi/v1/exchangeInfo",
            headers=self.header
        )
        return response.json()


if __name__ == "__main__":
    api = BinanceAPI()
    api.set_api(
        "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
        "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    )
    # print(api.set_dual_position(False))
    price = api.get_candles("DOGEUSDT", "5m").iloc[-1]["close_price"]
    # order1 = api.make_order("DOGEUSDT", "BUY", "LIMIT", price, 20, 100, time_in_force="GTC")
    # order2 = api.make_order("DOGEUSDT", "SELL", "STOP", price * 0.99, 20, 100,
    #                         stop_price=price * 0.99, time_in_force="GTC")
    # order3 = api.make_order("DOGEUSDT", "SELL", "TAKE_PROFIT", price * 1.03, 20, 100,
    #                         stop_price=price * 1.03, time_in_force="GTC")
    # print(order1, "open1")
    # print(order2, "open2")
    # print(order3, "open2")
    # print(api.cancel_order("DOGEUSDT", order1["clientOrderId"]), "close1")
    # print(api.cancel_order("DOGEUSDT", order2["clientOrderId"]), "close2")
