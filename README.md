# AcxiomCRM – Enterprise Customer Relationship Management System

[![Live Demo](https://img.shields.io/badge/Live-Demo%20on%20Render-brightgreen?style=for-the-badge&logo=render)](https://acxiomcrm-c6u0.onrender.com)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/Kottesirisha/AcxiomCRM)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.0-lightgrey?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)

**AcxiomCRM** is a production-grade, full-stack Customer Relationship Management (CRM) application built using **Python Flask**, **SQLAlchemy ORM**, **Flask-Login**, and **Bootstrap 5**. Designed with a modular blueprint architecture, it provides role-based access control (RBAC), end-to-end sales pipeline workflows, automated audit logging, business validations, executive reporting, and interactive Chart.js analytics.

---

## 🌐 Live Application Link

* **Live Deployment URL**: **[https://acxiomcrm-c6u0.onrender.com](https://acxiomcrm-c6u0.onrender.com)**
* **GitHub Repository**: **[https://github.com/Kottesirisha/AcxiomCRM](https://github.com/Kottesirisha/AcxiomCRM)**

---

## 🔑 Default Demo Accounts

The database comes pre-seeded with three tiers of authenticated users:

| Role | Email | Password | Scope & Responsibilities |
|---|---|---|---|
| **Administrator** | `admin@acxiomcrm.com` | `Admin@123` | Full system administration, user management, audit trails, and all CRM entities. |
| **Sales Manager** | `sarah.manager@acxiomcrm.com` | `Manager@123` | Team oversight, complete pipeline access, follow-ups, and executive reports. |
| **Sales Executive** | `alex.sales@acxiomcrm.com` | `Sales@123` | Individual assigned leads, customers, opportunities, and activities. |

---

## 🚀 Key Modules & Functional Features

### 1. Application Shell & Navigation
* Responsive layout designed with **Bootstrap 5**, **Bootstrap Icons**, and custom enterprise styling.
* Collapsible sidebar with dynamic active link indicators and role-aware navigation menus.
* Top navigation bar with breadcrumb tracking, user avatar profile menu, and flash alerts.

### 2. Authentication & Security
* **Password Hashing**: Werkzeug password hashing using adaptive PBKDF2/SHA-256.
* **Account Lockout Policy**: Tracks failed logins; locks an account for 15 minutes after 5 consecutive failed attempts.
* **Session Security**: Session cookies managed via `Flask-Login` with CSRF protection enforced by `Flask-WTF`.
* **Role-Based Access Control (RBAC)**: Fine-grained access decorators (`@role_required`, `@permission_required`) restricting unauthorized access across all HTTP endpoints.

### 3. Interactive KPI Dashboard & Charts
* **6 KPI Cards**: Total Customers, Total Leads, Open Opportunities, Won Opportunities, Lost Opportunities, and Total Pipeline Monetary Value.
* **Chart.js Visualizations**:
  * **Sales Pipeline Stage Distribution** (Bar chart).
  * **Opportunity Status Ratio** (Doughnut chart: Open vs. Won vs. Lost).
* **Dynamic Record Feeds**: Recent Customers, Recent Leads, Upcoming Follow-ups (with automatic red **Overdue** alerts), and Activity logs.

### 4. Customer Management
* Comprehensive CRUD (Create, Read, Update, Delete) with server-side and client-side validations.
* Live search by name, email, or company; industry filtering; pagination.
* Consolidated Customer 360° detail view with tabs for Opportunities, Follow-ups, and Activities.
* **Referential Integrity Cascade Guard**: Prevents deleting customers with linked active opportunities.

### 5. Lead Management & 1-Click Conversion Workflow
* Complete lead status lifecycle: `New` → `Contacted` → `Qualified` → `Unqualified` → `Converted`.
* Lead ratings: `Hot`, `Warm`, and `Cold`.
* **1-Click Conversion Engine**: Converts qualified leads directly into customer records, with optional simultaneous Opportunity generation and duplication prevention.

### 6. Opportunity Management & Kanban Pipeline
* Opportunity stages: `Qualification`, `Needs Analysis`, `Proposal`, `Negotiation`, `Closed Won`, and `Closed Lost`.
* Automatic stage-based probability updates and weighted revenue calculations (`Amount × Probability / 100`).
* **Kanban Pipeline Board** (`/opportunities/pipeline`): Visual deal progression columns with stage revenue sums and weighted forecast totals.

### 7. Follow-Up & Activity Management
* **Follow-Ups**: Schedule tasks against Customers, Leads, or Opportunities with due dates, status updates (`Pending`, `Completed`, `Cancelled`), and automated overdue detection.
* **Activities**: Log Calls, Meetings, Emails, and Tasks with timestamps and completion toggles.

### 8. User Administration & Security Audit Trail
* User CRUD, role assignment, and user activation/deactivation toggles (restricted to Admins).
* Comprehensive **Security Audit Log** (`/audit/`) recording `UserId`, `Action`, `Entity`, `RecordId`, `Description`, `IP Address`, and `Timestamp`. Filterable by User, Action, Entity, and Date range.

### 9. Executive Reports & CSV Data Export
* Overview metrics: **Lead Conversion Rate (%)**, **Closed Won Revenue**, and **Weighted Forecast Value**.
* **1-Click CSV Export**:
  * Export Customer Master Report (`/reports/export/customers`)
  * Export Leads & Conversion Report (`/reports/export/leads`)
  * Export Sales Pipeline Opportunities Report (`/reports/export/opportunities`)

### 10. RESTful APIs
* Fully authenticated JSON endpoints exposing:
  * `/api/dashboard/stats`
  * `/customers/api/customers`
  * `/leads/api/leads`
  * `/opportunities/api/opportunities`

---

## 🛠 Technology Stack

* **Backend**: Python 3.10+, Flask 3.0, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-CORS, Werkzeug, Gunicorn
* **Database**: MySQL 8.0 / PyMySQL (with automatic embedded SQLite fallback)
* **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
* **Deployment**: Render (Web Service + Gunicorn), GitHub, Vercel

---

## 📂 Project Architecture

```
AcxiomCRM/
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Local multi-container compose configuration
├── render.yaml             # Render deployment configuration
├── vercel.json             # Vercel proxy configuration
├── README.md               # Complete documentation
├── TESTING_FLOW.md         # System flow and testing manual
│
├── backend/                # Server-Side Application
│   ├── app.py              # Application factory & entry point
│   ├── config.py           # Configuration settings
│   ├── extensions.py       # Flask extensions (db, csrf, login_manager)
│   ├── models.py           # SQLAlchemy ORM models & entity schema
│   ├── requirements.txt    # Python dependencies
│   ├── seed.py             # Database seed CLI command
│   ├── tests.py            # Automated unit and integration test suite
│   ├── verify_flow.py      # End-to-end integration verification script
│   ├── database/
│   │   └── schema.sql      # MySQL 8.0 production DDL schema
│   └── routes/             # Modular Blueprint Controllers
│       ├── activities.py   # Activity logging
│       ├── audit.py        # Audit logging viewer
│       ├── auth.py         # Login, logout, registration & lockout
│       ├── customers.py    # Customer CRUD & REST APIs
│       ├── dashboard.py    # Analytics & KPI aggregations
│       ├── followups.py    # Follow-up scheduling & overdue rules
│       ├── helpers.py      # RBAC decorators & audit helper
│       ├── leads.py        # Lead lifecycle & conversion engine
│       ├── opportunities.py# Pipeline & Kanban views
│       ├── reports.py      # Executive summaries & CSV exports
│       └── users.py        # User & role administration
│
└── frontend/               # User Interface Assets
    ├── static/
    │   ├── css/style.css   # Custom CSS theme & components
    │   └── js/
    │       ├── dashboard.js# Chart.js initialization
    │       └── main.js     # UI interactions, modals & formatting
    └── templates/          # Jinja2 HTML Templates
        ├── base.html       # Master layout shell
        ├── activities/     # Activity views
        ├── audit/          # Audit log views
        ├── auth/           # Login and register pages
        ├── customers/      # Customer list, detail, and form views
        ├── dashboard/      # Main analytics dashboard
        ├── errors/         # Custom 403, 404, 500 error pages
        ├── followups/      # Follow-up list and modal views
        ├── leads/          # Lead list, detail, and conversion views
        ├── opportunities/  # Opportunity list, detail, and pipeline Kanban
        ├── reports/        # Reports hub & export center
        └── users/          # User administration views
```

---

## 💻 Local Setup & Installation

### 1. Prerequisites
* Python 3.10 or higher
* Git

### 2. Clone Repository
```bash
git clone https://github.com/Kottesirisha/AcxiomCRM.git
cd AcxiomCRM
```

### 3. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Initialize Database & Seed Sample Records
```bash
flask seed-db
```

### 6. Run Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5050`**

---

## 🧪 Running Automated Tests

Execute the unit and integration test suite:
```bash
python tests.py
```

Coverage includes:
* Database seeding and Administrator creation.
* Authentication, CSRF protection, and logout workflows.
* Customer CRUD operations and deletion cascade safeguards.
* Lead qualification and atomic conversion into Customer + Opportunity.
* Opportunity pipeline calculations and weighted value formulas.
* REST API endpoints and JSON serialization.
* Audit trail logging of security and data mutations.

---

## 📡 REST API Documentation

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `GET` | `/api/dashboard/stats` | Aggregate KPI statistics and chart metrics | Yes |
| `GET` | `/customers/api/customers` | List all scoped customers | Yes |
| `POST` | `/customers/api/customers` | Create a new customer | Yes |
| `PUT` | `/customers/api/customers/<id>` | Update an existing customer | Yes |
| `DELETE` | `/customers/api/customers/<id>` | Delete a customer (enforces opportunity checks) | Yes |
| `GET` | `/leads/api/leads` | List all scoped leads | Yes |
| `POST` | `/leads/api/leads` | Create a new lead | Yes |
| `PUT` | `/leads/api/leads/<id>` | Update an existing lead | Yes |
| `DELETE` | `/leads/api/leads/<id>` | Delete a lead | Yes |
| `GET` | `/opportunities/api/opportunities` | List all scoped opportunities | Yes |
| `POST` | `/opportunities/api/opportunities` | Create a new opportunity | Yes |
| `PUT` | `/opportunities/api/opportunities/<id>` | Update an opportunity | Yes |
| `DELETE` | `/opportunities/api/opportunities/<id>` | Delete an opportunity | Yes |

---

## 📄 License
This project is developed for educational and portfolio demonstration purposes. All rights reserved.
