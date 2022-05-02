'''Home automation bot'''
from asyncio.log import logger
import os
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackContext, CallbackQueryHandler, ConversationHandler
)
import download

stateSearch, stateCategory = range(2)

def main() -> None:
    """Start the bot."""
    updater = Updater(os.getenv('TELEGRAM_TOKEN'), arbitrary_callback_data=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_handler))
    dispatcher.add_handler(download.handler)

    updater.start_polling(timeout=600)
    updater.idle()


def start_handler(update: Update, context: CallbackContext) -> None:
    """start command handler"""
    update.message.reply_text("""/download movie
or /start to restart""")

if __name__ == '__main__':
    main()
