from .. import db


class EvidenceService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    def upload_evidence(self, org_id, control_id, task_id, file_obj, metadata=None):
        return {"file_name": getattr(file_obj, 'filename', 'unknown')}
