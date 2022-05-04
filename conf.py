

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_mail import Mail, Message
import os

app = Flask(__name__)


app.config['SECRET_KEY'] = 'truck'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MSEARCH_INDEX_NAME'] = 'msearch'
# simple,whoosh,elaticsearch, default is simple
app.config['MSEARCH_BACKEND'] = 'whoosh'
# table's primary key if you don't like to use id, or set __msearch_primary_key__ for special model
app.config['MSEARCH_PRIMARY_KEY'] = 'id'
# auto create or update index
app.config['MSEARCH_ENABLE'] = True




mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}

app.config.update(mail_settings)
mail = Mail(app)
db = SQLAlchemy(app)