import uuid
from datetime import datetime
from config.db_config import db
from flask import abort
from sqlalchemy import func

# Tabla intermedia perfiles_accesos
order_details = db.Table('order_details',
    db.Column('order_uuid', db.String(36), db.ForeignKey('orders.uuid'), primary_key=True),
    db.Column('product_uuid', db.String(36), db.ForeignKey('products.uuid'), primary_key=True),
    db.Column('price', db.Float, nullable=False),
    db.Column('quantity', db.Integer, nullable=False),
    db.Column('description', db.String(150)),
)

class OrderModel(db.Model):
    __tablename__ = 'orders'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.Integer, autoincrement=True)
    client_uuid = db.Column(db.String(36), db.ForeignKey('clients.uuid'), nullable=False)
    status_uuid = db.Column(db.String(36), db.ForeignKey('order_statuses.uuid'), nullable=False)
    transaction_uuid = db.Column(db.String(36), nullable=True)
    payment_method_uuid = db.Column(db.String(36), db.ForeignKey('payment_methods.uuid'), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    details = db.relationship('ProductsModel', secondary='order_details', backref=db.backref('orders', lazy='dynamic'))
    
    def __repr__(self):
        return '<Order %r>' % self.uuid

    def to_json(self):
        return {
            'uuid': self.uuid,
            'client_uuid': self.client_uuid,
            'status_uuid': self.status_uuid,
            'code': self.code,
            'purchase_date': self.purchase_date.isoformat(),
            'total': self.total,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_json(json_dict):
        # Importaciones locales para evitar importaciones circulares
        from models import ClientModel, OrderStatusesModel, PaymentMethodsModel

        # Verificar la existencia de client_uuid
        if not ClientModel.query.filter_by(uuid=json_dict['client_uuid']).first():
            abort(400, description="client_uuid does not correspond to a valid client.")
        
        # Verificar la existencia de status_uuid
        if not OrderStatusesModel.query.filter_by(uuid=json_dict['status_uuid']).first():
            abort(400, description="status_uuid does not correspond to a valid order status.")
        
        # Verificar la existencia de payment_method_uuid
        if 'payment_method_uuid' in json_dict and not PaymentMethodsModel.query.filter_by(uuid=json_dict['payment_method_uuid']).first():
            abort(400, description="payment_method_uuid does not correspond to a valid payment method.")

        # Convertir purchase_date de string ISO a datetime
        try:
            purchase_date = datetime.fromisoformat(json_dict['purchase_date'])
        except ValueError:
            abort(400, description="purchase_date must be a valid ISO date string.")

        # Consultar el máximo valor actual de 'code' en las órdenes existentes y sumarle uno
        max_code = db.session.query(func.max(OrderModel.code)).scalar()
        if max_code is None:
            # En caso de que no haya órdenes, empezamos desde 1
            next_code = 1
        else:
            next_code = max_code + 1

        return OrderModel(
            client_uuid=json_dict['client_uuid'],
            status_uuid=json_dict['status_uuid'],
            transaction_uuid=json_dict.get('transaction_uuid', None),
            payment_method_uuid=json_dict.get('payment_method_uuid'),
            purchase_date=purchase_date,
            code=next_code,
        )