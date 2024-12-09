from fastapi import FastAPI, Request, Header, Response, BackgroundTasks
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery
from datetime import datetime, timedelta
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
import Fastbot as f
import noj
import string
import os
from fastapi.responses import JSONResponse




# Token (Define all API tokens/credentials here) ___________
telegram_token = os.environ['telegram_token']
uri = "mongodb+srv://scdfmywellness.yxajj5p.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=SCDFmywellness"

bot = telegram.Bot(telegram_token)
app = FastAPI()
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='nm_db.pem')
users = mongo['SCDFMyWellness_v2']
rec = users['Users'] #recruit collection



templates = Jinja2Templates(directory="templates")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
                "time_joined": datetime.now(datetime.timezone.utc)(),
                "expiresAt": datetime.now(datetime.timezone.utc)() + timedelta(seconds=20),
                "state": ["/start", 0],
                "info_payload": {},
                "registration_status": "unregistered"
            }
            rec.insert_one(new_user)

            rec.create_index("expiresAt", expireAfterSeconds=0)

            await f.genesis({'chat_id':chat_id})
    except Exception as e:
        print(f"An error occurred with incoming object: {e}")
        return {"status": "not ok"}
    return {"status": "ok"}



# Create a payment confirmation page 
@app.get("/payment_confirmation")
async def payment_confirmation(request: Request):
    return templates.TemplateResponse("payment_confirmation.html", {"request": request})



