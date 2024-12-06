from fastapi import FastAPI, Request, Header, Response
import re
import string
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
from typing import Dict, List
import time
import telegram
from telegram import constants
from pymongo import MongoClient
import random
import string
import traceback
import json
from urllib.parse import urlparse, parse_qs, urlencode, quote
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from fastapi.templating import Jinja2Templates
import string
import noj

# Token (Define all API tokens/credentials here) ___________
telegram_token = os.environ['telegram_token']
uri = "mongodb+srv://scdfmywellness.yxajj5p.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=SCDFmywellness"

bot = telegram.Bot(telegram_token)
app = FastAPI()
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='nm_db.pem')
users = mongo['SCDFMyWellness_v2']
clients = users['Users'] #recruit collection


templates = Jinja2Templates(directory="templates")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-defined function: ________
async def update_info_payload(chat_id, key, pair):
    clients.update_one({"_id": chat_id}, {"$set": {str("info_payload."+key): pair}})

async def info_payload_reset(chat_id):
    clients.update_one({"_id": chat_id}, {"$set": {"info_payload": {}}})

async def send_text(chat_id, message_text):
    reply_markup = ReplyKeyboardRemove()
    await bot.send_message(chat_id, message_text, parse_mode=telegram.constants.ParseMode.HTML, disable_web_page_preview=True, reply_markup=reply_markup)

async def send_text_with_back(chat_id, message_text):
    buttons = [[InlineKeyboardButton(text="⏪", callback_data="previous")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup, parse_mode=telegram.constants.ParseMode.HTML, disable_web_page_preview=True)

async def delete_message(chat_id, message_id):
    await bot.delete_message(chat_id=chat_id, message_id=message_id)

async def update_state_client(chat_id, conversation, stage):
    clients.update_one(
        {"_id": chat_id},
        {"$set": {"state": [conversation, stage]}}
    )

async def send_options_buttons(chat_id, text, options, options_data):
    buttons = []
    #options and options_data needs to be the same length
    x = 0
    for option in options:
        buttons.append([InlineKeyboardButton(text=option, callback_data=options_data[x])])
        x += 1
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=telegram.constants.ParseMode.HTML, disable_web_page_preview=True)

async def send_text_with_url(chat_id, text, url, url_text):
    buttons = [[InlineKeyboardButton(text=url_text, url=url)]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=telegram.constants.ParseMode.HTML, disable_web_page_preview=True) 

# Create a send image(url) with caption function
async def send_image_with_caption(chat_id, image_url, caption):
    await bot.send_photo(chat_id=chat_id, photo=image_url, caption=caption, parse_mode=telegram.constants.ParseMode.HTML)


#noj handling functions: ________
async def handle_state(context):
    chat_id = context['chat_id']
    current_state = context['state'] #genesis, awaiting_code, code_auth
    conversation_flow = context['conversation_flow'] # /start, /register
    conversation_stage = context['conversation_stage'] # 0, 1, 2
    handling_fn = context['handling_fn']

    if conversation_stage == len(noj.noj['conversation_flows'][conversation_flow]) - 1:
        await handling_fn(context)
        await update_state_client(chat_id, "/start", 0)
    else:
        await handling_fn(context)
        await update_state_client(chat_id, conversation_flow, conversation_stage + 1)
    return {"status": "ok"}

    
async def genesis(context):
    chat_id = context['chat_id']
    await send_text(chat_id, "/start message goes here")
    return {"status": "ok"}

async def state_manager(context):
    chat_id = context['chat_id']
    user_input = context['user_input']
    info_payload = context['info_payload']
    state = context['state']
    conversation = context['conversation_flow']
    conversation_stage = context['conversation_stage']
    
    if state == "genesis": #special state becuase this routes to other states
        if user_input not in noj.noj['conversations']:
            await send_text(chat_id, "Please enter a valid command!")
            return {"status": "ok"}
        else:
            await update_state_client(chat_id, user_input, 0)
            context['conversation_flow'] = user_input
            context['state'] = noj.noj['conversation_flows'][user_input][0]
            await handle_state(context)
    else:
        await handle_state(context) #runs the handling fn and updates the state
 
    return {"status": "ok"}