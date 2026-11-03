"""AcxiomCRM – Opportunity Routes"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from extensions import db, csrf
from models import Opportunity, Customer, FollowUp, Activity, User
from routes.helpers import log_audit

opportunities_bp = Blueprint('opportunities', __name__, url_prefix='/opportunities')
PER_PAGE = 15
STAGE_PROB = {'Qualification': 10, 'Needs Analysis': 25, 'Proposal': 50, 'Negotiation': 75, 'Closed Won': 100, 'Closed Lost': 0}


def _base_query():
    q = Opportunity.query
    if not (current_user.is_admin() or current_user.is_manager()):
        q = q.filter_by(assigned_to=current_user.id)
    return q


@opportunities_bp.route('/')
@login_required
def list_opportunities():
    search = request.args.get('search', '').strip()
    stage = request.args.get('stage', '').strip()
    page = request.args.get('page', 1, type=int)
    q = _base_query()
    if search:
        q = q.filter(Opportunity.name.ilike(f'%{search}%'))
    if stage:
        q = q.filter_by(stage=stage)
    opportunities = q.order_by(Opportunity.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('opportunities/list.html', opportunities=opportunities)


@opportunities_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    customers = Customer.query.order_by(Customer.name).all()
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        customer_id = request.form.get('customer_id', type=int)
        if not name or not customer_id:
            flash('Name and customer are required.', 'danger')
            return render_template('opportunities/create.html', customers=customers, users=users)
        stage = request.form.get('stage', 'Qualification')
        amount = float(request.form.get('amount', 0) or 0)
        if amount <= 0:
            flash('Opportunity Amount must be greater than 0.', 'danger')
            return render_template('opportunities/create.html', customers=customers, users=users)

        probability = int(request.form.get('probability', STAGE_PROB.get(stage, 10)))
        if probability < 0 or probability > 100:
            flash('Probability must be between 0 and 100.', 'danger')
            return render_template('opportunities/create.html', customers=customers, users=users)

        close_date = None
        if request.form.get('expected_close_date'):
            close_date = datetime.strptime(request.form['expected_close_date'], '%Y-%m-%d').date()
            if stage not in ['Closed Won', 'Closed Lost'] and close_date < datetime.utcnow().date():
                flash('Expected Close Date cannot be in the past for an active opportunity.', 'danger')
                return render_template('opportunities/create.html', customers=customers, users=users)

        opp = Opportunity(
            name=name,
            customer_id=customer_id,
            amount=amount,
            stage=stage,
            probability=probability,
            expected_close_date=close_date,
            description=request.form.get('description', '').strip() or None,
            assigned_to=request.form.get('assigned_to', type=int) or current_user.id,
            created_by=current_user.id,
        )
        db.session.add(opp)
        db.session.commit()
        log_audit('Create', 'Opportunity', entity_id=opp.id, description=f'Created opportunity: {opp.name}')
        flash(f'Opportunity "{opp.name}" created.', 'success')
        return redirect(url_for('opportunities.detail', id=opp.id))
    return render_template('opportunities/create.html', customers=customers, users=users)


@opportunities_bp.route('/<int:id>')
@login_required
def detail(id):
    opp = Opportunity.query.get_or_404(id)
    followups = opp.followups.order_by(FollowUp.due_date.desc()).all()
    activities = opp.activities.order_by(Activity.activity_date.desc()).all()
    return render_template('opportunities/detail.html', opportunity=opp, followups=followups, activities=activities)


@opportunities_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    opp = Opportunity.query.get_or_404(id)
    customers = Customer.query.order_by(Customer.name).all()
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name is required.', 'danger')
            return render_template('opportunities/edit.html', opportunity=opp, customers=customers, users=users)
        opp.name = name
        opp.customer_id = request.form.get('customer_id', type=int) or opp.customer_id
        opp.amount = float(request.form.get('amount', 0) or 0)
        opp.stage = request.form.get('stage', opp.stage)
        opp.probability = int(request.form.get('probability', STAGE_PROB.get(opp.stage, 10)))
        opp.expected_close_date = datetime.strptime(request.form['expected_close_date'], '%Y-%m-%d').date() if request.form.get('expected_close_date') else None
        opp.description = request.form.get('description', '').strip() or None
        opp.assigned_to = request.form.get('assigned_to', type=int) or opp.assigned_to
        db.session.commit()
        log_audit('Update', 'Opportunity', entity_id=opp.id, description=f'Updated opportunity: {opp.name}')
        flash(f'Opportunity "{opp.name}" updated.', 'success')
        return redirect(url_for('opportunities.detail', id=opp.id))
    return render_template('opportunities/edit.html', opportunity=opp, customers=customers, users=users)


@opportunities_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    opp = Opportunity.query.get_or_404(id)
    FollowUp.query.filter_by(opportunity_id=opp.id).delete()
    Activity.query.filter_by(opportunity_id=opp.id).delete()
    name = opp.name
    db.session.delete(opp)
    db.session.commit()
    log_audit('Delete', 'Opportunity', entity_id=id, description=f'Deleted opportunity: {name}')
    flash(f'Opportunity "{name}" deleted.', 'success')
    return redirect(url_for('opportunities.list_opportunities'))


@opportunities_bp.route('/pipeline')
@login_required
def pipeline():
    from collections import OrderedDict
    stages = ['Qualification', 'Needs Analysis', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    pipe = OrderedDict()
    for s in stages:
        pipe[s] = _base_query().filter_by(stage=s).order_by(Opportunity.amount.desc()).all()
    open_opps = _base_query().filter(Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])).all()
    total_pipeline = sum(o.amount or 0 for o in open_opps)
    weighted_pipeline = sum(o.weighted_amount for o in open_opps)
    won_total = sum(o.amount or 0 for o in pipe.get('Closed Won', []))
    lost_total = sum(o.amount or 0 for o in pipe.get('Closed Lost', []))
    return render_template('opportunities/pipeline.html', pipeline=pipe,
                           total_pipeline=total_pipeline, weighted_pipeline=weighted_pipeline,
                           won_total=won_total, lost_total=lost_total)


# ── API ────────────────────────────────────────────
@opportunities_bp.route('/api/opportunities', methods=['GET'])
@login_required
def api_list():
    opps = _base_query().order_by(Opportunity.created_at.desc()).all()
    return jsonify({'opportunities': [{'id': o.id, 'name': o.name, 'amount': o.amount, 'stage': o.stage, 'customer': o.customer.name} for o in opps]})


@opportunities_bp.route('/api/opportunities', methods=['POST'])
@login_required
@csrf.exempt
def api_create():
    data = request.get_json(silent=True)
    if not data or not data.get('name') or not data.get('customer_id'):
        return jsonify({'error': 'Name and customer_id required'}), 400
    stage = data.get('stage', 'Qualification')
    opp = Opportunity(name=data['name'], customer_id=data['customer_id'], amount=float(data.get('amount', 0)),
                      stage=stage, probability=STAGE_PROB.get(stage, 10),
                      assigned_to=data.get('assigned_to', current_user.id), created_by=current_user.id)
    db.session.add(opp)
    db.session.commit()
    log_audit('Create', 'Opportunity', entity_id=opp.id, description=f'API created: {opp.name}')
    return jsonify({'id': opp.id, 'name': opp.name}), 201


@opportunities_bp.route('/api/opportunities/<int:id>', methods=['PUT'])
@login_required
@csrf.exempt
def api_update(id):
    opp = Opportunity.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    for f in ['name', 'amount', 'stage', 'probability', 'description']:
        if f in data:
            setattr(opp, f, data[f])
    if 'customer_id' in data:
        opp.customer_id = data['customer_id']
    db.session.commit()
    log_audit('Update', 'Opportunity', entity_id=opp.id, description=f'API updated: {opp.name}')
    return jsonify({'id': opp.id, 'name': opp.name})


@opportunities_bp.route('/api/opportunities/<int:id>', methods=['DELETE'])
@login_required
@csrf.exempt
def api_delete(id):
    opp = Opportunity.query.get_or_404(id)
    name = opp.name
    FollowUp.query.filter_by(opportunity_id=id).delete()
    Activity.query.filter_by(opportunity_id=id).delete()
    db.session.delete(opp)
    db.session.commit()
    log_audit('Delete', 'Opportunity', entity_id=id, description=f'API deleted: {name}')
    return jsonify({'message': f'Deleted {name}'}), 200
