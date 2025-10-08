# file: app/jobs/scheduler.py
import os
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import atexit

logger = logging.getLogger(__name__)
scheduler = None

def init_scheduler(app):
    """Initialize APScheduler with Flask app context"""
    global scheduler
    
    if scheduler is not None:
        return scheduler
    
    # Configure job stores and executors
    # Use MemoryJobStore for simpler operation (no pickle issues)
    jobstores = {
        'default': None  # Use in-memory storage
    }
    
    executors = {
        'default': ThreadPoolExecutor(20)
    }
    
    job_defaults = {
        'coalesce': False,
        'max_instances': 3,
        'misfire_grace_time': 300  # 5 minutes
    }
    
    scheduler = BackgroundScheduler(
        executors=executors,
        job_defaults=job_defaults,
        timezone=os.getenv('SCHEDULER_TIMEZONE', 'Europe/Berlin')
    )
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started successfully")
    
    # Add cleanup job that runs every minute to refresh schedules
    scheduler.add_job(
        func=refresh_user_schedules,
        trigger='interval',
        minutes=1,
        id='refresh_schedules',
        replace_existing=True,
        kwargs={'app': app}
    )
    
    # Shutdown scheduler when app exits
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler

def refresh_user_schedules(app):
    """Refresh all user schedules - runs every minute"""
    with app.app_context():
        try:
            from ..models import Schedule, User
            
            # Get all active schedules
            active_schedules = Schedule.query.filter_by(active=True).all()
            
            # Get current job IDs
            current_jobs = {job.id for job in scheduler.get_jobs()}
            
            # Expected job IDs based on active schedules
            expected_jobs = {f"schedule_{s.id}" for s in active_schedules}
            expected_jobs.add("refresh_schedules")  # Don't remove the refresh job
            
            # Remove jobs that are no longer active
            jobs_to_remove = current_jobs - expected_jobs
            for job_id in jobs_to_remove:
                try:
                    scheduler.remove_job(job_id)
                    logger.info(f"Removed inactive job: {job_id}")
                except Exception as e:
                    logger.error(f"Error removing job {job_id}: {e}")
            
            # Add/update active schedules
            for schedule in active_schedules:
                job_id = f"schedule_{schedule.id}"
                
                try:
                    # Parse CRON expression
                    cron_parts = schedule.cron_expression.strip().split()
                    if len(cron_parts) != 5:
                        logger.error(f"Invalid CRON expression for schedule {schedule.id}: {schedule.cron_expression}")
                        continue
                    
                    minute, hour, day, month, day_of_week = cron_parts
                    
                    # Create CRON trigger
                    trigger = CronTrigger(
                        minute=minute,
                        hour=hour,
                        day=day,
                        month=month,
                        day_of_week=day_of_week,
                        timezone=schedule.timezone or 'Europe/Berlin'
                    )
                    
                    # Add or replace job
                    scheduler.add_job(
                        func=execute_scheduled_post,
                        trigger=trigger,
                        id=job_id,
                        kwargs={'schedule_id': schedule.id, 'app': app},
                        replace_existing=True
                    )
                    
                    # Update next run time
                    job = scheduler.get_job(job_id)
                    if job and job.next_run_time:
                        schedule.next_run = job.next_run_time.replace(tzinfo=None)
                        from ..extensions import db
                        db.session.commit()
                
                except Exception as e:
                    logger.error(f"Error scheduling job for schedule {schedule.id}: {e}")
        
        except Exception as e:
            logger.error(f"Error in refresh_user_schedules: {e}")

