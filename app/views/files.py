# file: app/views/files.py
import os
import mimetypes
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..extensions import db
from ..forms import UploadFileForm
from ..models import FileAsset
from ..openai_service import (
    upload_file_to_openai, 
    add_file_to_vector_store, 
    create_vector_store
)

files_bp = Blueprint("files", __name__, url_prefix="/files")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'md', 'csv', 'json', 'xml',
    'jpg', 'jpeg', 'png', 'gif', 'webp',
    'mp3', 'wav', 'ogg', 'm4a',
    'mp4', 'avi', 'mov', 'wmv', 'webm'
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure upload folder exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@files_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = UploadFileForm()
    
    if form.validate_on_submit():
        ensure_upload_folder()
        
        file = form.file.data
        if file and allowed_file(file.filename):
            try:
                # Secure filename
                original_filename = file.filename
                filename = secure_filename(file.filename)
                
                # Add user prefix to avoid conflicts
                filename = f"user_{current_user.id}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                # Save file temporarily
                file.save(filepath)
                
                # Get file info
                file_size = os.path.getsize(filepath)
                mime_type = mimetypes.guess_type(filepath)[0]
                
                # Upload to OpenAI
                openai_file_id = upload_file_to_openai(
                    file_path=filepath,
                    purpose="assistants",
                    user_api_key=current_user.openai_api_key
                )
                
                if not openai_file_id:
                    flash("Fehler beim Hochladen zu OpenAI.", "danger")
                    os.remove(filepath)  # Clean up
                    return redirect(url_for("files.index"))
                
                # Handle vector store
                vector_store_id = form.vector_store_id.data.strip() if form.vector_store_id.data else None
                
                # Create vector store if user doesn't have one
                if not vector_store_id and not current_user.openai_vector_store_id:
                    vector_store_name = f"User_{current_user.id}_Knowledge_Base"
                    vector_store_id = create_vector_store(
                        name=vector_store_name,
                        user_api_key=current_user.openai_api_key
                    )
                    
                    if vector_store_id:
                        current_user.openai_vector_store_id = vector_store_id
                        db.session.commit()
                        flash(f"Neuer Vector Store erstellt: {vector_store_id}", "info")
                
                # Use user's default vector store if none specified
                if not vector_store_id:
                    vector_store_id = current_user.openai_vector_store_id
                
                # Add to vector store if available
                if vector_store_id and mime_type and mime_type.startswith('text/'):
                    success = add_file_to_vector_store(
                        file_id=openai_file_id,
                        vector_store_id=vector_store_id,
                        user_api_key=current_user.openai_api_key
                    )
                    if not success:
                        flash("Warnung: Datei konnte nicht zum Vector Store hinzugefügt werden.", "warning")
                
                # Save file record
                file_asset = FileAsset(
                    user_id=current_user.id,
                    filename=filename,
                    original_filename=original_filename,
                    file_size=file_size,
                    mime_type=mime_type,
                    openai_file_id=openai_file_id,
                    vector_store_id=vector_store_id,
                    processing_status="completed"
                )
                
                db.session.add(file_asset)
                db.session.commit()
                
                # Clean up temporary file
                os.remove(filepath)
                
                flash("Datei erfolgreich hochgeladen und zu OpenAI hinzugefügt.", "success")
                return redirect(url_for("files.index"))
                
            except Exception as e:
                # Clean up temporary file if exists
                if 'filepath' in locals() and os.path.exists(filepath):
                    os.remove(filepath)
                flash(f"Fehler beim Hochladen: {str(e)}", "danger")
        else:
            flash("Ungültiger Dateityp.", "danger")
    
    # Get user's files
    files = FileAsset.query.filter_by(user_id=current_user.id)\
                          .order_by(FileAsset.created_at.desc()).all()
    
    return render_template("files/index.html", form=form, files=files)

