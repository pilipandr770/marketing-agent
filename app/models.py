# file: app/models.py
from datetime import datetime
from flask_login import UserMixin
from .extensions import db

class User(db.Model, UserMixin):
    __table_args__ = {'schema': 'marketing_agent'}
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Multi-tenant social media channel configurations
    telegram_token = db.Column(db.String(256))
    telegram_chat_id = db.Column(db.String(128))
    facebook_access_token = db.Column(db.String(512))
    facebook_page_id = db.Column(db.String(128))
    linkedin_access_token = db.Column(db.String(512))
    instagram_access_token = db.Column(db.String(512))

    # OpenAI per-user configuration (scalable multi-tenancy)
    openai_vector_store_id = db.Column(db.String(128))
    openai_system_prompt = db.Column(db.Text)
    openai_api_key = db.Column(db.String(256))  # Optional: user can provide their own key

    # Stripe billing
    stripe_customer_id = db.Column(db.String(64))
    stripe_subscription_id = db.Column(db.String(64))
    plan = db.Column(db.String(32), default="free")  # free, basic, pro, enterprise
    plan_expires_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.email}>'

    def get_active_schedules(self):
        return Schedule.query.filter_by(user_id=self.id, active=True).all()

class Schedule(db.Model):
    __table_args__ = {'schema': 'marketing_agent'}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("marketing_agent.user.id"), nullable=False)
    
    # Scheduling configuration
    cron_expression = db.Column(db.String(64), nullable=False)  # CRON format or ISO datetime
    timezone = db.Column(db.String(64), default="Europe/Berlin")
    
    # Publishing configuration
    channel = db.Column(db.String(64), nullable=False)  # telegram, facebook, linkedin, instagram
    content_template = db.Column(db.Text, nullable=False)  # Topic/briefing for content generation
    
    # Content generation settings
    generate_image = db.Column(db.Boolean, default=False)
    generate_voice = db.Column(db.Boolean, default=False)
    content_type = db.Column(db.String(32), default="post")  # post, story, reel
    
    # Status
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)

    user = db.relationship("User", backref=db.backref("schedules", lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Schedule {self.id}: {self.channel} - {self.cron_expression}>'

class FileAsset(db.Model):
    __table_args__ = {'schema': 'marketing_agent'}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("marketing_agent.user.id"), nullable=False)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(128))
    
    # OpenAI integration
    openai_file_id = db.Column(db.String(128))
    vector_store_id = db.Column(db.String(128))
    processing_status = db.Column(db.String(32), default="pending")  # pending, completed, error
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("files", lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<FileAsset {self.filename} for user {self.user_id}>'

class GeneratedContent(db.Model):
    """Store generated content for reuse and analytics"""
    __table_args__ = {'schema': 'marketing_agent'}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("marketing_agent.user.id"), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey("marketing_agent.schedule.id"), nullable=True)
    
    # Generated content
    text_content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(512))
    voice_url = db.Column(db.String(512))
    
    # Publication status
    channel = db.Column(db.String(64), nullable=False)
    published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    publication_response = db.Column(db.Text)  # Store API response for debugging
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("generated_content", lazy=True))
    schedule = db.relationship("Schedule", backref=db.backref("generated_content", lazy=True))

    def __repr__(self):
        return f'<GeneratedContent {self.id} for {self.channel}>'