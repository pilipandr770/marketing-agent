# Meta (Facebook/Instagram) OAuth Configuration Guide

## 📋 Prerequisites

You need:
- Facebook Developer Account
- Facebook Page (for Facebook publishing)
- Instagram Business Account (for Instagram publishing)
- Meta App with Marketing API access

---

## 🔧 Step 1: Create Facebook App

1. Go to https://developers.facebook.com/apps/
2. Click **"Create App"**
3. Choose **"Business"** → **"Marketing API"**
4. Fill in:
   - **App name**: Marketing Agent
   - **App contact email**: your email
   - **Business account**: Select or create
5. Click **"Create App"**

---

## 🔑 Step 2: Get App Credentials

After creating the app:

1. Go to **"Settings"** → **"Basic"**
2. Copy:
   - **App ID**
   - **App Secret**

---

## 🌐 Step 3: Configure Facebook Login

1. In left menu, click **"Add Product"** → **"Facebook Login"**
2. Choose **"Web"**
3. Add your domain: `https://your-app-name.onrender.com`
4. In **"Facebook Login"** → **"Settings"**:
   - **Valid OAuth Redirect URIs**:
     ```
     https://your-app-name.onrender.com/meta/callback
     ```
5. Save changes

---

## 📊 Step 4: Add Marketing API

1. **"Add Product"** → **"Marketing API"**
2. Request access (may take time for approval)

---

## 🔗 Step 5: Get Facebook Page ID

### Method 1: From Facebook Page
1. Go to your Facebook Page
2. Click **"About"** or **"More Info"**
3. Scroll down to **"Page ID"** - copy the number

### Method 2: Using Graph API Explorer
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app
3. Add permission: `pages_read_engagement`
4. Query: `GET /me/accounts`
5. Find your page and copy the `id` field

---

## 📸 Step 6: Get Instagram Business Account ID

### Method 1: Link Instagram to Facebook Page
1. Go to your Facebook Page
2. Click **"Settings"** → **"Instagram"**
3. Link your Instagram Business account
4. The Instagram Business Account ID will be shown

### Method 2: Using Graph API
1. Use Graph API Explorer
2. Query: `GET /{facebook-page-id}?fields=instagram_business_account`
3. Copy the `instagram_business_account.id`

---

## 🔐 Step 7: Generate Long-Lived Access Token

### Using Graph API Explorer:
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app
3. Add these permissions:
   - `pages_manage_posts` (for Facebook)
   - `instagram_basic`
   - `instagram_content_publish` (for Instagram)
4. Click **"Generate Access Token"**
5. **Important**: Convert to long-lived token:

```
GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
```

6. Copy the **long-lived access token** (60 days validity)

---

## ⚙️ Step 8: Add Environment Variables to Render

```
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_REDIRECT_URI=https://your-app-name.onrender.com/meta/callback
```

---

## 📝 Step 9: Configure in App Settings

In your Marketing Agent settings:

1. **Meta Access Token**: Paste the long-lived token
2. **Facebook Page ID**: Paste the numeric page ID
3. **Instagram Business ID**: Paste the Instagram business account ID

---

## 🚀 Step 10: Test Publishing

1. Go to **"Content"** page
2. Select **"Facebook"** or **"Instagram"** as channel
3. Generate and publish a post
4. Check for success message

---

## 🔍 Troubleshooting

### Error: "Invalid access token"
- Token expired (60 days limit)
- Regenerate using the exchange endpoint

### Error: "(#200) Requires pages_manage_posts permission"
- Your token doesn't have the required permissions
- Regenerate token with correct permissions

### Error: "Invalid parameter" for Instagram
- Check that Instagram Business Account is properly linked to Facebook Page
- Verify Instagram Business Account ID

### Error: "Application request limit reached"
- Facebook has rate limits
- Wait and retry, or upgrade to higher limits

### No Facebook Page ID
- Make sure you have a Facebook Page
- Use Graph API Explorer to get the ID

### No Instagram Business Account ID
- Convert personal Instagram to Business account
- Link it to your Facebook Page
- Use Graph API to get the ID

---

## 📚 API Documentation

- [Facebook Graph API](https://developers.facebook.com/docs/graph-api/)
- [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api/)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/)

---

## ⚠️ Important Notes

- **Long-lived tokens expire in 60 days**
- **Short-lived tokens expire in 1 hour**
- Always use long-lived tokens for production
- Store tokens securely (never in client-side code)
- Monitor token expiration and implement refresh logic

---

## 🔄 Token Refresh (Future Enhancement)

To implement automatic token refresh:

1. Store the refresh token (if available)
2. Before expiration, exchange for new long-lived token
3. Update database with new token

Example refresh:
```python
requests.get(
    "https://graph.facebook.com/oauth/access_token",
    params={
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": current_token
    }
)
```
