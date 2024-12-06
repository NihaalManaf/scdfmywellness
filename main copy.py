from fastapi import FastAPI, Request, Header, Response, BackgroundTasks
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
from openai import OpenAI
from dateutil.relativedelta import relativedelta
import stripe
import qrcode
import boto3 
from io import BytesIO
import time
import os
from PIL import Image, ImageDraw, ImageFont
from fastapi.responses import JSONResponse



# Token (Define all API tokens/credentials here) ___________
telegram_token = os.environ['telegram_token']
uri = "mongodb+srv://untamed.rv4zzne.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=Untamed"
stripe.api_key = os.environ['api_key_test']

bot = telegram.Bot(telegram_token)
app = FastAPI()
mongo = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='ojas.cer') 
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

# Message: ___________
msg1 = "<b>Welcome to the Official NUS ICS Chat Bot 🤖</b>\n\nPlease press /buy to buy your tickets to <b>NUS ICS x Sikh Society’s Diwali Night 2024</b> "
msg2 = "Press /info for more information about <b>NUS ICS x Sikh Society’s Diwali Night 2024!</b> "
msg3 = "Your transaction has been cancelled. Please press /buy to buy tickets to NUS ICS x Sikh Society’s Diwali Night 2024!"
msg4 = """
Join us for <b>NUS ICS x Sikh Society’s Diwali Night 2024!</b> 🥳🤩

📅 <b>9th November 2024, Saturday</b>  
🕖 <b>7:00pm - 10:00pm</b> (registration is open from 6:30pm – 7:15pm)  
📍 <b>NUS Central Library Foyer, 12 Kent Ridge Cres, 119275</b>  
❗️<u>Open to all university students in Singapore</u>  

Don’t miss this unforgettable evening of cultural immersion, captivating performances, and delicious cuisine. Experience the luminous spirit of <b>Diwali</b> like never before at <b>NUS Indian Cultural Society’s Diwali Night 2024</b>! Join us for an evening filled with vibrant music, exciting booths, and an unforgettable celebration of culture and lights.

🎉 Dance to the rhythm of <b>Bollywood beats</b> with DJs from <u>UNTAMED</u>  
🎨 Explore <b>henna art, arts and crafts, and fun game booths</b>  
🍴 Enjoy <b>delicious vegetarian food</b> from <u>Shivam Restaurant</u>  

We are so excited to celebrate <b>Diwali</b> with you, so hope to see you there!! 🥳🎉  

<u>Press <b>/buy now</b> to secure your ticket!</u>  

(Please note: The event will include some <b>Hindu religious elements</b> as part of the cultural celebration. We welcome everyone to join us and participate as they feel comfortable.)
"""

msg6 = "<b>Please enter your full name:</b>\n\n↪️ Press /cancel to restart your booking for ICSXSikh Society Diwali 2024!"


def upload_to_s3(image, bucket_name, object_name):
    s3 = boto3.client('s3')
    buffer = BytesIO()
    image.save(buffer, 'PNG')
    buffer.seek(0)
    s3.put_object(Bucket=bucket_name, Key=object_name, Body=buffer, ContentType='image/png')
    expiration = 60 * 60 * 24 * 365 * 10  # 10 years in seconds
    url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)
    return url

def generate_qr_with_texts(uuid, ticket_number, name, filename):
    # Generate the QR code with higher resolution
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=30,  # Increase the box size for higher resolution
        border=1,
    )
    qr.add_data(uuid)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white').convert('RGB')

    # Load built-in font
    font_large = ImageFont.truetype("font.ttf", size=48)
    font_medium = ImageFont.truetype("font.ttf", size=36)
    font_small = ImageFont.truetype("font.ttf", size=25)

    # Calculate text sizes
    text_top = "#ICS X Sikh Society Diwali 2024"
    text_middle = name
    text_bottom = f"Ticket {ticket_number}"

    top_bbox = font_large.getbbox(text_top)
    middle_bbox = font_medium.getbbox(text_middle)
    bottom_bbox = font_small.getbbox(text_bottom)

    top_width = top_bbox[2] - top_bbox[0]
    middle_width = middle_bbox[2] - middle_bbox[0]
    bottom_width = bottom_bbox[2] - bottom_bbox[0]

    top_height = top_bbox[3] - top_bbox[1]
    middle_height = middle_bbox[3] - middle_bbox[1]
    bottom_height = bottom_bbox[3] - bottom_bbox[1]

    # Create a new image with extra space at the top and bottom for the text
    qr_width, qr_height = qr_img.size
    new_height = qr_height + top_height + middle_height + bottom_height + 80  # Add some padding

    new_img = Image.new('RGB', (qr_width, new_height), 'white')
    draw = ImageDraw.Draw(new_img)

    # Draw the top text
    top_x = (qr_width - top_width) / 2
    top_y = 10  # Padding from the top
    draw.text((top_x, top_y), text_top, fill='black', font=font_large)

    # Draw the QR code
    qr_y = top_y + top_height + 10  # Padding between top text and QR code
    new_img.paste(qr_img, (0, qr_y))

    # Draw the middle text
    middle_x = (qr_width - middle_width) / 2
    middle_y = qr_y + qr_height + 10  # Padding between QR code and middle text
    draw.text((middle_x, middle_y), text_middle, fill='black', font=font_medium)

    # Draw the bottom text
    bottom_x = (qr_width - bottom_width) / 2
    bottom_y = middle_y + middle_height + 10  # Padding between middle text and bottom text
    draw.text((bottom_x, bottom_y), text_bottom, fill='grey', font=font_small)
    url = upload_to_s3(new_img, 'untamed', f'{filename}.png')
    return url

