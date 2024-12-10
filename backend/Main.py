from fastapi import FastAPI, Request, Header, Response, BackgroundTasks
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery
from fastapi.responses import HTMLResponse
from typing import Dict, List
from datetime import datetime, timedelta, timezone
import telegram
from telegram import constants
from pymongo import MongoClient
import string
import traceback
import json
from urllib.parse import urlparse, parse_qs, urlencode, quote
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from fastapi.templating import Jinja2Templates
import backend.Fastbot as f
import backend.noj as noj
import string
import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import random
import asyncio
from asyncio import Semaphore




# Token (Define all API tokens/credentials here) ___________
telegram_token = os.environ['telegram_token']
uri = "mongodb+srv://scdfmywellness.yxajj5p.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=SCDFmywellness"

bot = telegram.Bot(telegram_token)
app = FastAPI()
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='backend/nm_db.pem')
users = mongo['SCDFMyWellness_v2']
rec = users['Users'] #recruit collection\
token = users['Token'] #token collection
Responses = users['Responses'] #responses collection
textbroadcasts = users['Broadcasts'] #broadcasts collection




origins = [
    'https://scdfmywellness.vercel.app',
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/telegram")
async def echo(request: Request):   
    try:
        update_data = await request.json()
        update = telegram.Update.de_json(update_data, bot)

        if update.message: # parsing input from user
            if update.message.text:
                chat_id = update.message.chat_id
                user_input = update.message.text
            elif update.message.contact:
                chat_id = update.message.chat_id
                user_input = update.message.contact.phone_number
            else:
                chat_id = update.message.chat_id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat_id
            user_input = update.callback_query.data
        else:
            await f.send_text(chat_id, "Your message type isn't supported.")
            return {"status": "ok"}
        
        if update.message:
                if "/cancel" == update.message.text.lower() or "/end" == update.message.text.lower():
                    await f.send_text(chat_id, "You have cancelled your current opeation. Please press /start to start again.")
                    await f.update_state_client(chat_id, "/start", 0)
                    await f.info_payload_reset(chat_id)
                    return {"status": "ok"}

        print("State management begins here")
        if rec.find_one({'_id': chat_id}):
            recruit = rec.find_one({'_id': chat_id})
            context = await f.generate_context(chat_id, user_input, recruit['info_payload'], recruit, f)
            print("Beware! This is the context before any processing or manipulation")
            print(context)
            await f.state_manager(context)
            print("State management ends here")

        else:
            # Insert a user that should be deleted after 3 months
            new_user = {
                "_id": chat_id,
                "time_joined": datetime.now(timezone.utc),
                "expiresAt": datetime.now(timezone.utc) + timedelta(days=90),
                "state": ["/start", 0],
                "info_payload": {},
                "registration_status": "unregistered"
            }
            rec.insert_one(new_user)

            await f.genesis({'chat_id':chat_id})
    except Exception as e:
        print(f"An error occurred with incoming object: {e}")
        return {"status": "not ok"}
    return {"status": "ok"}


class registerOTP(BaseModel):
    OTP: int

@app.post("/RegistrationModeOn", response_model=registerOTP)
async def registration_mode_on():
    otp = random.randint(1000, 9999)
    token.update_one({'_id': 1}, {'$set': {'mode': True, 'value': otp}})
    return registerOTP(OTP=otp)
    
@app.post("/RegistrationModeOff")
async def registration_mode_off():
    token.update_one({'_id': 1}, {'$set': {'mode': False}})
    return {"status": "ok"}

class registrationstatus(BaseModel):
    OTP: int
    mode: bool

@app.post("/RegistrationModeStatus", response_model=registrationstatus)
async def registration_mode_status():
    object = token.find_one({'_id': 1})
    return registrationstatus(OTP=object['value'], mode=object['mode'])

class textblast(BaseModel):
    message: str

@app.post("/TextBlast", response_model=textblast)
async def text_blast(message: textblast):
    semaphore = Semaphore(30)
    print(message.message)

    async def send_message(chat_id, message):
        async with semaphore:
            try:
                await f.send_text(chat_id, message)
            except Exception as e:
                print(f"Failed to send message to {chat_id}: {e}")

    registered_users = rec.find({'registration_status': 'registered'})
    tasks = [send_message(user['_id'], message.message) for user in registered_users]
    await asyncio.gather(*tasks)
    textbroadcasts.insert_one({'message': message.message, 'time_sent': datetime.now(timezone.utc)})
    return message

class eocinput(BaseModel):
    startDate: str
    endDate: str

class eocoutput(BaseModel):
    total_users: int
    total_users_reg: int
    total_qns: int
    total_broadcasts: int
    piedata: List[int]

@app.post("/generateEOC", response_model=eocoutput)
async def generate_eoc(eoc: eocinput):

    total_users = rec.count_documents({
        'time_joined': {
            '$gte': datetime.strptime(eoc.startDate, "%Y-%m-%d").replace(tzinfo=timezone.utc),
            '$lte': datetime.strptime(eoc.endDate, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        }
    })
    total_users_reg = rec.count_documents({
        'registration_status': 'registered',
        'time_joined': {
            '$gte': datetime.strptime(eoc.startDate, "%Y-%m-%d").replace(tzinfo=timezone.utc),
            '$lte': datetime.strptime(eoc.endDate, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        }
    })

    all_responses = Responses.find({
        'time_of_query': {
            '$gte': datetime.strptime(eoc.startDate, "%Y-%m-%d").replace(tzinfo=timezone.utc),
            '$lte': datetime.strptime(eoc.endDate, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        }
    })

    topics = [
        "Emotional Distress",
        "Salary Details",
        "ORD & POP [Operationally Ready Date and Passing Out Parade]",
        "Vocations",
        "Sign-on Related",
        "IPPT",
        "Training & Leaves",
        "Prohibited Items",
        "Miscellaneous/Other"
    ]
    total_qns = 0
    topics_count = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    for response in all_responses:
        item = response['category']
        index = topics.index(item)
        topics_count[index] += 1
        total_qns += 1


    total_broadcasts = textbroadcasts.count_documents({
        'time_sent': {
            '$gte': datetime.strptime(eoc.startDate, "%Y-%m-%d").replace(tzinfo=timezone.utc),
            '$lte': datetime.strptime(eoc.endDate, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        }
    })

    return eocoutput(piedata=topics_count, total_users=total_users, total_users_reg=total_users_reg, total_qns=total_qns, total_broadcasts=total_broadcasts)
