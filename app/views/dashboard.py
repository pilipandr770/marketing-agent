# file: app/views/dashboard.py
import os
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import SettingsForm
from ..models import User, Schedule, GeneratedContent
from ..billing.stripe_service import create_checkout_session

logger = logging.getLogger(__name__)

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
        # Update user settings - Telegram
        current_user.telegram_token = form.telegram_token.data.strip() if form.telegram_token.data else None
        current_user.telegram_chat_id = form.telegram_chat_id.data.strip() if form.telegram_chat_id.data else None
        
        # OpenAI
        current_user.openai_system_prompt = form.openai_system_prompt.data.strip() if form.openai_system_prompt.data else None
        current_user.openai_api_key = form.openai_api_key.data.strip() if form.openai_api_key.data else None
        
        # LinkedIn
        current_user.linkedin_access_token = form.linkedin_access_token.data.strip() if form.linkedin_access_token.data else None
        current_user.linkedin_urn = form.linkedin_urn.data.strip() if form.linkedin_urn.data else None
        
        # Meta (Facebook / Instagram)
        meta_token = form.meta_access_token.data.strip() if form.meta_access_token.data else None
        if meta_token:
            logger.info(f"Processing Meta token, length: {len(meta_token)}")
            # Try to exchange for long-lived token if credentials are available
            try:
                from .meta_oauth import exchange_for_long_lived_token
                old_token = meta_token
                meta_token = exchange_for_long_lived_token(meta_token)
                if meta_token != old_token:
                    logger.info("Meta token was successfully exchanged for long-lived token")
                else:
                    logger.warning("Meta token exchange failed, using original token")
            except Exception as e:
                logger.warning(f"Could not exchange Meta token for long-lived: {e}")
        else:
            logger.info("No Meta token provided")
        
        current_user.meta_access_token = meta_token
        current_user.facebook_page_id = form.facebook_page_id.data.strip() if form.facebook_page_id.data else None
        current_user.instagram_business_id = form.instagram_business_id.data.strip() if form.instagram_business_id.data else None
        
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


# === Data Deletion Routes (GDPR Compliance & Meta Requirement) ===

@dashboard_bp.route("/export-data")
@login_required
def export_user_data():
    """Export all user data as JSON (GDPR Article 20 - Right to data portability)"""
    import json
    from flask import Response
    from datetime import datetime
    from ..models import UserFile
    
    # Collect all user data
    user_data = {
        "export_date": datetime.utcnow().isoformat(),
        "user": {
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "is_premium": current_user.is_premium,
            "subscription_tier": current_user.subscription_tier
        },
        "settings": {
            "openai_system_prompt": current_user.openai_system_prompt,
            "has_openai_key": bool(current_user.openai_api_key),
            "has_telegram_token": bool(current_user.telegram_token),
            "has_linkedin_token": bool(current_user.linkedin_access_token),
            "has_meta_token": bool(current_user.meta_access_token),
            "linkedin_urn": current_user.linkedin_urn,
            "facebook_page_id": current_user.facebook_page_id,
            "instagram_business_id": current_user.instagram_business_id
        },
        "schedules": [
            {
                "id": schedule.id,
                "name": schedule.name,
                "cron_schedule": schedule.cron_schedule,
                "active": schedule.active,
                "channel": schedule.channel,
                "created_at": schedule.created_at.isoformat() if schedule.created_at else None
            }
            for schedule in Schedule.query.filter_by(user_id=current_user.id).all()
        ],
        "files": [
            {
                "filename": file.filename,
                "file_type": file.file_type,
                "uploaded_at": file.uploaded_at.isoformat() if file.uploaded_at else None
            }
            for file in UserFile.query.filter_by(user_id=current_user.id).all()
        ],
        "generated_content": [
            {
                "id": content.id,
                "platform": content.platform,
                "published": content.published,
                "created_at": content.created_at.isoformat() if content.created_at else None
            }
            for content in GeneratedContent.query.filter_by(user_id=current_user.id).order_by(GeneratedContent.created_at.desc()).limit(100).all()
        ]
    }
    
    # Create JSON response
    json_data = json.dumps(user_data, indent=2, ensure_ascii=False)
    
    response = Response(
        json_data,
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment; filename=marketing-agent-data-{current_user.id}.json'
        }
    )
    
    logger.info(f"User {current_user.email} exported their data")
    return response


@dashboard_bp.route("/delete-api-keys", methods=["POST"])
@login_required
def delete_api_keys():
    """Delete all stored API keys"""
    current_user.openai_api_key = None
    current_user.telegram_token = None
    current_user.telegram_chat_id = None
    current_user.linkedin_access_token = None
    current_user.linkedin_urn = None
    current_user.meta_access_token = None
    current_user.facebook_page_id = None
    current_user.instagram_business_id = None
    
    db.session.commit()
    
    logger.info(f"User {current_user.email} deleted all API keys")
    flash("Alle API-Keys wurden erfolgreich gelöscht.", "success")
    return redirect(url_for("public.data_deletion"))


@dashboard_bp.route("/delete-content", methods=["POST"])
@login_required
def delete_user_content():
    """Delete all user's schedules, files and generated content"""
    import os
    from ..models import UserFile
    
    # Delete schedules
    Schedule.query.filter_by(user_id=current_user.id).delete()
    
    # Delete files from filesystem and database
    files = UserFile.query.filter_by(user_id=current_user.id).all()
    for file in files:
        try:
            file_path = os.path.join("app", file.filepath)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Could not delete file {file.filepath}: {e}")
    
    UserFile.query.filter_by(user_id=current_user.id).delete()
    
    # Delete generated content
    GeneratedContent.query.filter_by(user_id=current_user.id).delete()
    
    db.session.commit()
    
    logger.info(f"User {current_user.email} deleted all content")
    flash("Alle Zeitpläne, Dateien und generierte Inhalte wurden gelöscht.", "success")
    return redirect(url_for("public.data_deletion"))


@dashboard_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    """Completely delete user account (GDPR Article 17 - Right to erasure)"""
    import os
    from flask_login import logout_user
    from ..models import UserFile, Subscription
    
    confirm_email = request.form.get("confirm_email", "").strip()
    
    # Verify email confirmation
    if confirm_email != current_user.email:
        flash("E-Mail-Bestätigung stimmt nicht überein. Konto wurde nicht gelöscht.", "danger")
        return redirect(url_for("public.data_deletion"))
    
    user_email = current_user.email
    user_id = current_user.id
    
    # Delete all user data
    try:
        # 1. Delete files from filesystem
        files = UserFile.query.filter_by(user_id=user_id).all()
        for file in files:
            try:
                file_path = os.path.join("app", file.filepath)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Could not delete file {file.filepath}: {e}")
        
        # 2. Delete database records (cascading)
        UserFile.query.filter_by(user_id=user_id).delete()
        Schedule.query.filter_by(user_id=user_id).delete()
        GeneratedContent.query.filter_by(user_id=user_id).delete()
        Subscription.query.filter_by(user_id=user_id).delete()
        
        # 3. Delete user account
        db.session.delete(current_user)
        db.session.commit()
        
        # 4. Logout
        logout_user()
        
        logger.info(f"User account deleted: {user_email} (ID: {user_id})")
        flash("Ihr Konto wurde erfolgreich gelöscht. Wir bedauern, Sie gehen zu sehen.", "success")
        return redirect(url_for("public.landing"))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user account {user_email}: {e}")
        flash("Fehler beim Löschen des Kontos. Bitte kontaktieren Sie den Support.", "danger")
        return redirect(url_for("public.data_deletion"))