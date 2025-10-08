# file: app/views/content.py
import base64
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from io import BytesIO
from ..forms import GenerateContentForm
from ..models import GeneratedContent
from ..extensions import db
from ..openai_service import (
    build_system_prompt, generate_post_text, 
    generate_image_b64, generate_tts_audio
)
from ..publishers.telegram_publisher import TelegramPublisher
from ..publishers.linkedin_publisher import LinkedInPublisher
from ..publishers.meta_publisher import FacebookPublisher, InstagramPublisher

content_bp = Blueprint("content", __name__, url_prefix="/content")

def get_publisher(channel: str, user):
    """
    Publisher factory - повертає інстанс паблішера залежно від каналу і налаштувань користувача.
    """
    if channel == "telegram":
        if not user.telegram_token or not user.telegram_chat_id:
            return None
        return TelegramPublisher({
            "bot_token": user.telegram_token,
            "chat_id": user.telegram_chat_id
        })

    if channel == "linkedin":
        if not user.linkedin_access_token or not user.linkedin_urn:
            return None
        return LinkedInPublisher({
            "access_token": user.linkedin_access_token,
            "urn": user.linkedin_urn
        })

    if channel == "facebook":
        if not user.meta_access_token or not user.facebook_page_id:
            return None
        return FacebookPublisher({
            "access_token": user.meta_access_token,
            "page_id": user.facebook_page_id
        })

    if channel == "instagram":
        if not user.meta_access_token or not user.instagram_business_id:
            return None
        return InstagramPublisher({
            "access_token": user.meta_access_token,
            "ig_business_id": user.instagram_business_id
        })

    return None

@content_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = GenerateContentForm()
    generated_content = None
    
    if form.validate_on_submit():
        try:
            # Build system prompt
            system_prompt = build_system_prompt(
                current_user.openai_system_prompt,
                form.channel.data
            )
            
            # Generate text content
            text_content = generate_post_text(
                topic=form.topic.data,
                channel=form.channel.data,
                system_prompt=system_prompt,
                user_api_key=current_user.openai_api_key
            )
            
            # Generate image if requested
            image_b64 = None
            if form.generate_image.data:
                image_b64 = generate_image_b64(
                    topic=form.topic.data,
                    channel=form.channel.data,
                    user_api_key=current_user.openai_api_key
                )
            
            # Generate voice if requested
            voice_bytes = None
            if form.generate_voice.data:
                voice_bytes = generate_tts_audio(
                    text=text_content,
                    user_api_key=current_user.openai_api_key
                )
            
            # Save generated content
            content = GeneratedContent(
                user_id=current_user.id,
                text_content=text_content,
                channel=form.channel.data
            )
            
            db.session.add(content)
            db.session.commit()
            
            # Auto-publish if requested and channel is configured
            if form.auto_publish.data:
                publisher = get_publisher(form.channel.data, current_user)
                if publisher:
                    try:
                        result = publisher.publish(
                            content_type=form.content_type.data,
                            text=text_content,
                            image_b64=image_b64
                        )
                        
                        if result.get("success"):
                            content.published = True
                            content.publication_response = str(result)
                            db.session.commit()
                            flash(f"Content erfolgreich auf {form.channel.data.title()} veröffentlicht!", "success")
                        else:
                            flash(f"Fehler bei Veröffentlichung: {result.get('error', 'Unbekannter Fehler')}", "warning")
                    
                    except Exception as e:
                        flash(f"Fehler bei der Veröffentlichung: {str(e)}", "warning")
                else:
                    flash(f"{form.channel.data.title()} ist nicht konfiguriert. Content wurde nur generiert.", "info")
            
            generated_content = {
                "text": text_content,
                "image_b64": image_b64,
                "voice_available": bool(voice_bytes),
                "content_id": content.id
            }
            
            # Store voice temporarily for download (in production, use proper storage)
            if voice_bytes:
                # You could store this in Redis, database, or file system
                # For now, we'll use session storage (not recommended for production)
                pass
            
        except Exception as e:
            flash(f"Fehler bei der Content-Generierung: {str(e)}", "danger")
    
    # Get recent generated content
    recent_content = GeneratedContent.query.filter_by(user_id=current_user.id)\
                                          .order_by(GeneratedContent.created_at.desc())\
                                          .limit(10).all()
    
    return render_template("content/generator.html", 
                          form=form, 
                          generated_content=generated_content,
                          recent_content=recent_content)

@content_bp.route("/history")
@login_required
def history():
    """View content generation history"""
    page = request.args.get('page', 1, type=int)
    
    content_history = GeneratedContent.query.filter_by(user_id=current_user.id)\
                                           .order_by(GeneratedContent.created_at.desc())\
                                           .paginate(page=page, per_page=20, error_out=False)
    
    return render_template("content/history.html", content_history=content_history)

@content_bp.route("/publish/<int:content_id>/<channel>")
@login_required
def publish_content(content_id, channel):
    """Publish existing generated content"""
    content = GeneratedContent.query.filter_by(
        id=content_id, 
        user_id=current_user.id
    ).first_or_404()
    
    publisher = get_publisher(channel, current_user)
    if not publisher:
        flash(f"{channel.title()} ist nicht konfiguriert.", "warning")
        return redirect(url_for("content.history"))
    
    try:
        result = publisher.publish(
            content_type="post",
            text=content.text_content
        )
        
        if result.get("success"):
            content.published = True
            content.channel = channel
            content.publication_response = str(result)
            db.session.commit()
            flash(f"Content erfolgreich auf {channel.title()} veröffentlicht!", "success")
        else:
            flash(f"Fehler bei Veröffentlichung: {result.get('error', 'Unbekannter Fehler')}", "warning")
    
    except Exception as e:
        flash(f"Fehler bei der Veröffentlichung: {str(e)}", "danger")
    
    return redirect(url_for("content.history"))

@content_bp.route("/test-connection/<channel>")
@login_required
def test_connection(channel):
    """Test connection to social media platform"""
    publisher = get_publisher(channel, current_user)
    
    if not publisher:
        return jsonify({
            "success": False,
            "message": f"{channel.title()} ist nicht konfiguriert."
        })
    
    try:
        if channel == "telegram":
            result = publisher.test_connection()
            if result.get("success"):
                bot_info = result["response"]["result"]
                return jsonify({
                    "success": True,
                    "message": f"Verbindung erfolgreich! Bot: @{bot_info.get('username', 'N/A')}"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"Verbindung fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}"
                })
        
        return jsonify({
            "success": False,
            "message": "Test für diesen Kanal noch nicht implementiert."
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Fehler beim Verbindungstest: {str(e)}"
        })