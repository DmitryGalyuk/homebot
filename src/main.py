'''Home automation bot'''
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import download, geTranslate, utils

stateSearch, stateCategory = range(2)

def main() -> None:
    """Start the bot."""
    updater = Updater(os.getenv('TELEGRAM_TOKEN'), arbitrary_callback_data=True)
    dispatcher = updater.dispatcher

    utils.build_start_menu(None)

    dispatcher.add_handler(download.handler)
    dispatcher.add_handler(geTranslate.handler)
    dispatcher.add_handler(CommandHandler("start", start_handler))

    updater.start_polling(timeout=600)
    updater.idle()


def start_handler(update: Update, context: CallbackContext) -> None:
    """start command handler"""
    if os.getenv("DEV_ENV")=="true":
        update.message.reply_text("Development environment")
    update.message.reply_text("Please choose the command from menu")


if __name__ == '__main__':
    main()
