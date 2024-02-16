import uuid
from datetime import datetime
from config.db_config import db
from flask import abort

class ClientModel(db.Model):
    __tablename__ = 'clients'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_uuid = db.Column(db.String(36), db.ForeignKey('users.uuid'), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dni = db.Column(db.String(20), nullable=True)
    cuil = db.Column(db.String(23), nullable=True)
    company_name = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    # Relaciones adicionales aquí según sea necesario

    def __repr__(self):
        return '<Client %r>' % self.uuid

    def to_json(self):
        return {
            'uuid': self.uuid,
            'user_uuid': self.user_uuid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'dni': self.dni,
            'cuil': self.cuil,
            'company_name': self.company_name,
            'address': self.address,
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
        optional_fields = ['dni', 'cuil', 'company_name', 'address', 'phone']
        for field in optional_fields:
            if field in json_dict and not json_dict[field]:
                abort(400, description=f"{field} cannot be an empty string.")

        return ClientModel(
            user_uuid=json_dict['user_uuid'],
            first_name=json_dict['first_name'],
            last_name=json_dict['last_name'],
            dni=json_dict.get('dni'),
            cuil=json_dict.get('cuil'),
            company_name=json_dict.get('company_name'),
            address=json_dict.get('address'),
            phone=json_dict.get('phone')
        )