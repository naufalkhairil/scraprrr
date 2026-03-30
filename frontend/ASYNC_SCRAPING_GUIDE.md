# Async Scraping with Live VNC Guide

## Overview

The Scraprrr frontend now uses **fully asynchronous scraping** with **immediate live VNC monitoring**. When you click "Search", the Job Monitor appears instantly and automatically opens the Live View (VNC) tab so you can watch the browser automation in real-time.

## User Flow

### Before (Synchronous - Old)
```
User clicks "Search" → Wait 30-60 seconds → Job Monitor appears → Job already done
```

### After (Asynchronous - New) ✅
```
User clicks "Search" → Job Monitor appears IMMEDIATELY → VNC tab opens automatically → 
Watch live scraping → Job completes → View results
```

## Step-by-Step Experience

### Step 1: User Enters Search Parameters

```
┌─────────────────────────────────────────────────────────────┐
│  ✈️ Flight Search                                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Origin: [CGK]  ←→  Destination: [DPS]                 │  │
│  │ Origin Name: [Jakarta]                                │  │
│  │ Destination Name: [Bali]                              │  │
│  │ ☑ Save results to files                               │  │
│  │                                                        │  │
│  │  [🔍 Search Flights]                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: User Clicks "Search" - Job Monitor Appears IMMEDIATELY

```
┌─────────────────────────────────────────────────────────────┐
│  Job Monitor                              🟡 Running        │
│  ─────────────────────────────────────────────────────────  │
│  Job ID: 550e8400-e29b-41d4-a716-446655440000               │
│  Job Type: [Flight Search]                                  │
│  Search: CGK → DPS                                          │
│                                                             │
│  Progress: 0%                                               │
│  ████████░░░░░░░░░░░░░░░░░░░░░░░░░ [Animated]               │
│  Starting scraper...                                        │
│                                                             │
│  ⚡ Scraping in progress...                                  │
│  Watch the live browser in the Live View (VNC) tab          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [Status] [🖥️ Live View (VNC)] [Results]              │   │
│  │          ↑ Auto-selected!                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🖥️ Selenium Live View                                 │   │
│  │ ┌────────────────────────────────────────────────┐   │   │
│  │ │                                                │   │   │
│  │ │   [Browser Window - LIVE from Selenium]        │   │   │
│  │ │                                                │   │   │
│  │ │   Traveloka.com is loading...                  │   │   │
│  │ │   Chrome is navigating to search page...       │   │   │
│  │ │                                                │   │   │
│  │ │   [You can WATCH this happening in real-time!] │   │   │
│  │ │                                                │   │   │
│  │ └────────────────────────────────────────────────┘   │   │
│  │ Password: secret (auto-filled)                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  [❌ Cancel Job]                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Watch Live Scraping (VNC Tab Auto-Opens)

```
┌─────────────────────────────────────────────────────────────┐
│  🖥️ Live View (VNC)                        🟢 Running       │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ⚡ Watching live browser automation                         │
│  Password: secret | Watch the scraper navigate Traveloka   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Chrome - Traveloka.com                               │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │  ✈️ Search Flights                                    │   │
│  │  ┌───────────────────────────────────────────────┐   │   │
│  │  │ From: CGK - Soekarno-Hatta, Jakarta           │   │   │
│  │  │ To:   DPS - Ngurah Rai, Bali                  │   │   │
│  │  │ Date: Mon, 30 Mar 2026                         │   │   │
│  │  │ [Searching...]                                 │   │   │
│  │  └───────────────────────────────────────────────┘   │   │
│  │                                                       │   │
│  │  ⏳ Loading flight results...                          │   │
│  │                                                       │   │
│  │  [You're watching this happen LIVE!]                  │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  Progress: 45%                                              │
│  ████████████████████░░░░░░░░░░░░░░░░░░░░                   │
│                                                             │
│  Having issues? [Open VNC in new tab]                       │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Scraping Continues - Auto-Scrolling

```
┌─────────────────────────────────────────────────────────────┐
│  🖥️ Live View (VNC)                        🟢 Running       │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Chrome - Traveloka.com                               │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │  Flight Results: CGK → DPS                            │   │
│  │  ─────────────────────────────────────────────────    │   │
│  │  Garuda Indonesia                                     │   │
│  │  08:00 CGK → 10:30 DPS | 2h 30m | Rp 1.500.000        │   │
│  │  ─────────────────────────────────────────────────    │   │
│  │  Lion Air                                             │   │
│  │  09:00 CGK → 11:30 DPS | 2h 30m | Rp 900.000          │   │
│  │  ─────────────────────────────────────────────────    │   │
│  │  AirAsia                                              │   │
│  │  10:00 CGK → 12:30 DPS | 2h 30m | Rp 850.000          │   │
│  │  ─────────────────────────────────────────────────    │   │
│  │                                                       │   │
│  │  📜 Auto-scrolling to load more results...            │   │
│  │     [You can WATCH the page scrolling!]               │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  Progress: 75%                                              │
│  ████████████████████████████████░░░░░░░░                   │
│  Scraping in progress...                                    │
└─────────────────────────────────────────────────────────────┘
```

### Step 5: Job Completes - Results Available

```
┌─────────────────────────────────────────────────────────────┐
│  Job Monitor                              ✅ Completed      │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ✅ Found 25 flights                                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [Status] [Live View (VNC)] [📋 Results ✅]            │   │
│  │                              ↑ 25                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  CGK → DPS                              25 flights found    │
│  ─────────────────────────────────────────────────────────  │
│  Airline        Departure  Arrival   Duration   Price       │
│  ─────────────────────────────────────────────────────────  │
│  Garuda         08:00 CGK  10:30 DPS 2h 30m    Rp 1.500.000 │
│  Lion Air       09:00 CGK  11:30 DPS 2h 30m    Rp 900.000   │
│  AirAsia        10:00 CGK  12:30 DPS 2h 30m    Rp 850.000   │
│  ... (22 more)                                               │
│                                                             │
│  [Clear]                                                     │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Immediate Feedback
- Job Monitor appears **instantly** after clicking "Search"
- No waiting for the scrape to complete
- User knows immediately that something is happening