def TextToDate(prompt):
    client = OpenAI()
    custom_functions = [
        {
            "type": "function",
            "function": {
                'name': 'Extract_Date_Components',
                'description': 'Extracts day, month, and year from a user inputted date in (MM DD YYYY) format',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'day': {
                            'type': 'string',
                            'description': 'The day of the month in numeric form'
                        },
                        'month': {
                            'type': 'string',
                            'description': 'The month in numeric form'
                        },
                        'year': {
                            'type': 'string',
                            'description': 'The year'
                        }
                    },
                    "required": ["day", "month", "year"]
                }
            }
        }
    ]
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            tools=custom_functions,
            tool_choice="auto",
        )
        arguments_json = response.choices[0].message.tool_calls[0].function.arguments
        output = json.loads(arguments_json)
        
        day = output['day']
        month = output['month']
        year = output['year']
        try:
            datetime.strptime(f"{day} {month} {year}", "%d %m %Y")
            return {'status': 'success', 'day': day, 'month': month, 'year': year}
        except ValueError:
            return {'status': 'failed', 'reason': "Invalid date format. Please enter the date in (DD MMM YYYY) format (e.g. 1 Jan 2022)"}
    
    except Exception as e:
        return {'status': 'failed', 'reason': "Invalid date format. Please enter the date in (DD MMM YYYY) format (e.g. 1 Jan 2022)"}

