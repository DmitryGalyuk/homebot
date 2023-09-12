'''
Module that controls the Phillips TV
API help is at 
https://github.com/eslavnov/pylips/blob/master/docs/Home.md

TV endpoint is at 
http://192.168.100.80:1925/5
'''

from asyncio import sleep
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import requests
from wakeonlan import send_magic_packet
import utils

TV_STATES = range (31)
TV_ENDPOINT = os.environ["TV_ENDPOINT"]
TV_MAC = os.environ["TV_MAC"]

button_label = {
    'turn_off': "🟢 Выключить",
    'turn_on': "🔴 Включить",
    'volume_down': "🔈 Тише",
    'volume_up': "🔊 Громче",
    'exit': "↩ Выход"
}

@utils.authorize
async def tv_command(update: Update, context) -> int:
    """Send a message with an inline keyboard."""

    reply_markup = ReplyKeyboardMarkup(keyboard_buttons(), one_time_keyboard=False, resize_keyboard=True)
    await update.effective_message.reply_text('Пульт управления телевизором Phillips', reply_markup=reply_markup)
    
    return TV_STATES

def keyboard_buttons():
    ''' Querries the TV state and creates the keyboard buttons collection and adds labels based on TV state
    Returns [[...]] or None '''
    tvstate = tv_state()
    if tvstate == "error":
        return None
    
    return [
        [button_label["turn_"+ ("off" if tvstate=="on" else "on")]],
        [button_label["volume_down"], button_label["volume_up"]],
        [button_label["exit"]]
    ]



@utils.authorize
async def button(update: Update, context) -> int:
    """Handle button presses."""
    action = update.message.text
    response = None

    if action == button_label['turn_on']:
        response = await turn_on()
    elif action == button_label["turn_off"]:
        response = await turn_off()
    elif action == button_label['volume_up']:
        response = volume_control(+1)
    elif action == button_label['volume_down']:
        response = volume_control(-1)

    if response:
        return await tv_command(update, context)

    await update.effective_message.reply_text(text='Exited. Use menu to choose the command.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def cancel_handler(update: Update, context: CommandHandler) -> int:
    '''cancel conversartion'''
    await utils.build_start_menu(update)
    await update.effective_message.reply_text("Cancelled")
    return ConversationHandler.END

def tv_state():
    """ returns "on", "off", "error" """
    response = requests.get(TV_ENDPOINT + "/powerstate", timeout=3)
    
    if response and response.status_code == 200:
        if response.json()["powerstate"] == "On":
            return "on"
        else: return "off"
    else:
        return "error"
    
async def turn_on(try_wake_on_lan=True):
    ''' Turn on
    wakeOnLan if needed to try to wake up on LAN'''
    response = requests.post(TV_ENDPOINT+"/input/key", json={"key": "Standby"}, timeout=1)
    
    if response.status_code and response.status_code==200:
        await sleep(2)
        return True

    if try_wake_on_lan:
        await wake_on_lan()
    return turn_on(False)
    
async def wake_on_lan():
    ''' send Wake On LAN package to TV '''
    send_magic_packet(TV_MAC)
    await sleep(2)


async def turn_off():
    ''' Turn off'''
    response = requests.post(TV_ENDPOINT+"/input/key", json={"key": "Standby"}, timeout=1)
    
    if response.status_code and response.status_code==200:
        await sleep(2)
        return True

    return False

def volume_control(direction):
    ''' Control the volume
    direction defines is should be increased (direction > 0) or decreased (direction < 0)'''
    if direction > 0:
        key = "VolumeUp"
    elif direction < 0:
        key = "VolumeDown"
    else:
        return False
    
    response = requests.post(TV_ENDPOINT+"/input/key", json={"key": key}, timeout=1)
    
    if response.status_code and response.status_code==200:
        return True

    return False

handler = ConversationHandler(
    entry_points=[CommandHandler('tv', tv_command)],
    states={
        TV_STATES: [MessageHandler(~filters.COMMAND, button)]
    },
    fallbacks=[CommandHandler('cancel', cancel_handler)]
)

