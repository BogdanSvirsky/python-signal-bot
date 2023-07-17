import numpy
from matplotlib import pyplot


def plot_approx_data(x_data: numpy.core.multiarray, y_data: numpy.core.multiarray,
                     y_approx_data: numpy.core.multiarray, y_diff_data: numpy.core.multiarray) -> None:
    print(y_approx_data)
    fig, ax = pyplot.subplots(ncols=1, nrows=1, figsize=(12, 12))
    ax.plot(x_data, y_data, marker="x", color="red", label="Исходные данные", linewidth=0)
    ax.plot(x_data, y_approx_data, linewidth=0.5, label="Аппроксимация")
    ax.plot(x_data, y_diff_data, linewidth=0.5, label="Производная")
    ax.set_xlabel("Временные метки")
    ax.set_ylabel("% отклонения от EMA200")
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
