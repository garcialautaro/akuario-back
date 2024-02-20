import uuid
from datetime import datetime
from config.db_config import db
import base64

# Definición de la tabla intermedia ProductCategories
product_categories = db.Table('product_categories',
    db.Column('product_uuid', db.String(36), db.ForeignKey('products.uuid'), nullable=False),
    db.Column('category_uuid', db.String(36), db.ForeignKey('categories.uuid'), nullable=False)
)

class ProductsModel(db.Model):
    __tablename__ = 'products'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_uuid =  db.Column(db.String(36), db.ForeignKey('brands.uuid'), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    sales_number = db.Column(db.Integer, nullable=False, default=0)
    code = db.Column(db.String(5), nullable=True)
    photo = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    categories = db.relationship('CategoriesModel', secondary=product_categories, backref=db.backref('products', lazy='dynamic'))

    def __repr__(self):
        return '<Product %r>' % self.uuid

    def to_json(self):
        categories = [categories.to_json() for categories in self.categories]
        photo_encoded = base64.b64encode(self.photo).decode('utf-8') if self.photo else None
        return {
            'uuid': self.uuid,
            'brand_uuid': self.brand_uuid,
            'description': self.description,
            'name': self.name,
            'price': self.price,
            'sales_number': self.sales_number,
            'code': self.code,
            'photo': photo_encoded,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'categories': categories
        }

    @staticmethod
    def from_json(json_dict):
        photo_decoded = base64.b64decode(json_dict['photo']) if 'photo' in json_dict and json_dict['photo'] else None
        return ProductsModel(
            brand_uuid=json_dict['brand_uuid'],
            description=json_dict['description'],
            name=json_dict['name'],
            price=json_dict.get('price'),
            sales_number=json_dict.get('sales_number'),
            code=json_dict.get('code'), #! DEBE TENER ENTRE 4 y 5 CARACTERES
            photo=photo_decoded
        )
