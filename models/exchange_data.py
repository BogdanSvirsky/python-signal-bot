from pandas import DataFrame, concat
from time import time


class ExchangeData:
    def __init__(self, start_data: DataFrame = None):
        if start_data is None:
            self.candles_data: DataFrame = DataFrame()
        else:
            self.candles_data = start_data.copy(True)

    def add_data(self, new_data: DataFrame):
        self.candles_data = concat([self.candles_data, new_data])
        self.candles_data = self.candles_data.sort_values("open_time")

    def get_data(self, timestamp: int = int(time()) * 1000, count_rows: int = 500, interval: str = "5m"):
        if interval == "5m":
            tmp = 5 * 60 * 1000
        else:
            tmp = 0
        print(timestamp - count_rows * tmp, timestamp)
        return self.candles_data.loc[(timestamp - count_rows * tmp) <= self.candles_data["open_time"]].loc[
            self.candles_data["open_time"] <= timestamp]
