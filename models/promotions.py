import uuid
from datetime import datetime
from config.db_config import db
from flask import abort

# Definición de la tabla intermedia PromotionProducts
promotion_products = db.Table('promotion_products',
    db.Column('uuid', db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    db.Column('promotion_uuid', db.String(36), db.ForeignKey('promotions.uuid'), nullable=False),
    db.Column('product_uuid', db.String(36), db.ForeignKey('products.uuid'), nullable=False),
    db.Column('discount_rate', db.Float, nullable=False)
)

class PromotionsModel(db.Model):
    __tablename__ = 'promotions'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    products = db.relationship('ProductsModel', secondary=promotion_products, backref=db.backref('promotions', lazy='dynamic'))

    def __repr__(self):
        return '<Promotion %r>' % self.name

    def to_json(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_json(json_dict):
        # Verificar que el campo 'name' esté presente y no sea solo espacios en blanco
        if 'name' not in json_dict or not json_dict['name'].strip():
            abort(400, description="The 'name' field is required and cannot be empty or just spaces.")

        # Verificar que el campo 'description', si se proporciona, no sea solo espacios en blanco
        if 'description' in json_dict and not json_dict['description'].strip():
            abort(400, description="The 'description' field cannot be an empty string or just spaces if provided.")

        # Verificar la validez de 'start_date' y 'end_date'
        try:
            start_date = datetime.fromisoformat(json_dict['start_date'])
            end_date = datetime.fromisoformat(json_dict['end_date'])
            if start_date >= end_date:
                abort(400, description="The 'start_date' must be before the 'end_date'.")
        except ValueError:
            abort(400, description="Invalid date format. Please use ISO format for 'start_date' and 'end_date'.")

        return PromotionsModel(
            name=json_dict['name'].strip(),
            description=json_dict.get('description', '').strip(),
            start_date=start_date,
            end_date=end_date
        )
