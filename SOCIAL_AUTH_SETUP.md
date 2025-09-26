# Social Authentication Setup Guide

This guide will help you set up Google and GitHub authentication for the FarmBot application.

## Prerequisites

1. Django server running on `http://localhost:8000`
2. React frontend running on `http://localhost:3000`

## Google OAuth Setup

### 1. Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set application type to "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/google/login/callback/`
7. Copy the Client ID and Client Secret

### 2. Configure Django Settings

Add these environment variables to your `.env` file:

```bash
# Google OAuth
GOOGLE_OAUTH2_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH2_CLIENT_SECRET=your_google_client_secret_here
```

### 3. Update Django Settings

Add these to your `farmbot_api/settings.py`:

```python
# Social Authentication Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Environment variables for OAuth
GOOGLE_OAUTH2_CLIENT_ID = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET')
```

## GitHub OAuth Setup

### 1. Create GitHub OAuth App

1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - Application name: `FarmBot App`
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:8000/api/auth/github/login/callback/`
4. Copy the Client ID and Client Secret

### 2. Configure Django Settings

Add these environment variables to your `.env` file:

```bash
# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
```

### 3. Update Django Settings

Add these to your `farmbot_api/settings.py`:

```python
# Social Authentication Settings
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': [
            'user',
            'email',
        ],
    }
}

# Environment variables for OAuth
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
```

## Testing

1. Start both servers:
   ```bash
   # Backend
   cd /home/calin/Documents/code/practica
   source .venv/bin/activate
   python manage.py runserver 0.0.0.0:8000

   # Frontend
   cd frontend
   npm start
   ```

2. Visit `http://localhost:3000`
3. Click on "Google" or "GitHub" buttons
4. Complete the OAuth flow
5. You should be redirected back to the main FarmBot interface

## Troubleshooting

- Make sure all redirect URIs match exactly
- Check that environment variables are loaded correctly
- Verify that the OAuth apps are configured with the correct callback URLs
- Check browser console for any JavaScript errors
- Check Django logs for authentication errors

## Security Notes

- Never commit OAuth credentials to version control
- Use environment variables for all sensitive configuration
- Consider using HTTPS in production
- Regularly rotate OAuth credentials
