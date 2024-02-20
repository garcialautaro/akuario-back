import uuid
from flask import Blueprint, request, jsonify
from firebase_admin import auth
from models import UserModel, EmployeeModel, ClientModel
from config.db_config import db

# Crea un Blueprint para los endpoints de autenticación
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def create_user():
    data = request.json
    try:
        # Crea el usuario en Firebase
        firebase_user = auth.create_user(
            email=data['email'],
            password=data['password']
        )

        # Generar UUID para el usuario en la base de datos MySQL
        user_uuid = str(uuid.uuid4())

        # Crea el usuario en la base de datos MySQL
        user = UserModel(
            firebase_uid=firebase_user.uid,
            username=data['username'].lower(),
            email=data['email'].lower()
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({'firebase_uid': firebase_user.uid, 'user_uuid': user_uuid}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/validate_token', methods=['POST'])
def validate_token():
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token is missing'}), 400

    try:
        # Verifica el token con Firebase Admin
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']

        # Busca al usuario en tu base de datos local por firebase_uid
        user = UserModel.query.filter_by(firebase_uid=uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Intenta encontrar un empleado asociado a este usuario
        employee = EmployeeModel.query.filter_by(user_uuid=user.uuid).first()
        # Intenta encontrar un cliente asociado a este usuario
        client = ClientModel.query.filter_by(user_uuid=user.uuid).first()

        # Prepara el objeto de respuesta del usuario
        user_response = user.to_json()

        # Agrega información adicional del empleado o cliente si existe
        if employee:
            return jsonify({
                'message': 'Token is valid', 
                'user': user_response,
                'employee': employee.to_json()
                }), 200
            
        elif client:
            return jsonify({
                'message': 'Token is valid', 
                'user': user_response,
                'client': client.to_json()
                }), 200
        
    except auth.ExpiredIdTokenError:
        return jsonify({'error': 'Token has expired'}), 401
    except auth.RevokedIdTokenError:
        return jsonify({'error': 'Token has been revoked'}), 401
    except auth.InvalidIdTokenError:
        return jsonify({'error': 'Token is invalid'}), 401
    except Exception as e:
        # Captura cualquier otro error
        return jsonify({'error': str(e)}), 500
