import os
import click
from flask.cli import with_appcontext
from extensions import db
from models import User, Role, Permission, Customer, Lead, Opportunity, FollowUp, Activity, AuditLog
from datetime import datetime, timedelta, date


@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """Seed comprehensive sample data for demonstration."""
    click.echo("Seeding database...")
    db.create_all()

    # Permissions & Roles
    perms = ['view', 'create', 'edit', 'delete']
    for p in perms:
        if not Permission.query.filter_by(name=p).first():
            db.session.add(Permission(name=p, description=f'Can {p} records'))
    db.session.commit()

    roles = {
        'Admin': perms,
        'Manager': ['view', 'create', 'edit'],
        'Sales Executive': ['view', 'create', 'edit'],
    }
    for r_name, r_perms in roles.items():
        role = Role.query.filter_by(name=r_name).first()
        if not role:
            role = Role(name=r_name, description=f'{r_name} role')
            db.session.add(role)
            db.session.commit()
        for pname in r_perms:
            perm = Permission.query.filter_by(name=pname).first()
            if perm and perm not in role.permissions:
                role.permissions.append(perm)
    db.session.commit()

    admin_role = Role.query.filter_by(name='Admin').first()
    manager_role = Role.query.filter_by(name='Manager').first()
    exec_role = Role.query.filter_by(name='Sales Executive').first()

    # Users
    admin = User.query.filter_by(email='admin@acxiomcrm.com').first()
    if not admin:
        admin = User(first_name='Admin', last_name='User', email='admin@acxiomcrm.com', role_id=admin_role.id)
        admin.set_password('Admin@123')
        db.session.add(admin)

    manager = User.query.filter_by(email='sarah.manager@acxiomcrm.com').first()
    if not manager:
        manager = User(first_name='Sarah', last_name='Connor', email='sarah.manager@acxiomcrm.com', role_id=manager_role.id)
        manager.set_password('Manager@123')
        db.session.add(manager)

    sales_exec = User.query.filter_by(email='alex.sales@acxiomcrm.com').first()
    if not sales_exec:
        sales_exec = User(first_name='Alex', last_name='Morgan', email='alex.sales@acxiomcrm.com', role_id=exec_role.id)
        sales_exec.set_password('Sales@123')
        db.session.add(sales_exec)

    db.session.commit()

    # Customers
    if Customer.query.count() == 0:
        customers = [
            Customer(name='Acme Cloud Solutions', email='contact@acmecloud.com', phone='+1-555-0101', company='Acme Corp', industry='Technology', city='San Francisco', state='CA', country='USA', assigned_to=sales_exec.id, created_by=admin.id),
            Customer(name='BioHealth Dynamics', email='procurement@biohealth.org', phone='+1-555-0102', company='BioHealth', industry='Healthcare', city='Boston', state='MA', country='USA', assigned_to=manager.id, created_by=admin.id),
            Customer(name='Apex Capital Management', email='partners@apexcap.com', phone='+1-555-0103', company='Apex Capital', industry='Finance', city='New York', state='NY', country='USA', assigned_to=sales_exec.id, created_by=admin.id),
            Customer(name='Nordic Retail Systems', email='hello@nordicretail.se', phone='+46-8-123456', company='Nordic Retail', industry='Retail', city='Stockholm', state='Stockholm', country='Sweden', assigned_to=sales_exec.id, created_by=sales_exec.id),
            Customer(name='Pinnacle EduTech', email='admissions@pinnacle.edu', phone='+1-555-0104', company='Pinnacle Edu', industry='Education', city='Austin', state='TX', country='USA', assigned_to=manager.id, created_by=admin.id),
        ]
        db.session.add_all(customers)
        db.session.commit()

    # Leads
    if Lead.query.count() == 0:
        leads = [
            Lead(name='Michael Scott', email='m.scott@dundermifflin.com', phone='+1-555-0201', company='Dunder Mifflin', source='Cold Call', status='Qualified', rating='Hot', description='Interested in modern CRM migration.', assigned_to=sales_exec.id, created_by=sales_exec.id),
            Lead(name='Elena Rostova', email='elena@quantumai.dev', phone='+1-555-0202', company='Quantum AI', source='Web', status='Contacted', rating='Warm', description='Requested enterprise demo.', assigned_to=sales_exec.id, created_by=sales_exec.id),
            Lead(name='David Zhao', email='dzhao@synthetix.io', phone='+1-555-0203', company='Synthetix', source='Referral', status='New', rating='Warm', description='Met at FinTech expo.', assigned_to=manager.id, created_by=admin.id),
            Lead(name='Rachel Green', email='rachel@ralphlauren.com', phone='+1-555-0204', company='Ralph Lauren', source='Advertisement', status='Unqualified', rating='Cold', description='Budget constrained until Q4.', assigned_to=sales_exec.id, created_by=sales_exec.id),
        ]
        db.session.add_all(leads)
        db.session.commit()

    # Opportunities
    if Opportunity.query.count() == 0:
        c1 = Customer.query.filter_by(name='Acme Cloud Solutions').first()
        c2 = Customer.query.filter_by(name='BioHealth Dynamics').first()
        c3 = Customer.query.filter_by(name='Apex Capital Management').first()
        c4 = Customer.query.filter_by(name='Nordic Retail Systems').first()

        opps = [
            Opportunity(name='Acme Enterprise CRM Expansion', customer_id=c1.id, amount=75000.0, stage='Proposal', probability=50, expected_close_date=date.today() + timedelta(days=30), description='Annual multi-seat license.', assigned_to=sales_exec.id, created_by=admin.id),
            Opportunity(name='BioHealth Compliance Portal', customer_id=c2.id, amount=120000.0, stage='Negotiation', probability=75, expected_close_date=date.today() + timedelta(days=15), description='HIPAA compliant deployment.', assigned_to=manager.id, created_by=admin.id),
            Opportunity(name='Apex Portfolio Analytics Add-on', customer_id=c3.id, amount=45000.0, stage='Needs Analysis', probability=25, expected_close_date=date.today() + timedelta(days=45), description='Custom reporting integration.', assigned_to=sales_exec.id, created_by=admin.id),
            Opportunity(name='Nordic Omnichannel Rollout', customer_id=c4.id, amount=95000.0, stage='Closed Won', probability=100, expected_close_date=date.today() - timedelta(days=5), description='Signed 2-year enterprise agreement.', assigned_to=sales_exec.id, created_by=sales_exec.id),
        ]
        db.session.add_all(opps)
        db.session.commit()

    # Follow-ups
    if FollowUp.query.count() == 0:
        c1 = Customer.query.filter_by(name='Acme Cloud Solutions').first()
        l1 = Lead.query.filter_by(name='Michael Scott').first()
        o2 = Opportunity.query.filter_by(name='BioHealth Compliance Portal').first()

        fus = [
            FollowUp(subject='Demo follow-up & RFP submission', customer_id=c1.id, due_date=datetime.now() + timedelta(days=2), status='Pending', assigned_to=sales_exec.id, created_by=sales_exec.id),
            FollowUp(subject='Contract legal review checkpoint', opportunity_id=o2.id, due_date=datetime.now() + timedelta(days=1), status='Pending', assigned_to=manager.id, created_by=admin.id),
            FollowUp(subject='Qualification discovery call', lead_id=l1.id, due_date=datetime.now() - timedelta(hours=4), status='Pending', assigned_to=sales_exec.id, created_by=sales_exec.id),
        ]
        db.session.add_all(fus)
        db.session.commit()

    # Activities
    if Activity.query.count() == 0:
        c1 = Customer.query.filter_by(name='Acme Cloud Solutions').first()
        acts = [
            Activity(subject='Technical Architecture Call', type='Call', customer_id=c1.id, activity_date=datetime.now() - timedelta(days=1), status='Completed', assigned_to=sales_exec.id, created_by=sales_exec.id, description='Reviewed SSO and API integration requirements.'),
            Activity(subject='Executive Proposal Review', type='Meeting', customer_id=c1.id, activity_date=datetime.now() + timedelta(days=3), status='Planned', assigned_to=manager.id, created_by=admin.id, description='Board review of annual SaaS commitment.'),
        ]
        db.session.add_all(acts)
        db.session.commit()

    # Audit Logs
    if AuditLog.query.count() == 0:
        log = AuditLog(user_id=admin.id, action='Login', entity='User', entity_id=admin.id, description='Admin logged into the portal', ip_address='127.0.0.1')
        db.session.add(log)
        db.session.commit()

    click.echo("Seeding completed successfully!")
