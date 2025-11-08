from extensions import db
from models.product import Product
from models.category import Category
def fetchProduct():
    products = (
        db.session.query(Product.id,
                         Product.name,
                         Product.description,
                         Product.cost,
                         Product.price,
                         Product.category_id,
                         Category.name.label("category_name"),
                         Product.image,
                         Product.stock)
        .join(Category,Product.category_id == Category.id)
        .all()
    )
    if products:
        return[
            {   'id':product.id,
                'name':product.name,
                'description':product.description,
                'cost':product.cost,
                'price':product.price,
                'category_id':product.category_id,
                'category_name':product.category_name,
                'image':product.image,
                'stock':product.stock
            }for product in products
        ]
    return []

def fetchCategory():
    categories = (
        db.session.query(Category.id,Category.name).all()
    )
    if categories:
        return[
            {
                'category_id': category.id,
                'category_name':category.name
            }for category in categories
        ]
    return []

def get_product_by_id(id):
    product = db.session.query(
        Product.id,
        Product.name,
        Product.description,
        Product.price,
        Category.name.label('category_name'),
        Product.image
    ).join(Category,Product.category_id == Category.id).filter(Product.id == id).first()
    if not product:
        return None
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description if product.description else " ",
        "category_name": product.category_name,
        "price":float(product.price),
        "image":product.image if product.image else "no-image.png"
    }
