'''
Module that controls the network, restarts the network connections and vpns
Relies on the following commands:
nmcli c up vpn.dk
nmcli c down vpn.dk
nmcli n off
nmcli n on

sudo nmcli c show
NAME                                 UUID                                  TYPE       DEVICE
'''

import os
from telegram import Update
from telegram.ext import ContextTypes
import utils

@utils.authorize
async def networkrestart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ''' uses nmcli to down and up the network connection '''
    stream = os.popen("/usr/bin/nmcli c")
    result = stream.read()

    await update.message.reply_text(result)

@utils.authorize
async def vpnup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ''' uses nmcli to up the vpn '''
    stream = os.popen("nmcli c up vpn.dk 2>&1")
    result = stream.read()

    await update.message.reply_text(result)

@utils.authorize
async def vpndown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ''' uses nmcli to down the vpn '''
    stream = os.popen("nmcli c down vpn.dk 2>&1")
    result = stream.read()

    await update.message.reply_text(result)
