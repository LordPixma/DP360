import uuid
from .. import db
from sqlalchemy.dialects.postgresql import UUID


class ComplianceFramework(db.Model):
    __tablename__ = 'compliance_frameworks'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
