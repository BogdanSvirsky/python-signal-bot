import time

from trade_bot import TradeBot, Predict
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from typing import Callable, NoReturn
from time import sleep
from api.binance_api import BinanceAPI
from api.kucoin_api import KucoinAPI


def auth(handler: Callable[[Update, ContextTypes], NoReturn]):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in current_users:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="У вас нет доступа к этому боту")
            return
        chat_id = update.effective_chat.id
        if chat_id not in current_chats:
            current_chats.append(chat_id)
        await handler(update, context)

    return wrapped


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Это бот для автоматического микротрейдинга на биржах")


@auth
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Управление ботом:\n  "
                                        "/help - помощник с командами\n  "
                                        "/start_trade - запустить торговлю\n  "
                                        "/stop_trade - запустить торговлю\n  "
                                        "или же просто тыкай на кнопки)")


@auth
async def start_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if trade_bot.running:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Торговля уже идёт")
    else:
        trade_bot.running = True
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Торговля начата")


@auth
async def stop_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if trade_bot.running:
        trade_bot.running = False
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Торговля остановлена")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Торговля уже остановлена")


coin_list: list[str] = ["ADAUSDT", "ATOMUSDT", "AVAXUSDT", "AXSUSDT", "BCHUSDT", "BNBUSDT", "BTCUSDT", "CHRUSDT",
                        "CRVUSDT", "DOTUSDT", "ETHUSDT", "FTMUSDT", "LINKUSDT", "MATICUSDT", "ONEUSDT", "SOLUSDT",
                        "CHZUSDT", "1INCHUSDT", "AAVEUSDT", "ADAUSDT", "ATOMUSDT", "AVAXUSDT", "AXSUSDT", "BCHUSDT",
                        "BNBUSDT", "BTCUSDT", "COMPUSDT", "CRVUSDT", "DASHUSDT", "DOTUSDT", "DYDXUSDT", "ENJUSDT",
                        "EOSUSDT", "ETCUSDT", "ETHUSDT", "FTMUSDT", "KAVAUSDT", "KSMUSDT", "LINKUSDT", "ONEUSDT",
                        "SANDUSDT", "SOLUSDT", "SUSHIUSDT", "SXPUSDT", "TRXUSDT", "UNIUSDT", "UNFIUSDT", "PEOPLEUSDT",
                        "DYDXUSDT", "ANTUSDT", "API3USDT", "BALUSDT", "BELUSDT", "BNXUSDT", "BNXUSDT",
                        "DARUSDT", "DENTUSDT", "DGBUSDT", "ENSUSDT", "HNTUSDT", "IMXUSDT", "KLAYUSDT", "LITUSDT",
                        "LRCUSDT", "MASKUSDT", "XEMUSDT", "NUUSDT", "ROSEUSDT", "SNXUSDT", "STMXUSDT", "TOMOUSDT",
                        "WOOUSDT", "YFIIUSDT"]

current_users = [557001882, 978982709]
current_chats = []

if __name__ == '__main__':
    # app = Application.builder().token("6385645019:AAG0VIYfnNbp18bZj_Ii720cm4aXadogGdA").build()
    # start_command_handler = CommandHandler("start", start)
    # help_command_handler = CommandHandler("help", help)
    # start_trade_command = CommandHandler("start_trade", start_trade)
    # stop_trade_command = CommandHandler("stop_trade", stop_trade)
    # app.add_handlers([start_command_handler, help_command_handler, start_trade_command, stop_trade_command])
    # app.run_polling()
    trade_bot = TradeBot()
    binance_api = BinanceAPI()
    binance_api.set_api(
        "GENPXi3IwkasQcarm6eBNcaWAeBR6bs5qTNaRZgKALhmHHKQBVzHnfvZD1nu7RSy",
        "2shPKm7JvugvqQY8CX2Nc5hFBGM7A6b9Wu7C4ztqEHHkcNc56Fp5d3rD0PB9oDX2"
    )
    currency_pairs_list = ["BTCUSDT", "DOGEUSDT"]
    orders: dict[str, tuple[str, str, int]] = {}  # tuple orderId and close time by symbol
    while True:
        for currency_pair in currency_pairs_list:
            if currency_pair not in orders.keys():
                data_frame = binance_api.get_candles(currency_pair, "5m")
                predict = trade_bot.make_prediction(data_frame)
                if predict:
                    price = data_frame.iloc[-1]["close_price"]
                    limit_order_id = binance_api.make_order(
                        currency_pair,
                        "BUY" if predict.type == "LONG" else "SELL",
                        "LIMIT",
                        price * 1.0001,
                        
                    )["clientOrderId"]
                    take_profit_order_id = binance_api.make_order(...)["clientOrderId"]
                    orders[currency_pair] = (
                        limit_order_id, take_profit_order_id, (int(time.time()) + 6 * 5 * 60) * 1000
                    )
            elif currency_pair in orders.keys():
                limit_order_id, take_profit_order_id, close_time = orders[currency_pair]
                if close_time <= time.time() * 1000 * 5 * 60 * 6:
                    binance_api.cancel_order(currency_pair, limit_order_id)
                    binance_api.cancel_order(currency_pair, take_profit_order_id)
                    del orders[currency_pair]