from flask import Flask, request, jsonify
from typing import Dict
import uuid

app = Flask(__name__)

# In-memory storage for products and orders
products: Dict[str, Dict] = {}
orders: Dict[str, Dict] = {}

class InvalidInputError(Exception):
    """Custom exception for invalid input data."""
    pass

def validate_product(product: Dict) -> None:
    """
    Validate the product data.
    Raises InvalidInputError if the product data is invalid.
    """
    if not isinstance(product, dict) or not all(field in product for field in ('name', 'price')):
        raise InvalidInputError("Product must be a dictionary with 'name' and 'price' fields")
    if not isinstance(product['name'], str) or not product['name'].strip():
        raise InvalidInputError("Product name must be a non-empty string")
    if not isinstance(product['price'], (int, float)) or product['price'] <= 0:
        raise InvalidInputError("Product price must be a positive number")

def validate_order(order: Dict) -> None:
    """
    Validate the order data.
    Raises InvalidInputError if the order data is invalid.
    """
    if not isinstance(order, dict) or not all(field in order for field in ('product_id', 'quantity')):
        raise InvalidInputError("Order must be a dictionary with 'product_id' and 'quantity' fields")
    if not isinstance(order['product_id'], str) or order['product_id'] not in products:
        raise InvalidInputError("Invalid product ID")
    if not isinstance(order['quantity'], int) or order['quantity'] <= 0:
        raise InvalidInputError("Order quantity must be a positive integer")

@app.route('/products', methods=['POST'])
def add_product():
    """Add a new product to the inventory."""
    try:
        product = request.json
        validate_product(product)
        product_id = str(uuid.uuid4())
        products[product_id] = product
        return jsonify({"message": "Product added successfully", "product_id": product_id}), 201
    except InvalidInputError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error in add_product: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/products/<product_id>', methods=['DELETE'])
def remove_product(product_id: str):
    """Remove a product from the inventory."""
    if not isinstance(product_id, str) or product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    del products[product_id]
    return jsonify({"message": "Product removed successfully"}), 200

@app.route('/orders', methods=['POST'])
def place_order():
    """Place a new order."""
    try:
        order = request.json
        validate_order(order)
        order_id = str(uuid.uuid4())
        orders[order_id] = order
        return jsonify({"message": "Order placed successfully", "order_id": order_id}), 201
    except InvalidInputError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error in place_order: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/orders/<order_id>', methods=['DELETE'])
def cancel_order(order_id: str):
    """Cancel an existing order."""
    if not isinstance(order_id, str) or order_id not in orders:
        return jsonify({"error": "Order not found"}), 404
    del orders[order_id]
    return jsonify({"message": "Order cancelled successfully"}), 200

@app.route('/products', methods=['GET'])
def list_products():
    """List all products in the inventory."""
    return jsonify(products), 200

@app.route('/orders', methods=['GET'])
def list_orders():
    """List all orders."""
    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(debug=True)
