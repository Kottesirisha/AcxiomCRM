"""
AcxiomCRM – Route Helpers
Shared utilities for audit logging and access control decorators.
"""

from functools import wraps
from flask import abort, request, flash, redirect, url_for
from flask_login import current_user
from extensions import db
from models import AuditLog


def log_audit(action, entity, entity_id=None, description=None):
    """Log an audit entry."""
    from flask_login import current_user
    log = AuditLog(
        user_id=current_user.id if current_user and current_user.is_authenticated else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        description=description,
        ip_address=request.remote_addr if request else None,
    )
    db.session.add(log)
    db.session.commit()


def role_required(*role_names):
    """Decorator to restrict access by role name."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role.name not in role_names:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required(perm_name):
    """Decorator to restrict access by permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if not current_user.has_permission(perm_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
