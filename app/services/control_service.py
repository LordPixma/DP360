from .. import db
from ..models.control import Control
from ..models.compliance_framework import ComplianceFramework
from ..models.organization_control import OrganizationControl
from ..models.user import User
from ..models.task import Task
from ..models.evidence import Evidence
from sqlalchemy.orm import joinedload
from sqlalchemy import and_


class ControlService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    def list_controls(self, framework_code=None, q=None, status=None, owner=None, risk=None, org_id=None):
        query = self.db.query(Control)
        if framework_code:
            sub = self.db.query(ComplianceFramework.id).filter(ComplianceFramework.code == framework_code).subquery()
            query = query.filter(Control.framework_id.in_(sub))
        if q:
            like = f"%{q}%"
            query = query.filter((Control.control_id.ilike(like)) | (Control.title.ilike(like)) | (Control.description.ilike(like)))
        # Join OrganizationControl + User when org filters are used
        if org_id or status or owner:
            query = query.outerjoin(OrganizationControl, OrganizationControl.control_id == Control.id)
            query = query.outerjoin(User, User.id == OrganizationControl.assigned_user_id)
            if org_id:
                query = query.filter(OrganizationControl.organization_id == org_id)
            if status:
                query = query.filter(OrganizationControl.status == status)
            if owner:
                query = query.filter(User.email == owner)
        if risk:
            query = query.filter(Control.risk_level == risk)
        return query.order_by(Control.control_id.asc()).limit(200).all()

    def get_control_detail(self, control_uuid, org_id=None):
        q = (
            self.db.query(Control, ComplianceFramework, OrganizationControl, User)
            .outerjoin(ComplianceFramework, ComplianceFramework.id == Control.framework_id)
            .outerjoin(OrganizationControl, OrganizationControl.control_id == Control.id)
            .outerjoin(User, User.id == OrganizationControl.assigned_user_id)
            .filter(Control.id == control_uuid)
        )
        if org_id:
            q = q.filter(OrganizationControl.organization_id == org_id)
        row = q.first()
        if not row:
            return None
        control, framework, org_control, user = row
        # Related tasks (limited) and evidence (limited) for quick preview
        # Join to User for assignee names
        tq = self.db.query(Task, User).outerjoin(User, User.id == Task.assigned_user_id).filter(Task.control_id == control.id)
        if org_id:
            tq = tq.filter(Task.organization_id == org_id)
        task_rows = tq.order_by(Task.created_at.desc()).limit(5).all()

        eq = self.db.query(Evidence).filter(Evidence.control_id == control.id)
        if org_id:
            eq = eq.filter(Evidence.organization_id == org_id)
        evidence = eq.order_by(Evidence.created_at.desc()).limit(5).all()
        return {
            "id": str(control.id),
            "control_id": control.control_id,
            "title": control.title,
            "description": control.description,
            "framework": framework.name if framework else None,
            "framework_code": framework.code if framework else None,
            "risk_level": control.risk_level,
            "status": getattr(org_control, 'status', None),
            "owner": (f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email) if user else None,
            "next_review_date": getattr(org_control, 'next_review_date', None).isoformat() if getattr(org_control, 'next_review_date', None) else None,
            "tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "status": t.status,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "assignee_id": str(t.assigned_user_id) if t.assigned_user_id else None,
                    "assignee_name": ((u.first_name or '') + ' ' + (u.last_name or '')).strip() if u else None,
                }
                for (t, u) in task_rows
            ],
            "evidence": [
                {
                    "id": str(ev.id),
                    "file_name": ev.file_name,
                    "file_type": ev.file_type,
                    "file_size": ev.file_size,
                    "created_at": ev.created_at.isoformat() if ev.created_at else None,
                }
                for ev in evidence
            ],
        }

    def get_filter_options(self, org_id=None):
        statuses = []
        owners = []
        if org_id:
            # Distinct statuses from OrganizationControl
            statuses = [r[0] for r in self.db.query(OrganizationControl.status).filter(OrganizationControl.organization_id == org_id).distinct().all() if r[0]]
            # Owners assigned on controls within org
            owners = [r[0] for r in (
                self.db.query(User.email)
                .join(OrganizationControl, OrganizationControl.assigned_user_id == User.id)
                .filter(OrganizationControl.organization_id == org_id)
                .distinct()
                .all()
            )]
        return {"statuses": statuses, "owners": owners}
