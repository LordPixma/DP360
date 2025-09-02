from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user


def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if getattr(current_user, 'role', None) != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
