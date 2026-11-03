"""AcxiomCRM – Lead Routes"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from extensions import db, csrf
from models import Lead, Customer, Opportunity, FollowUp, Activity, User
from routes.helpers import log_audit

leads_bp = Blueprint('leads', __name__, url_prefix='/leads')
PER_PAGE = 15


def _base_query():
    q = Lead.query
    if not (current_user.is_admin() or current_user.is_manager()):
        q = q.filter_by(assigned_to=current_user.id)
    return q


@leads_bp.route('/')
@login_required
def list_leads():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    source = request.args.get('source', '').strip()
    page = request.args.get('page', 1, type=int)
    q = _base_query()
    if search:
        pat = f'%{search}%'
        q = q.filter(db.or_(Lead.name.ilike(pat), Lead.email.ilike(pat), Lead.company.ilike(pat)))
    if status:
        q = q.filter_by(status=status)
    if source:
        q = q.filter_by(source=source)
    leads = q.order_by(Lead.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('leads/list.html', leads=leads)


@leads_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Lead name is required.', 'danger')
            return render_template('leads/create.html', users=users)
        lead = Lead(
            name=name,
            email=request.form.get('email', '').strip() or None,
            phone=request.form.get('phone', '').strip() or None,
            company=request.form.get('company', '').strip() or None,
            source=request.form.get('source', '').strip() or None,
            status=request.form.get('status', 'New').strip(),
            rating=request.form.get('rating', '').strip() or None,
            description=request.form.get('description', '').strip() or None,
            assigned_to=request.form.get('assigned_to', type=int) or current_user.id,
            created_by=current_user.id,
        )
        db.session.add(lead)
        db.session.commit()
        log_audit('Create', 'Lead', entity_id=lead.id, description=f'Created lead: {lead.name}')
        flash(f'Lead "{lead.name}" created.', 'success')
        return redirect(url_for('leads.detail', id=lead.id))
    return render_template('leads/create.html', users=users)


@leads_bp.route('/<int:id>')
@login_required
def detail(id):
    lead = Lead.query.get_or_404(id)
    if not (current_user.is_admin() or current_user.is_manager()) and lead.assigned_to != current_user.id:
        abort(403)
    followups = lead.followups.order_by(FollowUp.due_date.desc()).all()
    activities = lead.activities.order_by(Activity.activity_date.desc()).all()
    return render_template('leads/detail.html', lead=lead, followups=followups, activities=activities)


@leads_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    lead = Lead.query.get_or_404(id)
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    if not (current_user.is_admin() or current_user.is_manager()) and lead.assigned_to != current_user.id:
        abort(403)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Lead name is required.', 'danger')
            return render_template('leads/edit.html', lead=lead, users=users)
        lead.name = name
        lead.email = request.form.get('email', '').strip() or None
        lead.phone = request.form.get('phone', '').strip() or None
        lead.company = request.form.get('company', '').strip() or None
        lead.source = request.form.get('source', '').strip() or None
        lead.status = request.form.get('status', lead.status).strip()
        lead.rating = request.form.get('rating', '').strip() or None
        lead.description = request.form.get('description', '').strip() or None
        lead.assigned_to = request.form.get('assigned_to', type=int) or lead.assigned_to
        db.session.commit()
        log_audit('Update', 'Lead', entity_id=lead.id, description=f'Updated lead: {lead.name}')
        flash(f'Lead "{lead.name}" updated.', 'success')
        return redirect(url_for('leads.detail', id=lead.id))
    return render_template('leads/edit.html', lead=lead, users=users)


@leads_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    lead = Lead.query.get_or_404(id)
    FollowUp.query.filter_by(lead_id=lead.id).delete()
    Activity.query.filter_by(lead_id=lead.id).delete()
    name = lead.name
    db.session.delete(lead)
    db.session.commit()
    log_audit('Delete', 'Lead', entity_id=id, description=f'Deleted lead: {name}')
    flash(f'Lead "{name}" deleted.', 'success')
    return redirect(url_for('leads.list_leads'))


@leads_bp.route('/<int:id>/convert', methods=['GET', 'POST'])
@login_required
def convert(id):
    lead = Lead.query.get_or_404(id)
    if lead.converted:
        flash('This lead has already been converted.', 'warning')
        return redirect(url_for('leads.detail', id=lead.id))

    if request.method == 'POST':
        # Check duplicate customer by email
        email = request.form.get('email', '').strip() or None
        if email:
            existing = Customer.query.filter_by(email=email).first()
            if existing:
                flash(f'A customer with email {email} already exists.', 'danger')
                return render_template('leads/convert.html', lead=lead)

        customer = Customer(
            name=request.form.get('name', lead.name).strip(),
            email=email,
            phone=request.form.get('phone', '').strip() or None,
            company=request.form.get('company', '').strip() or None,
            industry=request.form.get('industry', '').strip() or None,
            address=request.form.get('address', '').strip() or None,
            city=request.form.get('city', '').strip() or None,
            state=request.form.get('state', '').strip() or None,
            country=request.form.get('country', '').strip() or None,
            assigned_to=lead.assigned_to or current_user.id,
            created_by=current_user.id,
        )
        db.session.add(customer)
        db.session.flush()

        # Optionally create opportunity
        if request.form.get('create_opportunity'):
            stage = request.form.get('opp_stage', 'Qualification')
            prob_map = {'Qualification': 10, 'Needs Analysis': 25, 'Proposal': 50, 'Negotiation': 75}
            opp = Opportunity(
                name=request.form.get('opp_name', f'{customer.name} - Opportunity').strip(),
                customer_id=customer.id,
                amount=float(request.form.get('opp_amount', 0) or 0),
                stage=stage,
                probability=prob_map.get(stage, 10),
                expected_close_date=datetime.strptime(request.form['opp_close_date'], '%Y-%m-%d').date() if request.form.get('opp_close_date') else None,
                assigned_to=lead.assigned_to or current_user.id,
                created_by=current_user.id,
            )
            db.session.add(opp)

        lead.status = 'Converted'
        lead.converted = True
        lead.converted_customer_id = customer.id
        lead.converted_date = datetime.utcnow()
        db.session.commit()

        log_audit('Update', 'Lead', entity_id=lead.id, description=f'Converted lead: {lead.name} to customer: {customer.name}')
        log_audit('Create', 'Customer', entity_id=customer.id, description=f'Customer created from lead conversion: {customer.name}')

        flash(f'Lead "{lead.name}" converted to customer "{customer.name}".', 'success')
        return redirect(url_for('customers.detail', id=customer.id))

    return render_template('leads/convert.html', lead=lead)


# ── API ────────────────────────────────────────────
@leads_bp.route('/api/leads', methods=['GET'])
@login_required
def api_list():
    leads = _base_query().order_by(Lead.created_at.desc()).all()
    return jsonify({'leads': [{'id': l.id, 'name': l.name, 'email': l.email, 'status': l.status, 'source': l.source} for l in leads]})


@leads_bp.route('/api/leads', methods=['POST'])
@login_required
@csrf.exempt
def api_create():
    data = request.get_json(silent=True)
    if not data or not data.get('name'):
        return jsonify({'error': 'Name required'}), 400
    lead = Lead(name=data['name'], email=data.get('email'), phone=data.get('phone'),
                company=data.get('company'), source=data.get('source'), status=data.get('status', 'New'),
                rating=data.get('rating'), assigned_to=data.get('assigned_to', current_user.id), created_by=current_user.id)
    db.session.add(lead)
    db.session.commit()
    log_audit('Create', 'Lead', entity_id=lead.id, description=f'API created: {lead.name}')
    return jsonify({'id': lead.id, 'name': lead.name}), 201


@leads_bp.route('/api/leads/<int:id>', methods=['PUT'])
@login_required
@csrf.exempt
def api_update(id):
    lead = Lead.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    for f in ['name', 'email', 'phone', 'company', 'source', 'status', 'rating', 'description']:
        if f in data:
            setattr(lead, f, data[f])
    db.session.commit()
    log_audit('Update', 'Lead', entity_id=lead.id, description=f'API updated: {lead.name}')
    return jsonify({'id': lead.id, 'name': lead.name})


@leads_bp.route('/api/leads/<int:id>', methods=['DELETE'])
@login_required
@csrf.exempt
def api_delete(id):
    lead = Lead.query.get_or_404(id)
    name = lead.name
    FollowUp.query.filter_by(lead_id=id).delete()
    Activity.query.filter_by(lead_id=id).delete()
    db.session.delete(lead)
    db.session.commit()
    log_audit('Delete', 'Lead', entity_id=id, description=f'API deleted: {name}')
    return jsonify({'message': f'Deleted {name}'}), 200
