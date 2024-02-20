from flask import Blueprint, request, jsonify
from config.db_config import db
from models import UserModel, EmployeeModel
from firebase_admin import auth as firebase_auth
from datetime import datetime 

employees_bp = Blueprint('employees_bp', __name__)

@employees_bp.route('/employees', methods=['POST'])
# @token_required
# @access_required('manage_employees')
def create_employee():
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

        employee_data = {
            'user_uuid': user.uuid, 
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'position': data.get('position'),
            'phone': data.get('phone'), 
        }
        employee = EmployeeModel.from_json(employee_data)
        db.session.add(employee)
        
        db.session.commit()
        return jsonify(
            {'message': 'Employee created successfully', 
             'user_uuid': user.uuid, 
             'employee_uuid': employee.uuid,
             'firebase_uid': firebase_user.uid
             }), 201
    except Exception as e:
        db.session.rollback()
        # Intenta eliminar el usuario de Firebase si fue creado previamente
        if firebase_user:
            try:
                firebase_auth.delete_user(firebase_user.uid)
            except Exception:
                # Si falla la eliminación, no hacer nada o loggear el error según sea necesario
                pass
        return jsonify({'error': str(e)}), 400


@employees_bp.route('/employees', methods=['GET'])
# @token_required
# @access_required('view_employees')
def get_all_employees():
    employees = EmployeeModel.query.filter(EmployeeModel.deleted_at == None).all()
    employees_data = [employee.to_json() for employee in employees]
    return jsonify(employees_data), 200

@employees_bp.route('/employees/<uuid>', methods=['GET'])
# @token_required
# @access_required('view_employee')
def get_employee(uuid):
    employee = EmployeeModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if employee:
        return jsonify(employee.to_json()), 200
    return jsonify({'message': 'Employee not found'}), 404

@employees_bp.route('/employees/<uuid>', methods=['PUT'])
# @token_required
# @access_required('manage_employees')
def update_employee(uuid):
    employee = EmployeeModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if employee:
        data = request.json

        employee.first_name = data.get('first_name', employee.first_name)
        employee.last_name = data.get('last_name', employee.last_name)
        employee.position = data.get('position', employee.position)
        employee.phone = data.get('phone', employee.phone)

        try:
            db.session.commit()
            return jsonify({'message': 'Employee updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'message': 'Employee not found'}), 404

@employees_bp.route('/employees/<uuid>', methods=['DELETE'])
# @token_required
# @access_required('manage_employees')
def delete_employee(uuid):
    employee = EmployeeModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if employee:
        # Busca el usuario asociado para obtener su firebase_uid
        user = UserModel.query.filter_by(uuid=employee.user_uuid, deleted_at=None).first()
        if user:
            # Intenta deshabilitar el usuario en Firebase
            success, message = disable_user_in_firebase(user.firebase_uid)
            if success:
                # Marca el empleado como eliminado en la base de datos
                employee.deleted_at = datetime.utcnow()
                db.session.commit()
                return jsonify({'message': 'Employee and associated user disabled successfully'}), 200
            else:
                # Si falla la deshabilitación en Firebase, devuelve un error
                return jsonify({'error': message}), 500
        else:
            return jsonify({'message': 'Associated user not found'}), 404
    else:
        return jsonify({'message': 'Employee not found'}), 404


def disable_user_in_firebase(firebase_uid):
    try:
        firebase_auth.update_user(
            firebase_uid,
            disabled=True
        )
        return True, 'User disabled successfully in Firebase.'
    except Exception as e:
        return False, f'Failed to disable user in Firebase: {str(e)}'
