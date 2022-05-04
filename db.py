from conf import db, app
from datetime import datetime
from flask_msearch import Search
search = Search(db=db)
search.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)

class File(db.Model):
    __searchable__ = ['file_name']

    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(), nullable=True)
    file_name = db.Column(db.String(), nullable=True, unique=True)
    date = db.Column(db.DateTime, default=datetime.today)


