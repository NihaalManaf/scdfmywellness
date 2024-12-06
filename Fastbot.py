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
import Fastbot as f
from openai import OpenAI


# Token (Define all API tokens/credentials here) ___________
telegram_token = os.environ['telegram_token']
uri = "mongodb+srv://scdfmywellness.yxajj5p.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=SCDFmywellness"
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

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


#noj abstractions: ________
async def handle_state(context):
    chat_id = context['chat_id']
    current_state = context['state'] #genesis, awaiting_code, code_auth
    conversation_flow = context['conversation_flow'] # /start, /register
    conversation_stage = context['conversation_stage'] # 0, 1, 2
    handling_fn = context['handling_fn']

    fn_response = await handling_fn(context)
    print(fn_response)
    print(len(noj.noj['conversation_flows'][conversation_flow]))
    if conversation_stage == len(noj.noj['conversation_flows'][conversation_flow]) - 1 and fn_response == True:
        await update_state_client(chat_id, "/start", 0)
    else:
        if fn_response == True:
            await update_state_client(chat_id, conversation_flow, conversation_stage + 1)
    return {"status": "ok"}

async def get_handlingfn(library, state):
    handling_fn = noj.noj['states'][state]['handling_fn']
    return getattr(library, handling_fn)

async def generate_context(chat_id: int, user_input: string, info_payload: object, recruit: object, library:object):
    state = noj.noj['conversation_flows'][recruit['state'][0]][recruit['state'][1]]
    context = {
        'chat_id': chat_id, #10 digit number
        'user_input': user_input,
        'info_payload': info_payload,#full info payload of user from user db
        'state': state, #current state of user - genesis, awaiting_code, code_auth
        'conversation_flow' : recruit['state'][0], # /start, /register
        'conversation_stage' : recruit['state'][1], # 0, 1, 2
        'handling_fn': await get_handlingfn(library, state), #function to handle state
        'recruit': recruit #full user db object in case
    }
    return context
    
async def state_manager(context):

    #this is just some unpacking of the context
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
        else: #if user input is a conversation, routing occurs here
            await update_state_client(chat_id, user_input, 0) #sets the conversation accordingly
            recruit = clients.find_one({'_id': chat_id})
            context = await generate_context(chat_id, user_input, info_payload, recruit, f) #context needs to be regenerated because of change in state and conversation
            await handle_state(context)
    else:
        await handle_state(context) #runs the handling fn and updates the state
 
    return {"status": "ok"}


#noj handling functions: ________
async def genesis(context):
    chat_id = context['chat_id']
    await send_text(chat_id, "/start message goes here")
    return True

async def awaiting_code(context):
    chat_id = context['chat_id']
    await send_text(chat_id, "Please enter the verification code")
    return True

async def code_auth(context):
    chat_id = context['chat_id']
    password = "1234"
    if context['user_input'] != password:
        await send_text(chat_id, "Invalid code. Please re-enter the code or press /cancel to cancel the operation.")
        return False
    await send_text(chat_id, "Code authenticated")
    clients.update_one({"_id": chat_id}, {"$set": {"registration_status": "registered"}})
    return True

async def realtime_convomode(context):
    chat_id = context['chat_id']
    user_input = context['user_input']
    recruit = context['recruit']
    registration_status = recruit['registration_status']
    await update_info_payload(chat_id, "convo_mode", True)
    convo_mode = context['info_payload'].get('convo_mode', False)

    if registration_status == "unregistered":
        await send_text(chat_id, "You are not registered. Please press /register to register.")
        return True
    else:
        if convo_mode == False:
            await send_text(chat_id, "You are registered. You can now proceed with the conversation. To end this mode, press /end.")
        response = await openai_req(context)
        await send_text(chat_id, response)
        return False

async def openai_req(context):
    client = OpenAI()

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

    print(completion.choices[0].message)


    return completion.choices[0].message