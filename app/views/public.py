# file: app/views/public.py
from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def landing():
    """Landing page for non-authenticated users"""
    return render_template("landing.html")

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
