import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import filters, MessageHandler,CommandHandler, ContextTypes,Application
from database import add_to_db, has_hit_limit, reset_user_record,MAX_BULLYING_MESSAGES


#maximum number of bullying_messages
NO_BANNED_DAYS=3
TOKEN=""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


import mindsdb_sdk
import pandas as pd
server = mindsdb_sdk.connect('https://cloud.mindsdb.com', login='salimonyinlola@outlook.com', password='Qwerty12345')
project = server.get_project("mindsdb")
model = project.list_models()[0] #Selecting the model to use. The index 0 is used because this is the first model in the list of models on the account

#check if text is cyberbullying
def is_cyberbullying(text):
    text = {text}
    result = pd.DataFrame(text)
    if model.predict(result)["oh_label"].loc[0] == 1:
        return True 
    else: 
        return False

#start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Give a simple explanation of what the bot 
        does"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"This is a cyber bullying bot. In a bid to kick against cyberbullying, I will help you remove users who engage in cyber-bullying on your group chats\nWondering how to use?\nAdd me as an admin to your group chat and give me permission to remove users, send and delete messages.  With this, users are given {MAX_BULLYING_MESSAGES} lifelines. If a user has sent up to {MAX_BULLYING_MESSAGES} messages recognized as cyberbullying, I will see to the user being removed and banned for {NO_BANNED_DAYS} days!"
    )

#cyberbullying handler
async def remove_cyberbullying(update: Update, context: ContextTypes.DEFAULT_TYPE):
   chat_id=update.effective_chat.id
   message=update.message
   sender_id=message.from_user.id
   if is_cyberbullying(message.text):
       add_to_db(sender_id,chat_id)

       #if user has hit limit
       if has_hit_limit(sender_id,chat_id):
           #current date
           current_date=datetime.now()
           ban_duration=timedelta(days=NO_BANNED_DAYS)
           unban_date=current_date+ban_duration

           #reset record
           reset_user_record(sender_id,chat_id)

           #remove user 
           await context.bot.send_message(chat_id=update.effective_chat.id, text=f"The message you sent in is ABUSIVE. Since you have exceeded the cyberbullying limit, you'll be banned from the group chat for {NO_BANNED_DAYS} days!!",reply_to_message_id=message.message_id)

           await context.bot.ban_chat_member(chat_id=chat_id,user_id=sender_id, revoke_messages=False, until_date=unban_date)

       else:
           #send a message that the person has sent an abusive message 
           await context.bot.send_message(chat_id=update.effective_chat.id, text="The message you've sent in is ABUSIVE. We strongly advise you to reconsider your actions and engage in conversations that are supportive and kind. You are advised to be careful and adhere with the guidelines. Else, you'll be removed from the group chat soon!",reply_to_message_id=message.message_id)

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    start_handler = CommandHandler("start", start, filters=~filters.ChatType.GROUPS)
    cyberbullying_handler = MessageHandler(filters.TEXT & filters.ChatType.GROUPS , remove_cyberbullying) #filters.TEXT & filters.ChatType.GROUPS tells us we want only text messages from group chats 
    application.add_handler(start_handler)
    application.add_handler(cyberbullying_handler)
    application.run_polling()
