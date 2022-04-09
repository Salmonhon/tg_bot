import telebot
import os
import docx
from db import User, File
from PyPDF2 import PdfFileReader
from conf import app, db


bot = telebot.TeleBot("5141677130:AAG7DC7yQ9KSLzsMo9bL8Lph8B2vLiAcUzI")

def getText(filename):
    doc = docx.opendocx(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return fullText
print(getText('2.docx'))

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


