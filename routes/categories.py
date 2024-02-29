from flask import Blueprint, request, jsonify
from config.db_config import db
from models import CategoriesModel
from datetime import datetime

categories_bp = Blueprint('categories_bp', __name__)

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.json
    try:
        new_category = CategoriesModel.from_json(data)
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': 'Category created successfully', 'uuid': new_category.uuid}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating category: {str(e)}'}), 500

@categories_bp.route('/categories', methods=['GET'])
def get_all_categories():
    categories = CategoriesModel.query.filter(CategoriesModel.deleted_at == None).all()
    categories_data = [category.to_json() for category in categories]
    return jsonify(categories_data), 200

@categories_bp.route('/categories/<uuid>', methods=['GET'])
def get_category(uuid):
    category = CategoriesModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if category:
        return jsonify(category.to_json()), 200
    return jsonify({'message': 'Category not found'}), 404

@categories_bp.route('/categories/<uuid>', methods=['PUT'])
def update_category(uuid):
    category = CategoriesModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if category:
        data = request.json
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        db.session.commit()
        return jsonify({'message': 'Category updated successfully'}), 200
    return jsonify({'message': 'Category not found'}), 404

@categories_bp.route('/categories/<uuid>', methods=['DELETE'])
def delete_category(uuid):
    category = CategoriesModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if category:
        category.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'}), 200
    return jsonify({'message': 'Category not found'}), 404
