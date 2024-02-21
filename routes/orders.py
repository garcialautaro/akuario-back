from datetime import datetime
from flask import Blueprint, request, jsonify
from config.db_config import db
from models import OrderModel, ProductsModel, OrderStatusesModel, PromotionsModel

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    try:
        new_order = OrderModel.from_json(data)
        
        # Verificar si los detalles de la orden se proporcionan correctamente
        if 'details' not in data or not data['details']:
            return jsonify({'message': 'Details of the order are required.'}), 400
        
        total = 0.0
        for detail in data['details']:
            product = ProductsModel.query.filter_by(uuid=detail['product_uuid']).first()
            if not product:
                return jsonify({'message': 'Product with uuid {} not found.'.format(detail['product_uuid'])}), 400
            
            # Obtener la promotion_product vigente para el producto actual
            promotion_product = db.metadata.tables['promotion_products'].query\
                .filter_by(uuid_product=detail['product_uuid'])\
                .join('promotions', 'promotion_products.uuid_promotion=promotions.uuid')\
                .filter('promotions.start_date <=', datetime.utcnow())\
                .filter('promotions.end_date >=', datetime.utcnow())\
                .first()
            
            if promotion_product:
                # Promoción vigente encontrada
                promotion = PromotionsModel.query.get(promotion_product.uuid_promotion)
                detail_price = product.price * (1 - promotion_product.discount_rate)
                discount_description = f"En este producto se aplica un descuento de {promotion_product.discount_rate} debido a la promoción {promotion.name} que tenía como vigencia desde {promotion.start_date.strftime('%d/%m/%Y')} hasta {promotion.end_date.strftime('%d/%m/%Y')}"
            else:
                # No se encontró una promoción vigente
                detail_price = product.price
                discount_description = None
                
            total += detail_price * detail['quantity']

            # Agregar el detalle de la orden a la base de datos
            db.session.execute(db.metadata.tables['order_details'].insert().values(
                order_uuid=new_order.uuid,
                product_uuid=detail['product_uuid'],
                price=detail_price,
                quantity=detail['quantity'],
                description=discount_description
            ))

        new_order.total = total

        # Establecer el estado de la orden como "Nuevo"
        new_order_status = OrderStatusesModel.query.filter_by(code="NUEVO").first()
        if not new_order_status:
            return jsonify({'message': 'Order status with code "NUEVO" not found.'}), 500
        new_order.status_uuid = new_order_status.uuid

        db.session.add(new_order)
        db.session.commit()

        return jsonify({'message': 'Order created successfully', 'uuid': new_order.uuid}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating order: {}'.format(str(e))}), 500


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
