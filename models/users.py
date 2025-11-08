from extensions import db
from datetime import datetime
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    email = db.Column(db.String(128))
    password = db.Column(db.String(128))
    gender = db.Column(db.String(128),default ="male")
    profile = db.Column(db.String(128),nullable=True)
    registered_date = db.Column(db.DateTime, default=datetime.now)