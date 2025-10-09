# LinkedIn OAuth Configuration Guide

## 📋 Prerequisites

You need a LinkedIn Developer account and an app created in the [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps).

---

## 🔧 Step 1: Create LinkedIn App

1. Go to https://www.linkedin.com/developers/apps
2. Click **"Create app"**
3. Fill in required information:
   - **App name**: Marketing Agent
   - **LinkedIn Page**: Select your company page (or create one)
   - **App logo**: Upload your logo
   - **Legal agreement**: Accept terms
4. Click **"Create app"**

---

## 🔑 Step 2: Get OAuth Credentials

After creating the app:

1. Go to the **"Auth"** tab
2. Copy your credentials:
   - **Client ID** (Идентификатор клиента)
   - **Client Secret** (Основной секрет клиента) - click "Show" to reveal

---

## 🌐 Step 3: Configure Redirect URIs

In the **"Auth"** tab, under **"OAuth 2.0 settings"**:

1. Click **"Add redirect URL"**
2. Add your production URL:
   ```
   https://your-app-name.onrender.com/linkedin/callback
   ```
3. For local development, also add:
   ```
   http://localhost:5000/linkedin/callback
   ```
4. Click **"Update"**

---

## ✅ Step 4: Request API Access

In the **"Products"** tab:

1. Find **"Share on LinkedIn"** or **"Marketing Developer Platform"**
2. Click **"Request access"**
3. Fill out the form explaining your use case
4. Wait for approval (usually takes 1-2 business days)

**Note**: Without approved access to "Share on LinkedIn", you can only post to your personal profile with limited scope.

---

## 🔐 Step 5: Add Credentials to Render

Go to your Render dashboard:

1. Open your web service
2. Go to **"Environment"** tab
3. Add these variables:
   ```
   LINKEDIN_CLIENT_ID=your_client_id_here
   LINKEDIN_CLIENT_SECRET=your_client_secret_here
   LINKEDIN_REDIRECT_URI=https://your-app-name.onrender.com/linkedin/callback
   ```
4. Click **"Save Changes"**

---

## 📝 Step 6: Required Scopes

The app requests these OAuth scopes:

- `openid` - Basic authentication
- `profile` - Access to profile information
- `email` - User's email address
- `w_member_social` - **Required for posting**

---

## 🚀 Step 7: Test the Integration

1. Deploy your app to Render
2. Login to your account
3. Go to **Settings**
4. Click **"Підключити LinkedIn"**
5. Authorize the app on LinkedIn
6. You should see: **"LinkedIn підключено!"**

---

## 🔍 Troubleshooting

### Error: "redirect_uri_mismatch"
- Check that the redirect URI in LinkedIn app settings **exactly** matches your Render URL
- Make sure there are no trailing slashes

### Error: "invalid_scope"
- Your app doesn't have "Share on LinkedIn" product access
- Request access in the Products tab

### Error: "unauthorized_client"
- Check that Client ID and Client Secret are correct in Render environment variables
- Regenerate Client Secret if needed

### No URN returned
- The OAuth flow should automatically get your person URN
- If it fails, check the logs on Render

---

## 📚 API Documentation

- [LinkedIn OAuth 2.0 Guide](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Share on LinkedIn API](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/share-api)
- [UGC Posts API](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api)

---

## 🎯 Next Steps

After successful OAuth integration:

1. Test posting to LinkedIn from the Content page
2. Configure scheduled posts with LinkedIn as target platform
3. Monitor post analytics (if using Marketing Developer Platform)

---

## ⚠️ Important Notes

- Access tokens from OAuth are **long-lived** (60 days) but need refresh
- Currently, the app doesn't implement token refresh - you'll need to re-authorize every 60 days
- For production, implement refresh token flow
- Personal profile posting has rate limits (check LinkedIn documentation)

---

## 🔄 Token Refresh (Future Enhancement)

To implement automatic token refresh:

1. Store `refresh_token` from OAuth response
2. Before token expires (check `expires_in`), use refresh token to get new access token
3. Update database with new token

Example refresh token request:
```python
requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "refresh_token",
        "refresh_token": stored_refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
)
```
