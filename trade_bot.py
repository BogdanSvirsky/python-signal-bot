import pandas
import pandas_ta as ta
import numpy
import utils
from api.binance_api import BinanceAPI
from typing import NoReturn
from scipy.optimize import fsolve
from dataclasses import dataclass


def process_data(data_frame: pandas.DataFrame):
    data_frame["EMA20"] = ta.ema(data_frame["close_price"], length=20)
    data_frame["EMA50"] = ta.ema(data_frame["close_price"], length=50)
    data_frame["EMA200"] = ta.ema(data_frame["close_price"], length=200)

    bbands: pandas.DataFrame = ta.bbands(data_frame["close_price"], length=20)
    data_frame["BBU"] = bbands["BBU_20_2.0"]  # Bollinger Bands Up
    data_frame["BBD"] = bbands["BBL_20_2.0"]  # Bollinger Bands Down

    data_frame["RSI20"] = ta.rsi(data_frame["close_price"], length=20)
    data_frame["RSI50"] = ta.rsi(data_frame["close_price"], length=50)
    data_frame["RSI200"] = ta.rsi(data_frame["close_price"], length=200)
    last = str(data_frame["RSI20"]) + str(data_frame["RSI50"]) + str(data_frame["RSI200"])
    data_frame.dropna(inplace=True)
    if data_frame.empty:
        print("empty2", last)


@dataclass
class Predict:
    type: str
    take_profit_price: float
    close_price: float

    def __str__(self):
        return ' '.join([self.type, str(self.take_profit_price), str(self.close_price)])


class TradeBot:
    def __init__(self):
        print("Trade bot initialized")
        self.down_ratio: float = 4
        self.up_ratio: float = 4.5
        self.degree: int = 6
        self.ratio_deviation: float = 1
        self.running: bool = True

    def make_prediction(self, data_frame: pandas.DataFrame) -> Predict | None:
        if not self.running:
            return None

        if "%DEV" not in data_frame.columns.values:
            process_data(data_frame)

        data_frame["%DEV"] = (data_frame["open_price"] / data_frame["EMA200"] - 1) * 100
        x_data = numpy.array(data_frame["open_time"].tolist())
        y_data = numpy.array(data_frame["%DEV"].tolist())
        try:
            approximation = numpy.polynomial.Polynomial.fit(x_data, y_data, self.degree)
        except Exception as e:
            print(e)
            return None
        last_timestamp = x_data[-1]
        interval = 10000  # interval in ms, where we want to see a roots
        diff_y = approximation.deriv()
        diff_roots = fsolve(diff_y, numpy.array([last_timestamp - interval, last_timestamp + interval]))
        for root in diff_roots:
            # current_price = data_frame["EMA200"].iloc[-1] * 1.0275  # test
            current_price = data_frame["close_price"].iloc[-1]
            if self.down_ratio <= approximation(root) <= self.up_ratio:
                predict = Predict("SHORT", current_price * 0.985, current_price * 1.005)
                return predict
            elif -self.down_ratio >= approximation(root) >= -self.up_ratio:
                predict = Predict("LONG", current_price * 1.015, current_price * 0.995)
                return predict
        return


if __name__ == "__main__":
    pass
    # trade_bot.make_prediction(api.get_candles("BTCUSDT", "5m"))
