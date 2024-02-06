import uuid
from config.db_config import db

class AccessModel(db.Model):
    __tablename__ = 'accesses'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return '<Access %r>' % self.name
