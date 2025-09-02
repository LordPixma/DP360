from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .. import db


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100))
    size_category = db.Column(db.String(20))
    subscription_tier = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship('User', backref='organization', lazy=True)
