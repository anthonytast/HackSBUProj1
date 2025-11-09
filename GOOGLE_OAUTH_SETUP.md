# Google Calendar OAuth Setup Guide

This guide will help you set up Google Calendar OAuth 2.0 authentication for the Study Planner app.

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name it something like "Study Planner" or "Canvas Study App"

## Step 2: Enable Google Calendar API

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google Calendar API"
3. Click on it and click **Enable**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Select **External** (unless you have a Google Workspace account)
3. Click **Create**
4. Fill in the required information:
   - **App name**: Study Planner AI
   - **User support email**: Your email
   - **Developer contact**: Your email
5. Click **Save and Continue**
6. On the **Scopes** page:
   - Click **Add or Remove Scopes**
   - Search for and add: `https://www.googleapis.com/auth/calendar`
   - Click **Update** and then **Save and Continue**
7. On **Test users** page (for External apps):
   - Click **Add Users**
   - Add your email address and any other test users
   - Click **Save and Continue**
8. Review and click **Back to Dashboard**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client ID**
3. Choose **Web application**
4. Name it "Study Planner Web Client"
5. Add **Authorized JavaScript origins**:
   ```
   http://localhost:5173
   http://localhost:3000
   ```
6. Add **Authorized redirect URIs**:
   ```
   http://localhost:8000/google/auth/callback
   http://localhost:5173/auth/callback
   ```
7. Click **Create**
8. **Save your Client ID and Client Secret** - you'll need these!

## Step 5: Configure Backend Environment Variables

1. In your backend directory, create or update `.env` file:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/google/auth/callback

# Other settings
GEMINI_API_KEY=your_gemini_key
```

2. **Never commit the `.env` file to Git!** Make sure it's in `.gitignore`

## Step 6: Update Frontend Environment

1. In your frontend directory, update `.env`:

```bash
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
```

## Step 7: Test the OAuth Flow

1. Start your backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start your frontend:
```bash
cd frontend
npm run dev
```

3. Open http://localhost:5173
4. Click "Connect Google Calendar"
5. You should be redirected to Google's consent screen
6. Grant permissions
7. You should be redirected back and authenticated!

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Make sure the redirect URI in Google Cloud Console exactly matches the one in your `.env` file
- Check for trailing slashes - they matter!
- URLs must match exactly (http vs https, ports, etc.)

### Error: "Access blocked: This app's request is invalid"
- Make sure you've added your email as a test user in the OAuth consent screen
- For External apps, you need to add test users before publishing

### Error: "invalid_client"
- Double-check your Client ID and Client Secret in `.env`
- Make sure there are no extra spaces or quotes

### Can't see the consent screen
- Try in an incognito/private browsing window
- Clear your browser cookies for google.com
- Make sure the OAuth consent screen is configured

## Production Deployment

When deploying to production:

1. **Update OAuth Consent Screen**:
   - Submit your app for verification if needed
   - Move from "Testing" to "In Production"

2. **Update Authorized Domains**:
   - Add your production domain to authorized JavaScript origins
   - Add your production domain to redirect URIs
   - Example: `https://yourdomain.com/auth/callback`

3. **Environment Variables**:
   - Set `GOOGLE_REDIRECT_URI` to your production callback URL
   - Use environment variables or secrets management (never hardcode)

4. **HTTPS Required**:
   - Google OAuth requires HTTPS in production
   - Local development can use HTTP

## Security Best Practices

1. **Never expose credentials**:
   - Keep `.env` files out of version control
   - Don't log credentials
   - Use environment variables in production

2. **Validate redirect URIs**:
   - Only whitelist your own domains
   - Remove test/development URIs in production

3. **Refresh tokens**:
   - The app automatically refreshes expired tokens
   - Store refresh tokens securely
   - Implement token rotation if needed

4. **Scope limitations**:
   - Only request calendar scope (we don't need full account access)
   - Users can see exactly what permissions they're granting

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) - Test OAuth flows

## Need Help?

Common issues:
- Make sure both backend and frontend servers are running
- Check browser console for errors
- Check backend logs for OAuth errors
- Verify all environment variables are set correctly

---

Once configured, users can authenticate with Google Calendar and the app will:
- Create study session events
- Avoid scheduling conflicts
- Set reminders
- Sync across all their devices
