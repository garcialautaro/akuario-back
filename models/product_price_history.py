import uuid
from datetime import datetime
from config.db_config import db
from flask import abort

class ProductPriceHistoryModel(db.Model):
    __tablename__ = 'product_price_history'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    uuid_product = db.Column(db.String(36), db.ForeignKey('products.uuid'), nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    change_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<ProductPriceHistory %r>' % self.uuid

    def to_json(self):
        return {
            'uuid': self.uuid,
            'uuid_product': self.uuid_product,
            'previous_price': self.previous_price,
            'new_price': self.new_price,
            'change_date': self.change_date.isoformat()
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
        
        # Asegura que los campos de precios sean flotantes válidos
        try:
            previous_price = float(json_dict['previous_price'])
            new_price = float(json_dict['new_price'])
        except ValueError:
            abort(400, description="Prices must be valid floats.")
        
        # Asegura que la fecha de cambio sea una fecha y hora válida
        try:
            change_date = datetime.fromisoformat(json_dict['change_date'])
        except ValueError:
            abort(400, description="change_date must be a valid ISO date string.")

        return ProductPriceHistoryModel(
            uuid_product=json_dict['uuid_product'],
            previous_price=previous_price,
            new_price=new_price,
            change_date=change_date
        )
