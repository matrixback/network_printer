# coding: utf-8

from ext import db
from datetime import datetime

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    size = db.Column(db.Integer)
    ctime = db.Column(db.DateTime, nullable=False)


    def __init__(self, name=None, alias=None,size=None, ctime=None):
        self.ctime = datetime.now()
        self.name = name
        self.size = size
        self.alias = alias

    def __repr__(self):
        return "<File: %s>" % self.name

class Text(db.Model):
    __tablename__ = 'texts'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    def __init__(self, content=None):
        self.content = content

    def __repr__(self):
        return "<text: %s>" % self.content