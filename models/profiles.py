import uuid
from config.db_config import db
from sqlalchemy.orm import backref

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
    # Relación muchos a muchos con Accesos
    accesses = db.relationship('AccessModel', secondary='profiles_accesses', backref=db.backref('profiles', lazy='dynamic'))

    def __repr__(self):
        return '<Profile %r>' % self.name