async def process_payment_async(amount, client_reference_id, stripe_id):
    client = clients.find_one({'buyer_id': client_reference_id})
    # if info_payload does not have the ticket_type, then return False
    if 'ticket_type' not in client['info_payload']:
        return False
    # Now, take all the information needed from the info_payload and add it to the transactions attribute in the client document
    transactions = client['transactions']
    purchaser_info = client['info_payload']
    transaction = {
        'purchaser_info': {
            'name': purchaser_info['name'],
            'nus_id': purchaser_info['nus_id'],
            'email':purchaser_info['email'],
            'permission':purchaser_info['permission']
        },
        'booking_id': ''.join(random.choices(string.ascii_uppercase, k=8)),
        'stripe_id': stripe_id,
        'ticket_type': purchaser_info['ticket_type'],
        'qty': int(purchaser_info['qty']),
        'payment_method': 'paynow',
        'tickets': []
    }
    # Depending on the qty, time to generate the tickets and it's relevant attributes
    count = 1
    for i in range(int(purchaser_info['qty'])):
        QR_secret = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        QR_Ref = ''.join(random.choices(string.ascii_uppercase, k=8))
        ticket_type_info = ticket_type.find_one({"_id": purchaser_info['ticket_type']})
        url = generate_qr_with_texts(QR_secret, count, f"{purchaser_info['name']} - {ticket_type_info['name']}", f"{QR_Ref}")
        ticket = {
            's3': url,
            'QR_secret': QR_secret,
            'QR_REF': QR_Ref,
            'inside': False
        }
        transaction['tickets'].append(ticket)
        count += 1
    transactions.append(transaction)
    clients.update_one({'buyer_id': client_reference_id}, {"$set": {"transactions": transactions}})
    """
    Data Structure of ticket_type collections:
        {
            _id: # 1-Early Bird, 2-Phrase 1, 3-phrase 2
            cost: # float
            quota_left: # INT
            counter: (OBJ){
                “paynow”: 0,
        “card”: 0,
        “grabpay”: 0,
        “alipay-wechat”: 0
        }
        }
    """
    # Append the counter
    ticket = ticket_type.find_one({"_id": purchaser_info['ticket_type']})
    ticket['counter']['paynow'] += int(purchaser_info['qty'])
    ticket['quota_left'] -= int(purchaser_info['qty'])
    ticket_type.update_one({"_id": purchaser_info['ticket_type']}, {"$set": ticket})
    client_id = client['_id']
    await Fastbot.info_payload_reset(client_id)
    await Fastbot.update_state_client(client_id, 0, 0)
    # Now, we need to send our user the tickets
    for i in range(int(purchaser_info['qty'])):
        ticket = transaction['tickets'][i]
        url = ticket['s3']
        ticket_number = i + 1
        await Fastbot.send_image_with_caption(client_id, url, f"<b>Ticket Number:</b> {ticket_number}\n<b>Ticket ID:</b> {ticket['QR_REF']}")
    # Add the fact that you need to click on the button and show the ticket at the venue
    ticket_type_info = ticket_type.find_one({"_id": purchaser_info['ticket_type']})
    await Fastbot.send_text(client_id, f"<b>Thank you for your purchase, {transaction['purchaser_info']['name']} 🥳🙏</b>\n\n#️⃣ <b>Your Booking ID:</b> {transaction['booking_id']}\n\n✅ <i>You have successfully booked {transaction['qty']} tickets of {ticket_type_info['name']} for ${amount}.</i>\n\n⚠️ <i>Please save and keep the above QR codes safe and only display it upon entry.</i>\n\n🔍 You may view your tickets again at\n/view_tickets.\n\nPress /buy to buy more tickets to ICSXSikh Society Diwali 2024!\n\n<b>See you soon ❤️‍🔥</b>")
    list_ticket_ids = [ticket['QR_REF'] for ticket in transaction['tickets']]
    send_appscript_request({"method": "update_sheet", "authe": os.environ['qrscanner'], "buyer_id": client_reference_id, "name": purchaser_info['name'], "email": purchaser_info['email'], "nus_id": purchaser_info['nus_id'], "permission": purchaser_info['permission'], "qty": purchaser_info['qty'], "amt": amount, "booking_id": transaction['booking_id'], "stripe_id": stripe_id, "ticket_ids": json.dumps(list_ticket_ids), "ticket_type": ticket_type_info['name']})
    print({"method": "update_sheet", "authe": os.environ['qrscanner'], "buyer_id": client_reference_id, "name": purchaser_info['name'], "email": purchaser_info['email'], "nus_id": purchaser_info['nus_id'], "permission": purchaser_info['permission'], "qty": purchaser_info['qty'], "amt": amount, "booking_id": transaction['booking_id'], "stripe_id": stripe_id, "ticket_ids": json.dumps(list_ticket_ids), "ticket_type": ticket_type_info['name']})
    return True

