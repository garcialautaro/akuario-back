import os
import firebase_admin
from firebase_admin import credentials

def init_firebase():
    if not firebase_admin._apps:
        script_dir = os.path.dirname(__file__)
        cred_path = os.path.join(script_dir, '../akuario-firebase.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase inicializado correctamente.")
    else:
        print("Firebase ya estaba inicializado.")
