# file: app/views/auth.py
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db, login_manager
from ..models import User
from ..forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing_user:
            flash("Diese E-Mail-Adresse ist bereits registriert.", "danger")
            return redirect(url_for("auth.register"))
        
        # Create new user
        user = User(
            email=form.email.data.lower().strip(),
            password_hash=generate_password_hash(form.password.data)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash("Konto erfolgreich erstellt! Sie können sich jetzt anmelden.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        
        if user and user.is_active and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            
            # Redirect to next page or dashboard (with open redirect protection)
            next_page = request.args.get('next')
            if next_page:
                # Security fix: validate next_page to prevent open redirect (CodeQL #1)
                from urllib.parse import urlparse, urljoin
                from flask import request as flask_request
                
                # Only allow relative URLs or URLs to the same host
                parsed = urlparse(next_page)
                if parsed.netloc and parsed.netloc != flask_request.host:
                    # External URL detected - redirect to dashboard instead
                    return redirect(url_for("dashboard.index"))
                
                # Make URL safe by joining with request base
                safe_url = urljoin(flask_request.host_url, next_page)
                return redirect(safe_url)
            return redirect(url_for("dashboard.index"))
        else:
            flash("Ungültige E-Mail-Adresse oder Passwort.", "danger")
    
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Sie wurden erfolgreich abgemeldet.", "info")
    return redirect(url_for("auth.login"))