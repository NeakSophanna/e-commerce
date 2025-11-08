from flask import Flask
from seed import seed_data
from config import Config
from routes import *
from routes.admin import admin_bp
from routes.frontend.auth import cust_bp
from extensions import *
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv('SECRET_KEY')
# Initialize base extensions
mail.init_app(app)
bcrypt.init_app(app)
db.init_app(app)
migrate.init_app(app, db)

# ---------------- CUSTOMER JWT CONFIG ----------------
with app.app_context():
    app.config["JWT_SECRET_KEY"] = Config.JWT_CUST_SECRET_KEY
    app.config["JWT_ACCESS_COOKIE_NAME"] = Config.JWT_CUST_ACCESS_COOKIE_NAME
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_CUST_ACCESS_TOKEN_EXPIRES
    app.config["JWT_COOKIE_CSRF_PROTECT"] = Config.JWT_CUST_COOKIE_CSRF_PROTECT
    jwt_customer.init_app(app)

# ---------------- ADMIN JWT CONFIG ----------------
with app.app_context():
    app.config["JWT_SECRET_KEY"] = Config.JWT_ADMIN_SECRET_KEY
    app.config["JWT_ACCESS_COOKIE_NAME"] = Config.JWT_ADMIN_ACCESS_COOKIE_NAME
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ADMIN_ACCESS_TOKEN_EXPIRES
    app.config["JWT_COOKIE_CSRF_PROTECT"] = Config.JWT_ADMIN_COOKIE_CSRF_PROTECT
    jwt_admin.init_app(app)

# ---------------- BLUEPRINTS ----------------
app.register_blueprint(home_bp, url_prefix="/")
app.register_blueprint(auth_bp, url_prefix="/admin/login")
app.register_blueprint(cust_bp, url_prefix="/")
app.register_blueprint(customer_bp, url_prefix="/")
app.register_blueprint(admin_bp, url_prefix="/admin")

# ---------------- SEED DATA ----------------
with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)
