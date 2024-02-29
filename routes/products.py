from flask import Blueprint, request, jsonify
from config.db_config import db
from models import ProductsModel, ProductPriceHistoryModel
from datetime import datetime

products_bp = Blueprint('products_bp', __name__)

# Crear un nuevo producto
@products_bp.route('/products', methods=['POST'])
def create_product():
    data = request.json
    try:
        new_product = ProductsModel.from_json(data)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'uuid': new_product.uuid}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating product: {str(e)}'}), 500

# Obtener todos los productos
@products_bp.route('/products', methods=['GET'])
def get_all_products():
    products = ProductsModel.query.all()
    return jsonify([product.to_json() for product in products]), 200

# Obtener un producto por UUID
@products_bp.route('/products/<uuid>', methods=['GET'])
def get_product(uuid):
    product = ProductsModel.query.filter_by(uuid=uuid).first()
    if product:
        return jsonify(product.to_json()), 200
    else:
        return jsonify({'message': 'Product not found'}), 404

# Actualizar un producto
@products_bp.route('/products/<uuid>', methods=['PUT'])
def update_product(uuid):
    product = ProductsModel.query.filter_by(uuid=uuid).first()
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    data = request.json
    try:
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        # Incluye otros campos si es necesario
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating product: {str(e)}'}), 500

# Eliminar un producto
@products_bp.route('/products/<uuid>', methods=['DELETE'])
def delete_product(uuid):
    product = ProductsModel.query.filter_by(uuid=uuid).first()
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    else:
        return jsonify({'message': 'Product not found'}), 404


# Endpoint para actualizar precio y stock de un producto
@products_bp.route('/products/<uuid>/update_price_stock', methods=['POST'])
def update_price_and_stock(uuid):
    product = ProductsModel.query.filter_by(uuid=uuid).first()
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    data = request.json
    previous_price = product.price
    new_price = data.get('price')
    new_stock = data.get('stock')

    if new_price is not None:
        product.price = new_price
        # Registrar el cambio de precio en ProductPriceHistoryModel
        price_history = ProductPriceHistoryModel(
            uuid_product=product.uuid,
            previous_price=previous_price,
            new_price=new_price,
            change_date=datetime.utcnow()
        )
        db.session.add(price_history)

    if new_stock is not None:
        product.stock = new_stock
    
    db.session.commit()
    return jsonify({'message': 'Product price and stock updated successfully'}), 200