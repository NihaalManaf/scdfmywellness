from telegram import Bot, Update
from telegram.ext import *
import openai
from openai import OpenAI
import logging
import time
from Config import *
import sqlite3
import sys
import re
from datetime import datetime



openai.api_key = OPENAI_TOKEN
bot = Bot(TOKEN)
BOT_USERNAME = "@SCDFmyWellnessBot"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Welcome to SCDF MyWellness! Please either click on the menu found in the bottom left corner to find more options or just tell us what you need to know!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To make this bot work, simply tell us how you are feeling or what information you need and we shall see how we can help! \n \nIf you do not have access to the bot, simply tell us the password! If you still cant gain access, please contact your supervisors!")

async def upcoming_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("As this bot is a prototype, features found here may seem quite limited. However, over time you will be able to do so much more such as get alerts regarding key dates for your training!")    

#admin login + functions ----------------------------------------------------------------------------------------------------
    
LOGIN, FUNCTION, DATE, INTAKE, DEF, UPDATE = range(6)
user_data = {}

def NRICparser(user_ics):
    strings = re.split('\n',user_ics)
    user_ics = [s for s in strings if s]
    return user_ics

def addusers(user_ics, date, intake):
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()

    user_ics_a = NRICparser(user_ics)

    cursor.execute("""
        SELECT * FROM pass;
        """)

    results = cursor.fetchall()
    for row in results:
        defaultpass = row[0]

    for i in range(0,len(user_ics_a)):
        cursor.execute(f"""
                        INSERT INTO user_accounts (user_ic, enlist_date, intake, password) VALUES ('{user_ics_a[i]}', '{date}', '{intake}','{defaultpass}');
                    """)
        
    conn.commit()
    conn.close()
    return

def resetpasswords(user_ics):
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()

    user_ics_a = NRICparser(user_ics)

    for i in range(0,len(user_ics_a)):
        cursor.execute(f"""
                        UPDATE user_accounts SET password = 'testtest' WHERE user_ic = '{user_ics_a[i]}'
                    """)
        
    conn.commit()
    conn.close()
    return

def changepass(new_pass):
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()

    cursor.execute(f"""
                        UPDATE pass SET password = '{new_pass}'
                    """)
        
    conn.commit()
    conn.close()

    return


#/admin converstaion ----------------------------------------------------------------------------------------------------
async def admin(update:Update, context):
    await update.message.reply_text("Welcome Admin. Please enter the password to access Admin functions")
    return LOGIN

async def admin_login(update, context):
    user_data['pass'] = update.message.text

    if admin_password not in user_data["pass"]:
        await update.message.reply_text("You have entered an invalid password. Sorry!")
        return ConversationHandler.END
    
    await update.message.reply_text("""
                                    Please select from the following functions
    1. addusers
    2. resetpasswords
    3. changedefault
                                    """)
    
    return FUNCTION

async def admin_function(update, context):
    user_data['function'] = update.message.text.replace(" ", "").lower()

    if user_data["function"] in 'addusers':
        await update.message.reply_text("Enter the date of enlistment for the recruits! Please enter the date in the following format: YYYYMMDD ")
        return DATE

    if user_data["function"] in 'resetpasswords':
        await update.message.reply_text("Please ensure you have the NRIC's ready by copying them directly from the excel spreadsheet. Ensure all the NRIC's are in one column and no extra lines have been copied. Type ok to acknowledge. ")
        x= 1
        return INTAKE
    
    if user_data["function"] in 'changedefaults':
        await update.message.reply_text("please enter the new default password. Please take note that the password is case sensitive! ")
        return DEF
    
    await update.message.reply_text("You have not selected a valid function. Please enter the admin password and try again!") 
    return LOGIN

async def admin_date(update, context):
    user_data['date'] = update.message.text.replace(" ", "").lower()
    await update.message.reply_text("Please enter the intake number and type of the recruits in the following format: 171xbrt or 171brt")
    
    return INTAKE

