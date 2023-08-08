'''download related converstations'''
from typing import List
import time
import os
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler
)
from qbittorrentapi import Client
import utils

stateSearch, stateCategory, stateStartDownload = range(10, 13)

@utils.authorize
async def download_handler(update: Update, context: CallbackQueryHandler) -> int:
    ''' Initiates the search and download process, asks for search query '''
    await utils.build_cancel_menu(update)
    await update.message.reply_text("Movie name")
    return stateSearch

@utils.authorize
async def search_handler(update: Update, context: MessageHandler) -> int:
    '''Search handler, accepts the movie name, searches in torrent client'''
    searchresult = search(update.message.text, 10)
    
    buttons = []
    counter = 0
    for r in searchresult:
        counter += 1
        await update.effective_chat.send_message(text="{counter}: {seeds} seeds, {size:.2f} GB - {name}".format(
            counter=counter,
            seeds=r.nbSeeders,
            size=r.fileSize/1024/1024/1024,
            name=r.fileName)
        )
        buttons.append(
            [InlineKeyboardButton(
                text="{counter}: {seeds} seeds, {size:.2f} GB - {name}".format(
                    counter=counter,
                    seeds=r.nbSeeders,
                    size=r.fileSize/1024/1024/1024,
                    name=r.fileName[0:50]),
                callback_data=r.fileUrl
            )]
        )

    await update.message.reply_text(text="choose torrent:", reply_markup=InlineKeyboardMarkup(buttons))

    return stateCategory

@utils.authorize
async def category_handler(update: Update, context: CallbackQueryHandler) -> int:
    '''offers to choose the category of downloaded file'''
    url = update.callback_query.data
    context.chat_data['url'] = url
    await update.callback_query.answer()
   
    cats = categories()
    buttons = [
        [ InlineKeyboardButton(text=c, callback_data=c) ]
        for c in cats
    ]
    await update.effective_message.reply_text(
        text='Choose category:',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    return stateStartDownload

@utils.authorize
async def start_download_handler(update: Update, context: CallbackQueryHandler) -> int:
    '''reads category and starts download'''
    category = update.callback_query.data
    await update.callback_query.answer()
    url = context.chat_data['url']
    download(url, category)
    await utils.build_start_menu(update)
    await update.effective_message.reply_text(text='Torrent added')

    return ConversationHandler.END

async def cancel_handler(update: Update, context: CommandHandler) -> int:
    '''cancel downlad conversartion'''
    await utils.build_start_menu(update)
    await update.effective_message.reply_text("Cancelled")
    return ConversationHandler.END

handler = ConversationHandler(
        entry_points=[CommandHandler("download", download_handler)],
        states={
            stateSearch : [
                MessageHandler(~filters.COMMAND, search_handler),
                CommandHandler('cancel', cancel_handler)
            ],
            stateCategory : [CallbackQueryHandler(category_handler), CommandHandler('cancel', cancel_handler)],
            stateStartDownload : [CallbackQueryHandler(start_download_handler), CommandHandler('cancel', cancel_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)],
        allow_reentry=False
)

def get_torrent_client():
    ''' Creates instance of qBittorrent client using host and credentials from environment variables
    TORRENT_HOST, TORRENT_USERNAME, TORRENT_PASSWORD'''
    return Client(
            host=os.getenv("TORRENT_HOST"),
            username=os.getenv("TORRENT_USERNAME"),
            password=os.getenv("TORRENT_PASSWORD")
        )


def search(query, limit_results: int = 5 ):
    '''start search in torrenct client
    query -- search query
    limit_results -- number of results to return'''
    
    client = get_torrent_client()
    search_job = client.search_start(pattern=query, plugins='all', category='all')

    while client.search_status()[0]['status']!='Stopped':
        time.sleep(0.5)

    result = client.search_results(search_job._search_job_id).results
    top5 = [r for r in sorted(result, key=lambda x:-x.nbSeeders)[0:limit_results-1]]

    return top5

def categories() -> List[str]:
    '''get the list of categories'''
    client = get_torrent_client()
    return client.torrents_categories().keys()

def download(url, category) -> None:
    '''send the request to download torrent'''
    client = get_torrent_client()
    client.torrents_add(category=category, urls=url)
