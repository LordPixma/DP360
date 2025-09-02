from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    # Placeholder data
    return render_template(
        'dashboard/index.html',
        compliance_percentage=0,
        frameworks=[],
        tasks=[],
    )
