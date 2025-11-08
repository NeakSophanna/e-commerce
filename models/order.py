from datetime import datetime
from extensions import db

class Order(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    customer_id = db.Column(db.Integer,db.ForeignKey("customer.id"),nullable=False)
    total_amount = db.Column(db.Float,nullable=False)
    payment_method = db.Column(db.String(50),nullable=False)
    status = db.Column(db.String(50),default='Pending')
    order_at = db.Column(db.DateTime,default=datetime.now)

    customer = db.relationship("Customer",backref=db.backref("order",lazy=True))
    items = db.relationship("OrderItem",backref="order",lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    order_id = db.Column(db.Integer,db.ForeignKey("order.id"),nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey("product.id"),nullable=False)
    quantity = db.Column(db.Integer,nullable=False,default=1)
    price = db.Column(db.Float,nullable=False)

    product = db.relationship("Product",backref=db.backref("order_items",lazy=True))