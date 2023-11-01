import numpy
from matplotlib import pyplot
from decimal import Decimal


def simple_plot(x_data, y_data):
    fig, ax = pyplot.subplots(ncols=1, nrows=1, figsize=(12, 12))
    ax.plot(x_data, y_data, marker="x", color="red", label="Значения", linewidth=0)
    ax.set_xlabel("Временные метки")
    ax.set_ylabel("% отклонения от EMA200")
    ax.legend()
    pyplot.show()


def plot_approx_data(x_data: numpy.core.multiarray, y_data: numpy.core.multiarray,
                     y_approx_data: numpy.core.multiarray) -> None:
    fig, ax = pyplot.subplots(ncols=1, nrows=1, figsize=(12, 12))
    ax.plot(x_data, y_data, marker="x", color="red", label="Исходные данные", linewidth=0)
    ax.plot(x_data, y_approx_data, linewidth=1, label="Аппроксимация")
    ax.set_xlabel("Временные метки")
    ax.set_ylabel("% отклонения от EMA200")
    ax.legend()
    pyplot.show()


def plot_win_rate(y_data: list, x_data: list):
    fig, ax = pyplot.subplots(ncols=1, nrows=1)
    ax.plot(x_data, y_data, color="red")
    ax.set_xlabel("Временные метки")
    ax.set_ylabel("Отношение побед ко всем сделкам")
    ax.legend()
    pyplot.show()


def plot_approx_diff_data(x_data: numpy.core.multiarray, y_approx_data: numpy.core.multiarray,
                          y_diff_data: numpy.core.multiarray):
    fig, axs = pyplot.subplots(nrows=2, ncols=1)
    for ax, n in zip(axs.flatten(), range(2)):
        if n == 1:
            ax.plot(x_data, y_approx_data)
            ax.set_title("Аппроксимация")
        else:
            ax.plot(x_data, y_diff_data, color="red", linewidth=0.2)
            ax.set_title("Производная")
        ax.legend()
    pyplot.show()


def get_price_tick_size(currency_pair: str, info: dict) -> Decimal:
    for item in info['symbols']:
        if item['symbol'] == currency_pair:
            for f in item['filters']:
                if f['filterType'] == 'PRICE_FILTER':
                    return Decimal(f['tickSize']).normalize()


def get_lot_tick_size(currency_pair: str, info: dict, is_market: bool) -> Decimal:
    for item in info['symbols']:
        if item['symbol'] == currency_pair:
            for f in item['filters']:
                if (is_market and f["filterType"] == "MARKET_LOT_SIZE") or \
                        (not is_market and f["filterType"] == "LOT_SIZE"):
                    return Decimal(f['stepSize']).normalize()


def get_precision(number: Decimal) -> int:
    n = 0
    while number * (10 ** n) != int(number * (10 ** n)):
        n += 1

    return n
