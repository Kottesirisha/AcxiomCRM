"""AcxiomCRM – Activity Routes"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import Activity, Customer, Lead, Opportunity, User
from routes.helpers import log_audit

activities_bp = Blueprint('activities', __name__, url_prefix='/activities')
PER_PAGE = 15


def _base_query():
    q = Activity.query
    if not (current_user.is_admin() or current_user.is_manager()):
        q = q.filter_by(assigned_to=current_user.id)
    return q


@activities_bp.route('/')
@login_required
def list_activities():
    act_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    q = _base_query()
    if act_type:
        q = q.filter_by(type=act_type)
    if status:
        q = q.filter_by(status=status)
    activities = q.order_by(Activity.activity_date.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('activities/list.html', activities=activities)


@activities_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    customers = Customer.query.order_by(Customer.name).all()
    leads = Lead.query.filter(Lead.converted == False).order_by(Lead.name).all()
    opportunities = Opportunity.query.filter(Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])).order_by(Opportunity.name).all()
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()

    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        act_type = request.form.get('type', '').strip()
        if not subject or not act_type:
            flash('Subject and type are required.', 'danger')
            return render_template('activities/create.html', customers=customers, leads=leads, opportunities=opportunities, users=users)

        date_str = request.form.get('activity_date', '').strip()
        activity_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M') if date_str else datetime.utcnow()

        activity = Activity(
            subject=subject,
            type=act_type,
            description=request.form.get('description', '').strip() or None,
            customer_id=request.form.get('customer_id', type=int) or None,
            lead_id=request.form.get('lead_id', type=int) or None,
            opportunity_id=request.form.get('opportunity_id', type=int) or None,
            assigned_to=request.form.get('assigned_to', type=int) or current_user.id,
            activity_date=activity_date,
            status=request.form.get('status', 'Planned'),
            created_by=current_user.id,
        )
        db.session.add(activity)
        db.session.commit()
        log_audit('Create', 'Activity', entity_id=activity.id, description=f'Created activity: {activity.subject}')
        flash(f'Activity "{activity.subject}" created.', 'success')
        return redirect(url_for('activities.detail', id=activity.id))
    return render_template('activities/create.html', customers=customers, leads=leads, opportunities=opportunities, users=users)


@activities_bp.route('/<int:id>')
@login_required
def detail(id):
    activity = Activity.query.get_or_404(id)
    return render_template('activities/detail.html', activity=activity)


@activities_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    activity = Activity.query.get_or_404(id)
    customers = Customer.query.order_by(Customer.name).all()
    leads = Lead.query.filter(Lead.converted == False).order_by(Lead.name).all()
    opportunities = Opportunity.query.filter(Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])).order_by(Opportunity.name).all()
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()

    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        act_type = request.form.get('type', '').strip()
        if not subject or not act_type:
            flash('Subject and type are required.', 'danger')
            return render_template('activities/edit.html', activity=activity, customers=customers, leads=leads, opportunities=opportunities, users=users)

        date_str = request.form.get('activity_date', '').strip()
        activity.activity_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M') if date_str else activity.activity_date

        activity.subject = subject
        activity.type = act_type
        activity.description = request.form.get('description', '').strip() or None
        activity.customer_id = request.form.get('customer_id', type=int) or None
        activity.lead_id = request.form.get('lead_id', type=int) or None
        activity.opportunity_id = request.form.get('opportunity_id', type=int) or None
        activity.assigned_to = request.form.get('assigned_to', type=int) or activity.assigned_to
        activity.status = request.form.get('status', activity.status)
        db.session.commit()
        log_audit('Update', 'Activity', entity_id=activity.id, description=f'Updated activity: {activity.subject}')
        flash(f'Activity "{activity.subject}" updated.', 'success')
        return redirect(url_for('activities.detail', id=activity.id))
    return render_template('activities/edit.html', activity=activity, customers=customers, leads=leads, opportunities=opportunities, users=users)


@activities_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    activity = Activity.query.get_or_404(id)
    activity.status = 'Completed'
    db.session.commit()
    log_audit('Update', 'Activity', entity_id=activity.id, description=f'Completed activity: {activity.subject}')
    flash(f'Activity "{activity.subject}" completed.', 'success')
    return redirect(url_for('activities.list_activities'))


@activities_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    activity = Activity.query.get_or_404(id)
    subject = activity.subject
    db.session.delete(activity)
    db.session.commit()
    log_audit('Delete', 'Activity', entity_id=id, description=f'Deleted activity: {subject}')
    flash(f'Activity "{subject}" deleted.', 'success')
    return redirect(url_for('activities.list_activities'))
