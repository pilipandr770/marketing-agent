# file: app/views/dashboard.py
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import SettingsForm
from ..models import User, Schedule, GeneratedContent
from ..billing.stripe_service import create_checkout_session

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
@login_required
def index():
    # Get user statistics
    stats = {
        'active_schedules': Schedule.query.filter_by(user_id=current_user.id, active=True).count(),
        'total_schedules': Schedule.query.filter_by(user_id=current_user.id).count(),
        'generated_content': GeneratedContent.query.filter_by(user_id=current_user.id).count(),
        'published_content': GeneratedContent.query.filter_by(user_id=current_user.id, published=True).count()
    }
    
    # Recent activity
    recent_content = GeneratedContent.query.filter_by(user_id=current_user.id)\
                                           .order_by(GeneratedContent.created_at.desc())\
                                           .limit(5).all()
    
    # Check if system API keys are available
    has_system_openai = bool(os.getenv('OPENAI_API_KEY'))
    
    return render_template("dashboard/index.html", stats=stats, recent_content=recent_content, has_system_openai=has_system_openai)

@dashboard_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm(obj=current_user)
    
    if form.validate_on_submit():
        # Update user settings
        current_user.telegram_token = form.telegram_token.data.strip() if form.telegram_token.data else None
        current_user.telegram_chat_id = form.telegram_chat_id.data.strip() if form.telegram_chat_id.data else None
        current_user.openai_system_prompt = form.openai_system_prompt.data.strip() if form.openai_system_prompt.data else None
        current_user.openai_api_key = form.openai_api_key.data.strip() if form.openai_api_key.data else None
        
        db.session.commit()
        flash("Einstellungen erfolgreich gespeichert.", "success")
        return redirect(url_for("dashboard.settings"))
    
    return render_template("dashboard/settings.html", form=form)

@dashboard_bp.route("/billing")
@login_required
def billing():
    return render_template("dashboard/billing.html")

@dashboard_bp.route("/subscribe/<plan>")
@login_required
def subscribe(plan):
    """Create Stripe checkout session for subscription"""
    price_map = {
        "basic": os.getenv("STRIPE_PRICE_BASIC"),
        "pro": os.getenv("STRIPE_PRICE_PRO"),
        "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE")
    }
    
    price_id = price_map.get(plan)
    if not price_id:
        flash("Unbekannter Tarif ausgewählt.", "danger")
        return redirect(url_for("dashboard.billing"))
    
    success_url = url_for("dashboard.billing", _external=True) + "?status=success"
    cancel_url = url_for("dashboard.billing", _external=True) + "?status=cancel"
    
    try:
        session = create_checkout_session(
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=current_user.email
        )
        return redirect(session.url, code=303)
    except Exception as e:
        flash(f"Fehler beim Erstellen der Zahlungssitzung: {str(e)}", "danger")
        return redirect(url_for("dashboard.billing"))