from flask import render_template, redirect, url_for, g, jsonify
from extensions import jwt_admin
from . import admin_bp
from models import Category,Customer,Product,User,Order
from helpers.dashboard import get_recent_orders,total_revenue,new_customer_this_month,low_stock_products

@jwt_admin.unauthorized_loader
def admin_unauthorized_callback(callback):
    return redirect(url_for('auth_bp.login_page'))
@admin_bp.route('')
@admin_bp.route('/dashboard')
def dashboard():
    return render_template("admin/dashboard/index.html",module="dashboard",user=g.current_user)
@admin_bp.get("/dashboard/list")
def list():
    category_count = Category.query.count()
    product_count = Product.query.count()
    customer_count = Customer.query.count()
    user_count = User.query.count()
    total_order = Order.query.count()
    recent_orders = get_recent_orders()
    total_amount = total_revenue()
    new_customer = new_customer_this_month()
    low_stock = low_stock_products()
    return jsonify({
        "category_count": category_count,
        "product_count": product_count,
        "customer_count": customer_count,
        "user_count": user_count,
        "total_revenue": total_amount,
        "total_order": total_order,
        "low_stock_product": low_stock,
        "new_customer_this_month":new_customer,
        "recent_orders": recent_orders
    })
