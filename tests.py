from pandas import DataFrame, concat
from api.binance_api import BinanceAPI, GetCandlesRequest
from trade_bot import TradeBot, Predict
from time import time
from typing import NoReturn
from datetime import datetime
from utils import plot_win_rate
from main import coin_list


def get_data(candles_data: DataFrame, timestamp: int = int(time()) * 1000, count_rows: int = 500, interval: str = "5m"):
    if interval == "5m":
        tmp = 5 * 60 * 1000
    else:
        tmp = 0
    result = candles_data.loc[(timestamp - count_rows * tmp) < candles_data["open_time"]].loc[
        candles_data["open_time"] <= timestamp]
    result.dropna(inplace=True)
    if len(result) < 200:
        return None
    else:
        return result


def test_work(start_timestamp: int, currency_pairs_list: list[str]) -> NoReturn:
    interval = "5m"
    api = BinanceAPI()
    api.set_api(
        "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
        "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    )
    trade_bot = TradeBot()
    trade_bot.up_ratio = 4
    trade_bot.down_ratio = 0
    timestamp: int = start_timestamp
    predicts: dict[str, Predict] = {}
    candles_data: dict[str, DataFrame] = {}
    now_timestamp = int(time()) * 1000
    print("getting data")

    for currency_pair in currency_pairs_list:
        count = 1500
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

        candles_data[currency_pair] = api.get_a_lot_of_candles(requests_list)
        timestamp = start_timestamp
        print(currency_pair, "done!")

    timestamp = start_timestamp + 500 * 5 * 60 * 1000
    print("data completed")
    win, lose = 0, 0
    win_rates = {}

    while timestamp <= int(time()) * 1000:
        for currency_pair in currency_pairs_list:
            data_frame = get_data(candles_data[currency_pair], timestamp)
            if currency_pair not in predicts.keys():
                print(datetime.utcfromtimestamp(timestamp / 1000).strftime("%d-%m-%Y %H:%M:%S"),
                      f"wins: {win}, loses: {lose}")
                if data_frame is None:
                    print("little data")
                    continue
                win_rates[data_frame.iloc[-1]["open_time"]] = win / (win + lose) if win != 0 or lose != 0 else 0
                predicts[currency_pair] = trade_bot.make_prediction(data_frame)
                if predicts[currency_pair] is not None:
                    print("OPEN", predicts[currency_pair], currency_pair)
                else:
                    del predicts[currency_pair]
            else:
                last_candle = data_frame.iloc[-1]
                predict = predicts[currency_pair]
                if last_candle["low_price"] <= predict.close_price <= last_candle["high_price"]:
                    print("CLOSE", "LOSE", predict, currency_pair)
                    del predicts[currency_pair]
                    lose += 1
                elif last_candle["low_price"] <= predict.take_profit_price <= last_candle["high_price"]:
                    print("CLOSE", "WIN", predict, currency_pair)
                    del predicts[currency_pair]
                    win += 1
        timestamp += 5 * 60 * 1000

    plot_win_rate(win_rates.values(), win_rates.keys())


if __name__ == "__main__":
    # api = BinanceAPI()
    # print(ExchangeData(api.get_candles("BTCUSDT", "5m")).get_data())
    test_work(1690880416000, ["BTCUSDT"])
    # for currency_pair in coin_list:
    #     make_csv_data(1687951557000, currency_pair, "5m")
    #     print(currency_pair, " done!")