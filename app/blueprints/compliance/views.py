from flask import Blueprint, render_template, request
from ...services.compliance_service import ComplianceService

compliance_bp = Blueprint('compliance', __name__)


@compliance_bp.route('/')
def list_frameworks():
    org_id = request.args.get('org')  # optional
    svc = ComplianceService()
    frameworks = svc.list_frameworks_with_progress(org_id)
    return render_template('compliance/frameworks.html', frameworks=frameworks)
