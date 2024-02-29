import uuid
from datetime import datetime
from config.db_config import db
from flask import abort

class PaymentMethodsModel(db.Model):
    __tablename__ = 'payment_methods'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<PaymentMethod %r>' % self.uuid

    def to_json(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_json(json_dict):
        # Verificar que el nombre esté presente y no sea solo espacios en blanco
        if 'name' not in json_dict or not json_dict['name'].strip():
            abort(400, description="The 'name' field is required and cannot be empty or just spaces.")

        # Verificar que la descripción no sea una cadena vacía si se proporciona
        if 'description' in json_dict and not json_dict['description'].strip():
            abort(400, description="The 'description' field cannot be an empty string or just spaces if provided.")

        return PaymentMethodsModel(
            name=json_dict['name'].strip(),
            description=json_dict.get('description', '').strip()
        )