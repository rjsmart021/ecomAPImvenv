import urllib

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database_details import DataBaseDetails

app = Flask(__name__)
db_details = DataBaseDetails()
try:
    encoded_password = urllib.parse.quote_plus(db_details.get_password)
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_details.get_user}:{encoded_password}@{db_details.get_host}:3306/{db_details.get_database}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
except Exception as e:
    print("Error in DB connection")

db = SQLAlchemy(app)


from ecommerce import customer_routes, product_routes, order_routes
from ecommerce import models
from ecommerce.models import OrderItem, Product, Customer, Orders
