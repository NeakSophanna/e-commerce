from pydoc import describe

from extensions import db,bcrypt
from models import User, Category, Product, Customer, Order, OrderItem


def seed_data():
    if not User.query.first():
        user = User(
            username="admin",
            email="admin@example.com",
            password=bcrypt.generate_password_hash("123"),
            gender="male"
        )
        db.session.add(user)
    db.session.commit()
    print("✅ Database seeded automatically")