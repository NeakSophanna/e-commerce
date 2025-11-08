from flask import Blueprint,g,current_app,redirect,url_for
from flask_jwt_extended import verify_jwt_in_request,get_jwt_identity
from models.users import User
from extensions import jwt_admin

admin_bp = Blueprint("admin_bp",__name__,url_prefix="/admin")
@admin_bp.before_request
def protect_admin_routes():
    # Temporarily set correct JWT cookie for admin
    current_app.config["JWT_ACCESS_COOKIE_NAME"] = current_app.config["JWT_ADMIN_ACCESS_COOKIE_NAME"]
    current_app.config["JWT_SECRET_KEY"] = current_app.config["JWT_ADMIN_SECRET_KEY"]

    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        g.current_user = User.query.get(int(user_id))
    except Exception as e:
        return redirect(url_for('auth_bp.login_page'))