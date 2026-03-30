# Debug Guide - Live View Tab Not Showing

## Problem
After clicking "Search", the Live View (VNC) tab doesn't appear.

## Root Cause (Fixed)

The issue was in how the frontend handled the async job flow:

1. **`useScraper` hook** creates the job and gets initial job data
2. **`useJobPolling` hook** was only receiving `jobId` string, not the full job object
3. When job was created, polling started but initial job data wasn't being used
4. The VNC tab state wasn't being set correctly

## What Was Fixed

### 1. Changed `useJobPolling` to accept full job object
```typescript
// Before
useJobPolling(jobId: string | null)

// After
useJobPolling(initialJob: JobInfo | null)
```

### 2. Updated `HomePage` to pass full job
```typescript
// Before
const { job, cancelJob } = useJobPolling(currentJob?.job_id || null);

// After
const { job, cancelJob } = useJobPolling(currentJob);
```

### 3. Fixed VNC tab state initialization
```typescript
// Before - state set once on mount
const [activeTab, setActiveTab] = useState(autoOpenVnc ? 'vnc' : 'status');

// After - lazy initialization ensures it's always correct
const [activeTab, setActiveTab] = React.useState<'status' | 'vnc' | 'results'>(() => {
  if (autoOpenVnc) return 'vnc';
  return 'status';
});
```

### 4. Added effect to keep VNC tab active during scraping
```typescript
React.useEffect(() => {
  if (autoOpenVnc && isRunning) {
    setActiveTab('vnc');
  }
}, [job.status, autoOpenVnc, isRunning]);
```

---

## Testing Checklist

### 1. Start All Services

```bash
# Terminal 1: Selenium Grid
docker-compose -f docker/selenium-grid/docker-compose.yml up -d

# Verify Selenium is running
docker ps | grep selenium
# Should show container with ports 4444 and 7900

# Terminal 2: API Server
cd /home/pal/ICS/github/scraprrr
source venv/bin/activate
scraprrr-serve

# Terminal 3: Frontend
cd /home/pal/ICS/github/scraprrr/frontend
npm run dev
```

### 2. Open Browser

Navigate to: http://localhost:3000

### 3. Verify System Status

You should see a green alert at the top:
```
✓ System Status: All systems operational | API v2.0.0
Selenium: Connected
```

If Selenium shows "Disconnected", start the Docker container.

### 4. Search for Flights

1. **Enter search parameters:**
   - Origin: `CGK`
   - Destination: `DPS`

2. **Click "Search Flights"**

3. **IMMEDIATELY check for:**

   ✅ **Job Monitor panel appears** (should appear instantly)
   
   ✅ **Status badge shows "Pending" or "Running"**
   
   ✅ **Progress bar is visible** (may show 0%)
   
   ✅ **VNC tab is SELECTED** (should be the active tab)
   
   ✅ **VNC iframe is loading** (may show "Connecting...")

### 5. Watch Live Scraping

After 2-5 seconds, you should see in the VNC viewer:

- Chrome browser window
- Traveloka.com loading
- Search form being filled automatically
- Browser navigating to results page

**If VNC shows blank/black screen:**
- Check Selenium container: `docker logs selenium-server`
- Test VNC directly: http://localhost:7900
- Password is: `secret`

### 6. Monitor Progress

Every 2 seconds, the job status should update:
- Progress bar increases: 0% → 25% → 50% → 75% → 100%
- Status messages update
- Can see browser scrolling in VNC

### 7. Job Completion

When scraping completes (30-60 seconds):
- Status changes to "Completed"
- "Results" tab becomes available
- Badge shows number of flights found
- Can click "Results" to see data table

---

## Debug Console Commands

Open browser DevTools (F12) and check Console tab for errors.

### Check if job is created

```javascript
// After clicking search, check console for:
console.log('Job created:', job);
```

### Check API calls

