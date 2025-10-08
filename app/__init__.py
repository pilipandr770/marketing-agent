# file: app/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db, migrate, login_manager, csrf
from .jobs.scheduler import init_scheduler

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    # Configuration
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev_secret_change_in_production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///marketing.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints (will be imported after models are defined)
    with app.app_context():
        from .views.auth import auth_bp
        from .views.dashboard import dashboard_bp
        from .views.schedule import schedule_bp
        from .views.content import content_bp
        from .views.files import files_bp
        from .billing.webhook import billing_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(schedule_bp)
        app.register_blueprint(content_bp)
        app.register_blueprint(files_bp)
        app.register_blueprint(billing_bp, url_prefix="/billing")

        # Initialize scheduler
        init_scheduler(app)

    @app.context_processor
    def inject_globals():
        return {
            "STRIPE_PUBLIC_KEY": os.getenv("STRIPE_PUBLIC_KEY", ""),
        }

    return app