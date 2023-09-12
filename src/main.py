'''Home automation bot'''
import asyncio
import os
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Application, ContextTypes, ApplicationBuilder, PicklePersistence
import download
import geTranslate
import tv
import utils
import network

stateSearch, stateCategory = range(2)

def main():
    """Start the bot."""
    persistence = PicklePersistence(filepath="arbitrarycallbackdatabot")
    application = (
        Application.builder()
        .token(os.getenv('TELEGRAM_TOKEN'))
        .persistence(persistence)
        .arbitrary_callback_data(True)
        .build()
    )
    

    application.add_handler(download.handler)
    application.add_handler(geTranslate.handler)
    application.add_handler(CommandHandler("start", start_handler))
    # application.add_handler(CommandHandler("networkrestart", network.networkrestart_handler))
    application.add_handler(CommandHandler("vpnup", network.vpnup_handler))
    application.add_handler(CommandHandler("vpndown", network.vpndown_handler))
    application.add_handler(tv.handler)

    application.run_polling(timeout=600)
    # application.shutdown()
    print("aa")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """start command handler"""
    if os.getenv("DEV_ENV")=="true":
        await update.message.reply_text(text="Dev environment")
    await utils.build_start_menu(update)
    await update.message.reply_text("Please choose the command from menu")    


if __name__ == '__main__':
    main()
