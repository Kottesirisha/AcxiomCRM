# AcxiomCRM

A web-based Customer Relationship Management (CRM) system built with Python (Flask) and MySQL/SQLite to help sales teams track leads, manage customer accounts, schedule follow-ups, and monitor the sales pipeline.

**Live Application:** [https://acxiomcrm-c6u0.onrender.com](https://acxiomcrm-c6u0.onrender.com)

---

## Demo Accounts

The database comes pre-seeded with three test users:

| Role | Email | Password |
|---|---|---|
| **Admin** | admin@acxiomcrm.com | Admin@123 |
| **Manager** | sarah.manager@acxiomcrm.com | Manager@123 |
| **Sales Executive** | alex.sales@acxiomcrm.com | Sales@123 |

---

## Features

- **Dashboard:** Overview cards showing customer count, open leads, pipeline value, and win/loss numbers. Charts built with Chart.js showing pipeline stage breakdown and deal status ratios.
- **Lead Management:** Track leads through statuses (`New`, `Contacted`, `Qualified`, `Unqualified`, `Converted`). One-click conversion turns qualified leads into customers with an optional linked opportunity.
- **Customer Directory:** Search by name/email/company and filter by industry. Each customer profile displays associated opportunities, follow-up history, and activities.
- **Opportunity Pipeline:** Move deals through stages (`Qualification`, `Needs Analysis`, `Proposal`, `Negotiation`, `Closed Won`, `Closed Lost`). Auto-calculates win probability and weighted pipeline values. Includes a Kanban-style pipeline view.
- **Follow-ups & Activities:** Schedule calls, meetings, tasks, and follow-ups against leads or customers. Automatically highlights overdue items.
- **User & Role Management:** Admins can invite users, assign roles (Admin, Manager, Sales Executive), and activate or deactivate accounts.
- **Security & Audit Logs:** Passwords hashed with Werkzeug. Protected by CSRF tokens and role-based route permissions. Account locks for 15 minutes after 5 consecutive failed login attempts. All key actions (logins, creates, updates, deletes) are written to an audit log table.
- **Reports & Export:** Summary metrics for conversion rates and revenue, with CSV export options for customers, leads, and opportunities.
- **REST APIs:** JSON endpoints for customers, leads, opportunities, and dashboard numbers.

---

## Tech Stack

- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-CORS, Gunicorn
- **Database:** MySQL 8.0 / SQLite
- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons, Chart.js

---

## Project Structure

```text
AcxiomCRM/
├── backend/
│   ├── app.py              # App factory and entry point
│   ├── config.py           # Configuration and database settings
│   ├── extensions.py       # Flask extensions (db, login_manager, csrf)
│   ├── models.py           # Database models and relationships
│   ├── requirements.txt    # Python packages
│   ├── seed.py             # Database seed command
│   ├── tests.py            # Unit tests
│   └── routes/             # Blueprints (auth, customers, leads, opps, etc.)
├── frontend/
│   ├── static/             # CSS and JavaScript files
│   └── templates/          # Jinja2 HTML templates
├── database/
│   └── schema.sql          # MySQL database schema
├── render.yaml             # Render deployment config
└── vercel.json             # Vercel proxy config
```

---

## Getting Started Locally

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone and Setup
```bash
git clone https://github.com/Kottesirisha/AcxiomCRM.git
cd AcxiomCRM/backend
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
Run the seed command to create the database tables and insert initial demo data:
```bash
flask seed-db
```

### 4. Run the Server
```bash
python app.py
```

Open [http://127.0.0.1:5050](http://127.0.0.1:5050) in your browser and sign in with any of the demo accounts listed above.

---

## Running Tests

To run the automated test suite:

```bash
python tests.py
```

This runs test cases covering login/logout, customer CRUD, lead conversion, pipeline calculations, REST APIs, and audit logging.

---

## API Endpoints

All endpoints return JSON and require authentication.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/stats` | Summary KPI figures and chart data |
| `GET` | `/customers/api/customers` | List all visible customers |
| `POST` | `/customers/api/customers` | Create a new customer |
| `PUT` | `/customers/api/customers/<id>` | Update an existing customer |
| `DELETE` | `/customers/api/customers/<id>` | Delete customer (blocks if open deals exist) |
| `GET` | `/leads/api/leads` | List all visible leads |
| `POST` | `/leads/api/leads` | Create a lead |
| `PUT` | `/leads/api/leads/<id>` | Update a lead |
| `DELETE` | `/leads/api/leads/<id>` | Delete a lead |
| `GET` | `/opportunities/api/opportunities` | List all visible opportunities |
| `POST` | `/opportunities/api/opportunities` | Create an opportunity |
| `PUT` | `/opportunities/api/opportunities/<id>` | Update an opportunity |
| `DELETE` | `/opportunities/api/opportunities/<id>` | Delete an opportunity |
