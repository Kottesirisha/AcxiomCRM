"""
AcxiomCRM – Authentication Routes
Handles login, registration, and logout.
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Role
from routes.helpers import log_audit

auth_bp = Blueprint('auth', __name__, url_prefix='')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page – authenticate user and redirect to dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if user:
            # Check lockout
            if user.is_locked_out:
                mins_remaining = int((user.lockout_until - datetime.utcnow()).total_seconds() / 60) + 1
                flash(f'Account is temporarily locked due to repeated failed logins. Try again in {mins_remaining} minutes.', 'danger')
                log_audit('Failed Login', 'User', entity_id=user.id, description=f'Locked out user attempt: {email}')
                return render_template('auth/login.html')

        if user is None or not user.check_password(password):
            if user:
                user.failed_login_count = (user.failed_login_count or 0) + 1
                if user.failed_login_count >= 5:
                    user.lockout_until = datetime.utcnow() + timedelta(minutes=15)
                    log_audit('Lockout', 'User', entity_id=user.id, description=f'Account locked out: {email} after 5 failed attempts')
                    flash('Account locked out for 15 minutes due to multiple failed login attempts.', 'danger')
                else:
                    attempts_left = 5 - user.failed_login_count
                    flash(f'Invalid credentials. {attempts_left} attempts remaining before account lockout.', 'danger')
                db.session.commit()
            else:
                flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated. Contact an administrator.', 'warning')
            return render_template('auth/login.html')

        # Reset failed login count on successful login
        user.failed_login_count = 0
        user.lockout_until = None
        db.session.commit()

        login_user(user, remember=remember)
        log_audit('Login', 'User', entity_id=user.id, description=f'User {user.full_name} logged in')

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page – create a new user with default Sales Executive role."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # ── Validation ──────────────────────────────────────────────
        errors = []
        if not first_name:
            errors.append('First name is required.')
        if not last_name:
            errors.append('Last name is required.')
        if not email:
            errors.append('Email is required.')
        if not password:
            errors.append('Password is required.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        # Check for duplicate email
        if email and User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('auth/register.html')

        # ── Create user ─────────────────────────────────────────────
        default_role = Role.query.filter_by(name='Sales Executive').first()
        if not default_role:
            # Fallback: create the role if seed data hasn't run yet
            default_role = Role(name='Sales Executive', description='Default sales team member')
            db.session.add(default_role)
            db.session.flush()

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            role_id=default_role.id,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        log_audit('Create', 'User', entity_id=user.id, description=f'New user registered: {user.full_name}')

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect to login page."""
    user_name = current_user.full_name
    user_id = current_user.id
    log_audit('Logout', 'User', entity_id=user_id, description=f'User {user_name} logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