async def create_checkout_session(ticket_name,cost_of_tickets, convenience_fee, client_reference_id, qty):
    try:
        # Calculate total cost in cents
        total_cost = int((cost_of_tickets + convenience_fee) * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['paynow'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'sgd',
                        'product_data': {
                            'name': ticket_name,
                        },
                        'unit_amount': int(cost_of_tickets * 100),  
                    },
                    'quantity': qty,
                },
                {
                    'price_data': {
                        'currency': 'sgd',
                        'product_data': {
                            'name': 'Convenience Fee',
                        },
                        'unit_amount': int(convenience_fee * 100),
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            client_reference_id=client_reference_id,
            success_url='https://ladesi-4f55f363a71e.herokuapp.com/payment_confirmation',
        )
        return session.url, session.id
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return None

async def expire_stripe_checkout_session_from_session_id(session_id):
    try:
        stripe.checkout.Session.expire(session_id)
        return True
    except Exception as e:
        return str(e)

def send_appscript_request(data):
    try:
        requests.get(os.environ['appscript_url'], params=data)
    except:
        traceback.print_exc()


@app.post("/telegram")
async def echo(request: Request):   
    try:
        update_data = await request.json()
        update = telegram.Update.de_json(update_data, bot)
        if update.message:
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
            await Fastbot.send_text(chat_id, "Your message type isn't supported.")
            return {"status": "ok"}
        if clients.find_one({'_id': chat_id}):
            client_status = clients.find_one({'_id': chat_id})
            if update.message:
                if "/cancel" == update.message.text:
                    if 'stripe_session_id' in client_status['info_payload']:
                        await expire_stripe_checkout_session_from_session_id(client_status['info_payload']['stripe_session_id'])
                        await Fastbot.send_text(chat_id, "<b>Your payment has been cancelled.</b>\nPlease press /buy to buy tickets to ICS X Sikh Society Diwali 2024!")
                        await Fastbot.update_state_client(chat_id, 0, 0)
                        await Fastbot.info_payload_reset(chat_id)
                        return {"status": "ok"}
                    await Fastbot.send_text(chat_id, msg3)
                    await Fastbot.update_state_client(chat_id, 0, 0)
                    await Fastbot.info_payload_reset(chat_id)
                    return {"status": "ok"}
            if client_status['state']['major'] == 0 and client_status['state']['minor'] == 0:
                if "/start" == user_input:
                    await Fastbot.send_text(chat_id, msg1)
                    await Fastbot.send_text(chat_id, msg2)
                    return {"status": "ok"}
                elif "/info" == user_input:
                    await Fastbot.send_text(chat_id, msg4)
                    return {"status": "ok"}
                elif "/buy" == user_input:
                    # await Fastbot.send_text(chat_id, 'Ticketing for ICS X Sikh Society Diwali 2024 has ended. Please press /contact to contact the organisers for more information.')
                    # return {"status": "ok"}
                    client = clients.find_one({"_id": chat_id})
                    transactions = client['transactions']
                    if len(transactions) > 0:
                        await Fastbot.send_text(chat_id, "You have already bought tickets to ICS X Sikh Society Diwali 2024. Press /view_tickets to view your ticket. Press /contact to contact the organisers.")
                        return {"status": "ok"}
                    current_ticket2 = ticket_type.find_one({"_id": 4})
                    current_ticket3 = ticket_type.find_one({"_id": 6})
                    choice = """
Join us for <b>NUS ICS x Sikh Society’s Diwali Night 2024!</b> 🥳🤩

📅 <b>9th November 2024, Saturday</b>  
🕖 <b>7:00pm - 10:00pm</b> (registration is open from 6:30pm – 7:15pm)  
📍 <b>NUS Central Library Foyer, 12 Kent Ridge Cres, 119275</b>  
❗️<u>Open to all university students in Singapore</u>  

Don’t miss this unforgettable evening of cultural immersion, exciting booths, and delicious cuisine. Experience the luminous spirit of Diwali like never before at <b>NUS Indian Cultural Society and Sikh Society’s Diwali Night 2024!</b> Join us for an evening filled with vibrant music, exciting booths, and an unforgettable celebration of culture and lights.

🎉 Dance to the rhythm of <b>Bollywood beats</b> with DJs from <u>UNTAMED</u>  
🎨 Explore <b>henna art, arts and crafts, and fun game booths</b>  
🍴 Enjoy <b>delicious vegetarian food</b> from <u>Shivam Restaurant</u>  

We are so excited to celebrate <b>Diwali</b> with you, so hope to see you there!! 🥳🎉  

<b>-----TICKETS-----</b>

<s>🎟️ <b>Early Bird (ONLY FOR NUS STUDENTS [50PAX])</b> $10</s>
🎟️ <b>NUS students</b> $12
🎟️ <b>Non-NUS students</b> $15

(Please note: The event will include some <b>Hindu religious elements</b> as part of the cultural celebration. We welcome everyone to join us and participate as they feel comfortable.)
"""
                    await Fastbot.send_options_buttons(chat_id, choice, [f"{current_ticket2['name']} (${current_ticket2['cost']})", f"{current_ticket3['name']} (${current_ticket3['cost']})"], [4,6])
                    await Fastbot.update_state_client(chat_id, 0, 1)
                    print("check 3")
                    return {"status": "ok"}
                elif "/view_tickets" == user_input:
                    client = clients.find_one({"_id": chat_id})
                    transactions = client['transactions']
                    if len(transactions) == 0:
                        await Fastbot.send_text(chat_id, "You have no tickets booked yet. Press /buy to buy tickets to ICS X Sikh Society Diwali 2024!")
                        return {"status": "ok"}
                    for transaction in transactions:
                        for ticket in transaction['tickets']:
                            url = ticket['s3']
                            ticket_number = transaction['tickets'].index(ticket) + 1
                            await Fastbot.send_image_with_caption(chat_id, url, f"<b>Ticket Number:</b> {ticket_number}\n<b>Ticket ID:</b> {ticket['QR_REF']}")
                    await Fastbot.send_text(chat_id, "You have viewed all your tickets. Press /buy to buy more tickets to ICS X Sikh Society Diwali 2024!")
                    return {"status": "ok"}
                elif "/contact" == user_input:
                    contact_message = """
If you have any queries, please contact the Vidita on Telegram: @viditachogle. You can also DM us on our Instagram account: @nus_ics.
"""                 
                    await Fastbot.send_text(chat_id, contact_message)
                else:
                    await Fastbot.send_text(chat_id, "I am not sure what you mean 😅.\nPlease press /buy tickets for ICS X Sikh Society Diwali 2024!\nOr press /info to get more information about ICS X Sikh Society Diwali 2024!")
                    return {"status": "ok"}
            elif client_status['state']['major'] == 0 and client_status['state']['minor'] == 1: #(ticket:name)
                print("User input is: ", user_input)
                print(type(user_input))
                if user_input not in ["4","6"]:
                    current_ticket2 = ticket_type.find_one({"_id": 4})
                    current_ticket3 = ticket_type.find_one({"_id": 6})
                    await Fastbot.send_options_buttons(chat_id, "<b>Please select the ticket type you would like to purchase</b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!", [f"{current_ticket2['name']} (${current_ticket2['cost']})", f"{current_ticket3['name']} (${current_ticket3['cost']})"], [4,6])
                    return {"status": "ok"}
                ticket = ticket_type.find_one({"_id": int(user_input)})
                ticket_name = ticket['name']
                ticket_cost = ticket['cost']
                msg5 = f"Your selection: <b>{ticket_name}</b> 🎟️\nTicket price <i>(before processing fees)</i>: <b>${ticket_cost}</b>"
                await Fastbot.send_text(chat_id, msg5)
                await Fastbot.send_text(chat_id, "Question 1 of 3 [█░░]\n\n" + msg6)
                await Fastbot.update_state_client(chat_id, 1, 0)
                await Fastbot.update_info_payload(chat_id, "ticket_type", int(user_input))
                return {"status": "ok"}
            elif client_status['state']['major'] == 1 and client_status['state']['minor'] == 0: #(name:NUS_ID)
                if not update.message:
                    await Fastbot.send_text(chat_id, "I am not sure what you mean. <b>Please enter your full name:</b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!")
                    return {"status": "ok"}
                if len(user_input) > 40 or re.search(r'[^a-zA-Z\s]', user_input):
                    await Fastbot.send_text(chat_id, "<b>Please enter a name in the correct format. It must not have any special characters and must be shorter than 40 characters.</b>\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!")
                    return {"status": "ok"}
                await Fastbot.update_info_payload(chat_id, "name", user_input)
                await Fastbot.send_text(chat_id, f"<b>Hey {user_input}</b>, we are excited to host you at ICS X Sikh Society Diwali 2024! 🎉")
                await Fastbot.send_text_with_back(chat_id,  "Question 2 of 3 [██░]\n\n" + "<b>Please enter your university email (Format: elon@u.nus.edu)</b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!")
                await Fastbot.update_state_client(chat_id, 1, 1)
                return {"status": "ok"}
            elif client_status['state']['major'] == 1 and client_status['state']['minor'] == 1: #(NUS_ID:email)
                if user_input == "previous":
                    await Fastbot.send_text(chat_id, msg6)
                    await Fastbot.update_state_client(chat_id, 1, 0)
                    return {"status": "ok"}
                valid_nus_id = Fastbot.is_valid_email(user_input)
                if not update.message or valid_nus_id == False:
                    await Fastbot.send_text(chat_id, "<b>Please enter a valid University Email</b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!")
                    return {"status": "ok"}
                await Fastbot.update_info_payload(chat_id, "nus_id", user_input)
                # Use send_options_buttons to send the options to the user for the gender
                await Fastbot.update_state_client(chat_id, 1, 3)
                await Fastbot.send_text_with_back(chat_id,"Question 3 of 3 [███]\n\n" + "<b>Please enter your university name!</b> (e.g. NTU)\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!")
                return {"status": "ok"}         
            elif client_status['state']['major'] == 1 and client_status['state']['minor'] == 3: #(email:confirmation)
                if user_input == "previous":
                    await Fastbot.update_state_client(chat_id, 1, 1)
                    await Fastbot.send_text(chat_id, "<b>Please enter your university email (Format: elon@u.nus.edu)</b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!")
                    return {"status": "ok"}
                
                # if Fastbot.is_valid_email(user_input) == False:
                #     await Fastbot.send_text(chat_id, "<b>Please enter a valid email address.</b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!")
                #     await Fastbot.update_state_client(chat_id, 1, 3)
                #     return {"status": "ok"}
                #     await Fastbot.update_state_client(chat_id, 1, 3)
                #     return {"status": "ok"}

                await Fastbot.update_info_payload(chat_id, "email", user_input)
                if update.message:
                    await Fastbot.update_state_client(chat_id, 1, 3.1)
                    user_details = client_status['info_payload']
                    user_name = user_details['name']
                    user_nus_id = user_details['nus_id']
                    user_email = user_input
                    # Make confirmation message with all details
                    msg7 = f"""

✅ <b>Please confirm your details:</b>
                    
<b>Name:</b> {user_name}
<b>University Email:</b> {user_nus_id}
<b>University Name:</b> {user_email}

Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!
                    """
                    # Send confirmation message to user asking yes or no
                    # Say your number has neen noted
                    await Fastbot.send_options_buttons(chat_id, msg7, ["Looks Good!", "Make a change!"], ["Yes", "No"])
                    return {"status": "ok"}
                else:
                    await Fastbot.send_text_with_back(chat_id,"Question 3 of 3 [███]\n\n" + "<b>Please enter your NUS Email! (Beginning with e..) </b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!")
                    return {"status": "ok"}

            elif client_status['state']['major'] == 1 and client_status['state']['minor'] == 3.1: #(confirmation:q1(yes/no))
                if not update.callback_query:
                    await Fastbot.send_text(chat_id, "Please select one of the options above!")
                    await Fastbot.update_state_client(chat_id, 1, 3.1)
                    return {"status":"ok"}
                
                if user_input == 'No':
                    await Fastbot.send_text(chat_id, "Noted! Press /buy again to <b>restart your booking</b> for ICS X Sikh Society Diwali 2024!")
                    await Fastbot.info_payload_reset(chat_id)
                    await Fastbot.update_state_client(chat_id, 0, 0)
                    return {"status":"ok"}
                qnone = """
<b>By clicking Yes on the Telegram bot, I :</b>
•	Agree to the terms and conditions of the NUS Personal Data Notice for Students (https://myportal.nus.edu.sg/studentportal/academics/all/docs/NUS-Registration-Personal-Data-Notice.pdf), and the NUS Privacy Notice (https://www.nus.edu.sg/ormc/personal-data-protection/nus-data-protection-policy). 
•	Consent to the collection, use and disclosure of the particulars provided below to NUS ICS and other third parties (including without limitation, information that may be deemed personal data under the Personal Data Protection Act 2012 of Singapore) for the following purposes: 

(a)	the signing up for the activity (NUS ICS x Sikh Society Diwali Night 2024);
(b)	the management of data for the event (NUS ICS x Sikh Society Diwali Night 2024);
(c)	any other incidental purposes related to or in connection with the above.

•	Further agree to receive updates, important announcements and publicity material by email from NUS ICS. All personal information will be kept confidential, and will be strictly used by NUS ICS for the purpose of related information and updates related to NUS ICS programmes.

<b>Should I wish to withdraw my consent and request for to NUS ICS to stop using and/or disclosing my personal data for any of the purposes listed above, I may submit my request via email at nus.indianculturalsoc@gmail.com to indicate so. Please note that the withdrawal of consent takes 5-working days to take effect.</b>

↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!
"""
                await Fastbot.send_options_buttons(chat_id, qnone, ["Yes"], ["yes"])
                await Fastbot.update_state_client(chat_id, 1, 3.2)
                return {"status":"ok"}
            
            elif client_status['state']['major'] == 1 and client_status['state']['minor'] == 3.2: #(q1(yes/no):q2(yes/no))
                if user_input == 'yes':
                    qntwo = """
I consent to having my photographs and any audio and/or video recordings bearing my image, voice and related transcripts taken by the organising team from NUS Indian Cultural Society and persons authorised by NUS Indian Cultural Society  for the purpose of NUS Indian Cultural Society’s marketing, publicity and media/social media.
"""
                    await Fastbot.send_options_buttons(chat_id, qntwo, ["Yes", "No"], ["yes", "no"])
                    await Fastbot.update_state_client(chat_id, 1, 3.5)
                    return {"status":"ok"}
                
                await Fastbot.send_text(chat_id, "You need to agree to the terms and conditions to proceed. Please press /buy to buy tickets to ICS X Sikh Society Diwali 2024!")
                await Fastbot.info_payload_reset(chat_id)
                await Fastbot.update_state_client(chat_id, 0, 0)
                return {"status":"ok"}
                
                 
            elif client_status['state']['major'] == 1 and client_status['state']['minor'] == 3.5: #(q2(yes/no):no_of_tickets)
                if not update.callback_query:
                    await Fastbot.send_text(chat_id, "Please select either the yes or no options above!")
                    await Fastbot.update_state_client(chat_id, 1, 3.5)
                    return {"status":"ok"}
                
                await Fastbot.update_info_payload(chat_id, "permission", user_input)
            # Check the quota left for the current ticket type
                current_type = client_status['info_payload']['ticket_type']
                ticket = ticket_type.find_one({"_id": current_type})
                ticket_quota = ticket['quota_left']
                if ticket_quota == 0:
                    await Fastbot.send_text(chat_id, "Sorry, the ticket quota for this ticket type has been exhausted. Please press /buy to buy tickets to ICS X Sikh Society Diwali 2024!")
                    await Fastbot.update_state_client(chat_id, 0, 0)
                    await Fastbot.info_payload_reset(chat_id)
                    return {"status": "ok"}
                if ticket_quota >= 1:
                    ticket_quota = 1
                if ticket_quota < 1:
                    await Fastbot.send_text(chat_id, "There is no more tickets left for this category. Please press /buy to buy tickets to ICS X Sikh Society Diwali 2024 FROM ANOTHER CATEGORY!")
                    await Fastbot.update_state_client(chat_id, 0, 0)
                    await Fastbot.info_payload_reset(chat_id)
                    return {"status": "ok"}
                await Fastbot.send_options_buttons(chat_id, "<b>🎫 Number of tickets</b> you would like to purchase?\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!", [str(i) for i in range(1, ticket_quota+1)], [str(i) for i in range(1, ticket_quota+1)])
                await Fastbot.update_state_client(chat_id, 1, 4)
                return {"status": "ok"}
            
            elif client_status['state']['major'] == 1 and client_status['state']['minor'] == 4: #(no_of_tickets:payment)
                # Check if the user_input is a number between 1 and ticket_quota
                current_type = client_status['info_payload']['ticket_type']
                ticket = ticket_type.find_one({"_id": current_type})
                ticket_quota = ticket['quota_left']
                if ticket_quota >= 1:
                    ticket_quota = 1
                if user_input not in [str(i) for i in range(1, ticket_quota+1)]:
                    await Fastbot.send_options_buttons(chat_id, "<b>Please select a quantity here</b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!", [str(i) for i in range(1, ticket_quota+1)], [str(i) for i in range(1, ticket_quota+1)])
                    return {"status": "ok"}
                await Fastbot.update_info_payload(chat_id, "qty", user_input)
                await Fastbot.update_state_client(chat_id, 1, 5)
                # Now, create a message which shows the total cost. It will be the cost of the ticket multiplied by the quantity. On top of that, add a 3.3% convenience fee
                ticket_cost = ticket['cost']
                ticket_qty = int(user_input)
                total_cost = ticket_cost * ticket_qty
                convenience_fee = total_cost * 0.015
                total_cost += convenience_fee
                # Write the number of tickets you have chosen
                await Fastbot.send_text(chat_id, f"You have chosen {user_input} ticket(s)")
                # In the message, clearly show all the breakdowns, first show the ticket cost multiplied by the quantity, then show the convenience fee
                msg8 = f"<b>💵 Total Cost Breakdown</b>\n\n<b>Cost of {user_input} tickets:</b> ${ticket_cost * ticket_qty:.2f}\n<b>Processing Fee:</b> ${convenience_fee:.2f}\n\n<b>Total: ${total_cost:.2f}</b>\n\n❗️You will receieve your tickets once <b>your payment has been processed.</b> Please click on the button below to proceed!\n\nElse, please press /cancel to restart the booking process."
                checkout_session_url, session_id = await create_checkout_session(ticket['name'], ticket['cost'], convenience_fee,client_status['buyer_id'], ticket_qty)
                await Fastbot.send_text_with_url(chat_id, msg8, checkout_session_url, "Proceed to Payment 💰")
                await Fastbot.update_info_payload(chat_id, "stripe_session_id", session_id)
                await Fastbot.update_info_payload(chat_id, "stripe_session_url", checkout_session_url)
                return {"status": "ok"}
            elif client_status['state']['major'] == 1 and client_status['state']['minor'] == 5:#(payment:repeat_payment)
                # Give them the payment summary again along with the payment url just like previously, tell them if they want to re-book, ask them to press /cancel
                current_type = client_status['info_payload']['ticket_type']
                ticket = ticket_type.find_one({"_id": current_type})
                ticket_cost = ticket['cost']
                ticket_qty = int(client_status['info_payload']['qty'])
                total_cost = ticket_cost * ticket_qty
                convenience_fee = total_cost * 0.015
                total_cost += convenience_fee
                msg8 = f"<b>Please make your payment</b>\n\n<b>Total Cost Breakdown</b>\n\n<b>Cost of {ticket_qty} tickets:</b> ${ticket_cost * ticket_qty:.2f}\n<b>Processing Fee:</b> ${convenience_fee:.2f}\n\n<b>Total: ${total_cost:.2f}</b>\n\n↪️ Press /cancel to restart your booking for ICS X Sikh Society Diwali 2024!"
                # use the same checkout session as last time
                await Fastbot.send_text_with_url(chat_id, msg8, client_status['info_payload']['stripe_session_url'], "Proceed to Payment 💰")
                return {"status": "ok"}
        else:
            new_user = {
                "_id": chat_id,
                "buyer_id": ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.digits, k=1)) + ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.digits, k=1)) + ''.join(random.choices(string.ascii_uppercase, k=1)),
                "time_joined": time.time(),
                "state": {
                    "major": 0,
                    "minor": 0
                },
                "transactions": [],
                "info_payload": {}
            }
            clients.insert_one(new_user)
            await Fastbot.send_text(chat_id, msg1)
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "not ok"}
    return {"status": "ok"}

