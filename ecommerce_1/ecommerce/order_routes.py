from datetime import datetime, timedelta

from flask import request, jsonify
from ecommerce import db
from ecommerce import app
from ecommerce.schemas import OrdersSchema

order_schema = OrdersSchema()


@app.route('/orders', methods=['POST'])
def place_order():
    """
    Method to post data to orders and order_item database.
    Example Data to post format:
    {
    "customer_id":1,
    "order_items":[{"product_id":101, "quantity": 31}, {"product_id":100, "quantity": 1}]
    }

    :return:
    """
    from ecommerce import Orders, Product, OrderItem
    try:
        data = request.get_json()
        customer_id = data.get("customer_id")
        order_items = data.get("order_items")
        current_date = datetime.now()
        ordered_date = current_date.strftime("%Y-%m-%d")
        new_date = current_date + timedelta(days=5)
        expected_date = new_date.strftime('%Y-%m-%d')

        order = Orders(customer_id=customer_id, order_date=ordered_date, expected_date=expected_date)
        db.session.add(order)
        for item in order_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            product = Product.query.get(product_id)
            if product and product.stock_available >= quantity:
                order_item = OrderItem(order_id=order.order_id, product_id=product_id, quantity=quantity, price=product.product_price)
                db.session.add(order_item)
                product.stock_available -= quantity
            else:
                db.session.rollback()
                return jsonify({"message": "Order placement failed. Insufficient stock."})

            db.session.commit()
            return jsonify({"message": "Order placed successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": f"Order placement failed. Error: {e}"})


# Retrieve Order
@app.route('/orders/<int:order_id>', methods=['GET'])
def retrieve_order(order_id):
    """
    This method is to get teh order details based on the id provided.
    :param order_id: id generated for each order, it is of type integer.
    :return: json
    """
    from ecommerce import Orders, OrderItem
    try:
        order = Orders.query.get(order_id)
        order_items = OrderItem.query.filter(OrderItem.order_id == order_id).all()

        if order:
            order_data = {
                "order_id": order.order_id,
                "order_date": order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "customer_id": order.customer_id,
                "order_items": []
            }
            for item in order_items:
                item_data = {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price
                }
                order_data["order_items"].append(item_data)

            return jsonify(order_data)
        else:
            return jsonify({"message": "Order not found"})

    except Exception as e:
        return jsonify({"message": f"Error while retrieving order with ID: {order_id}. Error: {e}"})


# Track Order
@app.route('/orders/<int:order_id>/status', methods=['GET'])
def track_order(order_id):
    """
    Method to track the order status based on its date of order and expected delivery date.
    :param order_id: id generated for each order, it is of type integer.
    :return: order progress in JSON else error message.
    """
    from ecommerce import Orders
    try:
        order = Orders.query.get(order_id)

        if order:
            return jsonify({"status": "In progress", "order_date": order.order_date.strftime("%Y-%m-%d %H:%M:%S"), "expected_date": order.expected_date.strftime("%Y-%m-%d") if order.expected_date else None})
        else:
            return jsonify({"message": "Order not found"})

    except Exception as e:
        return jsonify({"message": f"Error while tracking order with ID: {order_id}. Error: {e}"})
