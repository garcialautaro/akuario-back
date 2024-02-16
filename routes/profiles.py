from datetime import datetime
from flask import Blueprint, request, jsonify
from config.db_config import db
from models import ProfileModel, AccessModel
from decorators import token_required, access_required

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/profiles', methods=['POST'])
# @token_required
# @access_required('manage_profiles')
def create_profile():
    data = request.json
    new_profile = ProfileModel.from_json(data)  # Asumiendo la existencia de from_json
    db.session.add(new_profile)
    db.session.commit()
    return jsonify({'message': 'Profile created successfully', 'uuid': new_profile.uuid}), 201

@profile_bp.route('/profiles', methods=['GET'])
# @token_required
# @access_required('view_profiles')
def get_all_profiles():
    profiles = ProfileModel.query.filter(ProfileModel.deleted_at == None).all()
    profiles_data = [profile.to_json() for profile in profiles]  # Usando to_json
    return jsonify(profiles_data), 200

@profile_bp.route('/profiles/<uuid>', methods=['GET'])
# @token_required
# @access_required('view_profiles')
def get_profile(uuid):
    profile = ProfileModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if profile:
        return jsonify(profile.to_json()), 200  # Usando to_json
    return jsonify({'message': 'Profile not found'}), 404

@profile_bp.route('/profiles/<uuid>', methods=['PUT'])
# @token_required
# @access_required('manage_profiles')
def update_profile(uuid):
    profile = ProfileModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if profile:
        data = request.json
        profile.name = data.get('name', profile.name).lower()
        profile.description = data.get('description', profile.description)
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    return jsonify({'message': 'Profile not found'}), 404

@profile_bp.route('/profiles/<uuid>', methods=['DELETE'])
# @token_required
# @access_required('manage_profiles')
def delete_profile(uuid):
    profile = ProfileModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if profile:
        profile.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Profile deleted successfully'}), 200
    return jsonify({'message': 'Profile not found'}), 404

@profile_bp.route('/profiles/<uuid_profile>/set_accesses', methods=['POST'])
# @token_required
# @access_required('assign_accesses')
def set_accesses(uuid_profile):
    data = request.json
    profile = ProfileModel.query.filter_by(uuid=uuid_profile, deleted_at=None).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    accesses_uuids = data.get('uuid_accesses', [])
    accesses = AccessModel.query.filter(AccessModel.uuid.in_(accesses_uuids), AccessModel.deleted_at == None).all()
    if accesses:
        profile.accesses = accesses
        db.session.commit()
        return jsonify({'message': 'Accesses assigned successfully'}), 200
    else:
        return jsonify({'message': 'No valid accesses found to assign'}), 400

@profile_bp.route('/profiles/<uuid_profile>/accesses', methods=['GET'])
# @token_required
# @access_required('view_accesses')
def get_profile_accesses(uuid_profile):
    profile = ProfileModel.query.filter_by(uuid=uuid_profile, deleted_at=None).first()
    if profile:
        accesses_data = [access.to_json() for access in profile.accesses]
        return jsonify(accesses_data), 200
    return jsonify({'message': 'Profile not found'}), 404
