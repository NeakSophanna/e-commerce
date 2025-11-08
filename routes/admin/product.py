from flask import render_template, request, redirect, url_for, g, jsonify
from models.product import Product
from werkzeug.utils import secure_filename
import os,uuid
from extensions import db,jwt_admin
from . import admin_bp
from helpers.product import fetchProduct,fetchCategory

@jwt_admin.unauthorized_loader
def admin_unauthorized_callback(callback):
    return redirect(url_for('auth_bp.login_page'))

@admin_bp.route("/product",methods=["GET"])
def product():
    return render_template("admin/product/index.html",module="product",user=g.current_user)

@admin_bp.get("/product/list")
def product_list():
    products = fetchProduct()
    category = fetchCategory()
    return jsonify({
        "products":products,
        "category":category
    })
@admin_bp.post("/product/add")
def add_product():
    filename = None
    form = request.form
    file = request.files.get('image')
    if file:
        UPLOAD_DIR = os.path.join("static/image",'product')
        os.makedirs(UPLOAD_DIR,exist_ok=True)
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        filename = unique_filename
        file.save(os.path.join(UPLOAD_DIR,filename))
    product = Product(
        name=form.get('name'),
        description=form.get('description'),
        cost=form.get('cost'),
        price=form.get('price'),
        category_id=form.get('category_id'),
        stock=form.get('stock'),
        image=filename,
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message":"success"}),201

@admin_bp.post("/product/delete")
def delete_product():
    product_id = request.get_json().get('product_id')
    image = request.get_json().get('image')
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        if image:
            image_path= os.path.join("static/image",'product',image)
            if os.path.exists(image_path):
                os.remove(image_path)
        return jsonify({"message":"Success"}),201
    return jsonify({"message":"Product not found"}),404

@admin_bp.post("/product/update")
def update_product():
    filename = None
    form = request.form
    product = Product.query.get(form.get('id'))
    if product:
        file = request.files.get('image')
        if file:
            old_image = form.get('oldImage')
            image_path = os.path.join("static/image",'product',old_image)
            if os.path.exists(image_path):
                os.remove(image_path)
            UPLOAD_DIR = os.path.join("static/image",'product')
            os.makedirs(UPLOAD_DIR,exist_ok=True)
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            filename = unique_filename
            file.save(os.path.join(UPLOAD_DIR,filename))
        product.name = form.get('name')
        product.description = form.get('description')
        product.cost = form.get('cost')
        product.price = form.get('price')
        product.category_id = form.get('category_id')
        product.stock = form.get('stock')
        if filename:
            product.image = filename
        db.session.commit()
        return jsonify({"message":"success"}),201
    return jsonify({"message":"Product not found"}),404