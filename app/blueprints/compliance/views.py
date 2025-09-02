from flask import Blueprint, render_template

compliance_bp = Blueprint('compliance', __name__)


@compliance_bp.route('/')
def list_frameworks():
    return render_template('compliance/frameworks.html', frameworks=[])
