from datetime import datetime
from flask import Blueprint, request, jsonify
from config.db_config import db
from models import BrandsModel
# from decorators import token_required, access_required

brands_bp = Blueprint('brands_bp', __name__)

@brands_bp.route('/brands', methods=['POST'])
# @token_required
# @access_required('manage_brands')
def create_brand():
    data = request.json
    new_brand = BrandsModel.from_json(data)
    db.session.add(new_brand)
    db.session.commit()
    return jsonify({'message': 'Brand created successfully', 'uuid': new_brand.uuid}), 201

@brands_bp.route('/brands', methods=['GET'])
# @token_required
# @access_required('view_brands')
def get_all_brands():
    brands = BrandsModel.query.filter(BrandsModel.deleted_at == None).all()
    brands_data = [brand.to_json() for brand in brands]
    return jsonify(brands_data), 200

@brands_bp.route('/brands/<uuid>', methods=['GET'])
# @token_required
# @access_required('view_brands')
def get_brand(uuid):
    brand = BrandsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if brand:
        return jsonify(brand.to_json()), 200
    return jsonify({'message': 'Brand not found'}), 404

@brands_bp.route('/brands/<uuid>', methods=['PUT'])
# @token_required
# @access_required('manage_brands')
def update_brand(uuid):
    brand = BrandsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if brand:
        data = request.json
        brand.name = data.get('name', brand.name)
        db.session.commit()
        return jsonify({'message': 'Brand updated successfully'}), 200
    return jsonify({'message': 'Brand not found'}), 404

@brands_bp.route('/brands/<uuid>', methods=['DELETE'])
# @token_required
# @access_required('manage_brands')
def delete_brand(uuid):
    brand = BrandsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if brand:
        brand.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Brand deleted successfully'}), 200
    return jsonify({'message': 'Brand not found'}), 404
