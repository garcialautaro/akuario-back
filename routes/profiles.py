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
    new_profile = ProfileModel(
        name=data['name'].lower(),
        description=data.get('description', '')
    )
    db.session.add(new_profile)
    db.session.commit()
    return jsonify({'message': 'Profile created successfully', 'uuid': new_profile.uuid}), 201

@profile_bp.route('/profiles', methods=['GET'])
# @token_required
# @access_required('view_profiles')
def get_all_profiles():
    profiles = ProfileModel.query.all()
    profiles_data = [{'uuid': profile.uuid, 'name': profile.name, 'description': profile.description} for profile in profiles]
    return jsonify(profiles_data), 200

@profile_bp.route('/profiles/<uuid>', methods=['GET'])
# @token_required
# @access_required('view_profiles')
def get_profile(uuid):
    profile = ProfileModel.query.filter_by(uuid=uuid).first()
    if profile:
        return jsonify({'uuid': profile.uuid, 'name': profile.name, 'description': profile.description}), 200
    return jsonify({'message': 'Profile not found'}), 404

@profile_bp.route('/profiles/<uuid>', methods=['PUT'])
# @token_required
# @access_required('manage_profiles')
def update_profile(uuid):
    profile = ProfileModel.query.filter_by(uuid=uuid).first()
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
    profile = ProfileModel.query.filter_by(uuid=uuid).first()
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
    accesses_uuids = data.get('uuid_accesses', [])

    # Verificar si el array de UUIDs de accesos está vacío
    if not accesses_uuids:
        return jsonify({'error': 'No access UUIDs provided. At least one access UUID is required.'}), 400

    profile = ProfileModel.query.filter_by(uuid=uuid_profile).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    accesses = AccessModel.query.filter(AccessModel.uuid.in_(accesses_uuids)).all()
    profile.accesses = []  # Limpiar accesos existentes

    if accesses:
        profile.accesses.extend(accesses)
        db.session.commit()
        return jsonify({'message': 'Accesses assigned successfully'}), 200
    else:
        return jsonify({'message': 'No valid accesses found to assign'}), 400

@profile_bp.route('/profiles/<uuid_profile>/accesses', methods=['GET'])
# @token_required
# @access_required('assign_accesses')
def get_profile_accesses(uuid_profile):
    profile = ProfileModel.query.filter_by(uuid=uuid_profile).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    accesses = profile.accesses
    accesses_data = [{
        'uuid': access.uuid,
        'name': access.name,
        'description': access.description,
        # Agrega otros campos del modelo AccessModel si es necesario
    } for access in accesses]

    return jsonify(accesses_data), 200