### 2. Auto-Open VNC Tab
- VNC tab is **automatically selected** when job starts
- User sees the browser automation **immediately**
- No need to manually click the VNC tab

### 3. Live Progress Updates
- Progress bar animates in real-time
- Status messages update as scraping progresses
- Polling every 2 seconds for latest job status

### 4. Interactive Controls
- **Cancel Job** button visible during scraping
- **Clear** button appears when complete
- Can switch between tabs freely

### 5. Visual Indicators
- 🟡 **Running** badge with spinner
- 🟢 **Completed** badge with checkmark
- 🔴 **Failed** badge with error message
- Animated progress bar

## Technical Implementation

### Auto-Open VNC

```typescript
// JobMonitor.tsx
const [activeTab, setActiveTab] = React.useState<'status' | 'vnc' | 'results'>(
  autoOpenVnc ? 'vnc' : 'status'  // Start on VNC tab if autoOpenVnc is true
);

// Auto-open VNC when job starts running
React.useEffect(() => {
  if (autoOpenVnc && job.status === 'running' && activeTab === 'status') {
    setActiveTab('vnc');
  }
}, [job.status, autoOpenVnc, activeTab]);
```

### Immediate Display

```typescript
// HomePage.tsx
{job && (  // Shows as soon as job exists (not when completed)
  <JobMonitor
    job={job}
    onCancel={handleCancelJob}
    onClear={handleClear}
    autoOpenVnc={true}  // Auto-open VNC tab
  />
)}
```

### Continuous Polling

```typescript
// useJobPolling.ts
useEffect(() => {
  if (jobId) {
    startPolling();  // Start polling immediately
  }
  return () => stopPolling();
}, [jobId]);

// Poll every 2 seconds
const intervalRef = useRef<NodeJS.Timeout | null>(null);
intervalRef.current = setInterval(fetchJob, 2000);
```

## Benefits

| Before (Sync) | After (Async + Live VNC) |
|---------------|--------------------------|
| Wait 30-60s with no feedback | Immediate visual feedback |
| Job Monitor appears after completion | Job Monitor appears instantly |
| VNC tab disabled until manually enabled | VNC tab auto-opens |
| User wonders if anything is happening | User watches live automation |
| Can't cancel (already done) | Can cancel anytime |
| All or nothing | Full control and visibility |

## Usage Example

```typescript
// 1. User clicks "Search Flights"
<FlightSearchForm onSubmit={handleFlightSearch} />

// 2. API call starts async job
const job = await flightApi.searchAsync({
  origin: 'CGK',
  destination: 'DPS'
});

// 3. Job Monitor appears immediately
<JobMonitor job={job} autoOpenVnc={true} />

// 4. VNC tab is already selected - user watches live
// 5. Polling updates job status every 2 seconds
// 6. When complete, Results tab shows scraped data
```

## Troubleshooting

### VNC Not Auto-Opening

**Check**: `autoOpenVnc` prop is set to `true`

```tsx
<JobMonitor job={job} autoOpenVnc={true} />
```

### Job Monitor Not Appearing

**Check**: `job` state is being set after API call

```typescript
const job = await flightApi.searchAsync(request);
setCurrentJob(job);  // This triggers Job Monitor to appear
```

### VNC Shows Blank Screen

**Solutions**:
1. Verify Selenium is running: `docker ps | grep selenium`
2. Test VNC directly: http://localhost:7900
3. Check password is correct: `secret`
4. Try opening VNC in new tab

## Summary

✅ **Job Monitor appears immediately** when user clicks Search  
✅ **VNC tab auto-opens** to show live browser automation  
✅ **Progress updates every 2 seconds** via polling  
✅ **User can watch entire scraping process** in real-time  
✅ **Can cancel job anytime** during scraping  
✅ **Results appear automatically** when complete  

No more waiting wondering if something is happening - users see everything live!
