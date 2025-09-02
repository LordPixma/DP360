from flask import Blueprint, render_template

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/')
def list_tasks():
    return render_template('tasks/list.html', tasks=[])
