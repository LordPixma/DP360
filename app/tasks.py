from . import create_app

app = create_app()

if app.celery:
    celery = app.celery

    @celery.task
    def generate_recurring_tasks():
        return []

    @celery.task
    def send_deadline_notifications():
        return 0

    @celery.task
    def update_compliance_scores():
        return True

    @celery.task
    def sync_external_integrations():
        return True
