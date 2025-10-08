# file: app/billing/stripe_service.py
import os
import stripe
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_customer(email: str, name: Optional[str] = None) -> Optional[str]:
    """Create Stripe customer"""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                "source": "marketing_saas"
            }
        )
        return customer.id
    except stripe.error.StripeError as e:
        logger.error(f"Error creating Stripe customer: {e}")
        return None

def create_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None,
    customer_id: Optional[str] = None
) -> Optional[stripe.checkout.Session]:
    """Create Stripe checkout session for subscription"""
    try:
        params = {
            "mode": "subscription",
            "line_items": [{
                "price": price_id,
                "quantity": 1,
            }],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "billing_address_collection": "auto",
            "allow_promotion_codes": True,
            "subscription_data": {
                "metadata": {
                    "source": "marketing_saas"
                }
            }
        }
        
        # Set customer
        if customer_id:
            params["customer"] = customer_id
        elif customer_email:
            params["customer_email"] = customer_email
        
        session = stripe.checkout.Session.create(**params)
        return session
        
    except stripe.error.StripeError as e:
        logger.error(f"Error creating checkout session: {e}")
        return None

def create_portal_session(customer_id: str, return_url: str) -> Optional[str]:
    """Create customer portal session for subscription management"""
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url
    except stripe.error.StripeError as e:
        logger.error(f"Error creating portal session: {e}")
        return None

def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
    """Get subscription details"""
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return {
            "id": subscription.id,
            "status": subscription.status,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "price_id": subscription.items.data[0].price.id if subscription.items.data else None,
            "customer_id": subscription.customer
        }
    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving subscription: {e}")
        return None

def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    """Get customer details"""
    try:
        customer = stripe.Customer.retrieve(customer_id)
        return {
            "id": customer.id,
            "email": customer.email,
            "name": customer.name,
            "created": customer.created
        }
    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving customer: {e}")
        return None

def cancel_subscription(subscription_id: str) -> bool:
    """Cancel subscription at period end"""
    try:
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        return True
    except stripe.error.StripeError as e:
        logger.error(f"Error canceling subscription: {e}")
        return False

def reactivate_subscription(subscription_id: str) -> bool:
    """Reactivate canceled subscription"""
    try:
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=False
        )
        return True
    except stripe.error.StripeError as e:
        logger.error(f"Error reactivating subscription: {e}")
        return False

def get_price_details(price_id: str) -> Optional[Dict[str, Any]]:
    """Get price details"""
    try:
        price = stripe.Price.retrieve(price_id)
        return {
            "id": price.id,
            "amount": price.unit_amount,
            "currency": price.currency,
            "interval": price.recurring.interval if price.recurring else None,
            "interval_count": price.recurring.interval_count if price.recurring else None,
            "nickname": price.nickname,
            "product": price.product
        }
    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving price: {e}")
        return None

# Plan configuration
PLAN_LIMITS = {
    "free": {
        "name": "Kostenlos",
        "max_schedules": 1,
        "max_posts_per_month": 10,
        "channels": ["telegram"],
        "ai_features": False,
        "priority_support": False
    },
    "basic": {
        "name": "Basic",
        "max_schedules": 5,
        "max_posts_per_month": 100,
        "channels": ["telegram", "facebook"],
        "ai_features": True,
        "priority_support": False
    },
    "pro": {
        "name": "Pro",
        "max_schedules": 20,
        "max_posts_per_month": 500,
        "channels": ["telegram", "facebook", "linkedin", "instagram"],
        "ai_features": True,
        "priority_support": True
    },
    "enterprise": {
        "name": "Enterprise",
        "max_schedules": -1,  # Unlimited
        "max_posts_per_month": -1,  # Unlimited
        "channels": ["telegram", "facebook", "linkedin", "instagram"],
        "ai_features": True,
        "priority_support": True
    }
}

def get_plan_limits(plan: str) -> Dict[str, Any]:
    """Get plan limits and features"""
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

def check_plan_limit(user, limit_type: str) -> bool:
    """Check if user has reached plan limit"""
    plan_limits = get_plan_limits(user.plan)
    
    if limit_type == "schedules":
        max_schedules = plan_limits["max_schedules"]
        if max_schedules == -1:  # Unlimited
            return True
        
        current_schedules = user.schedules.count()
        return current_schedules < max_schedules
    
    elif limit_type == "posts":
        # Implement monthly post counting logic
        max_posts = plan_limits["max_posts_per_month"]
        if max_posts == -1:  # Unlimited
            return True
        
        # Count posts from current month
        from datetime import datetime, timezone
        from ..models import GeneratedContent
        
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_posts = GeneratedContent.query.filter(
            GeneratedContent.user_id == user.id,
            GeneratedContent.created_at >= month_start,
            GeneratedContent.published == True
        ).count()
        
        return current_posts < max_posts
    
    return True