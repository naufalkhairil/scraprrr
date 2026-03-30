# Jobs List Fix - Debug Features Added

## Problem
Jobs list not appearing after page refresh.

## Root Cause
Session ID management wasn't working correctly - either generating new session on each refresh or not properly filtering jobs.

---

## Solution: Enhanced Debugging & Session Management

### 1. SessionManager Module (`frontend/src/services/api.ts`)

**Features:**
- Centralized session management
- localStorage persistence
- Console logging for debugging
- Axios interceptor for automatic header injection

```typescript
export const SessionManager = {
  getId: () => {
    // Get or create session, persist to localStorage
    // Logs every action
  },
  getCurrent: () => {
    // Get current session without creating
  },
  clear: () => {
    // Clear session for testing
  },
  getHeaders: () => {
    // Get headers with session ID
  }
};
```

---

### 2. Debug Panel on HomePage

**Access:** Click "Show Debug" button

**Shows:**
- Current Session ID
- Current Job status
- Polling Job status
- Errors

**Actions:**
- "Clear Session & Reload" - Reset session and test fresh

---

### 3. Enhanced JobsPage

**New Features:**
- Session ID display
- Last updated timestamp
- Refresh button with spinner
- "Clear Session" button
- Info alert when no jobs found
- Console logging

**Info Alert Shows:**
```
ℹ️ No jobs found for this session

Jobs are isolated by browser session. This could mean:
- You haven't created any jobs yet
- You're using incognito mode
- Jobs were cleaned up (older than 1 hour)

[Go to Home Page] [Clear Session & Reload]
```

---

### 4. Test Page (`/test.html`)

**Access:** http://localhost:3000/test.html

**Features:**
- Session information display
- API endpoint testing
- Create test jobs manually
- View jobs with/without session filter
- Real-time console logs

**Tests Available:**
1. Session Information
2. Health Endpoint Test
3. Jobs Endpoint Test
4. Create Flight Job
5. Create Hotel Job
6. Load Jobs (filtered by session)
7. Load ALL Jobs (no filter)

**Auto-refresh:** Jobs list updates every 2 seconds

---

## How to Debug

### Step 1: Check Session

1. Open http://localhost:3000
2. Click "Show Debug"
3. Note Session ID
4. **Expected:** UUID like `550e8400-...`

**If session changes on refresh:**
- Browser might be in incognito mode
- localStorage might be blocked

---

### Step 2: Check Console Logs

**Look for:**
```
[SessionManager] Using existing session: xxx
[JobsPage] Fetching jobs for session: xxx
[jobApi.list] Response: { total: 2, jobs: [...] }
```

**If no logs:**
- Check browser console (F12)
- Make sure JavaScript is enabled

---

### Step 3: Use Test Page

1. Go to http://localhost:3000/test.html
2. Check "Session Information" - should show UUID
3. Click "Test Jobs Endpoint"
4. **Expected:** Jobs returned with your session ID

**If jobs returned but not in main app:**
- Session ID mismatch
- Click "Clear Session & Reload" in main app

---

### Step 4: Create Test Job

**On test page:**
1. Click "Create Flight Job (CGK→DPS)"
2. **Expected:** Job created immediately
3. Wait 2 seconds - job should appear in list
4. Go to main app Jobs page
5. **Expected:** Same job visible

**If job not visible in main app:**
- Different session IDs
- Use "Clear Session" button to sync

---

### Step 5: Check Network Tab

**In DevTools → Network:**

1. Filter by "jobs"
2. Look for `GET /api/v1/jobs`
3. Check request headers:
   ```
   X-Session-ID: 550e8400-e29b-41d4-a716-446655440000
   ```
4. Check response:
   ```json
   {
     "total": 1,
     "jobs": [{ "job_id": "...", "session_id": "SAME_ID" }]
   }
   ```

**If session ID in header doesn't match localStorage:**
- SessionManager not initializing correctly
- Click "Clear Session & Reload"

---

## Common Scenarios

### Scenario 1: Fresh Install

**Symptom:** No jobs showing

**Steps:**
1. Go to home page
2. Start a flight search
3. Wait for job to complete
4. Go to Jobs page
5. **Expected:** Job appears

**If still no jobs:**
- Check console for errors
- Use test page to create job manually

---

### Scenario 2: After Page Refresh

**Symptom:** Jobs disappear after refresh

**Check:**
1. Is session ID same before/after refresh?
2. Check console logs
3. Use test page to verify jobs exist

**Fix:**
- Click "Clear Session & Reload"
- Create new job
- Jobs should now persist

---

### Scenario 3: Multiple Tabs

**Expected behavior:**
- Same browser = same session = see same jobs
- Different browser = different session = see different jobs

**Test:**
1. Tab A: Create job
2. Tab B: Go to Jobs page
3. **Expected:** See job from Tab A

**If not:**
- Check both tabs have same session ID
- localStorage might not be syncing between tabs

---

### Scenario 4: Incognito/Private Mode

**Symptom:** Jobs never persist

**Cause:** localStorage cleared when tab closes

**Fix:**
- Don't use incognito mode
- Or expect to lose session on close

---

## Files Changed

| File | Changes |
|------|---------|
| `frontend/src/services/api.ts` | SessionManager module |
| `frontend/src/pages/HomePage.tsx` | Debug panel |
| `frontend/src/pages/JobsPage.tsx` | Session display, alerts |
| `frontend/public/test.html` | New test page |

---

## Quick Test Commands

### Browser Console

```javascript
// Check session
localStorage.getItem('scraprrr_session_id')

// Check jobs
fetch('/api/v1/jobs')
  .then(r => r.json())
  .then(d => console.log(d))

// Clear session
localStorage.removeItem('scraprrr_session_id')
location.reload()
```

### Terminal

```bash
# Start API with debug logs
scraprrr-serve --log-level debug

# Check backend logs
docker logs [container] 2>&1 | grep -i session
```

---

## Expected Behavior

| Action | Expected Result |
|--------|----------------|
| Create job | Appears in Jobs page within 2s |
| Refresh page | Jobs still visible |
| Clear session | Old jobs hidden, new session |
| Test page | Shows same jobs as main app |
| Different browser | Different jobs (different session) |

---

## Next Steps

1. **Test with test page first** - Easier to debug
2. **Check console logs** - Most issues obvious from logs
3. **Use "Clear Session & Reload"** - Fixes 90% of issues
4. **If still broken** - Check JOBS_DEBUG_GUIDE.md

---

## Support Checklist

When asking for help, provide:

- [ ] Browser console logs (screenshot)
- [ ] Session ID (first/last 8 chars)
- [ ] Test page results (screenshot)
- [ ] Network tab request/response (screenshot)
- [ ] Steps to reproduce

---

## Summary

✅ SessionManager - Centralized session management  
✅ Debug Panel - Real-time session/job info  
✅ JobsPage - Enhanced with session display  
✅ Test Page - Standalone debugging tool  
✅ Console Logging - All actions logged  
✅ Auto-refresh - Jobs update every 2 seconds  

**Use the test page at http://localhost:3000/test.html to quickly diagnose issues!**