async def admin_intake(update, context):
    user_data['intake'] = update.message.text.replace(" ", "").lower()
    await update.message.reply_text("Now, please enter all the NRIC's of the users. Ensure you directly copy the full column from an excel file and paste it here!")
    return UPDATE

async def admin_def_update(update, context):
    user_data['default'] = update.message.text
    print(user_data["default"])
    changepass(user_data["default"])

    await update.message.reply_text("You have successfully updated the database!")
    return ConversationHandler.END

async def admin_update(update, context):
    user_data['NRICs'] = update.message.text
    print(user_data['function'])
    
    if user_data["function"] in 'addusers':
        addusers(user_data['NRICs'], user_data['date'],user_data['intake'])

    if user_data["function"] in 'resetpasswords':
        resetpasswords(user_data['NRICs'])


    await update.message.reply_text("You have successfully updated the database!")
    return ConversationHandler.END

async def cancel(update, context: CallbackContext):
    await update.message.reply_text("Login Cancelled. Returning to Bot.")
    return ConversationHandler.END


#start of user login ----------------------------------------------------------------------------------------------------------

USERNRIC, USERPASS, UPDATEPASS = range(3)
rec_data = {}

def auth_user_check(NRIC): 
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()

    cursor.execute(f"""
    SELECT user_ic FROM user_accounts WHERE user_ic LIKE '%{NRIC}'
    """) 

    results = cursor.fetchall()
    conn.commit()
    conn.close()

    print("auth user check works")

    if len(results) == 0:
        return False
    else:
        return True

def auth_user_pass(NRIC, password):
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()
    x = 0

    cursor.execute(f"""
    SELECT password FROM user_accounts WHERE user_ic LIKE '%{NRIC}'
    """) 
    results = cursor.fetchall()

    cursor.execute(f"""
    SELECT password FROM pass
    """) 
    results2 = cursor.fetchall()

    conn.commit()
    conn.close()

    print("auth user pass works")

    for row in results:
        if password == row[0]:
            x = 1

    for row in results2:
        if password == row[0]:
            x = 2
    
    return x

def login_true(NRIC, chatid):
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()

    ph = rec_data[chatid][NRIC]
    
    cursor.execute(f" UPDATE user_accounts SET login_status = true, tele_id = '{chatid}' WHERE user_ic LIKE '%{ph}';")
        
    conn.commit()
    conn.close()

    print("login true works")

    return

def log_query(intake, query, response):
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()

    formatted_date = datetime.now().strftime("%Y%m%d")

    cursor.execute(f"""
                    INSERT INTO eoc (date, intake, query, response) VALUES ( '{formatted_date}', '{intake}', '{query}', '{response}');
                """)
        
    conn.commit()
    conn.close()
    return

async def login(update, context):
    await update.message.reply_text("Welcome to SCDF MyWellness! To login, Please enter the last 4 characters of your NRIC. e.g. 384G")
    return USERNRIC

async def usernric(update, context):
    chat_id = update.message.chat.id
    rec_data[chat_id]['NRIC'] = update.message.text

    if auth_user_check(rec_data[chat_id]["NRIC"]) == True:
        await update.message.reply_text("Please enter your password! If you are unsure of your password, please seek assitance from your supervisor")
        return USERPASS
    
    await update.message.reply_text("You have not been registered in our system. Please seek assistance from your supervisor. To try again, please press /login")
    return ConversationHandler.END

async def userpass(update, context):
    chat_id = update.message.chat.id
    rec_data[chat_id]["password"] = update.message.text
    
    if auth_user_pass(rec_data[chat_id]['NRIC'], rec_data[chat_id]["password"]) == 1:
        await update.message.reply_text("You have successfully Logged in!")
        chatid = update.message.chat.id
        login_true(rec_data[chat_id]["NRIC"],chatid)
        return ConversationHandler.END

    elif auth_user_pass(rec_data[chat_id]['NRIC'], rec_data[chat_id]["password"]) == 2:
        await update.message.reply_text("You are logging in for the first time. Please enter a new password! (Password is case sensitive)")
        chatid = update.message.chat.id
        login_true(rec_data[chat_id]["NRIC"],chatid)
        return UPDATEPASS
    
    else:
        await update.message.reply_text("You have input an incorrect password! Please seek assistance from your supervisor. To login again, press /login")
        return ConversationHandler.END
    
