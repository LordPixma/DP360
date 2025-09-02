from .. import db
from ..models.compliance_framework import ComplianceFramework
from ..models.control import Control
from ..models.organization_control import OrganizationControl
from sqlalchemy import func


class ComplianceService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    def get_compliance_status(self, org_id, framework_code=None):
        return {"org_id": str(org_id), "percentage": 0}

    def initialize_framework(self, org_id, framework_code):
        return True

    def update_control_status(self, org_control_id, status, notes=None):
        return True

    def generate_compliance_report(self, org_id, framework_code=None):
        return {"org_id": str(org_id), "framework": framework_code, "report": {}}

    def list_frameworks_with_progress(self, org_id=None):
        """Return list of frameworks with control counts and simple % implemented for org if provided."""
        frameworks = self.db.session.query(ComplianceFramework).filter(ComplianceFramework.is_active.is_(True)).all()
        results = []
        for f in frameworks:
            total_controls = self.db.session.query(func.count(Control.id)).filter(Control.framework_id == f.id, Control.is_active.is_(True)).scalar() or 0
            implemented = 0
            if org_id and total_controls:
                implemented = (
                    self.db.session.query(func.count(OrganizationControl.id))
                    .join(Control, Control.id == OrganizationControl.control_id)
                    .filter(
                        OrganizationControl.organization_id == org_id,
                        Control.framework_id == f.id,
                        OrganizationControl.status.in_(["Implemented", "Compliant", "Completed"]),
                    )
                    .scalar()
                    or 0
                )
            pct = int(round((implemented / total_controls) * 100)) if total_controls else 0
            results.append(
                {
                    "id": f.id,
                    "code": f.code,
                    "name": f.name,
                    "description": f.description,
                    "controls": total_controls,
                    "percentage": pct,
                    "assessed": None,
                }
            )
        return results
