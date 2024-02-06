from functools import wraps
from flask import request, jsonify
from firebase_admin import auth as firebase_auth
from models import UserModel
from config.db_config import db

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Elimina el prefijo 'Bearer ' del token, si existe
            if 'Bearer ' in token:
                token = token.replace('Bearer ', '', 1)
            decoded_token = firebase_auth.verify_id_token(token)
            firebase_uid = decoded_token['uid']
        except Exception as e:
            return jsonify({'message': 'Token is invalid', 'error': str(e)}), 401
        
        # Busca el usuario por firebase_uid
        user = UserModel.query.filter_by(firebase_uid=firebase_uid).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Añade el usuario al contexto de la solicitud
        request.user = user

        return f(*args, **kwargs)
    return decorated_function

def access_required(access_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(request, 'user', None)
            if user is None:
                return jsonify({'message': 'User not set, token required'}), 401
            
            # Verificar si el usuario tiene el acceso requerido
            has_access = False
            for profile in user.profiles:
                for access in profile.accesos:
                    if access.name == access_name:
                        has_access = True
                        break
                if has_access:
                    break
            
            if not has_access:
                return jsonify({'message': 'Access denied'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
