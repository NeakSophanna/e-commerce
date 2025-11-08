from flask import request, jsonify, Blueprint, render_template, make_response, url_for, current_app
from models.users import User
from extensions import bcrypt
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from werkzeug.utils import redirect

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.get("")
def login_page():
    return render_template("admin/auth/login.html")

@auth_bp.route('/login',methods=['POST'])
def login():
    """
    User Login Endpoint
    ---
    tags:
      - Authentication
    summary: Login to get JWT token
    description: Authenticates a user and returns an access token upon successful login.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              in: formData
              type: string
              required: true
              description: Username
            password:
              in: formData
              type: string
              required: true
              description: User password
    responses:
      200:
        description: Login successful, returns access token
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message":"Invalid username or password"}),401
    token = create_access_token(identity=str(user.id))
    resp = make_response(jsonify({"login":True}))
    current_app.config["JWT_ACCESS_COOKIE_NAME"] = "admin_access_token"
    set_access_cookies(resp, token)
    return resp

@auth_bp.get("/logout")
def logout():
    response = redirect(url_for("auth_bp.login_page"))
    unset_jwt_cookies(response)
    return response