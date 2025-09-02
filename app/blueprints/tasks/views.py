from flask import Blueprint, render_template, request
from ...services.task_service import TaskService

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/')
def list_tasks():
    svc = TaskService()
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(100, int(request.args.get('per_page', 20)))
    data = svc.list_tasks(
        org_id=request.args.get('org'),
        control_id=request.args.get('control'),
        status=request.args.get('status'),
        priority=request.args.get('priority'),
        q=request.args.get('q'),
        page=page,
        per_page=per_page,
    )
    return render_template('tasks/list.html', tasks=data["items"], pagination={k: data[k] for k in ("page","per_page","total","pages")})
