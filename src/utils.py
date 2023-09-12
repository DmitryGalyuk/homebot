''' various utils for Telegram bot '''
import os
from typing import Callable, List
from telegram import Bot, BotCommand, Update
from telegram.ext import BaseHandler, ConversationHandler, Updater

import telegram

def authorize(handler: Callable) -> Callable:
    ''' Decorator to compare user id with list of configured.
    Returns either handler or  ConversationHandler.END '''

    def wrapper(update: Updater, context: BaseHandler):
        if not str(update.effective_user.id) in os.getenv("TELEGRAM_USER_ID").split():
            update.effective_message.reply_text("Temporary unavailable")
            return ConversationHandler.END
        return handler(update, context)
  
    return wrapper

async def build_start_menu(update: Update):
    ''' sets the full command menu '''
    commands = [
        BotCommand('download', 'Search and download file'),
        BotCommand('translatgeorgian', 'Transliterate and translate Georgian text'),
        # BotCommand('networkrestart', 'Restart the network connection'),
        BotCommand('vpnup', 'Start VPN'),
        BotCommand('vpndown', 'Stop VPN'),
        BotCommand('tv', 'TV Remote')
    ]
    await _set_menu(commands, update)
    

async def build_cancel_menu(update: Update):
    ''' sets the only cancel command in menu '''
    commands = [
        BotCommand('cancel', 'cancel and choose new command')
    ]
    await _set_menu(commands, update)

async def _set_menu(commands: List[BotCommand], update: Update):
    ''' sets the chat commands menu '''
    bot = Bot(os.getenv('TELEGRAM_TOKEN'))
    await bot.delete_my_commands()
    await bot.set_my_commands(
        commands=commands,
        scope=telegram.BotCommandScopeChat(
            chat_id=update.effective_chat.id
    ))
