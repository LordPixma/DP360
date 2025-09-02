import os
from celery import Celery


def make_celery(app=None):
    broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    backend_url = broker_url
    celery = Celery(__name__, broker=broker_url, backend=backend_url)
    celery.conf.update(timezone='UTC', result_expires=3600)

    if app is not None:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask
    return celery
