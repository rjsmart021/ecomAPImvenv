from ecommerce import db


class Customer(db.Model):
    """
    Customer Relation Model.
    Attributes are:
    1. customer_id: integer and primary key. It will have auto increment
    2. customer_name: string of max length 100 and null is not allowed
    3. email: string of max length 100 and null is not allowed
    4. phone_number: string of max length 10 and null is not allowed
    """
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)


class Product(db.Model):
    """
        Product Relation Model.
        Attributes are:
        1. product_id: integer and primary key. It will have auto increment
        2. product_name: string of max length 100 and null is not allowed
        3. product_price: float and null is not allowed
        4. stock_available: Integer and null is not allowed
        """
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    stock_available = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
    """
    Order Relation.
    """
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False)
    expected_date = db.Column(db.Date, nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)


class OrderItem(db.Model):
    """
    Order Item relation.
    It refers to order and product table.
    It will have all the list of products for a particular order.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
