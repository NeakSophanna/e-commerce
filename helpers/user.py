import re
from models.users import User

def fetchUser():
    users = User.query.all()
    if users:
        return[
            {
                "id":user.id,
                "username":user.username,
                "email":user.email,
                "profile":user.profile,
                "gender":user.gender,
                "registered_date":user.registered_date.strftime("%d/%m/%Y")
            }for user in users
        ]
    return []
def validate_user(form):
    email = form.get("email")
    username = form.get("username")
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        return {"message": "Invalid email format"}, 400
    if User.query.filter_by(username=username).first():
        return {"message": "Username already existed"}, 409
    if User.query.filter_by(email=email).first():
        return {"message": "Email already existed"}, 409
    return None,None
def validate_gmail(form):
    email = form.get("email")
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        return {"message": "Invalid email format"}, 400
    return None,None
def username_exist_and_id_not(username, exclude_id=None):
    q = User.query.filter(User.username == username)
    if exclude_id:
        q = q.filter(User.id != exclude_id)
    return q.first() is not None

def email_exist_and_id_not(email, exclude_id=None):
    q = User.query.filter(User.email == email)
    if exclude_id:
        q = q.filter(User.id != exclude_id)
    return q.first() is not None