async def userupdate(update, context):
    chat_id = update.message.chat.id
    rec_data[chat_id]['new_password'] = update.message.text
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()

    ph = rec_data[chat_id]["new_password"]
    ph2 = rec_data[chat_id]['NRIC']

    cursor.execute(f"""
                        UPDATE user_accounts SET password = '{ph}' WHERE user_ic LIKE '%{ph2}';
                    """)
        
    conn.commit()
    conn.close()

    await update.message.reply_text("Your new password has been set and you have logged in! Please continue to use the bot to answer all of your questions!")
    return ConversationHandler.END

    
#Regular message handlers    
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

def check_user_login(chatid):
    conn = sqlite3.connect('Userbase.db')
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT login_status, intake FROM user_accounts WHERE tele_id = '{chatid}'
        """) 
    results = cursor.fetchall()

    for row in results:
        if row[0] == 1:
            intake = row[1]
            approved_users.update({chatid:""})

            rec_dict = {"status":True, "intake": intake}
            return rec_dict  
        
    rec_dict = {"status": False, "intake": ""}
    return rec_dict          


def handle_response(update:Update, text: str) -> str:

    processed: str = text.lower()
    input_pass = update.message.text
    response = 'Sorry! you have not logged in! Pleae use /login to access the bot!'

    current_member = update.message.chat.id    
    print(approved_users)

    if 'hello' in processed:
        return "Hi! Welcome to SCDF YourWellness"
    
    if 'thanks' in processed:
        return "No Problem! Have a good day!"

    #code to reduce number of queries per day per batallion per recruit to 1

    # if current_member not in approved_users:
    #     login_info = check_user_login(current_member) 

    #     if login_info['status'] == False: #Catch for non approved users. #point of entry to AI use
    #         return "Sorry You don't have access to this bot! Please use /login to login and gain access to this bot!"
        
    #     response = get_message(update, processed)
    #     log_query(login_info["status"], processed, response)
    #     print(login_info["status"], processed, response)
    

    login_info = check_user_login(current_member) 

    if login_info['status'] == False: #Catch for non approved users. #point of entry to AI use
            return "Sorry You don't have access to this bot! Please use /login to login and gain access to this bot!"

 
    response = get_message(update, processed)
    log_query(login_info["status"], processed, response)
    print(login_info["status"], processed, response)

    return response
    

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

   #Conversations ----------------------------------------------------------------------------------------------------
    admin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('admin',admin)],
        states={
            LOGIN: [MessageHandler(filters.TEXT, admin_login)],
            FUNCTION: [MessageHandler(filters.TEXT, admin_function)],
            DATE: [MessageHandler(filters.TEXT, admin_date)],
            INTAKE: [MessageHandler(filters.TEXT, admin_intake)],
            DEF: [MessageHandler(filters.TEXT, admin_def_update)],
            UPDATE: [MessageHandler(filters.TEXT, admin_update)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(admin_conv_handler)

    rec_login_handler = ConversationHandler(
        entry_points=[CommandHandler('login',login)],
        states={
            USERNRIC: [MessageHandler(filters.TEXT, usernric)],
            USERPASS: [MessageHandler(filters.TEXT, userpass)],
            UPDATEPASS: [MessageHandler(filters.TEXT, userupdate)],
            
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(rec_login_handler)

    #Commands ----------------------------------------------------------------------------------------------------
    app.add_handler(CommandHandler('start',start_command))
    app.add_handler(CommandHandler('help',help_command))
    app.add_handler(CommandHandler('upcoming',upcoming_command))
    app.add_handler(CommandHandler('cancel',cancel))

    #Messages ----------------------------------------------------------------------------------------------------
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors ----------------------------------------------------------------------------------------------------
    app.add_error_handler(error_handler)

    print("Polling...")
    app.run_polling(poll_interval=3) 
