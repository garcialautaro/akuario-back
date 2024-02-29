import uuid
from datetime import datetime
from config.db_config import db
from flask import abort
import base64

class PhotosModel(db.Model):
    __tablename__ = 'photos'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    uuid_product = db.Column(db.String(36), db.ForeignKey('products.uuid'), nullable=False)
    blob = db.Column(db.LargeBinary, nullable=False)  # Tipo de dato adecuado para MySQL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Photo %r>' % self.uuid

    def to_json(self):
        photo_encoded = base64.b64encode(self.blob).decode('utf-8') if self.blob else None
        return {
            'uuid': self.uuid,
            'uuid_product': self.uuid_product,
            'blob': photo_encoded,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_json(json_dict):
        from models import ProductsModel  # Importa el modelo ProductsModel aquí para evitar una importación circular
        
        if 'uuid_product' not in json_dict:
            abort(400, description="The 'uuid_product' field is required.")
        
        # Verifica si el uuid_product corresponde a un producto existente
        product = ProductsModel.query.filter_by(uuid=json_dict['uuid_product']).first()
        if not product:
            abort(400, description="uuid_product does not correspond to a valid product.")

        # Asegura que el blob está presente y no está vacío
        if 'blob' not in json_dict or not json_dict['blob']:
            abort(400, description="The 'blob' field is required and cannot be empty.")
        
        photo_decoded = base64.b64decode(json_dict['blob']) if 'blob' in json_dict and json_dict['blob'] else None
        
        return PhotosModel(
            uuid_product=json_dict['uuid_product'],
            blob=photo_decoded
        )
