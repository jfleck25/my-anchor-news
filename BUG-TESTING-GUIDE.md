# Bug Testing Guide

This guide will help you test for potential bugs in your code.

---

## Step 1: Start Your Flask Server

Open a terminal/command prompt and navigate to your project directory:

```bash
cd c:\Users\jimmy\Desktop\MyAnchor\my-anchor-news
python main.py
```

Or if you're using a different method (like `flask run` or `gunicorn`), use that instead.

**Expected:** You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Database connection successful.
```

---

## Step 2: Open Your App in Browser

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to: `http://localhost:5000` (or whatever port your app runs on)
3. Open **Developer Tools**:
   - **Chrome/Edge:** Press `F12` or `Ctrl+Shift+I`
   - **Firefox:** Press `F12` or `Ctrl+Shift+I`
   - **Safari:** Enable Developer menu first, then `Cmd+Option+I`

4. Go to the **Console** tab in Developer Tools

---

## Step 3: Test Each Bug Scenario

### Test 1: OAuth Callback Bug (State Missing)

**What we're testing:** What happens if someone navigates directly to the OAuth callback URL?

1. In your browser, go directly to: `http://localhost:5000/oauth2callback`
2. **Expected behavior:** Should show an error page or JSON error
3. **Bug behavior:** Would crash with KeyError if state is missing

**Check the debug log:** Look for entries with `"hypothesisId":"A"`

---

### Test 2: Rate Limiting Bug (Auth Check Order)

**What we're testing:** Does rate limiting try to get user info before checking if user is authenticated?

1. **Option A:** Open a new incognito/private window
2. Go to: `http://localhost:5000`
3. Open Developer Tools → Network tab
4. Try to access: `http://localhost:5000/api/fetch_emails` directly
   - Or click "Refresh" button in the app (if it shows up without login)
5. Check the Network tab for the response

**Check the debug log:** Look for entries with `"hypothesisId":"B"`

---

### Test 3: Audio Completion Tracking Bug

**What we're testing:** Does the audio completion event listener get added before the audio element exists?

1. **First, log in** to your app (if not already logged in)
2. Click **"Refresh"** to generate a briefing
3. Wait for briefing to load
4. Click **"Play Briefing"** button
5. **Let the audio play completely** (wait until it finishes)
6. Check the browser console for any errors

**Check the debug log:** Look for entries with `"hypothesisId":"C"`

---

### Test 4: Cache Race Condition

**What we're testing:** Can multiple requests overwrite the cache file simultaneously?

1. Open **two browser tabs** with your app
2. In **both tabs**, click "Refresh" at the same time (or very quickly)
3. Check if both requests complete successfully

**Check the debug log:** Look for entries with `"hypothesisId":"D"`

---

## Step 4: Check the Debug Log

After running the tests, check the debug log file:

**Location:** `c:\Users\jimmy\Desktop\MyAnchor\my-anchor-news\.cursor\debug.log`

### How to View It:

**Option 1: In VS Code/Cursor**
- Open the file: `.cursor\debug.log`
- It's in NDJSON format (one JSON object per line)

**Option 2: In Notepad**
- Right-click the file → Open with → Notepad
- Each line is a separate log entry

**Option 3: Command Line**
```bash
type .cursor\debug.log
```

### What to Look For:

The log entries will have fields like:
- `"hypothesisId"`: Which bug we're testing (A, B, C, or D)
- `"message"`: What happened
- `"data"`: Additional information
- `"location"`: Where in the code

**Example log entry:**
```json
{"id":"log_oauth_callback","timestamp":1733456789000,"location":"main.py:288","message":"OAuth callback entry","data":{"state_in_session":false,"session_keys":[]},"sessionId":"debug-session","runId":"run1","hypothesisId":"A"}
```

---

## Step 5: Share the Results

After testing, you can:

1. **Share the debug log file** - Copy the contents of `.cursor\debug.log`
2. **Or describe what happened:**
   - Did any tests crash?
   - Did you see errors in the browser console?
   - Did everything work normally?

---

## Quick Test (Simplest)

If you want to do a quick test:

1. **Start your server**
2. **Open the app in browser**
3. **Generate a briefing and play audio** (Test 3)
4. **Check the debug log** at `.cursor\debug.log`
5. **Share what you see**

This will catch the most likely bugs (audio completion tracking).

---

## Troubleshooting

**No debug log file created?**
- Make sure you ran at least one test that triggers the code
- Check that the `.cursor` folder exists
- Check file permissions

**Can't see the log file?**
- It might be hidden (starts with `.`)
- In File Explorer, enable "Show hidden files"
- Or use command line: `dir .cursor\debug.log`

**Server won't start?**
- Check for syntax errors: `python -m py_compile main.py`
- Check if port 5000 is already in use
- Check your Python version: `python --version` (needs 3.10+)

---

**Ready to test?** Start with Step 1 and work through the tests. Let me know what you find!
