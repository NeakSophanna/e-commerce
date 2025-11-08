from models.order import Order
from models.customer import Customer
from models.product import Product
from extensions import db
from sqlalchemy import func,extract
from datetime import datetime
def get_recent_orders():
    recent_order = Order.query.order_by(Order.order_at.desc()).limit(6).all()
    if not recent_order:
        return []
    return [
        {
            "customer_name":order.customer.username,
            "total":order.total_amount,
            "payment_method":order.payment_method,
            "status": order.status
        }for order in recent_order
    ]
def total_revenue():
    return db.session.query(func.sum(Order.total_amount)).scalar() or 0
def new_customer_this_month():
    current_month = datetime.now().month
    current_year = datetime.now().year
    new_customers = Customer.query.filter(
        extract('month', Customer.registered_date) == current_month,
        extract('year', Customer.registered_date) == current_year
    ).count()
    return new_customers
def low_stock_products():
    low_stock = Product.query.filter(Product.stock <5).count()
    return low_stock
