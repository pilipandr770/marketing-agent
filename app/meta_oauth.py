# file: app/meta_oauth.py
"""
Meta (Facebook/Instagram) OAuth 2.0 Integration
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

meta_bp = Blueprint('meta', __name__, url_prefix='/meta')

# Meta OAuth endpoints
AUTHORIZATION_URL = "https://www.facebook.com/v20.0/dialog/oauth"
TOKEN_URL = "https://graph.facebook.com/v20.0/oauth/access_token"
GRAPH_URL = "https://graph.facebook.com/v20.0"

# Required scopes for posting
SCOPES = [
    "pages_manage_posts",      # Facebook page posting
    "pages_read_engagement",   # Read page info
    "instagram_basic",         # Instagram basic access
    "instagram_content_publish" # Instagram posting
]

def get_oauth_config():
    """Get OAuth configuration from environment"""
    app_id = os.getenv("META_APP_ID")
    app_secret = os.getenv("META_APP_SECRET")
    redirect_uri = os.getenv("META_REDIRECT_URI")

    if not app_id or not app_secret:
        raise ValueError("Meta OAuth credentials not configured. Set META_APP_ID and META_APP_SECRET")

    return {
        "app_id": app_id,
        "app_secret": app_secret,
        "redirect_uri": redirect_uri or url_for('meta.callback', _external=True)
    }


@meta_bp.route('/auth')
@login_required
def auth():
    """
    Initiate Meta OAuth flow.
    Redirects user to Facebook authorization page.
    """
    try:
        config = get_oauth_config()

        # Generate and store state token for CSRF protection
        state = secrets.token_urlsafe(32)
        session['meta_oauth_state'] = state

        # Build authorization URL
        params = {
            "client_id": config["app_id"],
            "redirect_uri": config["redirect_uri"],
            "state": state,
            "scope": ",".join(SCOPES),
            "response_type": "code"
        }

        auth_url = f"{AUTHORIZATION_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        logger.info(f"Redirecting user {current_user.id} to Meta OAuth")

        return redirect(auth_url)

    except Exception as e:
        logger.error(f"Meta OAuth initiation failed: {e}")
        flash("Помилка при підключенні до Meta", "danger")
        return redirect(url_for('dashboard.settings'))


@meta_bp.route('/callback')
@login_required
def callback():
    """
    Handle OAuth callback from Meta.
    Exchange authorization code for access token.
    """
    try:
        # Verify state token (CSRF protection)
        state = request.args.get('state')
        stored_state = session.pop('meta_oauth_state', None)

        if not state or state != stored_state:
            raise ValueError("Invalid state parameter - possible CSRF attack")

        # Check for errors
        error = request.args.get('error')
        if error:
            error_description = request.args.get('error_description', 'Unknown error')
            raise ValueError(f"Meta OAuth error: {error} - {error_description}")

        # Get authorization code
        code = request.args.get('code')
        if not code:
            raise ValueError("No authorization code received")

        # Exchange code for access token
        config = get_oauth_config()
        token_response = requests.get(
            TOKEN_URL,
            params={
                "client_id": config["app_id"],
                "client_secret": config["app_secret"],
                "redirect_uri": config["redirect_uri"],
                "code": code
            },
            timeout=30
        )

        if token_response.status_code != 200:
            raise ValueError(f"Token exchange failed: {token_response.text}")

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise ValueError("No access token in response")

        # Get user's pages to obtain Facebook Page ID
        pages_response = requests.get(
            f"{GRAPH_URL}/me/accounts",
            params={"access_token": access_token},
            timeout=30
        )

        facebook_page_id = None
        if pages_response.status_code == 200:
            pages_data = pages_response.json()
            if pages_data.get("data"):
                # Take the first page (user can change later if needed)
                facebook_page_id = pages_data["data"][0]["id"]
                logger.info(f"Found Facebook Page ID: {facebook_page_id}")

        # Get Instagram Business Account ID from the page
        instagram_business_id = None
        if facebook_page_id:
            page_response = requests.get(
                f"{GRAPH_URL}/{facebook_page_id}",
                params={
                    "fields": "instagram_business_account{id}",
                    "access_token": access_token
                },
                timeout=30
            )

            if page_response.status_code == 200:
                page_data = page_response.json()
                ig_account = page_data.get("instagram_business_account")
                if ig_account:
                    instagram_business_id = ig_account["id"]
                    logger.info(f"Found Instagram Business Account ID: {instagram_business_id}")

        # Save to database
        current_user.meta_access_token = access_token
        current_user.facebook_page_id = facebook_page_id
        current_user.instagram_business_id = instagram_business_id
        db.session.commit()

        logger.info(f"Meta OAuth successful for user {current_user.id}: FB={facebook_page_id}, IG={instagram_business_id}")
        flash("Meta успішно підключено!", "success")

        return redirect(url_for('dashboard.settings'))

    except Exception as e:
        logger.error(f"Meta OAuth callback failed: {e}")
        flash(f"Помилка при підключенні Meta: {str(e)}", "danger")
        return redirect(url_for('dashboard.settings'))


@meta_bp.route('/disconnect')
@login_required
def disconnect():
    """
    Disconnect Meta account.
    Removes access token and IDs from database.
    """
    try:
        current_user.meta_access_token = None
        current_user.facebook_page_id = None
        current_user.instagram_business_id = None
        db.session.commit()

        logger.info(f"Meta disconnected for user {current_user.id}")
        flash("Meta відключено", "info")

    except Exception as e:
        logger.error(f"Meta disconnect failed: {e}")
        flash("Помилка при відключенні Meta", "danger")

    return redirect(url_for('dashboard.settings'))
