import re
from app import app

client = app.test_client()

# 1. Fetch login page and extract CSRF token
res = client.get('/login')
assert res.status_code == 200, f'Expected 200, got {res.status_code}'
match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.data.decode('utf-8'))
assert match, 'CSRF token missing'
csrf_token = match.group(1)

# 2. Perform authenticated login
res_login = client.post('/login', data={
    'email': 'admin@acxiomcrm.com',
    'password': 'Admin@123',
    'csrf_token': csrf_token
}, follow_redirects=True)

assert res_login.status_code == 200, f'Login failed: {res_login.status_code}'
assert b'Dashboard' in res_login.data, 'Dashboard view not returned'
print("Step 1: Login successful, landed on Dashboard.")

# 3. Check Customers view
res_customers = client.get('/customers/')
assert res_customers.status_code == 200, f'Customers view failed: {res_customers.status_code}'
print("Step 2: Customers view loads successfully.")

# 4. Check Reports view
res_reports = client.get('/reports/')
assert res_reports.status_code == 200, f'Reports view failed: {res_reports.status_code}'
print("Step 3: Reports view loads successfully.")

# 5. Check API stats
res_api = client.get('/api/dashboard/stats')
assert res_api.status_code == 200, f'API stats failed: {res_api.status_code}'
print("Step 4: REST API /api/dashboard/stats returns 200 OK.")

print("\nAll end-to-end verification steps passed successfully!")
