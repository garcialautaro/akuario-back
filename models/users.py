import uuid
from datetime import datetime
from config.db_config import db
from sqlalchemy.orm import backref

# Tabla intermedia perfiles_usuarios
profiles_users = db.Table('profiles_users',
    db.Column('user_uuid', db.String(36), db.ForeignKey('users.uuid'), primary_key=True),
    db.Column('profile_uuid', db.String(36), db.ForeignKey('profiles.uuid'), primary_key=True)
)

class UserModel(db.Model):
    __tablename__ = 'users'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200))
    company_name = db.Column(db.String(200))
    cuil = db.Column(db.String(20))
    dni = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    # Relación con ProfileModel aquí
    profiles = db.relationship('ProfileModel', secondary='profiles_users', lazy='subquery', backref=backref('users', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.username
    
