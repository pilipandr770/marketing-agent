# file: app/billing/webhook.py
import os
import stripe
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import User

logger = logging.getLogger(__name__)

billing_bp = Blueprint("billing", __name__)

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@billing_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({"error": "Invalid signature"}), 400
    
    # Handle the event
    try:
        if event["type"] == "customer.subscription.created":
            handle_subscription_created(event["data"]["object"])
        
        elif event["type"] == "customer.subscription.updated":
            handle_subscription_updated(event["data"]["object"])
        
        elif event["type"] == "customer.subscription.deleted":
            handle_subscription_deleted(event["data"]["object"])
        
        elif event["type"] == "invoice.payment_succeeded":
            handle_payment_succeeded(event["data"]["object"])
        
        elif event["type"] == "invoice.payment_failed":
            handle_payment_failed(event["data"]["object"])
        
        elif event["type"] == "checkout.session.completed":
            handle_checkout_completed(event["data"]["object"])
        
        else:
            logger.info(f"Unhandled event type: {event['type']}")
    
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return jsonify({"error": "Webhook handler failed"}), 500
    
    return jsonify({"status": "success"})

def handle_subscription_created(subscription):
    """Handle subscription creation"""
    logger.info(f"Subscription created: {subscription['id']}")
    
    customer_id = subscription["customer"]
    price_id = subscription["items"]["data"][0]["price"]["id"]
    
    # Find user by Stripe customer ID
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if not user:
        logger.warning(f"User not found for customer {customer_id}")
        return
    
    # Map price ID to plan
    plan = get_plan_from_price_id(price_id)
    
    # Update user subscription
    user.stripe_subscription_id = subscription["id"]
    user.plan = plan
    user.plan_expires_at = datetime.fromtimestamp(subscription["current_period_end"])
    
    db.session.commit()
    
    logger.info(f"Updated user {user.email} to plan {plan}")

def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    logger.info(f"Subscription updated: {subscription['id']}")
    
    # Find user by subscription ID
    user = User.query.filter_by(stripe_subscription_id=subscription["id"]).first()
    if not user:
        logger.warning(f"User not found for subscription {subscription['id']}")
        return
    
    # Update subscription status
    if subscription["status"] == "active":
        price_id = subscription["items"]["data"][0]["price"]["id"]
        plan = get_plan_from_price_id(price_id)
        
        user.plan = plan
        user.plan_expires_at = datetime.fromtimestamp(subscription["current_period_end"])
    
    elif subscription["status"] in ["canceled", "unpaid", "past_due"]:
        user.plan = "free"
        user.plan_expires_at = None
    
    db.session.commit()
    
    logger.info(f"Updated user {user.email} subscription status to {subscription['status']}")

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    logger.info(f"Subscription deleted: {subscription['id']}")
    
    # Find user by subscription ID
    user = User.query.filter_by(stripe_subscription_id=subscription["id"]).first()
    if not user:
        logger.warning(f"User not found for subscription {subscription['id']}")
        return
    
    # Revert to free plan
    user.plan = "free"
    user.stripe_subscription_id = None
    user.plan_expires_at = None
    
    db.session.commit()
    
    logger.info(f"Reverted user {user.email} to free plan")

def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    logger.info(f"Payment succeeded for invoice: {invoice['id']}")
    
    # Additional logic for payment success (e.g., send confirmation email)
    pass

def handle_payment_failed(invoice):
    """Handle failed payment"""
    logger.info(f"Payment failed for invoice: {invoice['id']}")
    
    # Additional logic for payment failure (e.g., send notification)
    pass

def handle_checkout_completed(session):
    """Handle completed checkout session"""
    logger.info(f"Checkout completed: {session['id']}")
    
    customer_id = session["customer"]
    
    # Find or create user
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        logger.info(f"Checkout completed for existing user: {user.email}")
    else:
        # For new users, you might need additional logic here
        logger.info(f"Checkout completed for new customer: {customer_id}")

def get_plan_from_price_id(price_id: str) -> str:
    """Map Stripe price ID to internal plan name"""
    price_to_plan = {
        os.getenv("STRIPE_PRICE_BASIC"): "basic",
        os.getenv("STRIPE_PRICE_PRO"): "pro",
        os.getenv("STRIPE_PRICE_ENTERPRISE"): "enterprise",
    }
    
    return price_to_plan.get(price_id, "free")