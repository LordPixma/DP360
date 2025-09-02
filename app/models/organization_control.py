from datetime import date, datetime
import uuid
from .. import db
from sqlalchemy.dialects.postgresql import UUID


class OrganizationControl(db.Model):
    __tablename__ = 'organization_controls'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'))
    control_id = db.Column(UUID(as_uuid=True), db.ForeignKey('controls.id'))
    status = db.Column(db.String(50))
    implementation_date = db.Column(db.Date)
    next_review_date = db.Column(db.Date)
    assigned_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
