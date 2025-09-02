from flask import Blueprint, render_template

integrations_bp = Blueprint('integrations', __name__)


@integrations_bp.route('/')
def list_integrations():
    return render_template('dashboard/index.html')
