import uuid
from datetime import datetime
from config.db_config import db
from flask import abort

class PromotionProductModel(db.Model):
    __tablename__ = 'promotion_products'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    promotion_uuid = db.Column(db.String(36), db.ForeignKey('promotions.uuid'), nullable=False)
    product_uuid = db.Column(db.String(36), db.ForeignKey('products.uuid'), nullable=False)
    discount_rate = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            'uuid': self.uuid,
            'promotion_uuid': self.promotion_uuid,
            'product_uuid': self.product_uuid,
            'discount_rate': self.discount_rate
        }
    
    @staticmethod
    def from_json(json_dict):
        # Verifica que todos los campos necesarios estén presentes
        if 'promotion_uuid' not in json_dict:
            abort(400, description="The 'promotion_uuid' field is required.")
        if 'product_uuid' not in json_dict:
            abort(400, description="The 'product_uuid' field is required.")
        if 'discount_rate' not in json_dict:
            abort(400, description="The 'discount_rate' field is required.")

        # Crear y retornar una instancia de PromotionProduct
        return PromotionProductModel(
            promotion_uuid=json_dict['promotion_uuid'],
            product_uuid=json_dict['product_uuid'],
            discount_rate=json_dict['discount_rate']
        )


