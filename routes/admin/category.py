from flask import render_template, request, redirect, url_for, g, jsonify
from models.category import Category
from werkzeug.utils import secure_filename
import os
from extensions import db,jwt_admin
from . import admin_bp
import uuid


@jwt_admin.unauthorized_loader
def admin_unauthorized_callback(callback):
    return redirect(url_for('auth_bp.login_page'))

@admin_bp.route("/category")
def category():
    return render_template("admin/category/index.html",module="category",user=g.current_user)

@admin_bp.get("/category/list")
def category_list():
    category = fetch_category()
    return category

@admin_bp.post("/category/create")
def create():
    filename = None
    form = request.form
    file = request.files.get('image')
    if file:
        UPLOAD_DIR = os.path.join("static/image",'category')
        os.makedirs(UPLOAD_DIR,exist_ok=True)
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        filename = unique_filename
        file.save(os.path.join(UPLOAD_DIR, filename))
    category = Category(
        name=form.get("name"),
        image=filename,
        description=form.get("description")
    )
    db.session.add(category)
    db.session.commit()
    return "Created"

@admin_bp.post("/category/delete")
def delete():
    category_id = request.get_json().get('category_id')
    image = request.get_json().get('image')
    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        if image:
            image_path = os.path.join("static/image", 'category', image)
            if os.path.exists(image_path):
                os.remove(image_path)
        return jsonify({"message": "Product deleted"}), 201
    return jsonify({"message": "Not found"}), 404

@admin_bp.put("/category/update")
def update():
    filename = None

    form = request.form
    file = request.files.get('image')
    category = Category.query.get(form.get('id'))
    if category:
        if file:
            oldImage = form.get('oldImage')
            image_path = os.path.join("static/image", 'category', oldImage)
            if os.path.exists(image_path):
                os.remove(image_path)
            UPLOAD_DIR = os.path.join("static/image",'category')
            os.makedirs(UPLOAD_DIR,exist_ok=True)
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            filename = unique_filename
            file.save(os.path.join(UPLOAD_DIR, filename))
        category.name=form.get('name')
        category.description=form.get('description')
        if filename:
            category.image=filename
        db.session.commit()
        return jsonify({"message": "Category updated successfully"}), 201
    return jsonify({"message": "Not found"}), 404
def fetch_category():
    category_data = Category.query.all()
    if category_data:
        return [
            {"id": cate.id,'name':cate.name,'image':cate.image,'description': '' if cate.description in (None, 'null') else cate.description} for cate in category_data
        ]
    return []

