from datetime import date, datetime
import uuid
from .. import db
from sqlalchemy.dialects.postgresql import UUID


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'))
    control_id = db.Column(UUID(as_uuid=True), db.ForeignKey('controls.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(50))
    assigned_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
