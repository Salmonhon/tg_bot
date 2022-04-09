from conf import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(), nullable=True)
    file_name = db.Column(db.String(), nullable=True, unique=True)
    date = db.Column(db.DateTime, default=datetime.today)

