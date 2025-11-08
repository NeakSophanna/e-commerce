from flask import url_for, render_template, g, jsonify,request
from werkzeug.utils import redirect, secure_filename
from models import Customer
from . import admin_bp
from extensions import jwt_admin, bcrypt,db
from helpers.customer import fetchCustomer,validate_gmail,username_exist_and_id_not,email_exist_and_id_not,validate_customer
import os,uuid

@jwt_admin.unauthorized_loader
def admin_unauthorized_callback(callback):
    return redirect(url_for('auth_bp.login_page'))
@admin_bp.route("/customer",methods=["GET"])
def customer():
    return render_template("admin/customer/index.html",module="customer",user=g.current_user)

@admin_bp.get("/customer/list")
def customer_list():
    customers = fetchCustomer()
    return jsonify({"customers":customers})
@admin_bp.post("/customer/add")
def add_customer():
    filename = None
    form = request.form
    error, status = validate_customer(form)
    if error:
        return jsonify(error), status

    file = request.files.get('profile')
    if file:
        UPLOAD_DIR=os.path.join("static/image","customer")
        os.makedirs(UPLOAD_DIR,exist_ok=True)
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        filename = unique_filename
        file.save(os.path.join(UPLOAD_DIR,filename))
    hashed_pw = bcrypt.generate_password_hash(form.get('password')).decode('utf-8')
    customer = Customer(
        username = form.get('username'),
        email = form.get('email'),
        password = hashed_pw,
        profile = filename
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({"message": "Customer created"}), 201

@admin_bp.post("/customer/delete")
def delete_customer():
    customer_id = request.json.get('customer_id')
    image = request.json.get('profile')
    customer = Customer.query.get(customer_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        if image:
            image_path = os.path.join("static/image", 'customer', image)
            if os.path.exists(image_path):
                os.remove(image_path)
        return jsonify({"message": "Customer deleted"}), 200
    return jsonify({"message":"Customer not found"}),404
@admin_bp.post("/customer/update")
def update_customer():
    filename = None
    form = request.form
    customer = Customer.query.get(form.get('id'))
    current_id = int(form.get('id'))
    error, status = validate_gmail(form)
    if error:
        return jsonify(error), status
    if username_exist_and_id_not(form.get('username'), current_id):
        return jsonify({"message": "Username already existed"}), 409

    if email_exist_and_id_not(form.get('email'), current_id):
        return jsonify({"message": "Email already existed"}), 409
    file = request.files.get('profile')
    if customer:
        if file:
            old_image_path = form.get('old_profile')
            image_path = os.path.join("static/image", 'customer', old_image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
            UPLOAD_DIR=os.path.join("static/image","customer")
            os.makedirs(UPLOAD_DIR,exist_ok=True)
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{original_filename}"
            filename = unique_filename
            file.save(os.path.join(UPLOAD_DIR,filename))
        customer.username = form.get('username')
        customer.email = form.get('email')
        if filename:
            customer.profile = filename
        if form.get('password'):
            hashed_pw = bcrypt.generate_password_hash(form.get('password')).decode('utf-8')
            customer.password=hashed_pw
        db.session.commit()
        return jsonify({"message": "Customer updated"}), 200
    return jsonify({"message": "Customer not found"}), 404