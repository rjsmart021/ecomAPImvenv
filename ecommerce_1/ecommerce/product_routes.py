from flask import jsonify, request
from ecommerce import app
from ecommerce.models import Product
from ecommerce import db
from ecommerce.schemas import ProductSchema

product_schema = ProductSchema()


# Create Product
@app.route('/products', methods=['POST'])
def add_product():
    """
    Method to add product details to product table in ecommerce database.
    Example data to send
    {
    "product_name": "Samsung Galaxy A22",
    "product_price": 328.5,
    "product_id": 23,
    "stock_available": 23
    }
    :return: Success or error message in JSON.
    """
    try:
        data = request.get_json()
        errors = product_schema.validate(data)

        if errors:
            return jsonify(errors), 400

        name = data.get("product_name")
        price = data.get("product_price")
        product_id = data.get("product_id")
        stock_available = data.get("stock_available")

        existing_product = Product.query.filter(
            (Product.product_name == name) | (Product.product_id == product_id)).first()

        if existing_product:
            return jsonify({"message": f"Product already exists"})

        product = Product(product_id=product_id, product_name=name, product_price=price,
                          stock_available=stock_available)
        db.session.add(product)
        db.session.commit()

        return jsonify({"message": "Product added successfully"})
    except Exception as e:
        return jsonify({"Error": f"Product not added. Error {e}"})


# Read Product
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    This method is to retrieve the product details based on the id for the product
    :param product_id: id of the product in ecommerce website
    :return: Product details if found successfully else error message.
    """
    try:
        product = Product.query.get(product_id)

        if product:
            product_data = {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "product_price": product.product_price,
                "stock_available": product.stock_available
            }
            return jsonify(product_data)
        else:
            return jsonify({"message": "Product not found"})

    except Exception as e:
        return jsonify(
            {"message": f"Error while fetching product with ID: {product_id}. Error: {e}"})


# Update Product
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Update product details. We need to PUT data same as POST format
    :param product_id: id of the product.
    :return: Update success message if updated successfully else error message.
    """
    try:
        product = Product.query.get(product_id)

        if product:
            data = request.get_json()
            errors = product_schema.validate(data)

            if errors:
                return jsonify(errors), 400
            product.product_name = data.get('name', product.product_name)
            product.product_price = data.get('price', product.product_price)
            product.stock_available = data.get('stock_available', product.stock_available)

            db.session.commit()
            return jsonify({"message": "Product updated successfully"})
        else:
            return jsonify({"message": "Product not found"})

    except Exception as e:
        return jsonify({"message": f"Error in updating product. Error: {e}"})


# Delete Product
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Delete a particular product.
    :param product_id: ID of the product to delete
    :return: Success message if deleted successfully else error message.
    """
    try:
        product = Product.query.get(product_id)

        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"message": "Product deleted successfully"})
        else:
            return jsonify({"message": "Product not found"})

    except Exception as e:
        return jsonify({"message": f"Error in deleting product. Error: {e}"})


# List Products
@app.route('/products', methods=['GET'])
def list_products():
    """
    List all the products in the product table in ecommerce database
    :return: Success message if deleted successfully else error message.
    """
    try:
        products = Product.query.all()

        if products:
            product_list = []
            for product in products:
                product_data = {
                    "product_id": product.product_id,
                    "name": product.product_name,
                    "price": product.product_price,
                    "Stock_available": product.stock_available
                }
                product_list.append(product_data)

            return jsonify(product_list)
        else:
            return jsonify({"message": "No products found"})

    except Exception as e:
        return jsonify({"message": f"Error in listing products. Error: {e}"})


@app.route('/products/<int:product_id>/stock', methods=['GET', 'PUT'])
def manage_product_stock(product_id):
    """
    This product is used to change the stock levels. Example PUT data to change the stock levels is:
    {"stock_available": 30}, with this stock_available is updated to 30.
    :param product_id:
    :return: success message or error message
    """
    try:
        product = Product.query.get(product_id)

        if product:
            if request.method == 'GET':
                return jsonify({"stock_available": product.stock_available})
            elif request.method == 'PUT':
                data = request.get_json()
                new_stock = data.get('stock_available')

                product.stock_available = new_stock
                db.session.commit()

                return jsonify({"message": "Product stock updated successfully"})
        else:
            return jsonify({"message": "Product not found"})

    except Exception as e:
        return jsonify({"message": f"Error in managing product stock. Error: {e}"})


@app.route('/products/restock', methods=['POST'])
def restock_products():
    """
    It will resize the stock if available is below threshold. We need to post threshold level and do adjustment as required.
    Example POST data: {"threshold": 20}
    :return:
    """
    try:
        data = request.get_json()
        threshold = data.get('threshold')

        low_stock_products = Product.query.filter(Product.stock_available <= threshold).all()

        if low_stock_products:
            for product in low_stock_products:
                product.stock_available = (product.stock_available + (threshold-product.stock_available))*2
            db.session.commit()

            return jsonify({"message": "Restocking completed successfully"})
        else:
            return jsonify({"message": "No products require restocking"})

    except Exception as e:
        return jsonify({"message": f"Error in restocking products. Error: {e}"})
