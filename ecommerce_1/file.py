from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, ValidationError
from my_password import password
from flask_cors import CORS

db_password = password
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{db_password}@localhost/advanced_e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("username", "password", "customer_id", "id")

class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("name", "price", "id")

class OrderSchema(ma.Schema):
    customer = fields.Nested(CustomerSchema)
    date = fields.Date(required=True)
    order_items = fields.String(required=True)

    class Meta:
        fields = ("id", "customer_id", "date", "order_items")

# Instance creation of Schemas
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# Creating Models
class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer')

class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)

# Association Table
order_product = db.Table('Order_Product',
    db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
)

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    products = db.relationship('Product', secondary=order_product, backref=db.backref('orders'))

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)


###App Route Methods
##Customer ----------------------------------------------------------------------------------------------------------------------------
# Get all customer info
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

# Get specific customer info by id
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    customer = Customer.query.filter(Customer.id == id).first()
    return customer_schema.jsonify(customer)

# Add a new customer
@app.route("/customers", methods=["POST"])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added sucesfully"}), 201

# Update existing customer by id
@app.route("/customers/<int:id>", methods=["PUT"])
def update_cusomter(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()

    return jsonify({"message": "Customer updated sucesfully"}), 200

# Delete Customer by id
@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer removed sucesfully"}), 200

## Customer Accounts ----------------------------------------------------------------------------------------------------------------------------
# Get all customer accounts
@app.route('/customer_accounts', methods=['GET'])
def get_customer_accounts():
    customer_accounts = CustomerAccount.query.all()
    return customer_accounts_schema.jsonify(customer_accounts)

# Get specific customer account info by CUSTOMER id
@app.route('/customer_accounts/<int:id>', methods=['GET'])
def get_customer_account_by_id(id):
    customer_account = CustomerAccount.query.filter(CustomerAccount.customer_id == id).first()
    return customer_account_schema.jsonify(customer_account)

# Add a new customer account
@app.route("/customer_accounts", methods=["POST"])
def add_customer_account():
    try:
        account_data = customer_account_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    new_account = CustomerAccount(username=account_data['username'], password=account_data['password'], customer_id=account_data['customer_id'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "New account added sucesfully"}), 201

# Update existing customer account by CUSTOMER id
@app.route("/customer_accounts/<int:id>", methods=["PUT"])
def update_cusomter_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    try:
        account_data = customer_account_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer_account.username = account_data['username']
    customer_account.password = account_data['password']
    db.session.commit()

    return jsonify({"message": "Customer account updated sucesfully"}), 200

# Delete Customer Account by customer id
@app.route("/customer_accounts/<int:accountId>", methods=["DELETE"])
def delete_customer_account(accountId):
    customer_account = CustomerAccount.query.get_or_404(accountId)
    db.session.delete(customer_account)
    db.session.commit()

    return jsonify({"message": "Customer account removed sucesfully"}), 200

## Products ----------------------------------------------------------------------------------------------------------------------------
# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

# Get specific product info by id
@app.route('/products/<int:id>', methods=['GET'])
def get_product_by_id(id):
    product = Product.query.filter(Product.id == id).first()
    return product_schema.jsonify(product)

# Add a new product
@app.route("/products", methods=["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New product added successfully"}), 201

# Update existing products by id
@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()

    return jsonify({"message": "Product updated sucesfully"}), 200

# Delete products by id
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product removed sucesfully"}), 200

## Orders ----------------------------------------------------------------------------------------------------------------------------
# Placing order
@app.route("/orders", methods=["POST"])
def place_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    new_order = Order(customer_id=order_data['customer_id'], date=order_data['date'], order_items=['order_items'])

    # for item_id in order_data['order_items']:
    #     new_order.products.append(Product.query.filter(Product.id == item_id).first())
    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "New order placed"}), 201

# Get all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return orders_schema.jsonify(orders)

# Retrieving order
@app.route("/orders/<int:id>", methods=["GET"])
def get_order_details(id):
    order = Order.query.filter(Order.id == id).first()
    return order_schema.jsonify(order)

# Show all customer orders
@app.route("/orders/customer/<int:id>", methods=["GET"])
def track_order(id):
    orders = Order.query.filter(Order.customer_id == id).all()
    return orders_schema.jsonify(orders)


# @app.route("/orders/form/<int:id>", methods=["GET"])
# def getOrderProducts(id):
#     products = Order.query(order_table).all()

## Running ----------------------------------------------------------------------------------------------------------------------------
# Creates database structure if it doesnt already exist
with app.app_context():
    db.create_all()

# Just for running from IDE
if __name__ == '__main__':
    app.run(debug = True)    
