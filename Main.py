from telegram import Bot, Update
from telegram.ext import *
import openai
from openai import OpenAI
import logging
import time
from Config import *
import sqlite3


openai.api_key = OPENAI_TOKEN
BOT_USERNAME = "@SCDFmyWellnessBot"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Welcome to SCDF MyWellness! Please either click on the menu found in the bottom left corner to find more options or just tell us what you need to know!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To make this bot work, simply tell us how you are feeling or what information you need and we shall see how we can help! \n \nIf you do not have access to the bot, simply tell us the password! If you still cant gain access, please contact your supervisors!")

async def upcoming_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("As this bot is a prototype, features found here may seem quite limited. However, over time you will be able to do so much more such as get alerts regarding key dates for your training!")    

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("welcome admin. Please enter the admin password to access admin functions!")
    reply = update.message.text   

    if reply == admin_password:
        return "You have logged in as an admin"

    conn = sqlite3.connect("Userbase.db")

    conn.close()
   
    

# def log_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     global chat_id_v # Declare global variable usage
#     chat_id_v = update.message.chat.id
#     return chat_id_v
    
# async def get_chatid(update:Update, context:ContextTypes.DEFAULT_TYPE): 
#     message_type: str = update.message.chat.type #type of chat - Group or private
#     text: str = update.message.text #any new message in group
#     chat_id_v = update.message.chat.id

def sendMessage(chat_id:int, text:str):
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=chat_id,text=text)

def get_message(update:Update,processed:str) -> str :

    current_member = update.message.chat.id
    client = OpenAI(api_key=OPENAI_TOKEN)

    if approved_users[current_member] == "":
        thread = client.beta.threads.create()
        approved_users[current_member] = thread.id
        print(thread)

    message = client.beta.threads.messages.create(
        thread_id = approved_users[current_member],
        role="user",
        content= f"{processed}"
    )

    run = client.beta.threads.runs.create(
        thread_id = approved_users[current_member],
        assistant_id = "asst_cxbjvIh6pDIJP7p7uK3Ol3fv"
    )

    while run.status == 'queued' or run.status == 'in_progress':

        run = client.beta.threads.runs.retrieve(
        thread_id= approved_users[current_member],
        run_id = run.id
    )  

    messages = client.beta.threads.messages.list(
        thread_id = approved_users[current_member]
    )

    for messages in messages.data:
        return messages.content[0].text.value

    # response = openai.chat.completions.create(
    #     #assistant_id = "asst_cxbjvIh6pDIJP7p7uK3Ol3fv",
    #     model = "gpt-3.5-turbo",
    #     messages = [
    #     {"role" : "system", "content": f"{content_ai}"},
    #     {"role" : "user", "content" : f"{processed}"} 
    #     ]
    # )
    # assistant_response = response.choices[0].message.content
    # return assistant_response

# async def chat_id_v(update:Update, context:ContextTypes.DEFAULT_TYPE): #used for debugging?
#     message_type: str = update.message.chat.type #type of chat - Group or private
#     text: str = update.message.text #any new message in group

#     if password in text:
#         approved_users.append(update.message.chat.id)
#         print(approved_users)
#         current_member = update.message.chat.id
#     else:
#         current_member = update.message.chat.id



def handle_response(update:Update, text: str) -> str:

    processed: str = text.lower()
    input_pass = update.message.text
    member = False

    current_member = update.message.chat.id

    if password in input_pass and member == False:
        approved_users.update({current_member:""})
        
    print(approved_users)

    if current_member in approved_users:
        member = True
    else:
        member = False

    if password in processed: #may need to remove
        return "You have successfully registered!"
    
    if member == False: #Catch for non approved users. #point of entry to AI usee
        return "Sorry You don't have access to this bot! Please input the password to continue."

    if 'hello' in processed:
        return "Hi! Welcome to SCDF YourWellness"
    
    if 'thanks' in processed:
        return "No Problem! Have a good day!"
    
    if '' in processed:
        return get_message(update, processed)
    
    return "I'm sorry! I am a simple bot. Please stick to simple words and phrases when speaking to me! Thanks!"
    

async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE): #used for debugging?
    message_type: str = update.message.chat.type #type of chat - Group or private
    text: str = update.message.text #any new message in group

    print(f'User({update.message.chat.id}) in  {message_type}: "{text}"')

    if message_type == 'supergroup':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response:str = handle_response(update, new_text)
        else:
            return
    else:
        response: str = handle_response(update, text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == "__main__":
    print("Starting bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    #Commands
    app.add_handler(CommandHandler('start',start_command))
    app.add_handler(CommandHandler('help',help_command))
    app.add_handler(CommandHandler('upcoming',upcoming_command))
    app.add_handler(CommandHandler('admin',admin_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
   

    #Errors
    app.add_error_handler(error_handler)

    print("Polling...")
    app.run_polling(poll_interval=3) 
