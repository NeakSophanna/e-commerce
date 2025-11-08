from flask import render_template,request,Blueprint,redirect,url_for,jsonify,g
from flask_jwt_extended import get_jwt_identity
import os,uuid

from werkzeug.utils import secure_filename

from helpers.main import send_order_to_telegram,send_mail_to_customer,prepare_invoice_message_to_telegram,insert_to_db
from helpers.product import fetchProduct,get_product_by_id
from models import Customer,Order,OrderItem
from product import products
from extensions import jwt_customer, db, bcrypt
from . import customer_bp


home_bp=Blueprint('home_bp',__name__)

@jwt_customer.unauthorized_loader
def customer_unauthorized_callback(callback):
    return redirect(url_for('cust_bp.login_page_for_customer'))

@customer_bp.get("/auth/check")
def auth_check():
    if g.current_customer:
        return jsonify({"logged_in": True}), 200
    return jsonify({"logged_in": False}), 401
@home_bp.route("/")
def index():
    return render_template("index.html", products=products)

@home_bp.route("/contact")
def contact():
    return render_template("contact.html")

@home_bp.route("/about")
def about():
    return render_template("about.html")

@customer_bp.route("/cart")
def cart():
    return render_template("cart.html")

@customer_bp.route("/checkout")
def checkOut():
    return render_template("checkout.html")

@home_bp.get("/product/list")
def productList():
    return fetchProduct()

@home_bp.route("/product")
def product_detail():
    pro_id = request.args.get('pro_id',type=int)
    product = get_product_by_id(pro_id)
    return render_template("detail.html", product=product)


@customer_bp.route("/placeOrder", methods=['POST'])
def placeOrder():

    data = request.get_json()
    send_mail_to_customer(data)
    message = prepare_invoice_message_to_telegram(data)
    send_order_to_telegram(message)
    order_id = insert_to_db(data)
    return "Invoice Sent!\n Thank you for your order."
@customer_bp.get("/me")
def get_current_customer():
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"message":"Customer not found"}),404
    return {
        "id":customer.id,
        "username":customer.username,
        "email":customer.email,
        "profile":customer.profile if customer.profile else "no-user-image.png",
        "registered_date":customer.registered_date
    }
@customer_bp.get("/profile")
def profile_page():
    return render_template("profile.html")

@customer_bp.post("/update-profile")
def update_profile():
    filename = None
    form = request.form
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"message":"Customer not found"}),404
    file = request.files.get('profile')
    username = form.get('username')
    if username in (None, 'null', ''):
        username = None
    if username:
        customer.username = form.get('username')
    if file:
        old_image_path = form.get('old_profile')
        image_path = os.path.join('static/image','customer',old_image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
        UPLOAD_DIR = os.path.join('static/image','customer')
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        filename = unique_filename
        file.save(os.path.join(UPLOAD_DIR, filename))
        customer.profile = filename
    db.session.commit()
    return jsonify({"message":"Customer update successfully"}),200
@customer_bp.post("/update-password")
def update_password():
    current_password = request.get_json().get('current_password')
    new_password = request.get_json().get('new_password')
    customer_id = request.get_json().get('id')
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"message":"Customer not found"}),404
    if bcrypt.check_password_hash(customer.password, current_password):
        customer.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        return jsonify({"message":"Password Updated"}),200
    return jsonify({"message":"Incorrect Password!"}),404
@customer_bp.get("/order-history")
def order_history():
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"message":"Customer not found"}),404
    orders = Order.query.filter_by(customer_id=customer.id).all()
    order_list = []
    if orders:
        order_list = [
            {
                "id": order.id,
                "customer_name": order.customer.username,
                "total": order.total_amount,
                "payment_method": order.payment_method,
                "status": order.status,
                "order_at": order.order_at.strftime("%d/%m/%Y %H:%M")
            } for order in orders
        ]
    return jsonify({"orders":order_list})

@customer_bp.get("/order_detail/<int:id>")
def order_detail(id):
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({"message":"Order not found"}),404
        return jsonify(
            {
                "order_id":id,
                "customer_name":order.customer.username,
                "payment_method":order.payment_method,
                "status":order.status,
                "order_at":order.order_at.strftime("%d/%m/%Y %H:%M"),
                "total": float(order.total_amount),
                "items":[
                    {
                        "id":item.id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "price": float(item.price)
                    }for item in order.items
                ]
            }
        )
    except Exception as e:
        print(e)
        return None