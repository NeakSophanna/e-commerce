from datetime import datetime

from extensions import db

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128),nullable=False)
    email = db.Column(db.String(128),nullable=False)
    password = db.Column(db.String(128),nullable=False)
    profile = db.Column(db.String(128),nullable=True)
    registered_date=db.Column(db.DateTime,default=datetime.now)