import uuid
from datetime import datetime
from config.db_config import db
from sqlalchemy.orm import backref
from flask import abort

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    profiles = db.relationship('ProfileModel', secondary='profiles_users', lazy='subquery', backref=backref('users', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.uuid

    def to_json(self):
        profiles = [profile.to_json() for profile in self.profiles]
        return {
            'uuid': self.uuid,
            'firebase_uid': self.firebase_uid,
            'username': self.username,
            'email': self.email,
            'profiles': profiles,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_json(json_dict):
        # Verificación de campos requeridos y no vacíos
        required_fields = ['firebase_uid', 'username', 'email']
        for field in required_fields:
            if field not in json_dict or not json_dict[field].strip():
                abort(400, description=f"The '{field}' field is required and cannot be empty or just spaces.")

        # Verificar la unicidad de firebase_uid, username, y email
        if UserModel.query.filter_by(firebase_uid=json_dict['firebase_uid']).first():
            abort(400, description="The 'firebase_uid' is already in use.")
        if UserModel.query.filter_by(username=json_dict['username']).first():
            abort(400, description="The 'username' is already in use.")
        if UserModel.query.filter_by(email=json_dict['email']).first():
            abort(400, description="The 'email' is already in use.")

        return UserModel(
            firebase_uid=json_dict['firebase_uid'].strip(),
            username=json_dict['username'].strip(),
            email=json_dict['email'].strip()
        )