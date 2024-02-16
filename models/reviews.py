import uuid
from datetime import datetime
from config.db_config import db

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
        return ReviewsModel(
            client_uuid=json_dict['client_uuid'],
            product_uuid=json_dict['product_uuid'],
            rating=json_dict['rating'],
            description=json_dict.get('description', '')
        )
