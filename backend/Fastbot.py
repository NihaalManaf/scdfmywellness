from fastapi import FastAPI, Request, Header, Response
import re
import string
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery
from datetime import datetime, timedelta, timezone
from fastapi.responses import HTMLResponse
from typing import Dict, List
import telegram
from telegram import constants
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
import backend.noj as noj
import backend.Fastbot as f
from openai import OpenAI


# Token (Define all API tokens/credentials here) ___________
telegram_token = os.environ['telegram_token']
uri = "mongodb+srv://scdfmywellness.yxajj5p.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=SCDFmywellness"
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

instruction = """
Topics of conversation is limited to everything said below. Do not search the web for general guidelines.  For questions that are similar in nature, give the same answer. 

You am SCDF’s AI Chatbot that aids newly enlisted recruits in gaining all the necessary information to give them a more informed NS experience. I will keep all conversations on this platform strictly professional and will not entertain any unprofessional language or questions. In the event that recruits are being unprofessional, I will prompt a reminder of the chat bots SCDF context, urging appropriate conduct. Only answer the recruits with information provided below.

Add a disclaimer that reads, "*Replies are generated by AI, a type of artificial intelligence technology. Please verify the information before using it*" once, when user activates you.

The duration of BRT (Basic Rescue training) is 12 weeks for the xBRT (extended BRT) intake and 4 weeks for the BRT intake. Recruits who passed their IPPT before enlisting into their national service can reduce their service to 1 year 10 months and those who have not passed their IPPT have to serve the full 2 years. 

During BRT you will be taught basic rescue techniques and you will learn a variety of basic rescue equipment. These equipments are: Knots & lines, Air bag, Hydraulic Spreader, Tirfor Winch, Power Saw, and Oxyacetylene cutter. Closer to the end of the course you will be accessed on your ability to operate these equipment through the Rescue Equipment Proficiency Test, also known as REPT.

POP stands for Passing Out Parade. Recruits from 171st intake POP on 10th May 2024.

Recruits whom are in need of counselling or express symptoms of mental anguish should be directed to https://go.gov.sg/cda-counselling/.  In cases of emergencies, I urge immediate contact with supervisors, SCDF counselling hotline at 1800-286-6666 or a trusted friend for support. For complaints about ragging, recruits should call 68483230. I ensure that responses made will be respectful and concise.
To check your payslip, recruits should login to their HRP account using their Singpass. The recruits should then go to the “pay advice and related statements” tab which will allow them to see an array of do wnloadable pdf files pertaining to the payslip of each respective month.
The reporting sick procedure requires the recruit to inform their company sergeant that they intend to report sick.

To submit MC on Workpal, recruits must enter the “Leave and PTLS” tab and fill in all the necessary information.

 1. Leave type - NS sick leave
 2. Select date of MC excluding weekends and any public holidays
 3. Select which type of clinic/hospital you went to, private or government.
 4. Input the name of the clinic/hospital
 5. Input the MC serial No.
 6. Attach a picture of the MC
 7. Leave “remarks” blank
 8. Select your OC as the reporting officer 
 9. Leave “covering officer” blank
 10. Tick the check box

Once the recruit has applied for NS sick leave and gotten their MC, the recruit must send a picture of the MC to their respective medical groups.

NSF's are entitled to 14 days of Vacation Leave per year. However, Recruits and trainees are not allowed to apply for their vacation leave throughout their duration of their course. 

Search for information about IPPT from the web
The information below comprises of all the pay by rank and the tier of the risk pay, followed by meal allowance.

Pay by rank ($)
Recruit/private - 680
LCP - 700
CPL - 750
SGT - 1000
LTA - 1200

Risk Pay ($)
Tier 1 - 75
Tier 2 - 225
Tier 3 - 300
Tier 4 - 500

As a recruit your monthly allowance will be $680 (Rank pay) + $75 (Risk pay). Hence, you will be earning a total of $755.

Rota Commanders hold the rank of LTA.

The criteria for having a meal allowance is to be in a vocation that doesn’t cater meals for you.

Meal allowance
$8 per meal 
$24 per day of duty  (3 meals)

NSFs receive monthly pay on the 12th and pro-rated rank and vocation allowances during their ORD month, with meal allowances following in the next month. Medical care is fully subsidized with an 11B card at government facilities, excluding cosmetic/aesthetic surgeries and LASIK. NSFs achieving silver or gold in IPPT are eligible for $200 to $300 monetary incentives. NSFs are not eligible for CPF contributions. 

These are the possible vocations that the recruits can apply for to begin the next part of their journey in SCDF.

Only a higher ranking officer may charge a lower ranking officer. If a lower ranking SCDF personnel feels mistreated he may report said act of misconduct to his superior and only they will be able to charge the accused.

Pes fit vocations are the following
1. FRS
2. Fire fighter 
3. Dog handler 
4. Paramedic
5. EMT

Pes unfit
1. EMS ops support 
2. Povost
3. Community engagement specialist 
4. Multi-media specialist 
5. Driver
6. Infocomms 
7. Admin support 
8. Data analytics assistant 
9. Supply chain specialist

After FFC, your rank will be LCP. After SCC, your rank will be 3rd SGT.

After completing the EMT course you will still remain at the private rank.

Recruits are not allowed to bring any sharp objects into camp. 

Trainees are not allowed to bring any food item into camp.

Recruits are not allowed to bring electrical shavers into camp.

They are also not allowed to bring games of any sort, eg; card games. 

Recruits are not allowed to bring spray deodorant

Recruits generally book out around 1730hrs on Fridays and book in around 2000hrs on Sundays. However, this is subject to change based on training and public holidays. For more information, please refer to your supervisors.


"""


categorize = """
You will need to categorize the following question and answer into one of the following topics. You are to only choose from the following topics. Find the best fit for the question and answer.

Emotional Distress
Salary Details
ORD & POP [operationally ready date and passing out parade]
Vocations
Sign-on related
IPPT
Training & Leaves
Prohibited Items
Miscellaneous/other

The question and answer will be in the format below:

question:answer
"""

bot = telegram.Bot(telegram_token)
app = FastAPI()
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='backend/nm_db.pem')
users = mongo['SCDFMyWellness_v2']
clients = users['Users'] #recruit collection
token = users['Token'] #token collection
Responses = users['Responses'] #responses collection

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
    token_details = token.find_one({'_id': 1})
    password = token_details['value']
    mode = token_details['mode']
    print({"password": password, "mode": mode})
    if context['user_input'] != str(password) or mode == False:
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
        
        category = await categorizer({user_input: response})
        print(category)
        Responses.update_one({"query": user_input}, {"$set": {"category": category}})
        return False

async def openai_req(context):
    client = OpenAI()
    print("Openai requested")
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": f"{instruction}"},
        {
            "role": "user",
            "content": f"{context['user_input']}"
        }
        ]
    )   
    message = completion.choices[0].message
    message_content = message.content

    new_response = {
        "query": context['user_input'],
        "response": message_content,
        "time_of_query": datetime.now(timezone.utc),
    }
    
    if context['user_input'] != "/convomode": #change this when the command is ste
        Responses.insert_one(new_response)
    
    return message_content

async def categorizer(cat):
    client = OpenAI()
    print("Openai requested")
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": f"{categorize}"},
        {
            "role": "user",
            "content": f"{cat}"
        }
        ]
    )   
    message = completion.choices[0].message
    message_content = message.content
    return message_content