def execute_scheduled_post(schedule_id, app):
    """Execute a scheduled social media post"""
    with app.app_context():
        try:
            from ..models import Schedule, User, GeneratedContent
            from ..extensions import db
            from ..openai_service import build_system_prompt, generate_post_text, generate_image_b64
            from ..publishers.telegram_publisher import TelegramPublisher
            from ..publishers.linkedin_publisher import LinkedInPublisher
            from ..publishers.meta_publisher import FacebookPublisher, InstagramPublisher
            
            # Get schedule and user
            schedule = Schedule.query.get(schedule_id)
            if not schedule or not schedule.active:
                logger.warning(f"Schedule {schedule_id} not found or inactive")
                return
            
            user = User.query.get(schedule.user_id)
            if not user or not user.is_active:
                logger.warning(f"User {schedule.user_id} not found or inactive")
                return
            
            logger.info(f"Executing scheduled post for user {user.email}, schedule {schedule.id}")
            
            # Check if user has OpenAI API key
            if not user.openai_api_key and not os.getenv("OPENAI_API_KEY"):
                logger.error(f"No OpenAI API key configured for user {user.email}")
                raise ValueError("OpenAI API key not configured")
            
            # Build system prompt
            system_prompt = build_system_prompt(user.openai_system_prompt, schedule.channel)
            
            # Generate content
            text_content = generate_post_text(
                topic=schedule.content_template,
                channel=schedule.channel,
                system_prompt=system_prompt,
                user_api_key=user.openai_api_key
            )
            
            # Generate image if requested
            image_b64 = None
            if schedule.generate_image:
                image_b64 = generate_image_b64(
                    topic=schedule.content_template,
                    channel=schedule.channel,
                    user_api_key=user.openai_api_key
                )
            
            # Save generated content
            content = GeneratedContent(
                user_id=user.id,
                schedule_id=schedule.id,
                text_content=text_content,
                channel=schedule.channel
            )
            db.session.add(content)
            
            # Publish to channel
            publisher = None
            if schedule.channel == "telegram":
                if not user.telegram_token or not user.telegram_chat_id:
                    logger.warning(f"Telegram not configured for user {user.email}. Content generated but not published.")
                    content.publication_response = "Telegram ist nicht konfiguriert. Content wurde nur generiert."
                else:
                    config = {
                        "bot_token": user.telegram_token,
                        "chat_id": user.telegram_chat_id
                    }
                    publisher = TelegramPublisher(config)
            
            elif schedule.channel == "linkedin":
                if not user.linkedin_access_token or not user.linkedin_urn:
                    logger.warning(f"LinkedIn not configured for user {user.email}. Content generated but not published.")
                    content.publication_response = "LinkedIn ist nicht konfiguriert. Content wurde nur generiert."
                else:
                    config = {
                        "access_token": user.linkedin_access_token,
                        "urn": user.linkedin_urn
                    }
                    publisher = LinkedInPublisher(config)
            
            elif schedule.channel == "facebook":
                if not user.meta_access_token or not user.facebook_page_id:
                    logger.warning(f"Facebook not configured for user {user.email}. Content generated but not published.")
                    content.publication_response = "Facebook ist nicht konfiguriert. Content wurde nur generiert."
                else:
                    config = {
                        "access_token": user.meta_access_token,
                        "page_id": user.facebook_page_id
                    }
                    publisher = FacebookPublisher(config)
            
            elif schedule.channel == "instagram":
                if not user.meta_access_token or not user.instagram_business_id:
                    logger.warning(f"Instagram not configured for user {user.email}. Content generated but not published.")
                    content.publication_response = "Instagram ist nicht konfiguriert. Content wurde nur generiert."
                else:
                    config = {
                        "access_token": user.meta_access_token,
                        "instagram_id": user.instagram_business_id
                    }
                    publisher = InstagramPublisher(config)
            
            if publisher:
                try:
                    result = publisher.publish(
                        content_type=schedule.content_type,
                        text=text_content,
                        image_b64=image_b64
                    )
                    
                    if result.get("success"):
                        content.published = True
                        content.published_at = datetime.utcnow()
                        content.publication_response = str(result)
                        logger.info(f"Successfully published scheduled post for user {user.email}")
                    else:
                        logger.error(f"Failed to publish scheduled post for user {user.email}: {result.get('error')}")
                        content.publication_response = f"Error: {result.get('error')}"
                
                except Exception as e:
                    logger.error(f"Exception publishing scheduled post for user {user.email}: {e}")
                    content.publication_response = f"Exception: {str(e)}"
            else:
                logger.warning(f"No publisher configured for {schedule.channel} for user {user.email}")
                content.publication_response = f"No publisher configured for {schedule.channel}"
            
            # Update schedule last run time
            schedule.last_run = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error executing scheduled post {schedule_id}: {e}")

def schedule_job(schedule_id):
    """Manually trigger a scheduled job"""
    if scheduler is None:
        logger.error("Scheduler not initialized")
        return False
    
    job_id = f"schedule_{schedule_id}"
    job = scheduler.get_job(job_id)
    
    if job:
        try:
            job.modify(next_run_time=datetime.now())
            return True
        except Exception as e:
            logger.error(f"Error triggering job {job_id}: {e}")
            return False
    else:
        logger.error(f"Job {job_id} not found")
        return False