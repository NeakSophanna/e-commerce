from extensions import jwt_admin
from flask import redirect, url_for, render_template, g, jsonify
from . import admin_bp
from models.order import Order
from helpers.order_management import fetchOrder
@jwt_admin.unauthorized_loader
def admin_unauthorized_callback(callback):
    return redirect(url_for('auth_bp.login_page'))
@admin_bp.route("/order",methods=["GET"])
def order():
    return render_template("admin/order/index.html",module="order",user=g.current_user)
@admin_bp.get("/order/list")
def order_list():
    order_list = fetchOrder()
    return jsonify({"orders":order_list})
@admin_bp.get("/order/<int:id>")
def order_detail(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({"message":"Order not found"}),404
    return jsonify({
        "id":order.id,
        "customer_name":order.customer.username,
        "total":float(order.total_amount),
        "payment_method":order.payment_method,
        "status":order.status,
        "order_at":order.order_at.strftime("%Y-%m-%d %H:%M"),
        "items": [
            {
                "id":i.id,
                "product_name":i.product.name,
                "quantity":i.quantity,
                "price": float(i.price)
            }for i in order.items
        ]
    })