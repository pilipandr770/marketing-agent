// file: app/static/js/pixel.js
// Facebook Pixel tracking events

// Track custom events
function trackEvent(eventName, parameters = {}) {
    if (typeof fbq !== 'undefined') {
        fbq('track', eventName, parameters);
        console.log('Facebook Pixel event tracked:', eventName, parameters);
    }
}

// Track content generation
function trackContentGeneration(platform, contentType) {
    trackEvent('GenerateContent', {
        platform: platform,
        content_type: contentType
    });
}

// Track content publishing
function trackContentPublish(platform) {
    trackEvent('Publish', {
        platform: platform
    });
}

// Track subscription events
function trackSubscription(plan) {
    trackEvent('Subscribe', {
        plan: plan
    });
}

// Track lead generation
function trackLead() {
    trackEvent('Lead');
}

// Export functions for global use
window.trackEvent = trackEvent;
window.trackContentGeneration = trackContentGeneration;
window.trackContentPublish = trackContentPublish;
window.trackSubscription = trackSubscription;
window.trackLead = trackLead;
