from flask import Blueprint, request, jsonify
from datetime import datetime
from config.db_config import db
from models import OrderStatusesModel

order_statuses_bp = Blueprint('order_statuses_bp', __name__)

@order_statuses_bp.route('/order_statuses', methods=['POST'])
def create_order_status():
    data = request.json
    new_order_status = OrderStatusesModel.from_json(data)
    db.session.add(new_order_status)
    db.session.commit()
    return jsonify({'message': 'Order status created successfully', 'uuid': new_order_status.uuid}), 201

@order_statuses_bp.route('/order_statuses', methods=['GET'])
def get_all_order_statuses():
    order_statuses = OrderStatusesModel.query.filter(OrderStatusesModel.deleted_at == None).all()
    return jsonify([order_status.to_json() for order_status in order_statuses]), 200

@order_statuses_bp.route('/order_statuses/<uuid>', methods=['GET'])
def get_order_status(uuid):
    order_status = OrderStatusesModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if order_status:
        return jsonify(order_status.to_json()), 200
    return jsonify({'message': 'Order status not found'}), 404

@order_statuses_bp.route('/order_statuses/<uuid>', methods=['PUT'])
def update_order_status(uuid):
    order_status = OrderStatusesModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if order_status:
        data = request.json
        order_status.name = data.get('name', order_status.name)
        order_status.description = data.get('description', order_status.description)
        db.session.commit()
        return jsonify({'message': 'Order status updated successfully'}), 200
    return jsonify({'message': 'Order status not found'}), 404

@order_statuses_bp.route('/order_statuses/<uuid>', methods=['DELETE'])
def delete_order_status(uuid):
    order_status = OrderStatusesModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if order_status:
        order_status.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Order status deleted successfully'}), 200
    return jsonify({'message': 'Order status not found'}), 404
