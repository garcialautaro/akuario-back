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
    users_data = [user.to_json() for user in users]  # Asumiendo que UserModel tiene to_json
    return jsonify(users_data), 200

@users_bp.route('/users/<uuid>', methods=['GET'])
# @token_required
# @access_required('view_users')
def get_user(uuid):
    user = UserModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if user:
        return jsonify(user.to_json()), 200  # Asumiendo que UserModel tiene to_json
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
            db.session.rollback()  # Rollback en caso de fallo con Firebase
            return jsonify({'error': 'Failed to disable user in Firebase', 'message': str(e)}), 500
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@users_bp.route('/users/<uuid_user>/set_profiles', methods=['POST'])
# @token_required
# @access_required('assign_profiles_to_user')
def set_profiles(uuid_user):
    data = request.json
    profiles_uuids = data.get('uuid_profiles', [])
    if not profiles_uuids:
        return jsonify({'error': 'No profile UUIDs provided. At least one profile UUID is required.'}), 400

    user = UserModel.query.filter_by(uuid=uuid_user, deleted_at=None).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    profiles = ProfileModel.query.filter(ProfileModel.uuid.in_(profiles_uuids), ProfileModel.deleted_at == None).all()
    user.profiles = profiles
    db.session.commit()
    return jsonify({'message': 'Profiles assigned successfully'}), 200

@users_bp.route('/users/<uuid_user>/profiles', methods=['GET'])
# @token_required
# @access_required('view_user_profiles')
def get_user_profiles(uuid_user):
    user = UserModel.query.filter_by(uuid=uuid_user, deleted_at=None).first()
    if user:
        profiles_data = [profile.to_json() for profile in user.profiles]  # Asumiendo ProfileModel tiene to_json
        return jsonify(profiles_data), 200
    return jsonify({'message': 'User not found'}), 404