@app.post("/stripe")
async def webhook_received(request: Request, background_tasks: BackgroundTasks, stripe_signature: str = Header(None)):
    data = await request.body()
    response = JSONResponse(content={"status": "success"})
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=os.environ['webhook_secret_test']
        )
        event_data = event['data']
    except Exception as e:
        print(e)
        return {"status": "ok"}
    
    try:
        amount = event_data['object']['amount_total'] / 100
        client_reference_id = event_data['object']['client_reference_id']
        if not clients.find_one({'buyer_id': client_reference_id}): 
            return response
        stripe_id = event_data['object']['payment_intent']
        status = event_data['object']['status']
        transaction_id = event_data['object']['id']
        if status == 'complete':
            client_id = clients.find_one({'buyer_id': client_reference_id})['_id']
            await Fastbot.send_text(client_id, f"<b>Payment of ${amount} received!</b>\n<b>Payment ID:</b> {stripe_id}\n🎫 Generating your tickets...\n<b>PLEASE WAIT\n<i>If there is any issue use /contact</i></b>")
            asyncio.create_task(process_payment_async(amount, client_reference_id, stripe_id))
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return response

@app.post("/scan")
async def echo(request: Request):
    try:
        update_data = await request.json()
        print(update_data)
        if update_data["auth"] == os.environ["qrscanner"]:
            qr_secret = update_data["qr"]
            client = clients.find_one({"transactions.tickets.QR_secret": qr_secret})
            if client:
                for transaction in client["transactions"]:
                    count = 1
                    for ticket in transaction["tickets"]:
                        if ticket["QR_secret"] == qr_secret:
                            if ticket["inside"]:
                                return {"status": "valid", "auth": os.environ["qrscanner"], "name": transaction["purchaser_info"]["name"], "enterStatus": False, "ticket_id": ticket["QR_REF"], "ticket_number": count, "bookingId": transaction["booking_id"]}
                            ticket["inside"] = True
                            clients.update_one({"_id": client["_id"]}, {"$set": client})
                            try:
                                send_appscript_request({"method": "update_attendance", "authe": os.environ['qrscanner'],"ticket_id": ticket["QR_REF"]})
                                print({"method": "update_attendance", "authe": os.environ['qrscanner'],"ticket_id": ticket["QR_REF"]})
                            except Exception as e:
                                print(f"An error occurred: {e}")
                            # infrom telegram user that the ticket has been scanned
                            await Fastbot.send_text(client["_id"], f"<b>Your ticket with ID {ticket['QR_REF']} has been scanned successfully. Enjoy the event! 🎉</b>")
                            return {"status": "valid", "auth": os.environ["qrscanner"], "name": transaction["purchaser_info"]["name"], "enterStatus": True, "ticket_id": ticket["QR_REF"], "ticket_number": count, "bookingId": transaction["booking_id"]}
                        count += 1
            else:
                return {"status": "invalid", "auth": os.environ["qrscanner"]} # True: Entering Now, False: Already Inside
        else:
            return {"status": "invalid", "auth": os.environ["qrscanner"]}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "invalid"}

# https://script.google.com/macros/s/AKfycbzjSUOteyx0eu7ctYkQ7MXKUUQhMGxer_Td8un9YM5vqXWcX0Y325xJXs9llRI6uF3CHw/exec

# Create a payment confirmation page 
@app.get("/payment_confirmation")
async def payment_confirmation(request: Request):
    return templates.TemplateResponse("payment_confirmation.html", {"request": request})



