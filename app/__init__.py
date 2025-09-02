from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import get_config
from .celery_app import make_celery

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from .blueprints.auth.views import auth_bp
    from .blueprints.dashboard.views import dashboard_bp
    from .blueprints.compliance.views import compliance_bp
    from .blueprints.controls.views import controls_bp
    from .blueprints.tasks.views import tasks_bp
    from .blueprints.reports.views import reports_bp
    from .blueprints.integrations.views import integrations_bp
    from .blueprints.admin.views import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(compliance_bp, url_prefix='/compliance')
    app.register_blueprint(controls_bp, url_prefix='/controls')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(integrations_bp, url_prefix='/integrations')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    # Setup Celery (optional runtime)
    try:
        app.celery = make_celery(app)
    except Exception:
        app.celery = None

    return app


# Avoid circular imports
from . import models  # noqa: E402,F401
