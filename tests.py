import pandas
from api.binance_api import BinanceAPI
from trade_bot import TradeBot, Predict
from time import time
from typing import NoReturn
from datetime import datetime
from main import coin_list


def test_api(api: BinanceAPI) -> None:
    account: dict = api.get_account()
    if account is None:
        raise Exception("BinanceAPI doesn't work!")
    else:
        print("BinanceAPI is working")


def calculate_max_dev_by_month(currency_pair: str) -> float:
    api = BinanceAPI(
        "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
        "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    )
    trade_bot = TradeBot()
    data_frames = []
    now: int = int(time())
    for timestamp in range((now - 2678400) * 1000, now * 1000, 449700000 - 5 * 3600000):
        data_frames.append(api.get_candles(currency_pair, "5m", timestamp, timestamp + 449700000, 1500))
    data_frame = pandas.concat(data_frames)
    trade_bot.make_prediction(data_frame)
    return max(data_frame["%DEV"].tolist())


def test_work(start_timestamp: int, currency_pairs_list: list[str]) -> NoReturn:
    interval = "5m"
    api = BinanceAPI(
        "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
        "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    )
    trade_bot = TradeBot()
    trade_bot.up_ratio = 5
    trade_bot.down_ratio = 3
    timestamp: int = start_timestamp
    predict: Predict = None
    while timestamp <= int(time()) * 1000:
        for currency_pair in currency_pairs_list:
            data_frame = api.get_candles(currency_pair, interval, end_time=timestamp)
            print(datetime.utcfromtimestamp(timestamp / 1000).strftime("%d-%m-%Y %H:%M:%S"))
            if predict is None:
                predict: Predict = trade_bot.make_prediction(data_frame)
            else:
                last_candle = data_frame.iloc[-1]
                if predict.take_profit_price <= last_candle["high_price"] and predict.close_price < last_candle["low_price"]:
                    print(predict, "WIN")
                    predict = None
                elif predict.close_price >= last_candle["low_price"]:
                    print(predict, "LOSE")
                    predict = None
            timestamp += 5 * 60 * 1000


if __name__ == "__main__":
    test_work(1685577600000, ["BTCUSDT"])
