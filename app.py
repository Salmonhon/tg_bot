
import telebot
import os
from db import User, File
from PyPDF2 import PdfFileReader
from conf import app, db, mail
import random
import imaplib
import email
import traceback
from telebot import types
from fuzzywuzzy import fuzz, process

random = random.randint(0,999999)

bot = telebot.TeleBot("5141677130:AAG7DC7yQ9KSLzsMo9bL8Lph8B2vLiAcUzI")

# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------
# there you define your email
ORG_EMAIL = "@gmail.com"
FROM_EMAIL = "medforum039" + ORG_EMAIL
FROM_PWD = "plzmqtfxrrrcrftq"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993
# this method for getting files from email
@bot.message_handler(commands=['refresh'])
def read_email_from_gmail(message):
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)
        mail.select('inbox')

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        flag = True
        bot.send_message(message.chat.id, "<i>Please wait ...</i>", parse_mode='html')
        for i in range(latest_email_id,first_email_id, -1):
            data = mail.fetch(str(i), '(RFC822)' )
            for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    msg = email.message_from_string(str(arr[1],'utf-8'))
                    for i in msg.walk():
                        if i.get_content_maintype() == 'multipart':
                            continue
                        if i.get('Content-Disposition') is None:
                            continue
                        file = i.get_filename()

                        if bool(file):

                            filepath = os.path.join('files/', str(random)+file)
                            if not os.path.isfile(filepath):
                                info = File.query.filter_by(file_name=file).first()
                                if info:
                                   flag = False
                                else:

                                    fp = open(filepath,'wb')
                                    fp.write(i.get_payload(decode=True))
                                    fp.close()
                                    text = reader(file,filepath)
                                    file = File(file_path=filepath, file_name=file, main_text=text, user_id="1")
                                    db.session.add(file)
                                    db.session.commit()
                                    flag = True
        if flag:
            bot.send_message(message.chat.id, "<b>You have new file</b>", parse_mode='html')
        else:
            bot.send_message(message.chat.id, "<b>Nothing new</b>", parse_mode='html')
    except Exception as e:
        traceback.print_exc()
        print(str(e))


#method for reading pdf 
def pdf_reader(file):
    pdf_document = file
    with open(pdf_document, "rb") as filehandle:
        pdf = PdfFileReader(filehandle)
        for i in range(1):
            page = pdf.getPage(i)
            text = page.extractText()
            f = open("first_pages/{}.txt".format(random), "w+")
            f.write(text)

    return f.name



#method for definding type of file u should improve it ))

def reader(file , file_path):
    file_name, file_extension = os.path.splitext(file)
    if file_extension == '.pdf':
        return pdf_reader(file_path)
    elif file_extension == '.txt':
        return "TXT file"
    elif file_extension == ".docx":
        return "for word file it will be paid"
    else:
        return "Dont get this type of file"
@bot.message_handler(commands=['start'])
@app.before_first_request
def start(message):
    db.create_all()

    author = User.query.filter_by(user_id=message.chat.id).first()
    if author:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("/refresh")
        btn2 = types.KeyboardButton("/search")
        btn3 = types.KeyboardButton("/stop_search")
        btn4 = types.KeyboardButton("/document")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, "Dont start again you are already registred", reply_markup=markup)
    else:
        name = f'Hello, <b>{message.from_user.first_name}</b> '
        bot.send_message(message.chat.id, name, parse_mode='html')
        new_user = User(user_id = message.chat.id)
        db.session.add(new_user)
        db.session.commit()


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    bot.send_message(message.chat.id, "Document is gotten ", parse_mode='html')
    file_name, file_extension = os.path.splitext(message.document.file_name)

    info = File.query.filter_by(file_name=file_name).first()
    if info:
        bot.send_message(message.chat.id, "This file is already exist", parse_mode='html')
    else:

        file_info = bot.get_file(message.document.file_id)
        download_file = bot.download_file(file_info.file_path)
        src = 'files/' + message.document.file_unique_id + message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(download_file)

        bot.send_message(message.chat.id, "Your file is saved", parse_mode='html')
        file = File(file_path=src, file_name=file_name)
        db.session.add(file)
        db.session.commit()

#method for searching from first pages 
def full_text_search(source, input):
    try:
        with open(source, 'r') as f:
            f = f.read().split()
            result = process.extract(input, f, limit=1)
            print("Source-",source)
            print(result)
        return result
    except:
        result = [(0, 0)]
        return result
@bot.message_handler(commands=['search'])
def handle_docs(message):
    bot.send_message(message.chat.id, "Write your file name ", parse_mode='html')
    if 'search':
        @bot.message_handler(content_types=['text'])
        def handle_docs(message):
            file_name = File.query.filter_by(file_name=message.text).first()

            if file_name:

                file = open(file_name.file_path, 'rb')
                bot.send_message(message.chat.id, file_name.date, parse_mode='html')
                bot.send_document(message.chat.id, file)
            elif not file_name:
                files = User.query.filter_by(id="1").first()
                for i in files.author_files:
                    searched = fuzz.token_sort_ratio(i.file_name, message.text)
                    print(searched)
                    if searched > 50:
                        file = open(i.file_path, 'rb')
                        bot.send_document(message.chat.id, file)
                    # if u uncommit this code u can use search in first pages but thereis some bug please fix it by yourself )) i dont have time 
                    # else:
                    #     score = full_text_search(i.main_text, message.text)
                    #     if score[0][1]>50:
                    #         file = open(i.file_path, 'rb')
                    #         bot.send_document(message.chat.id, file)

            else:
                bot.send_message(message.chat.id, "<b>Failed dont have this file</b>", parse_mode='html')


@bot.message_handler(commands=['stop_search'])
def handle_docs(message):
    bot.send_message(message.chat.id, "Ok", parse_mode='html')




@bot.message_handler(commands=['all'])
def show_all(message):
    file_path = "files/"

    bot.send_message(message.chat.id, "All file what we have on database", parse_mode='html')
    bot.send_message(message.chat.id, "Please wait end of process", parse_mode='html')
    for name in os.listdir('files'):

        file = open(file_path+name, 'rb')
        bot.send_document(message.chat.id, file)
    bot.send_message(message.chat.id, "Process is ended", parse_mode='html')



bot.polling(none_stop=True)


