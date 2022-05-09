from conf import db
from datetime import datetime




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    author_files = db.relationship('File', backref='user', lazy=True)


class File(db.Model):


    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(), nullable=True)
    file_name = db.Column(db.String(), nullable=True, unique=True)
    date = db.Column(db.DateTime, default=datetime.today)
    main_text = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return 'id:{}, file_path:{}, file_name:{}, date:{},user_id:{}'.format(self.id, self.file_path, self.file_name, self.date, self.user_id)