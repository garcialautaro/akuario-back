import uuid
from datetime import datetime
from config.db_config import db
from flask import abort
from models import BrandsModel

# Definición de la tabla intermedia ProductCategories
product_categories = db.Table('product_categories',
    db.Column('product_uuid', db.String(36), db.ForeignKey('products.uuid'), nullable=False),
    db.Column('category_uuid', db.String(36), db.ForeignKey('categories.uuid'), nullable=False)
)

class ProductsModel(db.Model):
    __tablename__ = 'products'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_uuid =  db.Column(db.String(36), db.ForeignKey('brands.uuid'), nullable=False)
    code = db.Column(db.String(5), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    sales_number = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    categories = db.relationship('CategoriesModel', secondary=product_categories, backref=db.backref('products', lazy='dynamic'))

    def __repr__(self):
        return '<Product %r>' % self.uuid

    def to_json(self):
        categories = [categories.to_json() for categories in self.categories]
        return {
            'uuid': self.uuid,
            'brand_uuid': self.brand_uuid,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'sales_number': self.sales_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'categories': categories
        }

    @staticmethod
    def from_json(json_dict):
            required_fields = ['brand_uuid', 'name', 'price', 'stock', 'sales_number']
            for field in required_fields:
                if field not in json_dict or json_dict[field] is None:
                    abort(400, description=f"{field} is required and cannot be empty.")

            if not BrandsModel.query.filter_by(uuid=json_dict['brand_uuid']).first():
                abort(400, description="brand_uuid does not correspond to a valid brand.")
            
            if 'code' in json_dict and (len(json_dict['code']) < 4 or len(json_dict['code']) > 5):
                abort(400, description="code must be between 4 and 5 characters.")

            if json_dict.get('price', 0) < 0:
                abort(400, description="price must be a non-negative number.")
            if json_dict.get('sales_number', 0) < 0:
                abort(400, description="sales_number must be a non-negative number.")

            return ProductsModel(
                brand_uuid=json_dict['brand_uuid'],
                name=json_dict['name'],
                description=json_dict.get('description', ''),
                price=json_dict['price'],
                stock=json_dict.get('stock', 0),
                sales_number=json_dict['sales_number'],
                code=json_dict.get('code', '')
            )
