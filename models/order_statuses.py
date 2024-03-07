import uuid
from datetime import datetime
from config.db_config import db
from flask import abort

class OrderStatusesModel(db.Model):
    __tablename__ = 'order_statuses'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(5), unique=True, nullable=False)
    color = db.Column(db.String(15), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<OrderStatus %r>' % self.uuid

    def to_json(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'code': self.code,
            'color': self.color,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_json(json_dict):
        # Validación para 'name'
        if 'name' not in json_dict or not json_dict['name'].strip():
            abort(400, description="The 'name' field is required and cannot be empty.")

        # Validación para 'code'
        if 'code' not in json_dict or not json_dict['code'].strip():
            abort(400, description="The 'code' field is required and cannot be empty.")
        if len(json_dict['code']) > 5:
            abort(400, description="The 'code' field must be no longer than 5 characters.")

        # Validación para 'color'
        if 'color' not in json_dict or not json_dict['color'].strip():
            abort(400, description="The 'color' field is required and cannot be empty.")
        # Esta es una validación básica para un color hexadecimal
        if not json_dict['color'].startswith('#') or len(json_dict['color']) not in [4, 7]:
            abort(400, description="The 'color' field must be a valid hexadecimal color code.")

        # Validación para 'description'
        if 'description' in json_dict and not json_dict['description'].strip():
            abort(400, description="The 'description' field cannot be an empty string if provided.")
        
        return OrderStatusesModel(
            name=json_dict['name'].strip(),
            code=json_dict['code'].strip().upper(),  # Normalizar el código a mayúsculas
            color=json_dict['color'].strip(),
            description=json_dict.get('description', '').strip()
        )