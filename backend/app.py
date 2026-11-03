
import os
from datetime import datetime

from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from extensions import db, login_manager, csrf
from models import User, Role, Permission, role_permissions


def create_app(config_class=Config):
    # Absolute paths for separated frontend and backend
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_DIR = os.path.abspath(
        os.path.join(BASE_DIR, "..", "frontend")
    )

    TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
    STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

    app = Flask(
        __name__,
        template_folder=TEMPLATE_DIR,
        static_folder=STATIC_DIR,
        static_url_path="/static"
    )

    app.config.from_object(config_class)

    # Enable CORS for decoupled frontends (e.g. Vercel)
    CORS(app, supports_credentials=True, origins=["*"])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.customers import customers_bp
    from routes.leads import leads_bp
    from routes.opportunities import opportunities_bp
    from routes.followups import followups_bp
    from routes.activities import activities_bp
    from routes.users import users_bp
    from routes.audit import audit_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(followups_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(reports_bp)

    # Register CLI commands
    from seed import seed_db_command
    app.cli.add_command(seed_db_command)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # Context processor
    @app.context_processor
    def utility_processor():
        return dict(now=datetime.utcnow())

    # Create tables and seed data
    with app.app_context():
        try:
            db.create_all()
            seed_data()
        except Exception as e:
            db.session.rollback()
            print(f"Warning: Database initialization skipped: {e}")

    return app


def seed_data():
    """Seed initial roles, permissions, and admin user."""

    # Create permissions
    perm_names = ["view", "create", "edit", "delete"]

    for pname in perm_names:
        if not Permission.query.filter_by(name=pname).first():
            db.session.add(
                Permission(
                    name=pname,
                    description=f"Can {pname} records"
                )
            )

    db.session.commit()

    # Create roles
    roles_config = {
        "Admin": perm_names,
        "Manager": ["view", "create", "edit"],
        "Sales Executive": ["view", "create", "edit"],
    }

    for role_name, perms in roles_config.items():
        role = Role.query.filter_by(name=role_name).first()

        if not role:
            role = Role(
                name=role_name,
                description=f"{role_name} role"
            )
            db.session.add(role)
            db.session.commit()

        # Assign permissions
        for pname in perms:
            perm = Permission.query.filter_by(name=pname).first()

            if perm and perm not in role.permissions:
                role.permissions.append(perm)

    db.session.commit()

    # Create admin user
    admin_role = Role.query.filter_by(name="Admin").first()

    admin_email = os.environ.get(
        "ADMIN_EMAIL",
        "admin@acxiomcrm.com"
    )

    admin_password = os.environ.get(
        "ADMIN_PASSWORD",
        "Admin@123"
    )

    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            first_name="Admin",
            last_name="User",
            email=admin_email,
            role_id=admin_role.id,
            is_active=True,
        )

        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="127.0.0.1", port=port, debug=False)
