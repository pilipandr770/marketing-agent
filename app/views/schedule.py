# file: app/views/schedule.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from ..extensions import db
from ..forms import ScheduleForm
from ..models import Schedule
from ..jobs.scheduler import schedule_job

schedule_bp = Blueprint("schedule", __name__, url_prefix="/schedule")

@schedule_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ScheduleForm()
    
    if form.validate_on_submit():
        # Check if selected channel is configured
        channel = form.channel.data
        channel_configured = True
        warning_msg = None
        
        if channel == "telegram":
            if not current_user.telegram_token or not current_user.telegram_chat_id:
                channel_configured = False
                warning_msg = "Warnung: Telegram ist nicht konfiguriert. Content wird generiert, aber nicht automatisch veröffentlicht."
        
        schedule = Schedule(
            user_id=current_user.id,
            channel=form.channel.data,
            cron_expression=form.cron_expression.data.strip(),
            content_template=form.content_template.data.strip(),
            generate_image=form.generate_image.data,
            generate_voice=form.generate_voice.data,
            content_type=form.content_type.data,
            active=form.active.data
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        flash("Zeitplan erfolgreich erstellt.", "success")
        if not channel_configured and warning_msg:
            flash(warning_msg, "warning")
        
        return redirect(url_for("schedule.index"))
    
    # Get user's schedules
    schedules = Schedule.query.filter_by(user_id=current_user.id)\
                            .order_by(Schedule.created_at.desc()).all()
    
    # Check channel configurations for display
    import json
    channel_config = {
        'telegram': bool(current_user.telegram_token and current_user.telegram_chat_id),
        'linkedin': bool(current_user.linkedin_access_token and current_user.linkedin_urn),
        'facebook': bool(current_user.meta_access_token and current_user.facebook_page_id),
        'instagram': bool(current_user.meta_access_token and current_user.instagram_business_id)
    }
    
    return render_template("schedule/index.html", 
                          form=form, 
                          schedules=schedules,
                          channel_config_json=json.dumps(channel_config))

@schedule_bp.route("/edit/<int:schedule_id>", methods=["GET", "POST"])
@login_required
def edit(schedule_id):
    schedule = Schedule.query.filter_by(
        id=schedule_id, 
        user_id=current_user.id
    ).first_or_404()
    
    form = ScheduleForm(obj=schedule)
    
    if form.validate_on_submit():
        schedule.channel = form.channel.data
        schedule.cron_expression = form.cron_expression.data.strip()
        schedule.content_template = form.content_template.data.strip()
        schedule.generate_image = form.generate_image.data
        schedule.generate_voice = form.generate_voice.data
        schedule.content_type = form.content_type.data
        schedule.active = form.active.data
        
        db.session.commit()
        
        flash("Zeitplan erfolgreich aktualisiert.", "success")
        return redirect(url_for("schedule.index"))
    
    return render_template("schedule/edit.html", form=form, schedule=schedule)

@schedule_bp.route("/toggle/<int:schedule_id>")
@login_required
def toggle(schedule_id):
    schedule = Schedule.query.filter_by(
        id=schedule_id, 
        user_id=current_user.id
    ).first_or_404()
    
    schedule.active = not schedule.active
    db.session.commit()
    
    status = "aktiviert" if schedule.active else "deaktiviert"
    flash(f"Zeitplan {status}.", "success")
    
    return redirect(url_for("schedule.index"))

@schedule_bp.route("/delete/<int:schedule_id>")
@login_required
def delete(schedule_id):
    schedule = Schedule.query.filter_by(
        id=schedule_id, 
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(schedule)
    db.session.commit()
    
    flash("Zeitplan gelöscht.", "info")
    return redirect(url_for("schedule.index"))

@schedule_bp.route("/run-now/<int:schedule_id>")
@login_required
def run_now(schedule_id):
    """Manually trigger a scheduled job"""
    schedule = Schedule.query.filter_by(
        id=schedule_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Check if channel is configured
    if schedule.channel == "telegram":
        if not current_user.telegram_token or not current_user.telegram_chat_id:
            flash("Telegram ist nicht konfiguriert. Bitte fügen Sie Bot Token und Chat ID in den Einstellungen hinzu.", "warning")
            return redirect(url_for("schedule.index"))
    
    try:
        if schedule_job(schedule_id):
            flash("Zeitplan wird ausgeführt... Überprüfen Sie Ihren Kanal in wenigen Sekunden.", "success")
        else:
            flash("Fehler beim Ausführen des Zeitplans. Scheduler möglicherweise nicht initialisiert.", "danger")
    except Exception as e:
        flash(f"Fehler beim Ausführen des Zeitplans: {str(e)}", "danger")
    
    return redirect(url_for("schedule.index"))

@schedule_bp.route("/validate-cron", methods=["POST"])
@login_required
def validate_cron():
    """Validate CRON expression via AJAX"""
    cron_expr = request.json.get('cron', '')
    
    try:
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime
        
        # Parse CRON expression
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            raise ValueError("CRON expression must have exactly 5 parts")
        
        minute, hour, day, month, day_of_week = parts
        
        # Create trigger to validate
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week
        )
        
        # Get next run times for preview
        now = datetime.now()
        next_runs = []
        
        for i in range(3):  # Show next 3 runs
            next_run = trigger.get_next_fire_time(None, now)
            if next_run:
                next_runs.append(next_run.strftime("%d.%m.%Y %H:%M"))
                now = next_run
            else:
                break
        
        return jsonify({
            "valid": True,
            "next_runs": next_runs
        })
    
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": str(e)
        })

@schedule_bp.route("/cron-examples")
@login_required
def cron_examples():
    """Show CRON examples"""
    examples = [
        {"cron": "0 9 * * *", "description": "Täglich um 9:00 Uhr"},
        {"cron": "0 9 * * 1-5", "description": "Werktags um 9:00 Uhr"},
        {"cron": "0 9,18 * * *", "description": "Täglich um 9:00 und 18:00 Uhr"},
        {"cron": "*/30 * * * *", "description": "Alle 30 Minuten"},
        {"cron": "0 12 * * 1", "description": "Jeden Montag um 12:00 Uhr"},
        {"cron": "0 9 1 * *", "description": "Am 1. jeden Monats um 9:00 Uhr"},
    ]
    
    return render_template("schedule/cron_examples.html", examples=examples)