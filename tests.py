from pandas import DataFrame, concat
from api.binance_api import BinanceAPI, GetCandlesRequest
from trade_bot import TradeBot, Predict
from models.exchange_data import ExchangeData
from time import time
from typing import NoReturn
from datetime import datetime
from main import coin_list


def test_work(start_timestamp: int, currency_pairs_list: list[str]) -> NoReturn:
    interval = "5m"
    api = BinanceAPI(
        "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
        "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    )
    trade_bot = TradeBot()
    trade_bot.up_ratio = 4
    trade_bot.down_ratio = 0
    timestamp: int = start_timestamp
    predicts: dict[str, Predict] = {}
    candles_data: dict[str, ExchangeData] = {}
    count = 1500
    now_timestamp = int(time()) * 1000
    print("getting data")

    for currency_pair in currency_pairs_list:
        requests_list: list[GetCandlesRequest] = []
        while timestamp < now_timestamp:
            if (now_timestamp - timestamp) // (5 * 60 * 1000) < 1500:
                count = (now_timestamp - timestamp) // (5 * 60 * 1000)
            if count < 0:
                break
            requests_list.append(
                GetCandlesRequest(currency_pair, interval, timestamp, timestamp + 5 * 60 * 1000 * count, 1500)
            )
            timestamp += 5 * 60 * 1000 * 1500  # for 5m

        candles_data[currency_pair] = ExchangeData(api.get_a_lot_of_candles(requests_list))
        timestamp = start_timestamp

    timestamp = start_timestamp + 500 * 5 * 60 * 1000
    print("data completed")
    win, lose = 0, 0

    while timestamp <= int(time()) * 1000:
        for currency_pair in currency_pairs_list:
            data_frame = candles_data[currency_pair].get_data(timestamp)
            print(datetime.utcfromtimestamp(timestamp / 1000).strftime("%d-%m-%Y %H:%M:%S")
                  + f"wins: {win}, loses: {lose}")
            if currency_pair not in predicts.keys():
                predicts[currency_pair] = trade_bot.make_prediction(data_frame)
                if predicts[currency_pair] is not None:
                    print("OPEN", predicts[currency_pair], currency_pair)
                else:
                    del predicts[currency_pair]
            else:
                last_candle = data_frame.iloc[-1]
                predict = predicts[currency_pair]
                if predict.take_profit_price <= last_candle["high_price"] and predict.close_price < last_candle[
                    "low_price"]:
                    print("CLOSE", "WIN", predict, currency_pair)
                    del predicts[currency_pair]
                    win += 1
                elif predict.close_price >= last_candle["low_price"]:
                    print("CLOSE", "LOSE", predict, currency_pair)
                    del predicts[currency_pair]
                    lose += 1
        timestamp += 5 * 60 * 1000


if __name__ == "__main__":
    # api = BinanceAPI(
    #     "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
    #     "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    # )
    # print(ExchangeData(api.get_candles("BTCUSDT", "5m")).get_data())
    test_work(1685577600000, ["BTCUSDT"])
    # for currency_pair in coin_list:
    #     make_csv_data(1687951557000, currency_pair, "5m")
    #     print(currency_pair, " done!")
