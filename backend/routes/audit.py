"""AcxiomCRM – Audit Log Routes"""
from datetime import datetime
from flask import Blueprint, render_template, request
from flask_login import login_required
from models import AuditLog, User
from routes.helpers import role_required

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')


@audit_bp.route('/')
@login_required
@role_required('Admin')
def list_logs():
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action', '').strip()
    entity = request.args.get('entity', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    page = request.args.get('page', 1, type=int)

    q = AuditLog.query
    if user_id:
        q = q.filter_by(user_id=user_id)
    if action:
        q = q.filter_by(action=action)
    if entity:
        q = q.filter_by(entity=entity)
    if date_from:
        try:
            q = q.filter(AuditLog.timestamp >= datetime.strptime(date_from, '%Y-%m-%d'))
        except ValueError:
            pass
    if date_to:
        try:
            q = q.filter(AuditLog.timestamp <= datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            pass

    logs = q.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=20, error_out=False)
    users = User.query.order_by(User.first_name).all()
    return render_template('audit/list.html', logs=logs, users=users)
