from flask import Flask
from .accesses import access_bp
from .auth import auth_bp
from .brands import brands_bp
from .categories import categories_bp
from .clients import clients_bp
from .employees import employees_bp
from .order_statuses import order_statuses_bp
from .orders import orders_bp
from .payment_methods import payment_methods_bp
from .photos import photos_bp
from .products import products_bp
from .profiles import profile_bp
from .promotions import promotions_bp
from .reviews import reviews_bp
from .users import users_bp

def init_app(app: Flask):
    app.register_blueprint(access_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(brands_bp, url_prefix='/api')
    app.register_blueprint(categories_bp, url_prefix='/api')
    app.register_blueprint(clients_bp, url_prefix='/api')
    app.register_blueprint(employees_bp, url_prefix='/api')
    app.register_blueprint(order_statuses_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(payment_methods_bp, url_prefix='/api')
    app.register_blueprint(photos_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(promotions_bp, url_prefix='/api')
    app.register_blueprint(reviews_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')

    # Registra otros blueprints aquí
