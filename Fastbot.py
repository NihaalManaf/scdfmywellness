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
import asyncio
from urllib.parse import urlparse, parse_qs, urlencode, quote
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from fastapi.templating import Jinja2Templates
import Fastbot
import string
import stripe

# Token (Define all API tokens/credentials here) ___________
telegram_token = os.environ['telegram_token']
uri = "mongodb+srv://untamed.rv4zzne.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=Untamed"
stripe.api_key = "sk_test_51PShQQCE2s0moqY6ZQckhHYiLOkKjog3xofaXLW0go7QZe18U0H8OIQdw8m7Gpubi2WKxs5JIfs10JO9WMBup6bp00YkIplte6"

bot = telegram.Bot(telegram_token)
app = FastAPI()
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='ojas.cer') # TODO: PUT KEY HERE
users = mongo['ICS_Navaratri']
clients = users['users']
ticket_type = users['ticket_type']
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

async def update_state_client(chat_id, major, minor):
    clients.update_one({"_id": chat_id}, {"$set": {"state.major": major, "state.minor": minor}})

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

def is_valid_nus_id(input):
    input = input.lower()
    
    if input.startswith('e'):
        return True
    else:
        return False
    

def is_valid_email(email):
    # Convert email to lowercase for case-insensitive comparison
    email = email.lower()
    
    # Regular expression to match a valid email pattern
    # It checks for a typical format: something@domain.extension
    pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    
    if pattern.match(email):
        return True
    else:
        return False