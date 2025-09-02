from datetime import datetime
import uuid
from .. import db
from sqlalchemy.dialects.postgresql import UUID


class Evidence(db.Model):
    __tablename__ = 'evidence'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.id'))
    control_id = db.Column(UUID(as_uuid=True), db.ForeignKey('controls.id'))
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tasks.id'))
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    uploaded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
