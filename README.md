# AcxiomCRM – Enterprise Customer Relationship Management Application

**AcxiomCRM** is a production-grade, full-stack Customer Relationship Management (CRM) web application built with **Python Flask**, **SQLAlchemy ORM**, **Flask-Login**, and **Bootstrap 5**. It is designed with modular blueprints, strict role-based access control (RBAC), automatic audit logging, and responsive UI.

---

## 🚀 Key Features & Modules

### 1. Authentication & Role-Based Access Control (RBAC)
- **User Roles**: `Admin`, `Manager`, and `Sales Executive`.
- **Permissions**: `view`, `create`, `edit`, `delete` permissions enforced via custom function decorators (`@role_required`, `@permission_required`).
- **Security**: Passwords hashed with `werkzeug.security` (PBKDF2/SHA256). Session management via `Flask-Login` and CSRF protection with `Flask-WTF`.
- **Audit Logging**: Automatic audit log creation for all logins, creates, updates, and deletes with IP tracking.

### 2. Modern KPI Dashboard & Analytics
- Dynamic KPI metrics:
  - Total Customers
  - Total Leads
  - Open Opportunities
  - Won & Lost Opportunities
  - Total Sales Pipeline Value & Weighted Pipeline Calculation
- Interactive **Chart.js** charts:
  - Sales Pipeline Distribution (Bar Chart by stage)
  - Opportunity Status Ratio (Doughnut Chart: Open vs Won vs Lost)
- Dynamic widgets for Recent Customers, Recent Leads, Upcoming & Overdue Follow-ups, and Recent Activities.

### 3. Customer Management
- Complete CRUD operations with search (name, email, company) and industry filtering.
- Pagination with customizable page sizes.
- Customer detail view with unified tabs displaying related Opportunities, Follow-ups, and Activities.
- Cascade protection preventing accidental customer deletions when active opportunities exist.

### 4. Lead Management & Conversion Workflow
- Full lifecycle tracking: `New`, `Contacted`, `Qualified`, `Unqualified`, and `Converted`.
- Lead ratings: `Hot`, `Warm`, and `Cold`.
- **One-Click Lead Conversion**:
  - Automatically transforms qualified leads into customer records.
  - Optional seamless creation of an associated Opportunity during conversion.
  - Duplication prevention and preserved conversion history links.

### 5. Opportunity Management & Sales Pipeline
- Deal tracking with stages: `Qualification`, `Needs Analysis`, `Proposal`, `Negotiation`, `Closed Won`, and `Closed Lost`.
- Stage-based automatic probability updates and weighted revenue calculations.
- **Kanban-style Pipeline View** grouping opportunities by deal stages with dynamic stage summary totals.

### 6. Follow-up & Activity Tracking
- **Follow-ups**: Schedule follow-ups linked to Customers, Leads, or Opportunities with due dates, pending/completed/cancelled states, and visual overdue notifications.
- **Activities**: Log Calls, Meetings, Emails, and Tasks with timestamps, status tracking, and history timelines.

### 7. User Administration & Security Audit Log
- Dedicated admin portal to create, edit, activate, and deactivate users with role assignment.
- Searchable and filterable Security Audit Log (filterable by User, Action, Entity, and Date range) accessible exclusively by Administrators.

