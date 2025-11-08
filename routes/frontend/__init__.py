from flask import Blueprint,g,current_app,redirect,url_for
from flask_jwt_extended import verify_jwt_in_request,get_jwt_identity
from models.customer import Customer

customer_bp = Blueprint('customer_bp',__name__,url_prefix='/')
@customer_bp.before_request
def protect_customer_route():
    current_app.config["JWT_ACCESS_COOKIE_NAME"] = current_app.config["JWT_CUST_ACCESS_COOKIE_NAME"]
    current_app.config["JWT_SECRET_KEY"] = current_app.config["JWT_CUST_SECRET_KEY"]

    try:
        verify_jwt_in_request()
        customer_id = get_jwt_identity()
        if customer_id:
            g.current_customer = Customer.query.get(customer_id)
        else:
            g.current_customer = None
    except Exception:
        return redirect(url_for('cust_bp.login_page_for_customer'))