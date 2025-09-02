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

    # Register CLI
    _register_cli(app)

    return app


# Avoid circular imports
from . import models  # noqa: E402,F401

# CLI seed command for demo data
def _register_cli(app: Flask):
    from .models.compliance_framework import ComplianceFramework
    from .models.control import Control
    from . import db

    @app.cli.command('seed-demo')
    def seed_demo():
        """Seed demo frameworks and controls."""
        from .models.organization import Organization
        from .models.organization_control import OrganizationControl
        from .models.user import User

        # Frameworks
        soc2 = ComplianceFramework.query.filter_by(code='SOC2').first() or ComplianceFramework(code='SOC2', name='SOC 2')
        iso  = ComplianceFramework.query.filter_by(code='ISO27001').first() or ComplianceFramework(code='ISO27001', name='ISO 27001')
        db.session.add_all([soc2, iso])
        db.session.flush()
        controls = [
            Control(framework_id=soc2.id, control_id='CC1.1', title='Logical Access Controls', risk_level='High'),
            Control(framework_id=soc2.id, control_id='CC1.2', title='Change Management', risk_level='Medium'),
            Control(framework_id=iso.id, control_id='A.9.2', title='User Access Management', risk_level='High'),
        ]
        for c in controls:
            if not Control.query.filter_by(control_id=c.control_id).first():
                db.session.add(c)
        db.session.flush()

        # Organization and users
        org = Organization.query.filter_by(name='Acme Corp').first() or Organization(name='Acme Corp')
        db.session.add(org)
        db.session.flush()

        if not User.query.filter_by(email='alice@example.com').first():
            u1 = User(organization_id=org.id, email='alice@example.com', first_name='Alice', last_name='Anderson', role='Compliance')
            u1.set_password('Password123!')
            db.session.add(u1)
        else:
            u1 = User.query.filter_by(email='alice@example.com').first()
        if not User.query.filter_by(email='bob@example.com').first():
            u2 = User(organization_id=org.id, email='bob@example.com', first_name='Bob', last_name='Baker', role='Security')
            u2.set_password('Password123!')
            db.session.add(u2)
        else:
            u2 = User.query.filter_by(email='bob@example.com').first()
        db.session.flush()

        # Map some controls
        cc11 = Control.query.filter_by(control_id='CC1.1').first()
        a92 = Control.query.filter_by(control_id='A.9.2').first()
        if cc11 and not OrganizationControl.query.filter_by(organization_id=org.id, control_id=cc11.id).first():
            db.session.add(OrganizationControl(organization_id=org.id, control_id=cc11.id, status='Implemented', assigned_user_id=u1.id))
        if a92 and not OrganizationControl.query.filter_by(organization_id=org.id, control_id=a92.id).first():
            db.session.add(OrganizationControl(organization_id=org.id, control_id=a92.id, status='In Progress', assigned_user_id=u2.id))

        db.session.commit()
        print('Seeded demo data (frameworks, controls, org, users, org_controls)')

    @app.cli.command('print-org-id')
    def print_org_id():
        """Print the seeded organization's UUID for quick linking."""
        from .models.organization import Organization
        org = Organization.query.filter_by(name='Acme Corp').first()
        if org:
            print(str(org.id))
        else:
            print('No seeded organization found. Run: flask seed-demo')

