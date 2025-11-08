from models.order import Order,OrderItem

def fetchOrder():
    orders = Order.query.all()
    if orders:
        return [
            {
                "id": order.id,
                "customer_name": order.customer.username,
                "total":order.total_amount,
                "payment_method":order.payment_method,
                "status":order.status,
                "order_at":order.order_at.strftime("%d/%m/%Y %H:%M")
            }for order in orders
        ]
    return []