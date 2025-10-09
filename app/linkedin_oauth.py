# file: app/linkedin_oauth.py
"""
LinkedIn OAuth 2.0 Integration
Implements Authorization Code Flow for obtaining access tokens.
"""

import os
import secrets
import requests
import logging
from flask import Blueprint, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from .extensions import db
from .models import User

logger = logging.getLogger(__name__)

linkedin_bp = Blueprint('linkedin', __name__, url_prefix='/linkedin')

# LinkedIn OAuth endpoints
AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"

# Required scopes for posting
SCOPES = [
    "openid",
    "profile",
    "email",
    "w_member_social"  # Required for posting on behalf of user
]

def get_oauth_config():
    """Get OAuth configuration from environment"""
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
    
    if not client_id or not client_secret:
        raise ValueError("LinkedIn OAuth credentials not configured. Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET")
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri or url_for('linkedin.callback', _external=True)
    }


@linkedin_bp.route('/auth')
@login_required
def auth():
    """
    Initiate LinkedIn OAuth flow.
    Redirects user to LinkedIn authorization page.
    """
    try:
        config = get_oauth_config()
        
        # Generate and store state token for CSRF protection
        state = secrets.token_urlsafe(32)
        session['linkedin_oauth_state'] = state
        
        # Build authorization URL
        params = {
            "response_type": "code",
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "state": state,
            "scope": " ".join(SCOPES)
        }
        
        auth_url = f"{AUTHORIZATION_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        logger.info(f"Redirecting user {current_user.id} to LinkedIn OAuth")
        
        return redirect(auth_url)
    
    except Exception as e:
        logger.error(f"LinkedIn OAuth initiation failed: {e}")
        flash("Помилка при підключенні до LinkedIn", "danger")
        return redirect(url_for('dashboard.settings'))


@linkedin_bp.route('/callback')
@login_required
def callback():
    """
    Handle OAuth callback from LinkedIn.
    Exchange authorization code for access token.
    """
    try:
        # Verify state token (CSRF protection)
        state = request.args.get('state')
        stored_state = session.pop('linkedin_oauth_state', None)
        
        if not state or state != stored_state:
            raise ValueError("Invalid state parameter - possible CSRF attack")
        
        # Check for errors
        error = request.args.get('error')
        if error:
            error_description = request.args.get('error_description', 'Unknown error')
            raise ValueError(f"LinkedIn OAuth error: {error} - {error_description}")
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            raise ValueError("No authorization code received")
        
        # Exchange code for access token
        config = get_oauth_config()
        token_response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "redirect_uri": config["redirect_uri"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if token_response.status_code != 200:
            raise ValueError(f"Token exchange failed: {token_response.text}")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise ValueError("No access token in response")
        
        # Get user's LinkedIn profile to obtain URN
        profile_response = requests.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if profile_response.status_code != 200:
            raise ValueError(f"Profile fetch failed: {profile_response.text}")
        
        profile_data = profile_response.json()
        linkedin_id = profile_data.get("sub")  # LinkedIn user ID
        
        if not linkedin_id:
            raise ValueError("Could not retrieve LinkedIn user ID")
        
        # Construct person URN
        linkedin_urn = f"urn:li:person:{linkedin_id}"
        
        # Save to database
        current_user.linkedin_access_token = access_token
        current_user.linkedin_urn = linkedin_urn
        db.session.commit()
        
        logger.info(f"LinkedIn OAuth successful for user {current_user.id}: {linkedin_urn}")
        flash("LinkedIn успішно підключено!", "success")
        
        return redirect(url_for('dashboard.settings'))
    
    except Exception as e:
        logger.error(f"LinkedIn OAuth callback failed: {e}")
        flash(f"Помилка при підключенні LinkedIn: {str(e)}", "danger")
        return redirect(url_for('dashboard.settings'))


@linkedin_bp.route('/disconnect')
@login_required
def disconnect():
    """
    Disconnect LinkedIn account.
    Removes access token and URN from database.
    """
    try:
        current_user.linkedin_access_token = None
        current_user.linkedin_urn = None
        db.session.commit()
        
        logger.info(f"LinkedIn disconnected for user {current_user.id}")
        flash("LinkedIn відключено", "info")
    
    except Exception as e:
        logger.error(f"LinkedIn disconnect failed: {e}")
        flash("Помилка при відключенні LinkedIn", "danger")
    
    return redirect(url_for('dashboard.settings'))
