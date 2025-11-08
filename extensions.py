from flask import redirect
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

mail = Mail()
jwt_admin = JWTManager()
jwt_customer = JWTManager()
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

@jwt_admin.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    response = redirect("/admin/login")
    unset_jwt_cookies(response)
    return response
@jwt_customer.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    response = redirect("/admin/login")
    unset_jwt_cookies(response)
    return response