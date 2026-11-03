from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager


# ── Association Tables ──────────────────────────────────────────────

role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)


# ── Role & Permission ──────────────────────────────────────────────

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.relationship('Permission', secondary=role_permissions, backref='roles')
    users = db.relationship('User', backref='role', lazy='dynamic')

    def has_permission(self, perm_name):
        return any(p.name == perm_name for p in self.permissions)

    def __repr__(self):
        return f'<Role {self.name}>'


class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Permission {self.name}>'


# ── User ────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    failed_login_count = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_locked_out(self):
        if self.lockout_until and self.lockout_until > datetime.utcnow():
            return True
        return False

    # Relationships
    customers = db.relationship('Customer', backref='assigned_user', lazy='dynamic', foreign_keys='Customer.assigned_to')
    leads = db.relationship('Lead', backref='assigned_user', lazy='dynamic', foreign_keys='Lead.assigned_to')
    opportunities = db.relationship('Opportunity', backref='assigned_user', lazy='dynamic', foreign_keys='Opportunity.assigned_to')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, perm_name):
        return self.role and self.role.has_permission(perm_name)

    def is_admin(self):
        return self.role and self.role.name == 'Admin'

    def is_manager(self):
        return self.role and self.role.name == 'Manager'

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── Customer ────────────────────────────────────────────────────────

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    industry = db.Column(db.String(50))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    opportunities = db.relationship('Opportunity', backref='customer', lazy='dynamic')
    followups = db.relationship('FollowUp', backref='customer', lazy='dynamic')
    activities = db.relationship('Activity', backref='customer', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Customer {self.name}>'


# ── Lead ────────────────────────────────────────────────────────────

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    source = db.Column(db.String(50))  # Web, Referral, Cold Call, etc.
    status = db.Column(db.String(20), default='New')  # New, Contacted, Qualified, Unqualified, Converted
    rating = db.Column(db.String(10))  # Hot, Warm, Cold
    description = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    converted = db.Column(db.Boolean, default=False)
    converted_customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    converted_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    followups = db.relationship('FollowUp', backref='lead', lazy='dynamic')
    activities = db.relationship('Activity', backref='lead', lazy='dynamic')
    converted_customer = db.relationship('Customer', foreign_keys=[converted_customer_id])
    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Lead {self.name}>'


# ── Opportunity ─────────────────────────────────────────────────────

class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    stage = db.Column(db.String(30), default='Qualification')
    probability = db.Column(db.Integer, default=10)  # 0-100
    expected_close_date = db.Column(db.Date)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    followups = db.relationship('FollowUp', backref='opportunity', lazy='dynamic')
    activities = db.relationship('Activity', backref='opportunity', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by])

    STAGES = [
        ('Qualification', 10),
        ('Needs Analysis', 25),
        ('Proposal', 50),
        ('Negotiation', 75),
        ('Closed Won', 100),
        ('Closed Lost', 0),
    ]

    @property
    def weighted_amount(self):
        return (self.amount or 0) * (self.probability or 0) / 100

    def __repr__(self):
        return f'<Opportunity {self.name}>'


# ── FollowUp ────────────────────────────────────────────────────────

class FollowUp(db.Model):
    __tablename__ = 'followups'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Completed, Cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    creator = db.relationship('User', foreign_keys=[created_by])

    @property
    def is_overdue(self):
        return self.status == 'Pending' and self.due_date < datetime.utcnow()

    def __repr__(self):
        return f'<FollowUp {self.subject}>'


# ── Activity ────────────────────────────────────────────────────────

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Call, Meeting, Email, Task
    description = db.Column(db.Text)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Planned')  # Planned, Completed, Cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Activity {self.subject}>'


# ── Audit Log ───────────────────────────────────────────────────────

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(20), nullable=False)  # Login, Create, Update, Delete
    entity = db.Column(db.String(50))  # Customer, Lead, Opportunity, etc.
    entity_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', backref='audit_logs')

    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity}>'
