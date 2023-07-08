import pandas
import pandas_ta as ta
import numpy
from api.binance_api import BinanceAPI
from scipy.optimize import fsolve
from time import time


class TradeBot:
    def __init__(self):
        print("Trade bot initialized")
        self.ratio: float = 2.75
        self.degree: int = 6
        self.ratio_deviation: float = 1
        self.running: bool = True

    def set_ratio(self, ratio: float):
        self.ratio = ratio

    def set_polynom_degree(self, degree: int):
        self.degree = degree

    def set_ratio_deviation(self, deviation: float):
        self.ratio_deviation = deviation

    def process_data(self, data_frame: pandas.DataFrame):
        data_frame["EMA20"] = ta.ema(data_frame["close_price"], length=20)
        data_frame["EMA50"] = ta.ema(data_frame["close_price"], length=50)
        data_frame["EMA200"] = ta.ema(data_frame["close_price"], length=200)

        bbands: pandas.DataFrame = ta.bbands(data_frame["close_price"], length=20)
        data_frame["BBU"] = bbands["BBU_20_2.0"]  # Bollinger Bands Up
        data_frame["BBD"] = bbands["BBL_20_2.0"]  # Bollinger Bands Down

        data_frame["RSI20"] = ta.rsi(data_frame["close_price"], length=20)
        data_frame["RSI50"] = ta.rsi(data_frame["close_price"], length=50)
        data_frame["RSI200"] = ta.rsi(data_frame["close_price"], length=200)

    def make_prediction(self, data_frame: pandas.DataFrame) -> dict | None:
        if not self.running:
            return None

        self.process_data(data_frame)

        predictions = {}
        data_frame["%DEV"] = (data_frame["open_price"] / data_frame["EMA200"] - 1) * 100
        data_frame.dropna(inplace=True)
        x_data = numpy.array(data_frame["open_time"].tolist())
        y_data = numpy.array(data_frame["%DEV"].tolist())
        approximation = numpy.polynomial.Polynomial.fit(x_data, y_data, self.degree)
        print(approximation)
        y_approx_data = approximation(x_data)
        approx_coefs = approximation.convert().coef
        diff_coefs = []
        for i in range(1, len(approx_coefs)):
            diff_coefs.append(approx_coefs[i] * i)
        diff_y = numpy.polynomial.Polynomial(diff_coefs)
        # utils.plot_approx_diff_data(x_data, y_approx_data, diff_y(x_data))
        diff_roots = fsolve(diff_y)
        print(diff_roots)
        current_time = int(time()) * 1000
        for root in diff_roots:
            if root >= current_time:
                predictions[root] = {

                }  # params of order

        return predictions if predictions != {} else None


if __name__ == "__main__":
    api = BinanceAPI(
        "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
        "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    )
    trade_bot = TradeBot()
    trade_bot.make_prediction(api.get_klines_data("BTCUSDT", "1m"))
