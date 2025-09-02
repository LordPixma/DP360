import uuid
from .. import db
from sqlalchemy.dialects.postgresql import UUID


class Control(db.Model):
    __tablename__ = 'controls'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_id = db.Column(UUID(as_uuid=True), db.ForeignKey('compliance_frameworks.id'))
    control_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    control_type = db.Column(db.String(50))
    risk_level = db.Column(db.String(20))
    testing_frequency = db.Column(db.String(50))
    owner_role = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
