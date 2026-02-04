# Sentry Error Tracking Setup Guide

## 🎯 Overview

Sentry is now integrated into My Anchor for both backend (Flask) and frontend (React) error tracking.

---

## 📋 Setup Steps

### 1. Create Sentry Account (Free Tier)

1. Go to: https://sentry.io/signup/
2. Sign up for a free account
3. Create a new project:
   - **Platform**: Flask (for backend)
   - **Project Name**: my-anchor-backend
4. Copy your **DSN** (looks like: `https://xxxxx@xxxxx.ingest.sentry.io/xxxxx`)

### 2. Create Frontend Project

1. In Sentry dashboard, create another project:
   - **Platform**: React
   - **Project Name**: my-anchor-frontend
2. Copy the **DSN** for frontend

---

## 🔧 Configuration

### Backend Setup (Flask)

Set the `SENTRY_DSN` environment variable:

**Windows (PowerShell):**
```powershell
$env:SENTRY_DSN="https://YOUR_BACKEND_DSN_HERE"
```

**Windows (Command Prompt):**
```cmd
set SENTRY_DSN=https://YOUR_BACKEND_DSN_HERE
```

**Linux/Mac:**
```bash
export SENTRY_DSN="https://YOUR_BACKEND_DSN_HERE"
```

**Or add to `.env` file:**
```
SENTRY_DSN=https://YOUR_BACKEND_DSN_HERE
```

### Frontend Setup (React)

Edit `index.html` line ~57 and replace:
```javascript
const SENTRY_DSN_FRONTEND = 'YOUR_SENTRY_DSN_HERE';
```

With your frontend DSN:
```javascript
const SENTRY_DSN_FRONTEND = 'https://YOUR_FRONTEND_DSN_HERE';
```

---

## 🧪 Testing

### Test Backend Error Tracking

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start your Flask server:**
   ```bash
   python main.py
   ```

3. **Trigger a test error:**
   ```bash
   curl http://localhost:5000/api/test_error
   ```
   
   Or visit in browser: http://localhost:5000/api/test_error

4. **Check Sentry Dashboard:**
   - Go to https://sentry.io/organizations/YOUR_ORG/issues/
   - You should see: "Test error - Sentry is working!"
   - Click on it to see full stack trace

### Test Frontend Error Tracking

1. **Open your app in browser**: http://localhost:5000

2. **Open browser console** (F12) and run:
   ```javascript
   // Test Sentry is loaded
   console.log('Sentry loaded:', typeof Sentry !== 'undefined');
   
   // Manually trigger test error
   if (typeof Sentry !== 'undefined') {
       Sentry.captureException(new Error('Frontend test error'));
   }
   ```

3. **Check Sentry Dashboard:**
   - Should see "Frontend test error" in the frontend project

---

## 📊 What Gets Tracked

### Backend Errors
- ✅ Unhandled exceptions in Flask routes
- ✅ Database errors
- ✅ API failures (Gmail, Gemini, TTS)
- ✅ Rate limit violations
- ✅ Authentication failures

### Frontend Errors
- ✅ React component errors (via ErrorBoundary)
- ✅ API call failures
- ✅ Uncaught JavaScript exceptions
- ✅ Promise rejections

### Error Context Captured
- User session information
- Request/response data
- Component stack traces
- Environment (dev/production)
- Release version
- Browser/OS information

---

## 🔍 Viewing Errors in Sentry

### Dashboard Overview
1. **Issues Tab**: List of all errors
2. **Performance Tab**: API performance monitoring
3. **Releases Tab**: Track errors by version

### Error Details
For each error, you'll see:
- **Stack Trace**: Full call stack
- **Breadcrumbs**: Events leading up to error
- **User Context**: Who experienced the error
- **Environment**: dev/production
- **Frequency**: How many times it occurred
- **First/Last Seen**: When it started/last occurred

---

## 🚀 Production Deployment

### Environment Variables

Set these on your production server (e.g., Heroku, Railway, etc.):

```bash
SENTRY_DSN=https://your-backend-dsn@sentry.io/xxxxx
FLASK_ENV=production
APP_VERSION=1.0.0
```

### Frontend Configuration

For production, you can inject the frontend DSN via:

1. **Server-side rendering** (inject into HTML template)
2. **Build-time environment variable**
3. **Runtime config endpoint** (fetch from `/api/config`)

**Recommended: Create a config endpoint:**

Add to `main.py`:
```python
@app.route('/api/config')
def get_config():
    return jsonify({
        'sentry_dsn_frontend': os.environ.get('SENTRY_DSN_FRONTEND'),
        'environment': os.environ.get('FLASK_ENV', 'development')
    })
```

Then in `index.html`, fetch it:
```javascript
fetch('/api/config')
    .then(r => r.json())
    .then(config => {
        if (config.sentry_dsn_frontend) {
            // Initialize Sentry with DSN from backend
        }
    });
```

---

## 📈 Monitoring Best Practices

1. **Set up Alerts**: Configure Sentry to email/Slack you on new errors
2. **Release Tracking**: Tag deployments with version numbers
3. **Performance Monitoring**: Enable transaction tracking (already configured)
4. **Error Grouping**: Sentry automatically groups similar errors
5. **Resolve Issues**: Mark errors as resolved after fixing

---

## 🆓 Free Tier Limits

Sentry free tier includes:
- **5,000 errors/month**
- **10,000 performance transactions/month**
- **1 team member**
- **30 days data retention**

This is more than enough for MVP and early users!

---

## 🐛 Troubleshooting

### Backend: "Sentry DSN not found"
- Check environment variable is set: `echo $SENTRY_DSN`
- Restart Flask server after setting variable

### Frontend: "Sentry not loaded"
- Check browser console for script loading errors
- Verify DSN is not 'YOUR_SENTRY_DSN_HERE'
- Check network tab for sentry-cdn.com requests

### Errors not appearing in Sentry
- Verify DSN is correct (should start with `https://`)
- Check Sentry project settings (not disabled)
- Test with deliberate error (see Testing section)
- Check browser ad blocker (disable for testing)

---

## ✅ Next Steps

After setting up Sentry:

1. ✅ Test backend error tracking
2. ✅ Test frontend error tracking
3. ✅ Set up email alerts in Sentry dashboard
4. ✅ Configure Slack integration (optional)
5. ✅ Review error patterns weekly
6. ✅ Mark resolved issues as "resolved" to track regressions

---

**Note**: Remember to also complete the PostHog analytics setup for complete observability!
