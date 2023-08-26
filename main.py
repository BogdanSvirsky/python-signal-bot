from trade_bot import TradeBot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from typing import Callable, NoReturn
from api.binance_api import BinanceAPI


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
                        "CHZUSDT", "1INCHUSDT", "AAVEUSDT",
                        "COMPUSDT", "DASHUSDT",  "DYDXUSDT", "ENJUSDT",
                        "EOSUSDT", "ETCUSDT",   "KAVAUSDT", "KSMUSDT",
                        "SANDUSDT",  "SUSHIUSDT", "SXPUSDT", "TRXUSDT", "UNIUSDT", "UNFIUSDT", "PEOPLEUSDT",
                         "ANTUSDT", "API3USDT", "BALUSDT", "BELUSDT", "BNXUSDT",
                        "DARUSDT", "DENTUSDT", "DGBUSDT", "ENSUSDT", "IMXUSDT", "KLAYUSDT", "LITUSDT",
                        "LRCUSDT", "MASKUSDT", "XEMUSDT", "ROSEUSDT", "SNXUSDT", "STMXUSDT", "TOMOUSDT",
                        "WOOUSDT", "YFIUSDT"]

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
    orders: dict[str, tuple[str, str, str]] = {}  # tuple orderId and close time by symbol
    while True:
        for currency_pair in currency_pairs_list:
            if currency_pair not in orders.keys():
                data_frame = binance_api.get_candles(currency_pair, "5m")
                if data_frame is None:
                    continue
                print("ok")
                predict = trade_bot.make_prediction(data_frame)
                if predict:
                    price = data_frame.iloc[-1]["close_price"]
                    limit_order = binance_api.make_order(
                        currency_pair,
                        "BUY" if predict.type == "LONG" else "SELL",
                        "LIMIT",
                        price,
                        20 if currency_pair != "BTCUSDT" else 75,
                        10 / price,
                        reduce_only=True,
                        time_in_force="GTC"
                    )
                    stop_loss_order = binance_api.make_order(
                        currency_pair,
                        "SELL" if predict.type == "LONG" else "BUY",
                        "STOP",
                        price * 0.995 if predict.type == "LONG" else price * 1.005,
                        20 if currency_pair != "BTCUSDT" else 75,
                        10 / price,
                        stop_price=price * 0.995 if predict.type == "LONG" else price * 1.005,
                        reduce_only=True,
                        time_in_force="GTC"
                    )
                    take_profit_order = binance_api.make_order(
                        currency_pair,
                        "SELL" if predict.type == "LONG" else "BUY",
                        "TAKE_PROFIT",
                        price * 0.985 if predict.type == "LONG" else price * 1.015,
                        20 if currency_pair != "BTCUSDT" else 75,
                        10 / price,
                        stop_price=price * 0.985 if predict.type == "LONG" else price * 1.015,
                        time_in_force="GTC"
                    )
                    orders[currency_pair] = (
                        limit_order["clientOrderId"],
                        take_profit_order["clientOrderId"],
                        stop_loss_order["clientOrderId"]
                    )
            elif currency_pair in orders.keys():
                limit_order = binance_api.get_order(currency_pair, orders[currency_pair][0])
                stop_loss_order = binance_api.get_order(currency_pair, orders[currency_pair][1])
                take_profit_order = binance_api.get_order(currency_pair, orders[currency_pair][2])
                statuses = [
                    limit_order["status"], stop_loss_order["status"], take_profit_order["status"]
                ]
                if "CANCELLED" in statuses or "EXPIRED" in statuses:
                    binance_api.cancel_all_open_orders(currency_pair)
                    del orders[currency_pair]