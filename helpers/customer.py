import re
from models.customer import Customer

def fetchCustomer():
    customers = Customer.query.all()
    if customers:
        return[
            {
                "id":customer.id,
                "username":customer.username,
                "email":customer.email,
                "profile":customer.profile,
                "registered_date":customer.registered_date.strftime("%d/%m/%Y")
            }for customer in customers
        ]
    return []

def validate_customer(form):
    email = form.get("email")
    username = form.get("username")
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        return {"message": "Invalid email format"}, 400
    if Customer.query.filter_by(username=username).first():
        return {"message": "Username already existed"}, 409

    if Customer.query.filter_by(email=email).first():
        return {"message": "Email already existed"}, 409
    return None,None

def validate_gmail(form):
    email = form.get("email")
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        return {"message": "Invalid email format"}, 400
    return None,None
def username_exist_and_id_not(username, exclude_id=None):
    q = Customer.query.filter(Customer.username == username)
    if exclude_id:
        q = q.filter(Customer.id != exclude_id)
    return q.first() is not None

def email_exist_and_id_not(email, exclude_id=None):
    q = Customer.query.filter(Customer.email == email)
    if exclude_id:
        q = q.filter(Customer.id != exclude_id)
    return q.first() is not None