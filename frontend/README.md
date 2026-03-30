# Scraprrr Frontend

React-based web interface for the Scraprrr travel scraper application.

## Features

- ✈️ **Flight Search** - Search flights by origin and destination airports
- 🏨 **Hotel Search** - Search hotels by location with popular destination quick-select
- 📊 **Real-time Monitoring** - Watch scraping progress with live VNC view of Selenium browser
- 📋 **Job Management** - View job history, cancel running jobs, cleanup old jobs
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🔌 **API Integration** - Seamless integration with FastAPI backend

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Scraprrr API server running (port 8000)
- Selenium Grid running (port 4444, VNC port 7900)

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Build and run with Docker Compose (includes API and Selenium)
docker-compose up -d

# Access frontend at http://localhost:3000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── FlightSearchForm.tsx
│   │   ├── HotelSearchForm.tsx
│   │   ├── JobMonitor.tsx      # With VNC integration
│   │   ├── FlightResults.tsx
│   │   ├── HotelResults.tsx
│   │   ├── JobList.tsx
│   │   ├── AppNavbar.tsx
│   │   └── HealthStatus.tsx
│   ├── pages/            # Page components
│   │   ├── HomePage.tsx
│   │   ├── JobsPage.tsx
│   │   └── AboutPage.tsx
│   ├── hooks/            # Custom React hooks
│   │   ├── useJobPolling.ts
│   │   └── useScraper.ts
│   ├── services/         # API client
│   │   └── api.ts
│   ├── types/            # TypeScript types
│   │   └── api.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Usage

### 1. Start Required Services

```bash
# Start Selenium Grid
docker-compose -f docker/selenium-grid/docker-compose.yml up -d

# Start API server
cd ..
scraprrr-serve
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

### 3. Use the Application

1. Open http://localhost:3000
2. Select "Flights" or "Hotels" tab
3. Enter search parameters
4. Click "Search" to start scraping
5. Monitor progress in the Job Monitor panel
6. Click "Live View (VNC)" tab to watch the browser automation
7. View results in the "Results" tab when complete

## Live VNC View

The Job Monitor includes an embedded VNC viewer that shows the Selenium browser in real-time:

- **URL**: http://localhost:7900 (also accessible via embedded iframe)
- **Password**: `secret`
- **Features**: Auto-connect, scale to fit

This allows you to:
- Watch the scraping process in real-time
- Debug any issues with the scraper
- Verify the browser is working correctly

## API Integration

The frontend communicates with the FastAPI backend using these endpoints:

| Action | Endpoint |
|--------|----------|
| Flight Search | `POST /api/v1/flights/search/async` |
| Hotel Search | `POST /api/v1/hotels/search/async` |
| Job Status | `GET /api/v1/flights/job/{id}` or `/api/v1/hotels/job/{id}` |
| Cancel Job | `DELETE /api/v1/flights/job/{id}` or `/api/v1/hotels/job/{id}` |
| List Jobs | `GET /api/v1/jobs` |
| Job Stats | `GET /api/v1/jobs/stats` |

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_SELENIUM_VNC_URL=http://localhost:7900
```

### Vite Configuration

The `vite.config.ts` includes:
- React plugin
- Path aliases (`@/*` → `src/*`)
- API proxy for development

## Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Bootstrap** - UI components
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **date-fns** - Date formatting

## Troubleshooting

### Cannot Connect to API

Ensure the API server is running:
```bash
scraprrr-serve
```

### VNC Not Loading

1. Check Selenium Grid is running: `docker ps | grep selenium`
2. Verify VNC port is accessible: http://localhost:7900
3. Check browser console for CORS errors

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## License

MIT License
