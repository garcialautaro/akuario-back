from datetime import datetime
from flask import Blueprint, request, jsonify
from config.db_config import db
from models import AccessModel
from decorators import token_required, access_required

access_bp = Blueprint('access_bp', __name__)

@access_bp.route('/accesses', methods=['POST'])
# @token_required
# @access_required('manage_accesses')
def create_access():
    data = request.json
    new_access = AccessModel.from_json(data) 
    db.session.add(new_access)
    db.session.commit()
    return jsonify({'message': 'Access created successfully', 'uuid': new_access.uuid}), 201

@access_bp.route('/accesses', methods=['GET'])
# @token_required
# @access_required('view_accesses')
def get_all_accesses():
    # Filtrar solo los accesos que no han sido eliminados
    accesses = AccessModel.query.filter(AccessModel.deleted_at == None).all()
    accesses_data = [access.to_json() for access in accesses]  # Usar to_json para cada acceso
    return jsonify(accesses_data), 200

@access_bp.route('/accesses/<uuid>', methods=['GET'])
# @token_required
# @access_required('view_accesses')
def get_access(uuid):
    access = AccessModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if access:
        return jsonify(access.to_json()), 200  # Usar to_json para devolver el acceso
    return jsonify({'message': 'Access not found'}), 404

@access_bp.route('/accesses/<uuid>', methods=['PUT'])
# @token_required
# @access_required('manage_accesses')
def update_access(uuid):
    access = AccessModel.query.filter_by(uuid=uuid).first()
    if access:
        data = request.json
        access.name = data.get('name', access.name).lower()
        access.description = data.get('description', access.description)
        db.session.commit()
        return jsonify({'message': 'Access updated successfully'}), 200
    return jsonify({'message': 'Access not found'}), 404

@access_bp.route('/accesses/<uuid>', methods=['DELETE'])
# @token_required
# @access_required('manage_accesses')
def delete_access(uuid):
    access = AccessModel.query.filter_by(uuid=uuid).first()
    if access:
        access.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Access deleted successfully'}), 200
    return jsonify({'message': 'Access not found'}), 404
