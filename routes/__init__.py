from flask import Flask
from .users import users_bp  # Importa otros blueprints según sea necesario
from .auth import auth_bp
from .accesses import access_bp
from .profiles import profile_bp



def init_app(app: Flask):
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(access_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')

    # Registra otros blueprints aquí
