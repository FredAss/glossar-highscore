from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/knut/glossar-highscore-angular/test.db'
db = SQLAlchemy(app)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    score = db.Column(db.Integer)
    time = db.Column(db.Float)
    datetime = db.Column(db.DateTime)

    def __init__(self, name, score, time):
        self.name = name
        self.time = time
        self.score = score
        self.datetime = datetime.now()

    def __repr__(self):
        return '<Entry %r>' % self.name

    def to_json(self):
        return {"name": self.name,
                "score": self.score,
                "time": self.time,
                "datetime": self.datetime.isoformat()
                }
