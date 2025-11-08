# Google Calendar OAuth Flow

## Overview
This document explains how the Google Calendar OAuth 2.0 authentication works in the Study Planner app.

## Flow Diagram

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Frontend  │         │   Backend   │         │    Google    │
│  (React)    │         │  (FastAPI)  │         │    OAuth     │
└──────┬──────┘         └──────┬──────┘         └──────┬───────┘
       │                       │                        │
       │ 1. Click "Connect"    │                        │
       │─────────────────────► │                        │
       │                       │                        │
       │                       │ 2. Generate auth URL   │
       │                       │───────────────────────►│
       │                       │                        │
       │                       │ 3. Return auth URL     │
       │                       │◄───────────────────────│
       │                       │                        │
       │ 4. Redirect to Google │                        │
       │───────────────────────┼───────────────────────►│
       │                       │                        │
       │                       │        5. User grants  │
       │                       │           permissions  │
       │                       │                        │
       │ 6. Callback with code │                        │
       │◄──────────────────────┼────────────────────────│
       │                       │                        │
       │ 7. Send code          │                        │
       │─────────────────────► │                        │
       │                       │                        │
       │                       │ 8. Exchange for tokens │
       │                       │───────────────────────►│
       │                       │                        │
       │                       │ 9. Return credentials  │
       │                       │◄───────────────────────│
       │                       │                        │
       │ 10. Store credentials │                        │
       │◄───────────────────── │                        │
       │                       │                        │
       │ ✅ Authenticated!     │                        │
       │                       │                        │
```

## Detailed Steps

### 1. User Initiates Authentication
- User clicks "Connect Google Calendar" button in frontend
- Frontend calls `GET /google/auth/url` endpoint

### 2. Backend Generates Authorization URL
```python
# In calendar_service.py
async def get_authorization_url(self):
    self.oauth_flow = Flow.from_client_config(
        self.client_config,
        scopes=self.SCOPES,
        redirect_uri=self.redirect_uri
    )
    authorization_url, state = self.oauth_flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url
```

### 3. Frontend Redirects to Google
```javascript
// In GoogleAuth.jsx
const response = await axios.get(`${API_BASE_URL}/google/auth/url`);
window.location.href = response.data.auth_url;
```

### 4. Google Consent Screen
- User sees Google's permission request screen
- Lists requested permissions (Calendar access)
- User grants or denies access

### 5. Google Redirects Back
- On approval, Google redirects to: `http://localhost:8000/google/auth/callback?code=xxx&state=yyy`
- The `code` parameter contains the authorization code
- The `state` parameter is for CSRF protection

### 6. Backend Handles Callback
```python
# In main.py
@app.get("/google/auth/callback")
async def google_auth_callback(code: str, state: Optional[str] = None):
    credentials = await calendar_service.handle_oauth_callback(code, state)
    return {"credentials": credentials}
```

### 7. Exchange Code for Tokens
```python
# In calendar_service.py
async def handle_oauth_callback(self, code: str, state: Optional[str] = None):
    self.oauth_flow.fetch_token(code=code)
    credentials = self.oauth_flow.credentials
    
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
```

### 8. Store Credentials
- Backend returns credentials to frontend
- Frontend stores in localStorage
- Frontend updates UI to show "Connected" status

## Token Management

### Access Token
- Short-lived (usually 1 hour)
- Used for API requests
- Automatically refreshed when expired

### Refresh Token
- Long-lived (can last indefinitely with `access_type='offline'`)
- Used to get new access tokens
- Only provided on first authorization or when `prompt='consent'`

### Auto-Refresh Logic
```python
# In calendar_service.py
async def authenticate(self, credentials: dict):
    self.creds = Credentials.from_authorized_user_info(credentials, self.SCOPES)
    
    # Check if token is expired
    if self.creds.expired and self.creds.refresh_token:
        self.creds.refresh(Request())  # Get new access token
    
    self.service = build('calendar', 'v3', credentials=self.creds)
```

## Security Considerations

### State Parameter
- Random value generated during authorization request
- Returned in callback to prevent CSRF attacks
- Should be validated (not currently implemented but recommended)

### Redirect URI Validation
- Google only allows pre-registered redirect URIs
- Must match exactly (including protocol, domain, port, path)
- Prevents malicious redirection

### Token Storage
- Currently stored in browser localStorage
- For production, consider:
  - Server-side session storage
  - Encrypted cookies
  - Token rotation
  - Automatic expiration

### HTTPS Requirement
- Development: HTTP is allowed on localhost
- Production: HTTPS is required by Google
- SSL certificate needed for production deployment

## Error Handling

### Common Errors

1. **redirect_uri_mismatch**
   - Redirect URI not whitelisted in Google Console
   - Fix: Add exact URI to authorized redirect URIs

2. **invalid_client**
   - Wrong client ID or secret
   - Fix: Check .env configuration

3. **access_denied**
   - User denied permission
   - Handle gracefully in UI

4. **invalid_grant**
   - Refresh token expired or revoked
   - Re-authenticate user

## Testing the Flow

### Local Development
```bash
# 1. Start backend
cd backend
uvicorn main:app --reload

# 2. Start frontend
cd frontend
npm run dev

# 3. Open browser
open http://localhost:5173

# 4. Click "Connect Google Calendar"
# 5. Complete OAuth flow
# 6. Check browser console and backend logs
```

### Debugging Tips

1. **Check Network Tab**
   - Look for failed API calls
   - Verify redirect URLs

2. **Backend Logs**
   - OAuth errors logged in terminal
   - Check token exchange success

3. **Browser Console**
   - JavaScript errors
   - State management issues

4. **Google Cloud Console**
   - Check OAuth consent screen status
   - Verify redirect URIs
   - Check test users list

## API Endpoints

### GET /google/auth/url
**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

### GET /google/auth/callback
**Parameters:**
- `code`: Authorization code from Google
- `state`: CSRF protection token

**Response:**
```json
{
  "message": "Authentication successful",
  "credentials": {
    "token": "ya29.xxx",
    "refresh_token": "1//xxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxx",
    "scopes": ["https://www.googleapis.com/auth/calendar"]
  }
}
```

### POST /google/authenticate
**Request Body:**
```json
{
  "credentials": {
    "token": "ya29.xxx",
    "refresh_token": "1//xxx",
    ...
  }
}
```

**Response:**
```json
{
  "message": "Google Calendar authentication successful",
  "authenticated": true
}
```

## Next Steps

After successful authentication:
1. User can fetch their calendar events
2. App can create study session events
3. App can check for scheduling conflicts
4. Calendar syncs across all user's devices

## Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Calendar API Guide](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 Best Practices](https://tools.ietf.org/html/rfc6749)
