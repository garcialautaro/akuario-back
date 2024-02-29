import uuid
from datetime import datetime
from config.db_config import db
from flask import abort

# Tabla intermedia perfiles_accesos
profiles_accesses = db.Table('profiles_accesses',
    db.Column('profile_uuid', db.String(36), db.ForeignKey('profiles.uuid'), primary_key=True),
    db.Column('access_uuid', db.String(36), db.ForeignKey('accesses.uuid'), primary_key=True)
)

class ProfileModel(db.Model):
    __tablename__ = 'profiles'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(255))
    accesses = db.relationship('AccessModel', secondary='profiles_accesses', backref=db.backref('profiles', lazy='dynamic'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Profile %r>' % self.uuid

    def to_json(self):
        accesses = [access.to_json() for access in self.accesses]
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'accesses': accesses,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }
    
    @staticmethod
    def from_json(json_dict):
        if 'name' not in json_dict or not json_dict['name'].strip():
            abort(400, description="The 'name' field is required and cannot be empty or just spaces.")

        if 'description' in json_dict and not json_dict['description'].strip():
            abort(400, description="The 'description' field cannot be an empty string or just spaces if provided.")

        return ProfileModel(
            name=json_dict['name'].strip(),
            description=json_dict.get('description', '').strip()
        )