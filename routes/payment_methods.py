from flask import Blueprint, request, jsonify
from config.db_config import db
from models import PaymentMethodsModel
from datetime import datetime

payment_methods_bp = Blueprint('payment_methods_bp', __name__)

@payment_methods_bp.route('/payment_methods', methods=['POST'])
def create_payment_method():
    data = request.json
    try:
        new_payment_method = PaymentMethodsModel.from_json(data)
        db.session.add(new_payment_method)
        db.session.commit()
        return jsonify({'message': 'Payment method created successfully', 'uuid': new_payment_method.uuid}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating payment method: {str(e)}'}), 500

@payment_methods_bp.route('/payment_methods', methods=['GET'])
def get_all_payment_methods():
    payment_methods = PaymentMethodsModel.query.filter(PaymentMethodsModel.deleted_at == None).all()
    return jsonify([method.to_json() for method in payment_methods]), 200

@payment_methods_bp.route('/payment_methods/<uuid>', methods=['GET'])
def get_payment_method(uuid):
    payment_method = PaymentMethodsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if payment_method:
        return jsonify(payment_method.to_json()), 200
    return jsonify({'message': 'Payment method not found'}), 404

@payment_methods_bp.route('/payment_methods/<uuid>', methods=['PUT'])
def update_payment_method(uuid):
    payment_method = PaymentMethodsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if payment_method:
        data = request.json
        payment_method.name = data.get('name', payment_method.name)
        payment_method.description = data.get('description', payment_method.description)
        db.session.commit()
        return jsonify({'message': 'Payment method updated successfully'}), 200
    return jsonify({'message': 'Payment method not found'}), 404

@payment_methods_bp.route('/payment_methods/<uuid>', methods=['DELETE'])
def delete_payment_method(uuid):
    payment_method = PaymentMethodsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if payment_method:
        payment_method.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Payment method deleted successfully'}), 200
    return jsonify({'message': 'Payment method not found'}), 404
