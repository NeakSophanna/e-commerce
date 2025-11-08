import os,requests
from logging import exception

from flask_jwt_extended import get_jwt_identity
from flask_mail import Message
from flask import current_app,render_template
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from extensions import mail, db
from models import Customer, Order, OrderItem


def send_order_to_telegram(message):
    token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # optional for formatting
    }
    try:
        res = requests.post(url, data=payload)
        res.raise_for_status()
        return
    except Exception as e:
        print("Telegram send error:", e)


def send_mail_to_customer(data):
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    if not customer:
        print("Customer not found.")
        return 404
    cart_items = data.get("cart", [])
    name = data['name']
    email = customer.email
    address = data['address']
    city = data['city']
    country = data['country']
    phone = data['phone']
    payment = data['payment']
    shipping_fee = data['shipping_fee']
    total = data['total']
    try:
        api_key= os.getenv("BREVO_API_KEY")
        from_email = os.getenv("FROM_EMAIL")
        api_endpoint = os.getenv("BREVO_API_ENDPOINT")
        html_body = render_template(
            "invoice_email.html",
            name=name,
            phone=phone,
            address=address,
            city=city,
            country=country,
            payment=payment,
            shipping_fee=float(shipping_fee),
            total=float(total),
            cart=cart_items,
            date=datetime.now().strftime("%d-%m-%Y %H:%M")
        )
        response = requests.post(
            api_endpoint,
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json={
                "sender": {"email": from_email, "name": "Pav Pav Fashion"},
                "to":[{"email":email}],
                "subject": "Invoice",
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

def prepare_invoice_message_to_telegram(data):
    # Send Message To Telegram
    cart_items = data.get("cart", [])
    name = data.get('name')
    total = data.get('total')
    customer_id = get_jwt_identity()
    customer =Customer.query.get(customer_id)
    if not Customer.query.get(customer_id):
        return None

    message = f"""
        🛒 <b>New Order Received!</b>

        👤 <b>Customer:</b> {name}
        📧 <b>Email:</b> {customer.email}
        📞 <b>Phone:</b> {data.get('phone')}
        🏠 <b>Address:</b> {data.get('address')} {data.get('city')} {data.get('country')}

        🛍️ <b>Items:</b>
        """
    for item in cart_items:
        message += f"• *{item['name']}*\n"
        message += f"  Quantity: {int(item['qty'])}\n"
        message += f"  Price: ${float(item['price']):.2f}\n\n"

    message += f"\n💰 <b>Total:</b> ${float(total):.2f}"
    message += f"\n💳 <b>Payment Method:</b> {data.get('payment')}"
    message += f"\n🕒 <b>Time:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    return message

def insert_to_db(data):
    cart_items = data.get("cart", [])
    customer_id = get_jwt_identity()
    total = data.get('total')
    payment = data.get('payment')
    try:
        order = Order(
            customer_id=customer_id,
            total_amount = float(total),
            payment_method = payment
        )
        db.session.add(order)
        db.session.flush()
        order_id = order.id
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['id'],
                quantity=int(item['qty']),
                price=float(item['price'])
            )
            db.session.add(order_item)
        db.session.commit()
        return order_id
    except SQLAlchemyError as e:
        db.session.rollback()
        print("Database Error:", e)
        return None

