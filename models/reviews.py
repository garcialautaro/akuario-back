import uuid
from datetime import datetime
from config.db_config import db
from models import ClientModel, ProductsModel
from flask import abort

class ReviewsModel(db.Model):
    __tablename__ = 'reviews'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_uuid = db.Column(db.String(36), db.ForeignKey('clients.uuid'), nullable=False)
    product_uuid = db.Column(db.String(36), db.ForeignKey('products.uuid'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Review %r>' % self.uuid

    def to_json(self):
        return {
            'uuid': self.uuid,
            'client_uuid': self.client_uuid,
            'product_uuid': self.product_uuid,
            'rating': self.rating,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_json(json_dict):
        # Verificar que los UUIDs del cliente y del producto estén presentes
        if not json_dict.get('client_uuid') or not json_dict.get('product_uuid'):
            abort(400, description="Both 'client_uuid' and 'product_uuid' are required and cannot be empty.")
        
        # Verificar que el client_uuid corresponda a un cliente existente
        if not ClientModel.query.filter_by(uuid=json_dict['client_uuid']).first():
            abort(400, description="The 'client_uuid' does not correspond to a valid client.")

        # Verificar que el product_uuid corresponda a un producto existente
        if not ProductsModel.query.filter_by(uuid=json_dict['product_uuid']).first():
            abort(400, description="The 'product_uuid' does not correspond to a valid product.")

        # Verificar el rating
        if 'rating' not in json_dict or type(json_dict['rating']) is not int or not (1 <= json_dict['rating'] <= 10):
            abort(400, description="The 'rating' must be an integer between 1 and 10.")

        # Verificar descripción
        if 'description' in json_dict and not json_dict['description'].strip():
            abort(400, description="The 'description' field cannot be an empty string or just spaces if provided.")

        return ReviewsModel(
            client_uuid=json_dict['client_uuid'],
            product_uuid=json_dict['product_uuid'],
            rating=json_dict['rating'],
            description=json_dict.get('description', '').strip()
        )