from .. import db


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
