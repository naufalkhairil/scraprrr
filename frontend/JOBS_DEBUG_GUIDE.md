# Jobs List Debugging Guide

## Problem
Jobs list doesn't show jobs after page refresh.

## Solution Implemented

I've added comprehensive debugging and fixed the session management. Here's how to diagnose and fix the issue:

---

## Step-by-Step Debugging

### 1. Check Session ID

**Open browser console (F12) and look for:**
```
[SessionManager] Using existing session: xxx-xxx-xxx
```

**Or check manually:**
```javascript
// In browser console
localStorage.getItem('scraprrr_session_id')
```

**Expected:** A UUID like `550e8400-e29b-41d4-a716-446655440000`

**If null or different on each refresh:**
- Browser might be in incognito/private mode
- localStorage might be blocked
- Extension might be clearing storage

---

### 2. Check API Requests

**Open DevTools → Network tab**

**Look for:**
1. `GET /api/v1/jobs` request
2. Check request headers for `X-Session-ID`

**Expected headers:**
```
X-Session-ID: 550e8400-e29b-41d4-a716-446655440000
```

**If header is missing:**
- SessionManager not initializing properly
- Check console for errors

---

### 3. Check API Response

**In Network tab, click on `/api/v1/jobs` request**

**Check response:**
```json
{
  "total": 2,
  "jobs": [
    {
      "job_id": "...",
      "job_type": "flight_search",
      "session_id": "YOUR_SESSION_ID",
      "status": "completed"
    }
  ]
}
```

**If `total: 0`:**
- Jobs were created with different session ID
- Jobs were cleaned up (older than 1 hour)
- Backend issue

---

### 4. Test with Debug Panel

**On home page, click "Show Debug" button**

**You'll see:**
```
Debug Info
Session ID: 550e8400-e29b-41d4-a716-446655440000
Current Job: Yes
Polling Job: Yes
Job Status: running | Type: flight_search | Progress: 45%
```

**Click "Clear Session & Reload"** to reset and test fresh.

---

### 5. Check Jobs Page Alerts

**If no jobs found, you'll see a blue alert:**

```
ℹ️ No jobs found for this session

Jobs are isolated by browser session. This could mean:
- You haven't created any jobs yet in this session
- You're using a different browser or incognito mode
- Jobs were cleaned up (older than 1 hour)

[Go to Home Page] [Clear Session & Reload]
```

---

## Common Issues & Fixes

### Issue 1: Different Session on Each Refresh

**Symptom:** Session ID changes every time you refresh

**Cause:** localStorage not persisting

**Fix:**
1. Check if browser is in incognito/private mode
2. Check browser settings - localStorage might be disabled
3. Try different browser

**Test:**
```javascript
// In console
localStorage.setItem('test', 'value');
location.reload();
// Then check
localStorage.getItem('test')
// Should return 'value'
```

---

### Issue 2: Jobs Created in Different Session

**Symptom:** Jobs exist but don't show in list

**Cause:** Jobs were created with different session ID

**Diagnosis:**
```javascript
// Check current session
localStorage.getItem('scraprrr_session_id')

// Check all jobs (bypass session filter)
fetch('/api/v1/jobs')
  .then(r => r.json())
  .then(data => console.log(data))
```

**Fix:**
1. Click "Clear Session & Reload" button
2. Create new jobs with current session
3. Or use same browser/tab where jobs were created

---

### Issue 3: Jobs Cleaned Up

**Symptom:** Jobs disappeared after some time

**Cause:** Jobs older than 1 hour are auto-cleaned

**Fix:**
- Jobs are meant to be temporary
- Export important results
- Adjust cleanup TTL in backend if needed

---

### Issue 4: Backend Not Receiving Session ID

**Symptom:** API returns all jobs or no jobs

**Check backend logs:**
```bash
# Look for session ID in logs
docker logs [api-container] 2>&1 | grep session
```

**Expected:**
```
Listing jobs for session 550e8400-e29b-41d4-a716-446655440000: 2 jobs
```

---

## Testing Workflow

### Test 1: Fresh Session

1. Open browser (not incognito)
2. Go to http://localhost:3000
3. Click "Show Debug" - note session ID
4. Start a flight search
5. Go to Jobs page (/jobs)
6. **Expected:** Job appears within 2 seconds

### Test 2: Page Refresh

1. While on Jobs page with visible job
2. Refresh page (F5)
3. **Expected:** 
   - Same session ID
   - Job still visible
   - Last updated timestamp refreshes

### Test 3: Multiple Tabs

1. Open tab A, start search
2. Open tab B (new tab, same browser)
3. Go to Jobs page in both tabs
4. **Expected:** Both tabs see same jobs (same session)

### Test 4: Different Browser

