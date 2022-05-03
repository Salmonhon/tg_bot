import telebot
import imaplib
import email
import traceback
import os
from flask_mail import  Message
from db import User, File
from PyPDF2 import PdfFileReader
from conf import app, db, mail
import random
import imaplib
import email
import traceback
from os import listdir
from os.path import isfile, join
random = random.randint(0,999999)

bot = telebot.TeleBot("5141677130:AAG7DC7yQ9KSLzsMo9bL8Lph8B2vLiAcUzI")

# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------
ORG_EMAIL = "@gmail.com"
FROM_EMAIL = "medforum039" + ORG_EMAIL
FROM_PWD = "plzmqtfxrrrcrftq"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993

def read_email_from_gmail():
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)
        mail.select('inbox')

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

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
                                fp=open(filepath,'wb')
                                fp.write(i.get_payload(decode=True))
                                fp.close()
                                file = File(file_path=filepath, file_name=file)
                                try:
                                    db.session.add(file)
                                    db.session.commit()
                                except:
                                    print("This file already exist")

    except Exception as e:
        traceback.print_exc()
        print(str(e))

read_email_from_gmail()
read_email_from_gmail()

def pdf_reader(file):
    pdf_document = file
    with open(pdf_document, "rb") as filehandle:
        pdf = PdfFileReader(filehandle)

        info = pdf.getDocumentInfo()
        pages = pdf.getNumPages()
        print("Количество страниц в документе: %i\n\n" % pages)
        print("Мета-описание: ", info)

        for i in range(pages):
            page = pdf.getPage(i)
            print(page.extractText())


def reader(file):
    file_name, file_extension = os.path.splitext(file.file_name)
    if file_extension == '.pdf':
        pdf_reader(file)
    elif file_extension == '.txt':
        pass


@bot.message_handler(commands=['start'])
@app.before_first_request
def start(message):
    db.create_all()

    author = User.query.filter_by(user_id=message.chat.id).first()
    if author:
        bot.send_message(message.chat.id, "Dont start again you are already registred", parse_mode='html')
        with app.app_context():
            msg = Message(subject="Hello",
                          sender=app.config.get("MAIL_USERNAME"),
                          recipients=["is.salmonforsi@gmail.com"],  # replace with your email for testing
                          body="This is a test email I sent with Gmail and Python!")
            mail.send(msg)
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

            else:
                bot.send_message(message.chat.id, "<b>Failed dont have this file</b>", parse_mode='html')


@bot.message_handler(commands=['stop'])
def handle_docs(message):
    bot.send_message(message.chat.id, "Goood ", parse_mode='html')




@bot.message_handler(commands=['all'])
def show_all(message):
    file_path = "files/"

    bot.send_message(message.chat.id, "All file what we have on database", parse_mode='html')
    bot.send_message(message.chat.id, "Please wait end of process", parse_mode='html')
    for name in os.listdir('files'):

        file = open(file_path+name, 'rb')
        bot.send_document(message.chat.id, file)
    bot.send_message(message.chat.id, "Process is ended", parse_mode='html')


# @bot.message_handler(commands=['read'])
# def handle_docs(message):
#     bot.send_message(message.chat.id, "Write your file name ", parse_mode='html')
#     if 'read':
#         @bot.message_handler(content_types=['text'])
#         def handle_docs(message):
#             file_name = File.query.filter_by(file_name=message.text).first()
#             if file_name:
#                 pdf_document = file_name.file_path
#                 with open(pdf_document, "rb") as filehandle:
#                     pdf = PdfFileReader(filehandle)
#
#                     info = pdf.getDocumentInfo()
#                     pages = pdf.getNumPages()
#                     bot.send_message(message.chat.id, 'Number of pages '+str(pages), parse_mode='html')
#
#
#                     for i in range(pages):
#                         page = pdf.getPage(i)
#                         bot.send_message(message.chat.id, page.extractText(), parse_mode='html')
#
#             else:
#                 bot.send_message(message.chat.id, "<b>Failed dont have this file</b>", parse_mode='html')


bot.polling(none_stop=True)


