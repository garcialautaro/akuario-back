from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import aliased
from config.db_config import db
from models import OrderModel, ProductsModel, OrderStatusesModel, PromotionsModel, PromotionProductModel

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    try:
        new_order = OrderModel.from_json(data)
        db.session.add(new_order) 
        db.session.flush()

        if 'details' not in data or not data['details']:
            return jsonify({'message': 'Details of the order are required.'}), 400

        total = 0.0
        for detail in data['details']:
            product = ProductsModel.query.filter_by(uuid=detail['product_uuid']).first()
            if not product:
                return jsonify({'message': f"Product with uuid {detail['product_uuid']} not found."}), 400

            if product.stock < int(detail['quantity']):
                db.session.rollback()  # Revierte la transacción antes de enviar la respuesta
                return jsonify({'message': f"Not enough stock for product with name '{product.name}' and description '{product.description}' "}), 400
            
            product.stock -= detail['quantity']
            
            current_time = datetime.utcnow()
            
            # Realizar un join para encontrar la primera promoción vigente
            promo_alias = aliased(PromotionsModel)  # Alias para facilitar el join
            promotion = db.session.query(PromotionProductModel, promo_alias).join(
                promo_alias, PromotionProductModel.promotion_uuid == promo_alias.uuid
            ).filter(
                PromotionProductModel.product_uuid == product.uuid,
                promo_alias.start_date <= current_time,
                promo_alias.end_date >= current_time
            ).order_by(promo_alias.start_date).first()

            if promotion:
                promo_product, promo = promotion
                discount_rate = promo_product.discount_rate
                promotion_name = promo.name
                start_date = promo.start_date.strftime('%d/%m/%Y')
                end_date = promo.end_date.strftime('%d/%m/%Y')
                detail_price = product.price * (1 - discount_rate)
                discount_description = f"En este producto se aplica un descuento de {discount_rate*100}% debido a la promoción {promotion_name}, vigente desde {start_date} hasta {end_date}."
            else:
                detail_price = product.price
                discount_description = None

            total += detail_price * detail['quantity']

            # Accediendo a order_details a través de db.metadata para la inserción
            order_details_table = db.metadata.tables['order_details']
            db.session.execute(order_details_table.insert().values(
                order_uuid=new_order.uuid,
                product_uuid=detail['product_uuid'],
                price=detail_price,
                quantity=detail['quantity'],
                description=discount_description
            ))

        new_order.total = total
        new_order_status = OrderStatusesModel.query.filter_by(code="NUEVO").first()
        if not new_order_status:
            return jsonify({'message': 'Order status with code "NUEVO" not found.'}), 500
        new_order.status_uuid = new_order_status.uuid

        db.session.commit()

        return jsonify({'message': 'Order created successfully', 'uuid': new_order.uuid}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating order: {str(e)}'}), 500

@orders_bp.route('/orders', methods=['GET'])
def get_all_orders():
    orders = OrderModel.query.filter(OrderModel.deleted_at == None).all()
    orders_data = [order.to_json() for order in orders]
    return jsonify(orders_data), 200

@orders_bp.route('/orders/<uuid>', methods=['GET'])
def get_order(uuid):
    order = OrderModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if order:
        return jsonify(order.to_json()), 200
    return jsonify({'message': 'Order not found'}), 404

@orders_bp.route('/orders/<uuid>/update-status', methods=['PUT'])
def update_order_status(uuid):
    order = OrderModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if order:
        data = request.json
        new_status_uuid = data.get('status_uuid')

        # Verificar si el nuevo estado es válido
        new_status = OrderStatusesModel.query.filter_by(uuid=new_status_uuid).first()
        if not new_status:
            return jsonify({'message': 'Invalid status_uuid provided'}), 400

        # Cambiar el estado de la orden
        order.status_uuid = new_status_uuid
        db.session.commit()
        return jsonify({'message': 'Order status updated successfully'}), 200
    return jsonify({'message': 'Order not found'}), 404

@orders_bp.route('/orders/<uuid>', methods=['DELETE'])
def delete_order(uuid):
    order = OrderModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if order:
        order.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'}), 200
    return jsonify({'message': 'Order not found'}), 404
