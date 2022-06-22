''' various utils for Telegram bot '''

import os
from turtle import up
from typing import Callable
from telegram import Update
from telegram.ext import Handler, ConversationHandler

def authorize(handler: Callable) -> Callable:
    ''' Compares user id with list of configured.
    Returns either handler or  ConversationHandler.END '''

    def wrapper(update: Update, context: Handler):
        if not str(update.effective_user.id) in os.getenv("TELEGRAM_USER_ID").split():
            update.effective_message.reply_text("Temporary unavailable")
            return ConversationHandler.END
        return handler(update, context)
  
    return wrapper
