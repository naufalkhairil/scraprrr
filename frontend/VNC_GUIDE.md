# VNC Live View Guide

## Overview

Scraprrr embeds Selenium's noVNC viewer directly in the web interface, allowing you to watch the browser automation in real-time.

## How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                     Scraprrr Web Interface                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Job Monitor                                                 │  │
│  │ ┌──────────────────────────────────────────────────────┐   │  │
│  │ │ Status: 🟢 Running | Progress: ████████░░ 75%        │   │  │
│  │ └──────────────────────────────────────────────────────┘   │  │
│  │ ┌──────────────────────────────────────────────────────┐   │  │
│  │ │ [Status] [📺 Live View (VNC)] [Results]              │   │  │
│  │ │                                                       │   │  │
│  │ │ ┌─────────────────────────────────────────────────┐  │   │  │
│  │ │ │  Selenium Live View                             │  │   │  │
│  │ │ │  ┌───────────────────────────────────────────┐  │  │   │  │
│  │ │ │  │                                           │  │  │   │  │
│  │ │ │  │   [Browser Window - Live from Selenium]   │  │  │   │  │
│  │ │ │  │                                           │  │  │   │  │
│  │ │ │  │   Traveloka.com                           │  │  │   │  │
│  │ │ │  │   ┌─────────────────────────────────┐     │  │  │   │  │
│  │ │ │  │   │ From: CGK (Jakarta)             │     │  │  │   │  │
│  │ │ │  │   │ To:   DPS (Bali)                │     │  │  │   │  │
│  │ │ │  │   │ Date: 2026-03-30                │     │  │  │   │  │
│  │ │ │  │   │ [Search]                        │     │  │  │   │  │
│  │ │ │  │   └─────────────────────────────────┘     │  │  │   │  │
│  │ │ │  │                                           │  │  │   │  │
│  │ │ │  │   Loading flight results...               │  │  │   │  │
│  │ │ │  │   Scrolling to load more...               │  │  │   │  │
│  │ │ │  │                                           │  │  │   │  │
│  │ │ │  └───────────────────────────────────────────┘  │  │   │  │
│  │ │ │   Password: secret (auto-filled)                │  │   │  │
│  │ │ └─────────────────────────────────────────────────┘  │   │  │
│  │ └──────────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Start Selenium Grid with VNC

```bash
docker-compose -f docker/selenium-grid/docker-compose.yml up -d
```

This starts:
- **Port 4444**: WebDriver (for Selenium commands)
- **Port 7900**: noVNC viewer (web-based VNC)

### 2. Verify VNC is Running

Open browser to: http://localhost:7900

