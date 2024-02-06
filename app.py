from flask import Flask
from dotenv import load_dotenv
from config.firebase_config import init_firebase
from config.db_config import init_db, db
from routes import init_app

app = Flask(__name__)

# Cargar variables de entorno
load_dotenv()

# Inicializa Firebase y la base de datos
init_firebase()
init_db(app)

# Crea las tablas en la base de datos
with app.app_context():
    db.create_all()

# Inicializar y registrar todos los blueprints
init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