### 8. RESTful APIs
- JSON API endpoints for Customers, Leads, Opportunities, and Dashboard Statistics.
- Standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`) with appropriate status codes (`200`, `201`, `400`, `403`, `404`, `409`).

---

## 🛠 Technology Stack

- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug
- **Database**: MySQL 8.0+ / PyMySQL (SQLAlchemy ORM) with automatic fallback for local test environments
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4

---

## 📁 Project Structure

```
AcxiomCRM/
├── app.py                  # Application factory, error handlers & CLI
├── config.py               # Environment configuration settings
├── extensions.py           # Flask extensions (db, login_manager, csrf)
├── models.py               # SQLAlchemy ORM models & relationships
├── seed.py                 # Database sample seeding script
├── tests.py                # Automated unit & integration test suite
├── requirements.txt        # Production Python dependencies
├── .env.example            # Environment variable template
├── README.md               # Documentation
├── database/
│   └── schema.sql          # Production MySQL DDL schema
├── routes/
│   ├── auth.py             # Login, register, logout routes
│   ├── dashboard.py        # Dashboard stats, charts & API
│   ├── customers.py        # Customer CRUD & REST APIs
│   ├── leads.py            # Lead lifecycle & conversion
│   ├── opportunities.py    # Opportunity management & pipeline
│   ├── followups.py        # Follow-up scheduling & overdue alerts
│   ├── activities.py       # Activity logging (Calls, Meetings, Tasks)
│   ├── users.py            # User administration & role management
│   ├── audit.py            # Audit log inspection
│   └── helpers.py          # RBAC decorators & audit helper
├── static/
│   ├── css/style.css       # Enterprise theme & component styling
│   ├── js/main.js          # Interactive UX (modals, auto-probability)
│   └── js/dashboard.js     # Chart.js initialization & renders
└── templates/
    ├── base.html           # Master layout with sidebar & navigation
    ├── auth/               # Login & Register views
    ├── dashboard/          # Dashboard index & KPI cards
    ├── customers/          # Customer list, form & detail
    ├── leads/              # Lead list, form, detail & conversion
    ├── opportunities/      # Opportunity list, form, detail & pipeline
    ├── followups/          # Follow-up list & scheduling
    ├── activities/         # Activity list, form & detail
    ├── users/              # User management views
    ├── audit/              # Audit log viewer
    └── errors/             # 403, 404, 500 custom error pages
```

---

## ⚙️ Setup and Installation

### 1. Prerequisites
- Python 3.10 or higher
- MySQL Server 8.0+ (Optional: SQLite can be used for rapid local development/testing)

### 2. Clone / Open Directory
```bash
cd AcxiomCRM
```

### 3. Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: MySQL (Production Standard)
1. Ensure your MySQL server is running.
2. Create the database:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
3. Copy `.env.example` to `.env` and set your credentials:
   ```env
   SECRET_KEY=your-secure-random-secret-key
   DATABASE_URL=mysql+pymysql://root:password@localhost:3306/acxiomcrm
   ADMIN_EMAIL=admin@acxiomcrm.com
   ADMIN_PASSWORD=Admin@123
   ```

#### Option B: SQLite (Quick Local Development & Demo)
If MySQL is not installed locally:
```bash
set DATABASE_URL=sqlite:///acxiomcrm.db
```

### 5. Initialize & Seed Database
Run the seed command to create default roles, permissions, admin user, and sample CRM data:
```bash
flask seed-db
```

Default credentials seeded:
- **Admin**: `admin@acxiomcrm.com` / `Admin@123`
- **Manager**: `sarah.manager@acxiomcrm.com` / `Manager@123`
- **Sales Executive**: `alex.sales@acxiomcrm.com` / `Sales@123`

### 6. Run Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🧪 Running Tests
Run the comprehensive automated test suite (covering authentication, customer CRUD, lead conversion, opportunities pipeline, APIs, and audit logging):
```bash
python tests.py
```

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/dashboard/stats` | Retrieve aggregated KPI & chart statistics | Yes |
| `GET` | `/customers/api/customers` | List all visible customers | Yes |
| `POST` | `/customers/api/customers` | Create a new customer | Yes |
| `PUT` | `/customers/api/customers/<id>` | Update an existing customer | Yes |
| `DELETE` | `/customers/api/customers/<id>` | Delete customer (checks cascades) | Yes |
| `GET` | `/leads/api/leads` | List all visible leads | Yes |
| `POST` | `/leads/api/leads` | Create a new lead | Yes |
| `PUT` | `/leads/api/leads/<id>` | Update an existing lead | Yes |
| `DELETE` | `/leads/api/leads/<id>` | Delete a lead | Yes |
| `GET` | `/opportunities/api/opportunities` | List all visible opportunities | Yes |
| `POST` | `/opportunities/api/opportunities` | Create an opportunity | Yes |
| `PUT` | `/opportunities/api/opportunities/<id>` | Update an opportunity | Yes |
| `DELETE` | `/opportunities/api/opportunities/<id>` | Delete an opportunity | Yes |
