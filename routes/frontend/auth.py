import requests
from flask import request, jsonify, Blueprint, render_template, make_response, url_for, current_app, session
from models.customer import Customer
from extensions import bcrypt,db,mail
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from werkzeug.utils import redirect
import re,random,os
from flask_mail import Message
from datetime import datetime,timedelta
from dotenv import load_dotenv
load_dotenv()

cust_bp = Blueprint("cust_bp", __name__)

@cust_bp.get("/login")
def login_page_for_customer():
    return render_template("auth/login.html")

@cust_bp.get("/register")
def register_page_for_customer():
    return render_template("auth/register.html")
@cust_bp.get("/forgot-password")
def forgot_password_page():
    return render_template("auth/forgot_password.html")
@cust_bp.post("/register")
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']

    if Customer.query.filter_by(username=username).first():
        return jsonify({"message": "Name already existed"}), 409
    if not session.get('email_verified'):
        return jsonify({'message': 'Please verify your email first.'}),403


    customer = Customer(
        username=username,
        email=email,
        password=bcrypt.generate_password_hash(password).decode('utf-8')
    )
    db.session.add(customer)
    db.session.commit()
    session.pop('otp',None)
    session.pop('email_verified',None)
    session.pop('otp_expiry', None)
    return jsonify({"message": "Registration successful."}), 201

@cust_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        return {"message": "Invalid email format"}, 400
    customer = Customer.query.filter_by(email=email).first()
    if not customer or not bcrypt.check_password_hash(customer.password, password):
        return jsonify({"message":"Invalid email or password"}),401
    token = create_access_token(identity=str(customer.id))
    resp = make_response(jsonify({"login":True}))
    current_app.config["JWT_ACCESS_COOKIE_NAME"] = "customer_access_token"
    set_access_cookies(resp, token)
    return resp

@cust_bp.get("/logout")
def logout():
    response = redirect(url_for("cust_bp.login_page_for_customer"))
    unset_jwt_cookies(response)
    return response

def send_mail(to_email,subject,otp):
    """SEND MAIL USING BREVO API"""
    try:
        api_key= os.getenv("BREVO_API_KEY")
        from_email = os.getenv("FROM_EMAIL")
        api_endpoint = os.getenv("BREVO_API_ENDPOINT")
        html_body = render_template("otp_email.html", otp=otp)
        response = requests.post(
            api_endpoint,
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json={
                "sender": {"email": from_email, "name": "Pav Pav Fashion"},
                "to":[{"email":to_email}],
                "subject": subject,
                "htmlContent": html_body,
            },
            timeout=10,
        )
        if response.status_code not in(200,201):
            print("❌ Brevo error:", response.text)
            return response

        return response
    except Exception as e:
        print("💥 Email send failed:", e)
        return False
@cust_bp.post("/sent-otp")
def send_otp():
    email = request.json.get("email")
    if Customer.query.filter_by(email=email).first():
        return jsonify({"message": "Email already existed"}), 409
    otp = str(random.randint(100000, 999999))

    session['otp'] = otp
    session['email'] = email
    session['otp_expiry'] = (datetime.utcnow() + timedelta(minutes=5)).timestamp()
    response = send_mail(
        email,
        "Verify your email",
        otp
    )
    if response.status_code==201:
        return jsonify({"message": "OTP sent successfully", "otp": otp}), 200
    else:
        return jsonify({
            "error": "Failed to send OTP",
            "details": response.text
        }), 500
@cust_bp.post("/sent-reset-otp")
def send_reset_otp():
    email = request.json.get("email")
    if not Customer.query.filter_by(email=email).first():
        return jsonify({"message": "Email not found"}), 404
    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['email'] = email
    session['otp_expiry'] = (datetime.utcnow() + timedelta(minutes=5)).timestamp()
    msg = Message(
        subject='Email Verification - Pav E-Commerce',
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[email]
    )
    msg.html = render_template("otp_email.html",otp=otp)
    try:
        mail.send(msg)
        return jsonify({'message': 'Verification code sent successfully'})
    except Exception as e:
        current_app.logger.error(f"Mail send error: {e}")
        return jsonify({'message': f'Failed to send email: {str(e)}'}), 500

@cust_bp.post("/verify-otp")
def verify_otp():
    user_otp = request.json.get("otp")
    if 'otp_expiry' not in session or datetime.utcnow().timestamp() > session['otp_expiry']:
        return jsonify({'message': 'OTP expired'}), 400
    if user_otp == session.get('otp'):
        session['email_verified'] = True
        return jsonify({"message": "Email verified successfully"}), 200
    return jsonify({"message": "Invalid Verification Code"}), 400
@cust_bp.post("/verify-reset-otp")
def verify_reset_otp():
    user_otp = request.json.get("otp")
    if 'otp_expiry' not in session or datetime.utcnow().timestamp() > session['otp_expiry']:
        return jsonify({'message': 'OTP expired'}), 400
    if user_otp == session.get('otp'):
        session['email_verified'] = True
        return jsonify({"message": "Email verified successfully"}), 200
    return jsonify({"message": "Invalid Verification Code"}), 400

@cust_bp.post("/reset-password")
def reset_password():
    email = request.json.get("email")
    password = request.json.get("password")
    customer = Customer.query.filter_by(email=email).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    customer.password = bcrypt.generate_password_hash(password).decode('utf-8')
    db.session.commit()
    return jsonify({"message": "Password reset successful"}), 200