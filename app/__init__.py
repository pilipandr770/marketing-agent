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
    
    # Database configuration with SSL support
    # Try DATABASE_URL first (Render's automatic variable), then SQLALCHEMY_DATABASE_URI
    database_uri = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL", "sqlite:///marketing.db")
    
    # Fix dialect for psycopg3 if needed
    if database_uri.startswith("postgres://"):
        database_uri = database_uri.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_uri.startswith("postgresql://") and "+psycopg" not in database_uri:
        database_uri = database_uri.replace("postgresql://", "postgresql+psycopg://", 1)
    
    # Add SSL mode if PostgreSQL and not present (for external connections)
    if "postgresql" in database_uri and "sslmode=" not in database_uri:
        separator = "&" if "?" in database_uri else "?"
        database_uri = f"{database_uri}{separator}sslmode=require"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    
    # Connection pool settings for better stability
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 300,    # Recycle connections every 5 minutes
        "pool_size": 10,        # Maximum number of connections
        "max_overflow": 20      # Maximum overflow connections
    }

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints (will be imported after models are defined)
    with app.app_context():
        from .views.public import public_bp
        from .views.auth import auth_bp
        from .views.dashboard import dashboard_bp
        from .views.schedule import schedule_bp
        from .views.content import content_bp
        from .views.files import files_bp
        from .billing.webhook import billing_bp
        from .linkedin_oauth import linkedin_bp
        
        app.register_blueprint(public_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(schedule_bp)
        app.register_blueprint(content_bp)
        app.register_blueprint(files_bp)
        app.register_blueprint(billing_bp, url_prefix="/billing")
        app.register_blueprint(linkedin_bp)

        # Initialize scheduler
        init_scheduler(app)
        
        # Register CLI commands
        from . import cli
        cli.init_app(app)

    @app.context_processor
    def inject_globals():
        return {
            "STRIPE_PUBLIC_KEY": os.getenv("STRIPE_PUBLIC_KEY", ""),
        }

    return app