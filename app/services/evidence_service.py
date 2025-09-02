from .. import db
from ..models.evidence import Evidence
from ..models.user import User
from math import ceil


class EvidenceService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    def list_evidence(self, org_id=None, control_id=None, q=None, page: int = 1, per_page: int = 20):
        query = self.db.query(Evidence, User).outerjoin(User, User.id == Evidence.uploaded_by)
        if org_id:
            query = query.filter(Evidence.organization_id == org_id)
        if control_id:
            query = query.filter(Evidence.control_id == control_id)
        if q:
            like = f"%{q}%"
            query = query.filter((Evidence.file_name.ilike(like)) | (Evidence.description.ilike(like)))
        query = query.order_by(Evidence.created_at.desc())
        total = query.count()
        rows = query.offset(max(0, (page - 1) * per_page)).limit(per_page).all()
        items = [
            {
                "id": str(ev.id),
                "file_name": ev.file_name,
                "file_type": ev.file_type,
                "file_size": ev.file_size,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "uploaded_by": (((u.first_name or '') + ' ' + (u.last_name or '')).strip() if u else None) or None,
            }
            for (ev, u) in rows
        ]
        pages = ceil(total / per_page) if per_page else 1
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}
from .. import db


class EvidenceService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    def upload_evidence(self, org_id, control_id, task_id, file_obj, metadata=None):
        return {"file_name": getattr(file_obj, 'filename', 'unknown')}
