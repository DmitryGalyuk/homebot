'''download related converstations'''
from typing import List
import time
import os
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackContext, CallbackQueryHandler, ConversationHandler
)
from qbittorrentapi import Client

stateSearch, stateCategory, stateStartDownload = range(3)


def download_handler(update: Update, context: CallbackQueryHandler) -> int:
    '''Download command entrance, asks for movie name'''
    if str(update.effective_user.id) != os.getenv("TELEGRAM_USER_ID"):
        return ConversationHandler.END

    update.message.reply_text("Movie name")
    return stateSearch

def search_handler(update: Update, context: MessageHandler) -> int:
    '''Search handler, accepts the movie name, searches in torrent client'''
    searchresult = search(update.message.text)
    output = [
        [
            InlineKeyboardButton(
                text="{seeds} seeds, {size:.2f} GB - {name}".format(
                    seeds=r.nbSeeders,
                    size=r.fileSize/1024/1024/1024,
                    name=r.fileName[0:50]),
                callback_data=r.fileUrl
            )
        ]
        for r in searchresult
    ]
    update.message.reply_text(text="choose torrent:", reply_markup=InlineKeyboardMarkup(output))

    return stateCategory

def category_handler(update: Update, context: CallbackQueryHandler) -> int:
    '''offers to choose the category of downloaded file'''
    url = update.callback_query.data
    context.chat_data['url'] = url
    update.callback_query.answer()
   
    cats = categories()
    buttons = [
        [ InlineKeyboardButton(text=c, callback_data=c) ]
        for c in cats
    ]
    update.effective_message.reply_text(
        text='Choose category:',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    return stateStartDownload

def start_download_handler(update: Update, context: CallbackQueryHandler) -> int:
    '''reads category and starts download'''
    category = update.callback_query.data
    update.callback_query.answer()
    url = context.chat_data['url']
    download(url, category)
    update.effective_message.reply_text(text='Torrent added')

    return ConversationHandler.END

def cancel_handler(update: Update, context: CommandHandler) -> int:
    '''cancel downlad conversartion'''
    update.effective_message.reply_text("/start")
    return ConversationHandler.END

handler = ConversationHandler(
        entry_points=[CommandHandler("download", download_handler)],
        states={
            stateSearch : [
                # MessageHandler(Filters.text, search_handler),
                MessageHandler(~Filters.command, search_handler),
                CommandHandler('cancel', cancel_handler)
            ],
            stateCategory : [CallbackQueryHandler(category_handler), CommandHandler('cancel', cancel_handler)],
            stateStartDownload : [CallbackQueryHandler(start_download_handler, CommandHandler('cancel', cancel_handler))]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)],
)

def search(query):
    '''start search in torrenct client'''
    client = Client(
        host=os.getenv("TORRENT_HOST"),
        username=os.getenv("TORRENT_USERNAME"),
        password=os.getenv("TORRENT_PASSWORD")
    )
    search_job = client.search_start(pattern=query, plugins='all', category='all')

    while client.search_status()[0]['status']!='Stopped':
        time.sleep(0.5)

    result = client.search_results(search_job._search_job_id).results
    top5 = [r for r in sorted(result, key=lambda x:-x.nbSeeders)[0:4]]

    return top5

def categories() -> List[str]:
    '''get the list of categories'''
    client = Client(
        host=os.getenv("TORRENT_HOST"),
        username=os.getenv("TORRENT_USERNAME"),
        password=os.getenv("TORRENT_PASSWORD")
    )
    return client.torrents_categories().keys()

def download(url, category) -> None:
    '''send the request to download torrent'''
    client = Client(
        host=os.getenv("TORRENT_HOST"),
        username=os.getenv("TORRENT_USERNAME"),
        password=os.getenv("TORRENT_PASSWORD")
    )
    client.torrents_add(category=category, urls=url)
