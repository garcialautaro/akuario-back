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

        if 'name' not in json_dict or not json_dict['name'].strip():
            abort(400, description="The 'name' field is required and cannot be empty.")
            
        if 'description' in json_dict and not json_dict['description'].strip():
            abort(400, description="The 'description' field cannot be an empty string if provided.")
            
        return OrderStatusesModel(
            name=json_dict['name'],
            description=json_dict['description']
        )