''' various utils for Telegram bot '''
import os
from typing import Callable, List
from telegram import Update, Bot, BotCommand
from telegram.ext import Handler, ConversationHandler

import telegram

def authorize(handler: Callable) -> Callable:
    ''' Decorator to compare user id with list of configured.
    Returns either handler or  ConversationHandler.END '''

    def wrapper(update: Update, context: Handler):
        if not str(update.effective_user.id) in os.getenv("TELEGRAM_USER_ID").split():
            update.effective_message.reply_text("Temporary unavailable")
            return ConversationHandler.END
        return handler(update, context)
  
    return wrapper

def build_start_menu(update: Update):
    ''' sets the full command menu '''
    commands = [
        BotCommand('download', 'Search and download file'),
        BotCommand('translatgeorgian', 'Transliterate and translate Georgian text'),
    ]
    _set_menu(commands, update)
    

def build_cancel_menu(update: Update):
    ''' sets the only cancel command in menu '''
    commands = [
        BotCommand('cancel', 'cancel and choose new command')
    ]
    _set_menu(commands, update)

def _set_menu(commands: List[BotCommand], update: Update):
    ''' sets the chat commands menu '''
    bot = Bot(os.getenv('TELEGRAM_TOKEN'))
    bot.delete_my_commands()
    if update:
        bot.set_my_commands(
            commands=commands,
            scope=telegram.BotCommandScopeChat(
                chat_id=update.effective_chat.id
        ))
    else:
        bot.set_my_commands(commands=commands)
