import uuid
from flask import Blueprint, request, jsonify
from firebase_admin import auth
from models import UserModel
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
            email=data['email'].lower(),
            address=data.get('address', ''),
            company_name=data.get('company_name', ''),
            cuil=data.get('cuil', ''),
            dni=data.get('dni', ''),
            uuid=user_uuid
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

        # Prepara el objeto de usuario para la respuesta, excluyendo información sensible
        user_data = {
            'uuid': user.uuid,
            'firebase_uid': user.firebase_uid,
            'username': user.username,
            'email': user.email,
            # Incluye otros campos según sea necesario, pero omite campos sensibles como contraseñas o tokens
            'address': user.address,
            'company_name': user.company_name,
            'cuil': user.cuil,
            'dni': user.dni,
            # Puedes incluir más campos aquí
        }

        # Si el token es válido y el usuario existe, devuelve una respuesta positiva con el objeto de usuario
        return jsonify({'message': 'Token is valid', 'user': user_data}), 200
    except auth.ExpiredIdTokenError:
        return jsonify({'error': 'Token has expired'}), 401
    except auth.RevokedIdTokenError:
        return jsonify({'error': 'Token has been revoked'}), 401
    except auth.InvalidIdTokenError:
        return jsonify({'error': 'Token is invalid'}), 401
    except Exception as e:
        # Captura cualquier otro error
        return jsonify({'error': str(e)}), 500
