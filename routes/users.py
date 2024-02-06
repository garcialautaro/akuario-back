from datetime import datetime
from flask import Blueprint, request, jsonify
from firebase_admin import auth as firebase_auth
from config.db_config import db
from models import UserModel, ProfileModel
from decorators import token_required, access_required

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/users', methods=['GET'])
# @token_required
# @access_required('view_users')
def get_all_users():
    users = UserModel.query.filter(UserModel.deleted_at == None).all()
    users_data = [{'uuid': user.uuid, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(users_data), 200

@users_bp.route('/users/<uuid>', methods=['GET'])
# @token_required
# @access_required('view_users')
def get_user(uuid):
    user = UserModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if user:
        user_data = {'uuid': user.uuid, 'username': user.username, 'email': user.email}
        return jsonify(user_data), 200
    return jsonify({'message': 'User not found'}), 404

@users_bp.route('/users/<uuid>', methods=['PUT'])
# @token_required
# @access_required('manage_users')
def update_user(uuid):
    user = UserModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if user:
        data = request.json
        user.address = data.get('address', user.address)
        user.company_name = data.get('company_name', user.company_name)
        user.cuil = data.get('cuil', user.cuil)
        user.dni = data.get('dni', user.dni)
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@users_bp.route('/users/<uuid>', methods=['DELETE'])
# @token_required
# @access_required('manage_users')
def delete_user(uuid):
    user = UserModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if user:
        user.deleted_at = datetime.utcnow()
        try:
            firebase_auth.update_user(user.firebase_uid, disabled=True)
        except Exception as e:
            db.session.rollback()  # Deshace el cambio si no quieres completar el borrado
            return jsonify({'error': 'Failed to disable user in Firebase', 'message': str(e)}), 500
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@users_bp.route('/users/<uuid_user>/set_profiles', methods=['POST'])
# @token_required
# @access_required('assign_profiles')
def set_profiles(uuid_user):
    data = request.json
    profiles_uuids = data.get('uuid_profiles', [])

    # Verificar si el array de UUIDs de perfiles está vacío
    if not profiles_uuids:
        return jsonify({'error': 'No profile UUIDs provided. At least one profile UUID is required.'}), 400

    user = UserModel.query.filter_by(uuid=uuid_user, deleted_at=None).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    profiles = ProfileModel.query.filter(ProfileModel.uuid.in_(profiles_uuids)).all()
    user.profiles = []  # Limpiar perfiles existentes

    if profiles:
        user.profiles.extend(profiles)
        db.session.commit()
        return jsonify({'message': 'Profiles assigned successfully'}), 200
    else:
        return jsonify({'message': 'No valid profiles found to assign'}), 400

@users_bp.route('/users/<uuid_user>/profiles', methods=['GET'])
# @token_required
# @access_required('assign_profiles')
def get_user_profiles(uuid_user):
    user = UserModel.query.filter_by(uuid=uuid_user, deleted_at=None).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    profiles = user.profiles
    profiles_data = [{
        'uuid': profile.uuid,
        'name': profile.name,
        'description': profile.description,
        # Agrega otros campos del modelo ProfileModel si es necesario
    } for profile in profiles]

    return jsonify(profiles_data), 200
