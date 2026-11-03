"""
AcxiomCRM – Dashboard Routes
Main dashboard with stats, charts, and a JSON API endpoint.
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from extensions import db
from models import Customer, Lead, Opportunity, FollowUp, Activity

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='')


# ── Helpers ─────────────────────────────────────────────────────────


def _build_dashboard_data():
    """Collect all dashboard statistics and return as a dict."""

    # ── Counts ───────────────────────────────────────────────────
    total_customers = Customer.query.count()
    total_leads = Lead.query.count()

    open_opportunities = Opportunity.query.filter(
        Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])
    ).count()

    won_opportunities = Opportunity.query.filter_by(stage='Closed Won').count()
    lost_opportunities = Opportunity.query.filter_by(stage='Closed Lost').count()

    # ── Pipeline values ──────────────────────────────────────────
    pipeline_q = Opportunity.query.filter(
        Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])
    )

    total_pipeline_value = db.session.query(
        func.coalesce(func.sum(Opportunity.amount), 0)
    ).filter(
        Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])
    ).scalar()

    # Weighted pipeline: sum(amount * probability / 100)
    weighted_pipeline = db.session.query(
        func.coalesce(
            func.sum(Opportunity.amount * Opportunity.probability / 100), 0
        )
    ).filter(
        Opportunity.stage.notin_(['Closed Won', 'Closed Lost'])
    ).scalar()

    # ── Recent records ───────────────────────────────────────────
    recent_customers = Customer.query.order_by(
        Customer.created_at.desc()
    ).limit(5).all()

    recent_leads = Lead.query.order_by(
        Lead.created_at.desc()
    ).limit(5).all()

    upcoming_followups = FollowUp.query.filter_by(
        status='Pending'
    ).order_by(
        FollowUp.due_date.asc()
    ).limit(5).all()

    recent_activities = Activity.query.order_by(
        Activity.created_at.desc()
    ).limit(5).all()

    # ── Chart data: opportunity stage counts ─────────────────────
    stage_counts = db.session.query(
        Opportunity.stage, func.count(Opportunity.id)
    ).group_by(Opportunity.stage).all()

    opportunity_stages = {stage: count for stage, count in stage_counts}

    # ── Chart data: monthly won sales (last 6 months) ────────────
    six_months_ago = datetime.utcnow() - timedelta(days=180)

    monthly_rows = db.session.query(
        extract('year', Opportunity.updated_at).label('year'),
        extract('month', Opportunity.updated_at).label('month'),
        func.coalesce(func.sum(Opportunity.amount), 0).label('total'),
    ).filter(
        Opportunity.stage == 'Closed Won',
        Opportunity.updated_at >= six_months_ago,
    ).group_by('year', 'month').order_by('year', 'month').all()

    monthly_sales = [
        {
            'year': int(row.year),
            'month': int(row.month),
            'total': float(row.total),
        }
        for row in monthly_rows
    ]

    return {
        'total_customers': total_customers,
        'total_leads': total_leads,
        'open_opportunities': open_opportunities,
        'won_opportunities': won_opportunities,
        'lost_opportunities': lost_opportunities,
        'total_pipeline_value': float(total_pipeline_value),
        'weighted_pipeline': float(weighted_pipeline),
        'recent_customers': recent_customers,
        'recent_leads': recent_leads,
        'upcoming_followups': upcoming_followups,
        'recent_activities': recent_activities,
        'opportunity_stages': opportunity_stages,
        'monthly_sales': monthly_sales,
    }


# ── Routes ──────────────────────────────────────────────────────────


@dashboard_bp.route('/')
@login_required
def root():
    """Root URL redirects to the dashboard."""
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard view with all statistics."""
    data = _build_dashboard_data()

    # Prepare chart data for templates
    all_stages = ['Qualification', 'Needs Analysis', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    pipeline_chart = {
        'labels': all_stages,
        'values': [data['opportunity_stages'].get(s, 0) for s in all_stages],
    }
    status_chart = {
        'labels': ['Open', 'Won', 'Lost'],
        'values': [data['open_opportunities'], data['won_opportunities'], data['lost_opportunities']],
    }

    return render_template(
        'dashboard/index.html',
        total_customers=data['total_customers'],
        total_leads=data['total_leads'],
        open_opportunities=data['open_opportunities'],
        won_opportunities=data['won_opportunities'],
        lost_opportunities=data['lost_opportunities'],
        total_pipeline=data['total_pipeline_value'],
        weighted_pipeline=data['weighted_pipeline'],
        recent_customers=data['recent_customers'],
        recent_leads=data['recent_leads'],
        upcoming_followups=data['upcoming_followups'],
        recent_activities=data['recent_activities'],
        pipeline_chart=pipeline_chart,
        status_chart=status_chart,
    )


@dashboard_bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats_api():
    """JSON endpoint returning all dashboard statistics."""
    data = _build_dashboard_data()

    # Serialise ORM objects to dicts for JSON response
    serialised = {
        'total_customers': data['total_customers'],
        'total_leads': data['total_leads'],
        'open_opportunities': data['open_opportunities'],
        'won_opportunities': data['won_opportunities'],
        'lost_opportunities': data['lost_opportunities'],
        'total_pipeline_value': data['total_pipeline_value'],
        'weighted_pipeline': data['weighted_pipeline'],
        'opportunity_stages': data['opportunity_stages'],
        'monthly_sales': data['monthly_sales'],
        'recent_customers': [
            {
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'company': c.company,
                'created_at': c.created_at.isoformat() if c.created_at else None,
            }
            for c in data['recent_customers']
        ],
        'recent_leads': [
            {
                'id': l.id,
                'name': l.name,
                'email': l.email,
                'company': l.company,
                'status': l.status,
                'created_at': l.created_at.isoformat() if l.created_at else None,
            }
            for l in data['recent_leads']
        ],
        'upcoming_followups': [
            {
                'id': f.id,
                'subject': f.subject,
                'due_date': f.due_date.isoformat() if f.due_date else None,
                'status': f.status,
                'is_overdue': f.is_overdue,
            }
            for f in data['upcoming_followups']
        ],
        'recent_activities': [
            {
                'id': a.id,
                'subject': a.subject,
                'type': a.type,
                'status': a.status,
                'activity_date': a.activity_date.isoformat() if a.activity_date else None,
            }
            for a in data['recent_activities']
        ],
    }

    return jsonify(serialised)
