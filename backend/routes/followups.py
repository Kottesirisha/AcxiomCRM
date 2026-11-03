"""AcxiomCRM – Follow-up Routes"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import FollowUp, Customer, Lead, Opportunity, User
from routes.helpers import log_audit

followups_bp = Blueprint('followups', __name__, url_prefix='/followups')
PER_PAGE = 15


def _base_query():
    q = FollowUp.query
    if not (current_user.is_admin() or current_user.is_manager()):
        q = q.filter_by(assigned_to=current_user.id)
    return q


@followups_bp.route('/')
@login_required
def list_followups():
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    q = _base_query()
    if status:
        q = q.filter_by(status=status)
    followups = q.order_by(FollowUp.due_date.asc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('followups/list.html', followups=followups)


@followups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    customers = Customer.query.order_by(Customer.name).all()
    leads = Lead.query.filter(Lead.converted == False).order_by(Lead.name).all()
    opportunities = Opportunity.query.filter(Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])).order_by(Opportunity.name).all()
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()

    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        if not subject or not due_date_str:
            flash('Subject and due date are required.', 'danger')
            return render_template('followups/create.html', customers=customers, leads=leads, opportunities=opportunities, users=users)
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            if due_date.date() < datetime.utcnow().date():
                flash('Follow-up date cannot be earlier than today for a new/planned follow-up.', 'danger')
                return render_template('followups/create.html', customers=customers, leads=leads, opportunities=opportunities, users=users)
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('followups/create.html', customers=customers, leads=leads, opportunities=opportunities, users=users)

        fu = FollowUp(
            subject=subject,
            description=request.form.get('description', '').strip() or None,
            customer_id=request.form.get('customer_id', type=int) or None,
            lead_id=request.form.get('lead_id', type=int) or None,
            opportunity_id=request.form.get('opportunity_id', type=int) or None,
            assigned_to=request.form.get('assigned_to', type=int) or current_user.id,
            due_date=due_date,
            status=request.form.get('status', 'Pending'),
            created_by=current_user.id,
        )
        db.session.add(fu)
        db.session.commit()
        log_audit('Create', 'FollowUp', entity_id=fu.id, description=f'Created follow-up: {fu.subject}')
        flash(f'Follow-up "{fu.subject}" scheduled.', 'success')
        return redirect(url_for('followups.list_followups'))
    return render_template('followups/create.html', customers=customers, leads=leads, opportunities=opportunities, users=users)


@followups_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    fu = FollowUp.query.get_or_404(id)
    customers = Customer.query.order_by(Customer.name).all()
    leads = Lead.query.filter(Lead.converted == False).order_by(Lead.name).all()
    opportunities = Opportunity.query.filter(Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])).order_by(Opportunity.name).all()
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()

    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        if not subject or not due_date_str:
            flash('Subject and due date are required.', 'danger')
            return render_template('followups/edit.html', followup=fu, customers=customers, leads=leads, opportunities=opportunities, users=users)
        try:
            fu.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('followups/edit.html', followup=fu, customers=customers, leads=leads, opportunities=opportunities, users=users)

        fu.subject = subject
        fu.description = request.form.get('description', '').strip() or None
        fu.customer_id = request.form.get('customer_id', type=int) or None
        fu.lead_id = request.form.get('lead_id', type=int) or None
        fu.opportunity_id = request.form.get('opportunity_id', type=int) or None
        fu.assigned_to = request.form.get('assigned_to', type=int) or fu.assigned_to
        fu.status = request.form.get('status', fu.status)
        db.session.commit()
        log_audit('Update', 'FollowUp', entity_id=fu.id, description=f'Updated follow-up: {fu.subject}')
        flash(f'Follow-up "{fu.subject}" updated.', 'success')
        return redirect(url_for('followups.list_followups'))
    return render_template('followups/edit.html', followup=fu, customers=customers, leads=leads, opportunities=opportunities, users=users)


@followups_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    fu = FollowUp.query.get_or_404(id)
    fu.status = 'Completed'
    db.session.commit()
    log_audit('Update', 'FollowUp', entity_id=fu.id, description=f'Completed follow-up: {fu.subject}')
    flash(f'Follow-up "{fu.subject}" marked as completed.', 'success')
    return redirect(url_for('followups.list_followups'))


@followups_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    fu = FollowUp.query.get_or_404(id)
    fu.status = 'Cancelled'
    db.session.commit()
    log_audit('Update', 'FollowUp', entity_id=fu.id, description=f'Cancelled follow-up: {fu.subject}')
    flash(f'Follow-up "{fu.subject}" cancelled.', 'success')
    return redirect(url_for('followups.list_followups'))


@followups_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    fu = FollowUp.query.get_or_404(id)
    subject = fu.subject
    db.session.delete(fu)
    db.session.commit()
    log_audit('Delete', 'FollowUp', entity_id=id, description=f'Deleted follow-up: {subject}')
    flash(f'Follow-up "{subject}" deleted.', 'success')
    return redirect(url_for('followups.list_followups'))