You should see:
```
┌─────────────────────────────┐
│  noVNC                      │
│  ┌───────────────────────┐  │
│  │                       │  │
│  │  [Desktop Preview]    │  │
│  │                       │  │
│  │  Password: ●●●●●●     │  │
│  │  [Connect]            │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

**Password**: `secret`

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Use the Web Interface

1. Open http://localhost:3000
2. Enter flight/hotel search parameters
3. Click "Search"
4. Job Monitor appears showing "Running" status
5. **Click "Live View (VNC)" tab**
6. Watch the browser automate in real-time!

## What You'll See

### During Flight Search

```
┌────────────────────────────────────────────────┐
│ Chrome                                         │
├────────────────────────────────────────────────┤
│ https://www.traveloka.com/.../flights          │
├────────────────────────────────────────────────┤
│                                                │
│  ✈️ Search Flights                             │
│  ┌──────────────────────────────────────────┐  │
│  │ From: CGK - Soekarno-Hatta, Jakarta      │  │
│  │ To:   DPS - Ngurah Rai, Bali             │  │
│  │ Date: Mon, 30 Mar 2026                    │  │
│  │ Passengers: 1                             │  │
│  │ [Search]                                  │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ⏳ Loading...                                 │
│                                                │
│  ───────────────────────────────────────────   │
│  Garuda Indonesia                              │
│  08:00 CGK → 10:30 DPS | 2h 30m | Rp 1.500.000 │
│  ───────────────────────────────────────────   │
│  Lion Air                                      │
│  09:00 CGK → 11:30 DPS | 2h 30m | Rp 900.000   │
│  ───────────────────────────────────────────   │
│                                                │
│  📜 Auto-scrolling to load more results...     │
│                                                │
└────────────────────────────────────────────────┘
```

### During Hotel Search

```
┌────────────────────────────────────────────────┐
│ Chrome                                         │
├────────────────────────────────────────────────┤
│ https://www.traveloka.com/.../hotels           │
├────────────────────────────────────────────────┤
│                                                │
│  🏨 Search Hotels                              │
│  ┌──────────────────────────────────────────┐  │
│  │ Destination: Jakarta                     │  │
│  │ Check-in: 30 Mar 2026                    │  │
│  │ Check-out: 31 Mar 2026                   │  │
│  │ Rooms: 1 | Guests: 2                     │  │
│  │ [Search]                                 │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ⏳ Loading...                                 │
│                                                │
│  ───────────────────────────────────────────   │
│  Mercure Jakarta Gatot Subroto                 │
│  ⭐⭐⭐⭐ | 8.8/10 | Rp 990.000                   │
│  ───────────────────────────────────────────   │
│  Hotel Indonesia Kempinski                     │
│  ⭐⭐⭐⭐⭐ | 9.2/10 | Rp 2.500.000                │
│  ───────────────────────────────────────────   │
│                                                │
│  📜 Auto-scrolling to load more hotels...      │
│                                                │
└────────────────────────────────────────────────┘
```

## Troubleshooting

### VNC Not Loading in Iframe

**Problem**: The VNC viewer shows "Connection failed" or blank screen.

**Solutions**:

1. **Check Selenium container is running**:
   ```bash
   docker ps | grep selenium
   ```

2. **Test VNC directly**:
   Open http://localhost:7900 in a new browser tab

3. **Check for CORS issues**:
   The iframe may be blocked by CORS. Solutions:
   - Use the direct VNC URL in a separate tab
   - Configure nginx to proxy VNC connections

4. **Verify password**:
   Default password is `secret`

### Browser Not Automating

**Problem**: VNC shows browser but nothing happens.

**Solutions**:

1. Check API logs for errors:
   ```bash
   docker logs [api-container-name]
   ```

2. Verify Selenium is connected:
   ```bash
   curl http://localhost:4444/status
   ```

3. Check if the job failed:
   - Look at the Job Monitor "Status" tab
   - Check for error messages

### Poor Performance

**Problem**: VNC is laggy or slow.

**Solutions**:

1. Reduce browser window size in docker-compose:
   ```yaml
   environment:
     - SE_SCREEN_WIDTH=1280
     - SE_SCREEN_HEIGHT=720
   ```

2. Increase shared memory:
   ```yaml
   shm_size: 4gb
   ```

3. Use a separate browser tab for VNC instead of embedded iframe

## Alternative: Direct VNC Access

If the embedded iframe doesn't work, you can:

1. **Open VNC in new tab**:
   Click the "VNC Viewer" link in the navbar

2. **Use external VNC client**:
   ```
   Host: localhost
   Port: 5900 (if exposed)
   Password: secret
   ```

3. **Use noVNC directly**:
   http://localhost:7900/?password=secret

## Technical Details

### noVNC URL Parameters

The embedded iframe uses:
```
http://localhost:7900/?autoconnect=1&resize=scale&password=secret
```

Parameters:
- `autoconnect=1`: Automatically connect on load
- `resize=scale`: Scale desktop to fit iframe
- `password=secret`: Auto-fill VNC password

### Selenium noVNC Configuration

The Selenium Docker image includes noVNC by default:
- **Image**: `selenium/standalone-chrome:latest`
- **VNC Port**: 7900
- **Password**: Set via `SE_VNC_PASSWORD` env var

### Browser Automation Flow

```
User clicks "Search"
    ↓
Frontend calls API: POST /api/v1/flights/search/async
    ↓
API creates background job
    ↓
API starts Selenium WebDriver
    ↓
Selenium opens Chrome browser (visible in VNC)
    ↓
Chrome navigates to Traveloka.com
    ↓
Selenium fills search form
    ↓
Selenium clicks Search button
    ↓
Selenium scrolls to load results
    ↓
Selenium extracts data
    ↓
API saves results
    ↓
Frontend shows "Completed" status
    ↓
User clicks "Results" tab to see data
```

## Security Notes

⚠️ **Important**: The VNC viewer is for development/testing only.

For production:
- Don't expose VNC port publicly
- Use authentication
- Consider disabling VNC entirely
- Use HTTPS for the frontend