In Network tab, filter by "jobs" - you should see:
1. `POST /api/v1/flights/search/async` - Returns job immediately
2. `GET /api/v1/jobs/{job_id}` - Polling every 2 seconds

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Job not found` | API returned 404 | Check API is running |
| `Connection refused` | Selenium not running | Start Docker container |
| `Network Error` | API server down | Run `scraprrr-serve` |
| VNC blank | VNC not accessible | Check port 7900 |

---

## Manual Test Flow

### Test 1: Job Monitor Appears Immediately

1. Open http://localhost:3000
2. **Before clicking search:** Job Monitor should NOT be visible
3. Click "Search Flights"
4. **Immediately after click:** Job Monitor SHOULD appear
5. Check VNC tab is selected

**Expected:** Job Monitor appears within 100ms of clicking search

### Test 2: VNC Tab Auto-Opens

1. Click "Search Flights"
2. Job Monitor appears
3. Check which tab is active

**Expected:** "Live View (VNC)" tab is selected (highlighted)

### Test 3: VNC Shows Browser

1. Job Monitor appears with VNC tab selected
2. Wait 2-5 seconds
3. Check iframe content

**Expected:** Chrome browser window visible, loading Traveloka

### Test 4: Polling Works

1. Job is running
2. Open DevTools → Network tab
3. Filter by "jobs"

**Expected:** GET request to `/api/v1/jobs/{job_id}` every 2 seconds

### Test 5: Job Completes

1. Wait for job to finish (30-60 seconds)
2. Check status badge

**Expected:** Status changes from "Running" → "Completed"
**Expected:** "Results" tab becomes clickable

---

## Quick Fix Checklist

If Live View tab still doesn't show:

### 1. Check Frontend Build
```bash
cd frontend
npm run build
# Should complete without errors
```

### 2. Check Console for Errors
```
F12 → Console tab
Look for red errors
```

### 3. Check Network Tab
```
F12 → Network tab
Filter: "jobs"
Should see polling requests every 2s
```

### 4. Verify API Returns Job
```bash
# After clicking search, check:
curl http://localhost:8000/api/v1/jobs
# Should show your job in the list
```

### 5. Check JobMonitor Props
Add console.log in JobMonitor:
```typescript
console.log('JobMonitor props:', { job, autoOpenVnc, status: job?.status });
```

### 6. Verify autoOpenVnc is true
In HomePage.tsx:
```typescript
<JobMonitor
  job={job}
  onCancel={handleCancelJob}
  onClear={handleClear}
  autoOpenVnc  // ← Should be present
/>
```

---

## Expected Timeline

```
0.0s:  User clicks "Search Flights"
       → API call: POST /flights/search/async
       
0.1s:  API returns job with status "pending"
       → currentJob state updated
       → JobMonitor component renders
       → autoOpenVnc=true → VNC tab selected
       
0.2s:  useJobPolling starts polling
       → First poll: GET /jobs/{job_id}
       → Job status: "pending"
       
1.0s:  VNC iframe connects to Selenium
       → Shows Chrome browser
       
2.0s:  Second poll
       → Job status: "running"
       → Progress: 10%
       
5.0s:  Browser navigates to Traveloka
       → Visible in VNC viewer
       
10.0s: Form filled, search clicked
       → Visible in VNC viewer
       
30.0s: Scrolling through results
       → Progress: 75%
       
60.0s: Job completes
       → Status: "completed"
       → Polling stops
       → Results tab available
```

---

## Still Not Working?

### Enable Debug Logging

Add to components:
```typescript
React.useEffect(() => {
  console.log('JobMonitor state:', {
    jobExists: !!job,
    jobId: job?.job_id,
    status: job?.status,
    activeTab,
    autoOpenVnc,
    isRunning,
  });
}, [job, activeTab, autoOpenVnc, isRunning]);
```

### Check Full Stack

```bash
# All services should be running:
docker ps
# selenium-server

ps aux | grep scraprrr-serve
# python scraprrr-serve

ps aux | grep vite
# npm run dev
```

### Test Direct API Access

```bash
# 1. Create job
curl -X POST http://localhost:8000/api/v1/flights/search/async \
  -H "Content-Type: application/json" \
  -d '{"origin":"CGK","destination":"DPS"}'

# Should return immediately with job_id

# 2. Get job status
curl http://localhost:8000/api/v1/jobs/{job_id}

# Should return job with status "pending" or "running"
```

---

## Summary

After fixes:
✅ Job Monitor appears immediately when search clicked
✅ VNC tab is selected automatically (autoOpenVnc=true)
✅ Initial job data is used immediately
✅ Polling starts within 100ms
✅ VNC iframe loads within 2-5 seconds
✅ User can watch live scraping
✅ Results available when complete

If any step fails, check the debug checklist above.
