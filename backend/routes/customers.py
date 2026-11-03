"""AcxiomCRM – Customer Routes"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from extensions import db, csrf
from models import Customer, Opportunity, FollowUp, Activity, User
from routes.helpers import log_audit

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')
PER_PAGE = 15


def _base_query():
    q = Customer.query
    if not (current_user.is_admin() or current_user.is_manager()):
        q = q.filter_by(assigned_to=current_user.id)
    return q


@customers_bp.route('/')
@login_required
def list_customers():
    search = request.args.get('search', '').strip()
    industry = request.args.get('industry', '').strip()
    page = request.args.get('page', 1, type=int)
    q = _base_query()
    if search:
        pat = f'%{search}%'
        q = q.filter(db.or_(Customer.name.ilike(pat), Customer.email.ilike(pat), Customer.company.ilike(pat)))
    if industry:
        q = q.filter_by(industry=industry)
    customers = q.order_by(Customer.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('customers/list.html', customers=customers)


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip() or None
        phone = request.form.get('phone', '').strip() or None

        if not name:
            flash('Customer name is required.', 'danger')
            return render_template('customers/create.html', users=users)

        # Mandatory Unique Validations
        if email:
            existing_email = Customer.query.filter_by(email=email).first()
            if existing_email:
                flash(f'A customer with email "{email}" already exists.', 'danger')
                return render_template('customers/create.html', users=users)

        if phone:
            existing_phone = Customer.query.filter_by(phone=phone).first()
            if existing_phone:
                flash(f'A customer with phone "{phone}" already exists.', 'danger')
                return render_template('customers/create.html', users=users)
        customer = Customer(
            name=name,
            email=request.form.get('email', '').strip() or None,
            phone=request.form.get('phone', '').strip() or None,
            company=request.form.get('company', '').strip() or None,
            industry=request.form.get('industry', '').strip() or None,
            address=request.form.get('address', '').strip() or None,
            city=request.form.get('city', '').strip() or None,
            state=request.form.get('state', '').strip() or None,
            country=request.form.get('country', '').strip() or None,
            assigned_to=request.form.get('assigned_to', type=int) or current_user.id,
            created_by=current_user.id,
        )
        db.session.add(customer)
        db.session.commit()
        log_audit('Create', 'Customer', entity_id=customer.id, description=f'Created customer: {customer.name}')
        flash(f'Customer "{customer.name}" created successfully.', 'success')
        return redirect(url_for('customers.detail', id=customer.id))
    return render_template('customers/create.html', users=users)


@customers_bp.route('/<int:id>')
@login_required
def detail(id):
    customer = Customer.query.get_or_404(id)
    if not (current_user.is_admin() or current_user.is_manager()) and customer.assigned_to != current_user.id:
        abort(403)
    opportunities = customer.opportunities.order_by(Opportunity.created_at.desc()).all()
    followups = customer.followups.order_by(FollowUp.due_date.desc()).all()
    activities = customer.activities.order_by(Activity.activity_date.desc()).all()
    return render_template('customers/detail.html', customer=customer, opportunities=opportunities, followups=followups, activities=activities)


@customers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    if not (current_user.is_admin() or current_user.is_manager()) and customer.assigned_to != current_user.id:
        abort(403)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Customer name is required.', 'danger')
            return render_template('customers/edit.html', customer=customer, users=users)
        customer.name = name
        customer.email = request.form.get('email', '').strip() or None
        customer.phone = request.form.get('phone', '').strip() or None
        customer.company = request.form.get('company', '').strip() or None
        customer.industry = request.form.get('industry', '').strip() or None
        customer.address = request.form.get('address', '').strip() or None
        customer.city = request.form.get('city', '').strip() or None
        customer.state = request.form.get('state', '').strip() or None
        customer.country = request.form.get('country', '').strip() or None
        customer.assigned_to = request.form.get('assigned_to', type=int) or customer.assigned_to
        db.session.commit()
        log_audit('Update', 'Customer', entity_id=customer.id, description=f'Updated customer: {customer.name}')
        flash(f'Customer "{customer.name}" updated.', 'success')
        return redirect(url_for('customers.detail', id=customer.id))
    return render_template('customers/edit.html', customer=customer, users=users)


@customers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    if not (current_user.is_admin() or current_user.is_manager()) and customer.assigned_to != current_user.id:
        abort(403)
    if customer.opportunities.count() > 0:
        flash(f'Cannot delete "{customer.name}" – has related opportunities.', 'danger')
        return redirect(url_for('customers.detail', id=customer.id))
    FollowUp.query.filter_by(customer_id=customer.id).delete()
    Activity.query.filter_by(customer_id=customer.id).delete()
    name = customer.name
    db.session.delete(customer)
    db.session.commit()
    log_audit('Delete', 'Customer', entity_id=id, description=f'Deleted customer: {name}')
    flash(f'Customer "{name}" deleted.', 'success')
    return redirect(url_for('customers.list_customers'))


# ── API ────────────────────────────────────────────────────
@customers_bp.route('/api/customers', methods=['GET'])
@login_required
def api_list():
    customers = _base_query().order_by(Customer.created_at.desc()).all()
    return jsonify({'customers': [{'id': c.id, 'name': c.name, 'email': c.email, 'company': c.company} for c in customers]})


@customers_bp.route('/api/customers', methods=['POST'])
@login_required
@csrf.exempt
def api_create():
    data = request.get_json(silent=True)
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    customer = Customer(name=data['name'], email=data.get('email'), phone=data.get('phone'),
                        company=data.get('company'), industry=data.get('industry'),
                        assigned_to=data.get('assigned_to', current_user.id), created_by=current_user.id)
    db.session.add(customer)
    db.session.commit()
    log_audit('Create', 'Customer', entity_id=customer.id, description=f'API created: {customer.name}')
    return jsonify({'id': customer.id, 'name': customer.name}), 201


@customers_bp.route('/api/customers/<int:id>', methods=['PUT'])
@login_required
@csrf.exempt
def api_update(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    for field in ['name', 'email', 'phone', 'company', 'industry', 'address', 'city', 'state', 'country']:
        if field in data:
            setattr(customer, field, data[field])
    db.session.commit()
    log_audit('Update', 'Customer', entity_id=customer.id, description=f'API updated: {customer.name}')
    return jsonify({'id': customer.id, 'name': customer.name})


@customers_bp.route('/api/customers/<int:id>', methods=['DELETE'])
@login_required
@csrf.exempt
def api_delete(id):
    customer = Customer.query.get_or_404(id)
    if customer.opportunities.count() > 0:
        return jsonify({'error': 'Has related opportunities'}), 409
    FollowUp.query.filter_by(customer_id=customer.id).delete()
    Activity.query.filter_by(customer_id=customer.id).delete()
    name = customer.name
    db.session.delete(customer)
    db.session.commit()
    log_audit('Delete', 'Customer', entity_id=id, description=f'API deleted: {name}')
    return jsonify({'message': f'Deleted {name}'}), 200
