import uuid
from datetime import datetime
from config.db_config import db
from flask import abort

class EmployeeModel(db.Model):
    __tablename__ = 'employees'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_uuid = db.Column(db.String(36), db.ForeignKey('users.uuid'), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(80), nullable=True)  # Cargo o posición del empleado en la empresa
    phone = db.Column(db.String(20), nullable=True)  # Teléfono de contacto laboral
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Employee %r>' % self.uuid

    def to_json(self):
        return {
            'uuid': self.uuid,
            'user_uuid': self.user_uuid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'position': self.position,
            'phone': self.phone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_json(json_dict):
        from models import UserModel

        # Verificar campos requeridos
        required_fields = ['user_uuid', 'first_name', 'last_name']
        for field in required_fields:
            if field not in json_dict or not json_dict[field]:
                abort(400, description=f"{field} is required and cannot be empty.")

        # Verificar que user_uuid corresponda a un usuario existente
        if not UserModel.query.filter_by(uuid=json_dict['user_uuid']).first():
            abort(400, description="user_uuid does not correspond to a valid user.")
        
        # Verificaciones adicionales para campos opcionales que no deben estar vacíos si se proporcionan
        optional_fields = ['position', 'phone']
        for field in optional_fields:
            if field in json_dict and not json_dict[field]:
                abort(400, description=f"{field} cannot be an empty string.")

        return EmployeeModel(
            user_uuid=json_dict['user_uuid'],
            first_name=json_dict['first_name'],
            last_name=json_dict['last_name'],
            position=json_dict.get('position'),
            phone=json_dict.get('phone')
        )
