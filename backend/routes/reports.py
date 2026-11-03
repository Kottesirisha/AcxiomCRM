"""AcxiomCRM – Reports & Export Routes"""
import csv
import io
from flask import Blueprint, render_template, Response, request
from flask_login import login_required, current_user
from models import Customer, Lead, Opportunity, FollowUp, Activity, User
from routes.helpers import role_required

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def index():
    """Reports overview dashboard."""
    # Data collections according to role
    if current_user.is_admin() or current_user.is_manager():
        customers = Customer.query.all()
        leads = Lead.query.all()
        opportunities = Opportunity.query.all()
        followups = FollowUp.query.all()
    else:
        customers = Customer.query.filter_by(assigned_to=current_user.id).all()
        leads = Lead.query.filter_by(assigned_to=current_user.id).all()
        opportunities = Opportunity.query.filter_by(assigned_to=current_user.id).all()
        followups = FollowUp.query.filter_by(assigned_to=current_user.id).all()

    # Metrics
    converted_leads = [l for l in leads if l.converted]
    conversion_rate = (len(converted_leads) / len(leads) * 100) if leads else 0.0

    won_opps = [o for o in opportunities if o.stage == 'Closed Won']
    total_won_value = sum(o.amount for o in won_opps)

    open_opps = [o for o in opportunities if o.stage not in ['Closed Won', 'Closed Lost']]
    total_pipeline_value = sum(o.amount for o in open_opps)
    weighted_pipeline_value = sum(o.weighted_amount for o in open_opps)

    return render_template(
        'reports/index.html',
        customers=customers,
        leads=leads,
        opportunities=opportunities,
        followups=followups,
        conversion_rate=round(conversion_rate, 1),
        total_won_value=total_won_value,
        total_pipeline_value=total_pipeline_value,
        weighted_pipeline_value=weighted_pipeline_value,
    )


@reports_bp.route('/export/<report_type>')
@login_required
def export_csv(report_type):
    """Export CRM report data as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'customers':
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Company', 'Industry', 'City', 'Created Date'])
        q = Customer.query if (current_user.is_admin() or current_user.is_manager()) else Customer.query.filter_by(assigned_to=current_user.id)
        for c in q.all():
            writer.writerow([c.id, c.name, c.email or '', c.phone or '', c.company or '', c.industry or '', c.city or '', c.created_at])
        filename = "customers_report.csv"

    elif report_type == 'leads':
        writer.writerow(['ID', 'Name', 'Email', 'Company', 'Source', 'Status', 'Rating', 'Converted', 'Created Date'])
        q = Lead.query if (current_user.is_admin() or current_user.is_manager()) else Lead.query.filter_by(assigned_to=current_user.id)
        for l in q.all():
            writer.writerow([l.id, l.name, l.email or '', l.company or '', l.source or '', l.status, l.rating or '', l.converted, l.created_at])
        filename = "leads_report.csv"

    elif report_type == 'opportunities':
        writer.writerow(['ID', 'Name', 'Customer', 'Amount', 'Stage', 'Probability', 'Expected Close Date'])
        q = Opportunity.query if (current_user.is_admin() or current_user.is_manager()) else Opportunity.query.filter_by(assigned_to=current_user.id)
        for o in q.all():
            writer.writerow([o.id, o.name, o.customer.name if o.customer else '', o.amount, o.stage, f"{o.probability}%", o.expected_close_date or ''])
        filename = "pipeline_opportunities_report.csv"

    else:
        return "Invalid report type", 400

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
