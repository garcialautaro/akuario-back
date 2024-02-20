from datetime import datetime
from flask import Blueprint, request, jsonify
from config.db_config import db
from models import UserModel, ClientModel
from firebase_admin import auth as firebase_auth
# from decorators import token_required, access_required

clients_bp = Blueprint('clients_bp', __name__)

@clients_bp.route('/clients', methods=['POST'])
# @token_required
# @access_required('manage_clients')
def create_client():
    data = request.json
    firebase_user = None  # Inicializa la variable fuera del bloque try para poder acceder después
    try:
        firebase_user = firebase_auth.create_user(
            email=data['email'],
            password=data['password']
        )
        
        user_data = {
            'firebase_uid': firebase_user.uid,
            'username': data['username'].lower(),
            'email': data['email'].lower()
        }
        user = UserModel.from_json(user_data)
        db.session.add(user)
        db.session.flush()
        
        client_data = {
            'user_uuid': user.uuid,
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'dni': data.get('dni'),
            'cuil': data.get('cuil'),
            'company_name': data.get('company_name'),
            'address': data.get('address'),
            'phone': data.get('phone'),
        }
        new_client = ClientModel.from_json(client_data)
        db.session.add(new_client)
        
        db.session.commit()
        return jsonify(
            {'message': 'Client created successfully', 
             'user_uuid': user.uuid, 
             'employee_uuid': new_client.uuid,
             'firebase_uid': firebase_user.uid}), 201
    except Exception as e:
        db.session.rollback()
        if firebase_user:
            try:
                # Intenta eliminar el usuario de Firebase si fue creado previamente
                firebase_auth.delete_user(firebase_user.uid)
            except Exception:
                # Si falla la eliminación, no hacer nada o loggear el error según sea necesario
                pass
        return jsonify({'error': str(e)}), 400


@clients_bp.route('/clients', methods=['GET'])
# @token_required
# @access_required('view_clients')
def get_all_clients():
    clients = ClientModel.query.filter(ClientModel.deleted_at == None).all()
    clients_data = [client.to_json() for client in clients]
    return jsonify(clients_data), 200

@clients_bp.route('/clients/<uuid>', methods=['GET'])
# @token_required
# @access_required('view_clients')
def get_client(uuid):
    client = ClientModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if client:
        return jsonify(client.to_json()), 200
    return jsonify({'message': 'Client not found'}), 404

@clients_bp.route('/clients/<uuid>', methods=['PUT'])
# @token_required
# @access_required('manage_clients')
def update_client(uuid):
    client = ClientModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if client:
        data = request.json
        # Actualiza los campos con los datos proporcionados, manteniendo los valores actuales si no se especifican nuevos
        client.first_name = data.get('first_name', client.first_name)
        client.last_name = data.get('last_name', client.last_name)
        client.dni = data.get('dni', client.dni)
        client.cuil = data.get('cuil', client.cuil)
        client.company_name = data.get('company_name', client.company_name)
        client.address = data.get('address', client.address)
        client.phone = data.get('phone', client.phone)
        db.session.commit()
        return jsonify({'message': 'Client updated successfully'}), 200
    return jsonify({'message': 'Client not found'}), 404

@clients_bp.route('/clients/<uuid>', methods=['DELETE'])
# @token_required
# @access_required('manage_clients')
def delete_client(uuid):
    client = ClientModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if client:
        success, message = disable_user_in_firebase(client.user_uuid)  # Reutilizar la función de deshabilitación
        if success:
            client.deleted_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'message': f'Client and associated user {message}'}), 200
        else:
            return jsonify({'error': message}), 500
    return jsonify({'message': 'Client not found'}), 404

# Suponiendo que esta función está en el mismo archivo o tienes acceso a firebase_auth
def disable_user_in_firebase(user_uuid):
    user = UserModel.query.filter_by(uuid=user_uuid, deleted_at=None).first()
    if user:
        user.deleted_at = datetime.utcnow()
        try:
            firebase_auth.update_user(user.firebase_uid, disabled=True)
            db.session.commit()
            return True, 'User disabled successfully'
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to disable user in Firebase: {str(e)}'
    else:
        return False, 'User not found'