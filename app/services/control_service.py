from .. import db


class ControlService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    def list_controls(self, framework_code=None):
        return []