@files_bp.route("/delete/<int:file_id>")
@login_required
def delete(file_id):
    """Delete file from database and OpenAI"""
    file_asset = FileAsset.query.filter_by(
        id=file_id,
        user_id=current_user.id
    ).first_or_404()
    
    try:
        # Delete from OpenAI if file_id exists
        if file_asset.openai_file_id:
            from ..openai_service import get_openai_client
            client = get_openai_client(current_user.openai_api_key)
            try:
                client.files.delete(file_asset.openai_file_id)
            except Exception as e:
                flash(f"Warnung: Datei konnte nicht von OpenAI gelöscht werden: {str(e)}", "warning")
        
        # Delete from database
        db.session.delete(file_asset)
        db.session.commit()
        
        flash("Datei erfolgreich gelöscht.", "success")
        
    except Exception as e:
        flash(f"Fehler beim Löschen: {str(e)}", "danger")
    
    return redirect(url_for("files.index"))

@files_bp.route("/vector-stores")
@login_required
def vector_stores():
    """Manage user's vector stores"""
    try:
        from ..openai_service import get_openai_client
        
        # Check if user has API key
        if not current_user.openai_api_key:
            flash("Bitte fügen Sie zuerst einen OpenAI API-Schlüssel in den Einstellungen hinzu.", "warning")
            return redirect(url_for("files.index"))
        
        client = get_openai_client(current_user.openai_api_key)
        
        # List vector stores
        vector_stores = client.beta.vector_stores.list()
        
        return render_template("files/vector_stores.html", 
                             vector_stores=vector_stores.data)
    
    except TypeError as e:
        flash(f"OpenAI API Kompatibilitätsfehler. Bitte aktualisieren Sie Ihren API-Schlüssel.", "danger")
        return redirect(url_for("files.index"))
    except Exception as e:
        flash(f"Fehler beim Laden der Vector Stores: {str(e)}", "danger")
        return redirect(url_for("files.index"))

@files_bp.route("/create-vector-store", methods=["POST"])
@login_required
def create_vector_store_endpoint():
    """Create new vector store"""
    name = request.form.get('name', '').strip()
    
    if not name:
        flash("Name ist erforderlich.", "danger")
        return redirect(url_for("files.vector_stores"))
    
    try:
        vector_store_id = create_vector_store(
            name=name,
            user_api_key=current_user.openai_api_key
        )
        
        if vector_store_id:
            # Set as user's default if they don't have one
            if not current_user.openai_vector_store_id:
                current_user.openai_vector_store_id = vector_store_id
                db.session.commit()
            
            flash(f"Vector Store '{name}' erfolgreich erstellt.", "success")
        else:
            flash("Fehler beim Erstellen des Vector Stores.", "danger")
    
    except Exception as e:
        flash(f"Fehler: {str(e)}", "danger")
    
    return redirect(url_for("files.vector_stores"))

@files_bp.route("/set-default-vector-store/<vector_store_id>")
@login_required
def set_default_vector_store(vector_store_id):
    """Set default vector store for user"""
    current_user.openai_vector_store_id = vector_store_id
    db.session.commit()
    
    flash("Standard Vector Store aktualisiert.", "success")
    return redirect(url_for("files.vector_stores"))

@files_bp.route("/usage")
@login_required
def usage():
    """Show file usage statistics"""
    stats = {
        'total_files': FileAsset.query.filter_by(user_id=current_user.id).count(),
        'total_size': db.session.query(db.func.sum(FileAsset.file_size))\
                               .filter_by(user_id=current_user.id).scalar() or 0,
        'by_type': db.session.query(FileAsset.mime_type, db.func.count(FileAsset.id))\
                            .filter_by(user_id=current_user.id)\
                            .group_by(FileAsset.mime_type).all()
    }
    
    # Convert bytes to MB
    stats['total_size_mb'] = round(stats['total_size'] / 1024 / 1024, 2)
    
    return render_template("files/usage.html", stats=stats)