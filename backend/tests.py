import unittest
import json
from app import create_app
from extensions import db
from models import User, Role, Customer, Lead, Opportunity, FollowUp, Activity, AuditLog
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ENGINE_OPTIONS = {}


class AcxiomCRMTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email='admin@acxiomcrm.com', password='Admin@123'):
        return self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def test_seed_and_admin_user(self):
        admin = User.query.filter_by(email='admin@acxiomcrm.com').first()
        self.assertIsNotNone(admin)
        self.assertEqual(admin.role.name, 'Admin')
        self.assertTrue(admin.check_password('Admin@123'))

    def test_login_logout(self):
        # Test valid login
        res = self.login()
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dashboard', res.data)

        # Test logout
        res = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Sign In', res.data)

    def test_customer_crud(self):
        self.login()
        # Create
        res = self.client.post('/customers/create', data={
            'name': 'Acme Corp',
            'email': 'contact@acme.com',
            'phone': '1234567890',
            'company': 'Acme Industries',
            'industry': 'Technology'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        cust = Customer.query.filter_by(name='Acme Corp').first()
        self.assertIsNotNone(cust)

        # Edit
        res = self.client.post(f'/customers/{cust.id}/edit', data={
            'name': 'Acme Global',
            'email': 'info@acmeglobal.com',
            'phone': '9876543210',
            'company': 'Acme Global Inc'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        cust_updated = Customer.query.get(cust.id)
        self.assertEqual(cust_updated.name, 'Acme Global')

        # List
        res = self.client.get('/customers/')
        self.assertIn(b'Acme Global', res.data)

        # Delete
        res = self.client.post(f'/customers/{cust.id}/delete', follow_redirects=True)
        self.assertIsNone(Customer.query.get(cust.id))

    def test_lead_conversion(self):
        self.login()
        # Create Lead
        res = self.client.post('/leads/create', data={
            'name': 'Jane Doe',
            'email': 'jane@startup.io',
            'company': 'Startup IO',
            'status': 'Qualified',
            'source': 'Web'
        }, follow_redirects=True)
        lead = Lead.query.filter_by(name='Jane Doe').first()
        self.assertIsNotNone(lead)

        # Convert Lead
        res = self.client.post(f'/leads/{lead.id}/convert', data={
            'name': 'Jane Doe',
            'email': 'jane@startup.io',
            'company': 'Startup IO',
            'create_opportunity': '1',
            'opp_name': 'Startup Big Deal',
            'opp_amount': '50000',
            'opp_stage': 'Proposal'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify Lead converted and Customer + Opportunity created
        lead_refreshed = Lead.query.get(lead.id)
        self.assertTrue(lead_refreshed.converted)
        cust = Customer.query.filter_by(email='jane@startup.io').first()
        self.assertIsNotNone(cust)
        opp = Opportunity.query.filter_by(name='Startup Big Deal').first()
        self.assertIsNotNone(opp)
        self.assertEqual(opp.amount, 50000.0)

    def test_opportunity_pipeline_and_kpis(self):
        self.login()
        cust = Customer(name='Test Client', email='client@test.com', created_by=1)
        db.session.add(cust)
        db.session.commit()

        opp = Opportunity(
            name='Cloud Migration',
            customer_id=cust.id,
            amount=20000,
            stage='Negotiation',
            probability=75,
            created_by=1
        )
        db.session.add(opp)
        db.session.commit()

        res = self.client.get('/opportunities/pipeline')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Cloud Migration', res.data)

        # Check dashboard API
        res = self.client.get('/api/dashboard/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_pipeline_value', data)

    def test_api_endpoints(self):
        self.login()
        # Customer API
        res = self.client.post('/customers/api/customers', json={
            'name': 'API Tech Corp',
            'email': 'api@tech.com'
        })
        self.assertEqual(res.status_code, 201)
        cust_id = res.get_json()['id']

        res = self.client.get('/customers/api/customers')
        self.assertEqual(res.status_code, 200)

        # Opportunities API
        res = self.client.post('/opportunities/api/opportunities', json={
            'name': 'API Deal',
            'customer_id': cust_id,
            'amount': 15000,
            'stage': 'Qualification'
        })
        self.assertEqual(res.status_code, 201)

    def test_audit_log(self):
        self.login()
        res = self.client.get('/audit/')
        self.assertEqual(res.status_code, 200)
        logs = AuditLog.query.all()
        self.assertTrue(len(logs) > 0)


if __name__ == '__main__':
    unittest.main()
