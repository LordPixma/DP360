from flask import Blueprint, render_template, request
from ...services.evidence_service import EvidenceService

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
def list_reports():
    return render_template('reports/compliance_status.html')


@reports_bp.route('/evidence')
def list_evidence():
    svc = EvidenceService()
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(100, int(request.args.get('per_page', 20)))
    data = svc.list_evidence(
        org_id=request.args.get('org'),
        control_id=request.args.get('control'),
        q=request.args.get('q'),
        page=page,
        per_page=per_page,
    )
    return render_template('reports/evidence_list.html', items=data['items'], pagination={k: data[k] for k in ("page","per_page","total","pages")})