1. Open Chrome, start search
2. Open Firefox, go to Jobs page
3. **Expected:** Different jobs (different sessions)

---

## Manual Debugging Commands

### Check Session in Console
```javascript
// Get current session
const session = localStorage.getItem('scraprrr_session_id');
console.log('Session:', session);

// Check if valid UUID
const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
console.log('Valid UUID:', uuidRegex.test(session));
```

### Check API Directly
```javascript
// Get session ID
const sessionId = localStorage.getItem('scraprrr_session_id');

// Fetch jobs with session
fetch('/api/v1/jobs', {
  headers: { 'X-Session-ID': sessionId }
})
.then(r => r.json())
.then(data => {
  console.log('Total jobs:', data.total);
  console.log('Jobs:', data.jobs);
});

// Fetch ALL jobs (no session filter)
fetch('/api/v1/jobs')
.then(r => r.json())
.then(data => console.log('All jobs:', data));
```

### Create Test Job
```javascript
// Start a test search
fetch('/api/v1/flights/search/async', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Session-ID': localStorage.getItem('scraprrr_session_id')
  },
  body: JSON.stringify({
    origin: 'CGK',
    destination: 'DPS'
  })
})
.then(r => r.json())
.then(job => console.log('Created job:', job));
```

---

## Backend Debugging

### Enable Debug Logs

```bash
# Start API with debug logging
scraprrr-serve --log-level debug
```

**Look for:**
```
DEBUG - Listing jobs for session xxx: N jobs
INFO - Created job xxx of type flight_search for session xxx
```

### Check JobManager State

```python
# In Python shell (for debugging)
from scraprrr.api.core.job_manager import job_manager

# List all jobs
print(f"Total jobs: {len(job_manager.get_all_jobs())}")

# List by session
session_id = "your-session-id"
print(f"Session jobs: {len(job_manager.get_session_jobs(session_id))}")

# Check job details
for job in job_manager.get_all_jobs():
    print(f"Job {job.job_id}: session={job.session_id}, status={job.status}")
```

---

## Quick Fixes

### Fix 1: Clear Everything and Start Fresh

```javascript
// In browser console
localStorage.clear();
location.reload();
```

Then create a new search.

### Fix 2: Force Session ID

```javascript
// In browser console
const fixedSession = 'fixed-session-12345';
localStorage.setItem('scraprrr_session_id', fixedSession);
location.reload();
```

### Fix 3: Check Backend is Running

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test jobs endpoint
curl http://localhost:8000/api/v1/jobs
```

---

## Expected Behavior Summary

| Action | Expected Result |
|--------|----------------|
| Create job | Appears in Jobs page within 2s |
| Refresh page | Jobs still visible, same session |
| Open new tab (same browser) | See same jobs |
| Open different browser | See different jobs |
| Wait 1+ hour | Jobs auto-cleaned |
| Click "Clear Session" | New session, old jobs hidden |

---

## Still Not Working?

### Collect Debug Info

1. **Browser console logs** (F12 → Console)
   - Look for `[SessionManager]` and `[JobsPage]` messages
   
2. **Network tab**
   - Screenshot of `/api/v1/jobs` request/response
   
3. **Session ID**
   - Run: `localStorage.getItem('scraprrr_session_id')`
   
4. **Backend logs**
   - Run: `scraprrr-serve --log-level debug`

### Share Debug Info

When asking for help, provide:
1. Browser console logs
2. Network tab screenshot
3. Session ID (first/last 8 chars)
4. Backend logs
5. Steps to reproduce

---

## Implementation Details

### Session Flow

```
Browser loads
    ↓
SessionManager.getId() called
    ↓
Check localStorage for 'scraprrr_session_id'
    ↓
If exists: return it
If not: create UUID, save to localStorage, return it
    ↓
All API requests include X-Session-ID header
    ↓
Backend filters jobs by session_id
    ↓
Only session's jobs returned
```

### Job Creation Flow

```
User clicks "Search"
    ↓
Frontend: POST /flights/search/async
Headers: { X-Session-ID: "abc123" }
    ↓
Backend: Creates job with session_id="abc123"
    ↓
Backend: Returns job info
    ↓
Frontend: Polls every 2s for updates
    ↓
Jobs page: GET /jobs?X-Session-ID="abc123"
    ↓
Backend: Returns only jobs with session_id="abc123"
```

---

## Next Steps

If jobs still don't appear after following this guide:

1. **Check Selenium is running** - Jobs won't complete without it
2. **Check API logs** - Look for errors
3. **Test with curl** - Bypass frontend, test API directly
4. **Check browser extensions** - Some block localStorage
5. **Try different browser** - Rule out browser-specific issues

The debug panel and console logs should help identify exactly where the issue is!
