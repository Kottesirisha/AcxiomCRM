"""AcxiomCRM – User Management Routes"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import User, Role
from routes.helpers import log_audit, role_required

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@login_required
@role_required('Admin')
def list_users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/list.html', users_list=users_list)


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def create():
    roles = Role.query.all()
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role_id = request.form.get('role_id', type=int)

        if not all([first_name, last_name, email, password, role_id]):
            flash('All required fields must be filled.', 'danger')
            return render_template('users/create.html', roles=roles)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('users/create.html', roles=roles)

        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'danger')
            return render_template('users/create.html', roles=roles)

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            role_id=role_id,
            phone=request.form.get('phone', '').strip() or None,
            is_active=bool(request.form.get('is_active')),
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_audit('Create', 'User', entity_id=user.id, description=f'Created user: {user.full_name}')
        flash(f'User "{user.full_name}" created.', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/create.html', roles=roles)


@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def edit(id):
    user = User.query.get_or_404(id)
    roles = Role.query.all()
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        role_id = request.form.get('role_id', type=int)

        if not all([first_name, last_name, email, role_id]):
            flash('All required fields must be filled.', 'danger')
            return render_template('users/edit.html', user=user, roles=roles)

        # Check email uniqueness
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user.id:
            flash('A user with this email already exists.', 'danger')
            return render_template('users/edit.html', user=user, roles=roles)

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.role_id = role_id
        user.phone = request.form.get('phone', '').strip() or None
        user.is_active = bool(request.form.get('is_active'))

        password = request.form.get('password', '')
        if password:
            if len(password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('users/edit.html', user=user, roles=roles)
            user.set_password(password)

        db.session.commit()
        log_audit('Update', 'User', entity_id=user.id, description=f'Updated user: {user.full_name}')
        flash(f'User "{user.full_name}" updated.', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/edit.html', user=user, roles=roles)


@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('users.list_users'))
    user.is_active = False
    db.session.commit()
    log_audit('Update', 'User', entity_id=user.id, description=f'Deactivated user: {user.full_name}')
    flash(f'User "{user.full_name}" deactivated.', 'success')
    return redirect(url_for('users.list_users'))


@users_bp.route('/<int:id>/activate', methods=['POST'])
@login_required
@role_required('Admin')
def activate(id):
    user = User.query.get_or_404(id)
    user.is_active = True
    db.session.commit()
    log_audit('Update', 'User', entity_id=user.id, description=f'Activated user: {user.full_name}')
    flash(f'User "{user.full_name}" activated.', 'success')
    return redirect(url_for('users.list_users'))
