# file: app/views/public.py
from flask import Blueprint, render_template, redirect, url_for

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def landing():
    """Landing page for non-authenticated users"""
    return render_template("landing.html")

@public_bp.route("/favicon.ico")
def favicon():
    """Redirect legacy favicon.ico requests to favicon.png"""
    return redirect(url_for("static", filename="img/favicon.png"), code=301)

@public_bp.route("/datenschutz")
def datenschutz():
    """Privacy policy page"""
    return render_template("datenschutz.html")

@public_bp.route("/agb")
def agb():
    """Terms and conditions page"""
    return render_template("agb.html")

@public_bp.route("/impressum")
def impressum():
    """Imprint page (German legal requirement)"""
    return render_template("impressum.html")

@public_bp.route("/data-deletion")
def data_deletion():
    """Data deletion page (GDPR compliance & Meta requirement)"""
    from flask_login import current_user
    from ..models import Schedule, FileAsset
    from ..extensions import db
    
    schedule_count = 0
    file_count = 0
    
    if current_user.is_authenticated:
        schedule_count = Schedule.query.filter_by(user_id=current_user.id).count()
        file_count = FileAsset.query.filter_by(user_id=current_user.id).count()
    
    return render_template("data_deletion.html", 
                          schedule_count=schedule_count,
                          file_count=file_count)
