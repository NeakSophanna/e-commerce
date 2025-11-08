from flask import url_for, render_template, g, jsonify,request
from werkzeug.utils import redirect, secure_filename
from models.users import User
from . import admin_bp
from extensions import jwt_admin, bcrypt,db
from helpers.user import fetchUser,validate_user,validate_gmail,username_exist_and_id_not,email_exist_and_id_not
import os,uuid

@jwt_admin.unauthorized_loader
def admin_unauthorized_callback(callback):
    return redirect(url_for('auth_bp.login_page'))
@admin_bp.route("/user",methods=["GET"])
def user():
    return render_template("admin/user/index.html",module="user",user=g.current_user)
@admin_bp.get("/user/list")
def user_list():
    users = fetchUser()
    return jsonify({"users":users})
@admin_bp.post("/user/add")
def add_user():
    filename = None
    form = request.form
    error, status = validate_user(form)
    if error:
        return jsonify(error), status

    file = request.files.get('profile')
    if file:
        UPLOAD_DIR=os.path.join("static/image","user")
        os.makedirs(UPLOAD_DIR,exist_ok=True)
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        filename = unique_filename
        file.save(os.path.join(UPLOAD_DIR,filename))
    hashed_pw = bcrypt.generate_password_hash(form.get('password')).decode('utf-8')
    user = User(
        username = form.get('username'),
        email = form.get('email'),
        password = hashed_pw,
        gender=form.get('gender'),
        profile = filename
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201
@admin_bp.post("/user/delete")
def delete_user():
    user_id = request.json.get('user_id')
    image = request.json.get('profile')
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        if image:
            image_path = os.path.join("static/image", 'user', image)
            if os.path.exists(image_path):
                os.remove(image_path)
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"message":"User not found"}),404
@admin_bp.post("/user/update")
def update_user():
    filename = None
    form = request.form
    user = User.query.get(form.get('id'))
    if user:
        current_id = int(form.get('id'))
        error, status = validate_gmail(form)
        if error:
            return jsonify(error), status
        if username_exist_and_id_not(form.get('username'), current_id):
            return jsonify({"message": "Username already existed"}), 409

        if email_exist_and_id_not(form.get('email'), current_id):
            return jsonify({"message": "Email already existed"}), 409
        file = request.files.get('profile')
        if file:
            old_image_path = form.get('old_profile')
            image_path = os.path.join("static/image", 'user', old_image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
            UPLOAD_DIR=os.path.join("static/image","user")
            os.makedirs(UPLOAD_DIR,exist_ok=True)
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{original_filename}"
            filename = unique_filename
            file.save(os.path.join(UPLOAD_DIR,filename))
        user.username = form.get('username')
        user.email = form.get('email')
        user.gender = form.get('gender')
        if filename:
            user.profile = filename
        if form.get('password'):
            hashed_pw = bcrypt.generate_password_hash(form.get('password')).decode('utf-8')
            user.password=hashed_pw
        db.session.commit()
        return jsonify({"message": "User updated"}), 200
    return jsonify({"message": "User not found"}), 404