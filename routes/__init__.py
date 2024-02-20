from flask import Flask
from .users import users_bp  # Importa otros blueprints según sea necesario
from .auth import auth_bp
from .accesses import access_bp
from .profiles import profile_bp
from .brands import brands_bp
from .clients import clients_bp
from .employees import employees_bp
from .order_statuses import order_statuses_bp


def init_app(app: Flask):
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(access_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(brands_bp, url_prefix='/api')
    app.register_blueprint(clients_bp, url_prefix='/api')
    app.register_blueprint(employees_bp, url_prefix='/api')
    app.register_blueprint(order_statuses_bp, url_prefix='/api')

    # Registra otros blueprints aquí
