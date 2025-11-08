import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    #JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=float(os.getenv('JWT_ACCESS_TOKEN_EXPIRES')))
    JWT_ACCESS_COOKIE_NAME='access_token_default'
    JWT_TOKEN_LOCATION=['cookies']
    JWT_ACCESS_COOKIE_PATH ='/'
    JWT_COOKIE_SECURE=False
    JWT_COOKIE_CSRF_PROTECT=False
    JWT_COOKIE_HTTPONLY=True
    # ============ Admin JWT ============
    JWT_ADMIN_SECRET_KEY = os.getenv('JWT_ADMIN_SECRET_KEY')
    JWT_ADMIN_ACCESS_TOKEN_EXPIRES = timedelta(minutes=float(os.getenv('JWT_ADMIN_ACCESS_TOKEN_EXPIRES')))
    JWT_ADMIN_ACCESS_COOKIE_NAME = os.getenv('JWT_ADMIN_ACCESS_COOKIE_NAME')
    JWT_ADMIN_COOKIE_CSRF_PROTECT=False
    # ============ Customer JWT ============
    JWT_CUST_SECRET_KEY = os.getenv('JWT_CUST_SECRET_KEY')
    JWT_CUST_ACCESS_TOKEN_EXPIRES = timedelta(minutes=float(os.getenv('JWT_CUST_ACCESS_TOKEN_EXPIRES')))
    JWT_CUST_ACCESS_COOKIE_NAME = os.getenv('JWT_CUST_ACCESS_COOKIE_NAME')
    JWT_CUST_COOKIE_CSRF_PROTECT=False
    #Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')



