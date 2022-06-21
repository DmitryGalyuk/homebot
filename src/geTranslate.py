'''Georgian translation command'''
import os, requests, uuid
from typing import List
from telegram import Update
from telegram.ext import Updater, MessageHandler
from transliterate import translit

def translate_handler(update: Update, context: MessageHandler) -> int:
    '''Converts from latin letters to georgian, sends to translation service and returns the translation'''
    user_input = update.message.text

    georgian = translit(user_input, language_code='ka')
    
    translations = azure_translate(georgian, 'ka', ["ru", "en"])

    for lang in translations:
        update.message.reply_text(translations[lang])

def azure_translate(msg: str, src: str, dest: List[str]) -> str:
    '''querries translator service to translate and returns translated messages
    msg: message to translate
    src: source language (two letters abbreviation like 'ka', 'de', etc)
    dst: target languages array  (two letters abbreviation like 'ka', 'de', etc)
    returns dictionary {"language": "translation"}
    '''

    key_var_name = 'TRANSLATOR_TEXT_SUBSCRIPTION_KEY'
    if not key_var_name in os.environ:
        raise Exception('Please set/export the environment variable: {}'.format(key_var_name))
    subscription_key = os.environ[key_var_name]

    region_var_name = 'TRANSLATOR_TEXT_REGION'
    if not region_var_name in os.environ:
        raise Exception('Please set/export the environment variable: {}'.format(region_var_name))
    region = os.environ[region_var_name]

    endpoint_var_name = 'TRANSLATOR_TEXT_ENDPOINT'
    if not endpoint_var_name in os.environ:
        raise Exception('Please set/export the environment variable: {}'.format(endpoint_var_name))
    endpoint = os.environ[endpoint_var_name]

    # If you encounter any issues with the base_url or path, make sure
    # that you are using the latest endpoint: https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
    path = '/translate?api-version=3.0'
    params = f'&from={src}{"".join([f"&to={d}" for d in dest])}'
    
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text' : msg
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()

    return transform_azure_response(response)

def transform_azure_response(inp):
    ''' returns {language:translation} dictionary '''
    return {
        item['to'] : item['text']
            for item
            in inp[0]['translations']
    }
