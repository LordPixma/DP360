from .. import db
from ..models.task import Task
from ..models.user import User
from math import ceil


class TaskService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    def create_automated_tasks(self, org_id, control_id):
        return []

    def assign_task(self, task_id, user_id):
        return True

    def get_upcoming_deadlines(self, org_id, days_ahead=30):
        return []

    def mark_task_complete(self, task_id, evidence_files=None):
        return True

    def list_tasks(self, org_id=None, control_id=None, status=None, priority=None, q=None, page: int = 1, per_page: int = 20):
        query = (
            self.db.query(Task, User)
            .outerjoin(User, User.id == Task.assigned_user_id)
        )
        if org_id:
            query = query.filter(Task.organization_id == org_id)
        if control_id:
            query = query.filter(Task.control_id == control_id)
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if q:
            like = f"%{q}%"
            query = query.filter((Task.title.ilike(like)) | (Task.description.ilike(like)))
        # Order tasks: non-null due-date ascending, then created_at desc
        query = query.order_by(Task.due_date.is_(None), Task.due_date.asc(), Task.created_at.desc())
        total = query.count()
        items_raw = query.offset(max(0, (page - 1) * per_page)).limit(per_page).all()
        items = [
            {
                "id": str(t.id),
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "assignee_name": (((u.first_name or '') + ' ' + (u.last_name or '')).strip() if u else None) or None,
            }
            for (t, u) in items_raw
        ]
        pages = ceil(total / per_page) if per_page else 1
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}
