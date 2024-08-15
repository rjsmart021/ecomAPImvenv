from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from ecommerce import app

ma = Marshmallow()


class CustomerSchema(ma.Schema):
    customer_id = fields.Integer(dump_only=True)
    customer_name = fields.String(required=True)
    email = fields.Email(required=True, validate=validate.Regexp(r'^.+@[^\.].*\.[a-z]{2,}$',
                                                                 error='Invalid email address'))
    phone_number = fields.String(required=True, validate=validate.Length(min=10, max=20,
                                                                         error='Invalid phone number'))


class ProductSchema(ma.Schema):
    product_id = fields.Integer(required=True)
    product_name = fields.String(required=True)
    product_price = fields.Float(required=True)
    stock_available = fields.Integer(required=True)


class OrdersSchema(ma.Schema):
    order_id = fields.Integer(dump_only=True)
    order_date = fields.DateTime(required=True)
    expected_date = fields.Date(allow_none=True)
    customer_id = fields.Integer(required=True)


class OrderItemSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    order_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True)
    price = fields.Float(required=True)


ma.init_app(app)
