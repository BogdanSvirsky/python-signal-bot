import telegram

from trade_bot import TradeBot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from typing import Callable, NoReturn


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


coin_list = ["ADAUSDT", "ATOMUSDT", "AVAXUSDT", "AXSUSDT", "BCHUSDT", "BNBUSDT", "BTCUSDT", "CHRUSDT", "CRVUSDT",
             "DOTUSDT", "ETHUSDT", "FTMUSDT", "LINKUSDT", "MATICUSDT", "ONEUSDT", "SOLUSDT", "CHZUSDT", "1INCHUSDT",
             "AAVEUSDT", "ADAUSDT", "ATOMUSDT", "AVAXUSDT", "AXSUSDT", "BCHUSDT", "BNBUSDT", "BTCUSDT", "COMPUSDT",
             "CRVUSDT", "DASHUSDT", "DOTUSDT", "DYDXUSDT", "ENJUSDT", "EOSUSDT", "ETCUSDT", "ETHUSDT", "FTMUSDT",
             "KAVAUSDT", "KSMUSDT", "LINKUSDT", "ONEUSDT", "SANDUSDT", "SOLUSDT", "SUSHIUSDT", "SXPUSDT", "TRXUSDT",
             "UNIUSDT", "UNFIUSDT", "PEOPLEUSDT", "DYDXUSDT", "ANCUSDT", "ANTUSDT", "API3USDT", "BALUSDT", "BELUSDT",
             "BNXUSDT", "BNXUSDT", "DARUSDT", "DENTUSDT", "DGBUSDT", "ENSUSDT", "HNTUSDT", "IMXUSDT", "KLAYUSDT",
             "LITUSDT", "LRCUSDT", "MASKUSDT", "XEMUSDT", "NUUSDT", "ROSEUSDT", "SNXUSDT", "STMXUSDT", "TOMOUSDT",
             "WOOUSDT", "YFIIUSDT"]

current_users = [557001882, 978982709]
current_chats = []
trade_bot = TradeBot()

if __name__ == '__main__':
    app = Application.builder().token("6385645019:AAG0VIYfnNbp18bZj_Ii720cm4aXadogGdA").build()
    start_command_handler = CommandHandler("start", start)
    help_command_handler = CommandHandler("help", help)
    start_trade_command = CommandHandler("start_trade", start_trade)
    stop_trade_command = CommandHandler("stop_trade", stop_trade)
    app.add_handlers([start_command_handler, help_command_handler, start_trade_command, stop_trade_command])
    app.run_polling()
