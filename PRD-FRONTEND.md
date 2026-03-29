# Product Requirements Document (PRD)
# Scraprrr Web Application - Frontend

**Version:** 1.0.0  
**Date:** March 29, 2026  
**Author:** Scraprrr Team  
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Product Overview](#product-overview)
3. [Goals and Objectives](#goals-and-objectives)
4. [Target Users](#target-users)
5. [Backend Integration](#backend-integration)
6. [Frontend Architecture](#frontend-architecture)
7. [Functional Requirements](#functional-requirements)
8. [User Interface Requirements](#user-interface-requirements)
9. [Non-Functional Requirements](#non-functional-requirements)
10. [Page Specifications](#page-specifications)
11. [Component Library](#component-library)
12. [State Management](#state-management)
13. [API Integration](#api-integration)
14. [Security Requirements](#security-requirements)
15. [Deployment Strategy](#deployment-strategy)
16. [Milestones and Timeline](#milestones-and-timeline)
17. [Success Metrics](#success-metrics)
18. [Appendices](#appendices)

---

## Executive Summary

Scraprrr Web Application is a modern, responsive frontend that provides users with an intuitive interface to manage e-commerce scraping operations for travel platforms (Traveloka, Booking.com, Agoda, etc.). The application enables users to create scraper jobs, monitor real-time progress, view results in tabular format with AI-powered explanations, and export data to files or databases.

### Key Value Propositions

- **Visual Job Management**: Create and manage scraper jobs through an intuitive UI
- **Real-time Monitoring**: Live dashboard showing scraper progress via WebSocket
- **Smart Results Display**: Tabular data with AI-generated insights and explanations
- **Flexible Export**: One-click export to CSV, Excel, JSON, or direct PostgreSQL ingestion
- **Multi-Platform Support**: Scrape flights, hotels, and more from multiple providers

---

## Product Overview

### Problem Statement

The current Scraprrr CLI tool requires technical expertise and lacks:
- Visual feedback during scraping operations
- Easy result exploration and filtering
- Quick export capabilities
- Real-time progress visibility
- Accessible interface for non-technical users

### Solution

A React-based web application that:
1. Provides a visual interface for creating and managing scraper jobs
2. Displays real-time progress via WebSocket connections
3. Shows results in interactive tables with sorting, filtering, and pagination
4. Offers AI-powered explanations of scraping results
5. Enables one-click exports to multiple formats
6. Integrates with the existing FastAPI backend

### Scope

**In Scope:**
- Dashboard with job overview and system status
- Job creation wizard for flights and hotels
- Real-time job monitoring page
- Results viewer with table and chart visualizations
- Export management interface
- Settings and configuration pages
- Authentication flow

**Out of Scope (Phase 1):**
- Mobile native applications
- Offline mode
- Advanced analytics dashboard
- Custom scraper builder
- Multi-language support (i18n)

---

## Goals and Objectives

### Primary Goals

| Goal | Description | Success Metric |
|------|-------------|----------------|
| **G1: Usability** | Enable non-technical users to run scrapers | 90% task completion rate |
| **G2: Real-time Visibility** | Show live scraper progress | < 1s update latency |
| **G3: Data Exploration** | Easy result filtering and analysis | < 3 clicks to find data |
| **G4: Export Simplicity** | One-click export to any format | < 5s export initiation |
| **G5: Performance** | Fast, responsive interface | < 2s page load time |

### Key Objectives

1. **O1**: Build responsive UI that works on desktop and tablet
2. **O2**: Implement WebSocket for real-time updates
3. **O3**: Create reusable component library
4. **O4**: Integrate with existing FastAPI backend
5. **O5**: Achieve 90+ Lighthouse performance score

---

## Target Users

### User Personas

#### 1. Business Analyst (Primary)
- **Technical Level**: Intermediate
- **Needs**: Quick data access, export to Excel, visual insights
- **Pain Points**: CLI is too technical, no visual feedback
- **Goals**: Monitor price trends, generate reports

#### 2. Product Manager (Primary)
- **Technical Level**: Basic
- **Needs**: Simple interface, quick results, easy sharing
- **Pain Points**: Can't run scrapers independently
- **Goals**: Competitive analysis, pricing insights

#### 3. Data Engineer (Secondary)
- **Technical Level**: Advanced
- **Needs**: Database integration, API access, automation
- **Pain Points**: Manual data pipeline setup
- **Goals**: Automated data ingestion, monitoring

#### 4. Developer (Secondary)
- **Technical Level**: Advanced
- **Needs**: API documentation, webhook integration
- **Pain Points**: Limited integration options
- **Goals**: Custom workflows, system integration

---

## Backend Integration

### Backend Architecture Reference

The frontend integrates with the existing Scraprrr backend as documented in `DOCUMENTATION.md` and `PRD.md`:

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Dashboard │  │   Job       │  │   Results           │  │
│  │   Page      │  │   Monitor   │  │   Viewer            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                              │                                │
│         ┌────────────────────┼────────────────────┐          │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │  REST API   │     │  WebSocket  │     │   Export    │    │
│  │  (HTTP)     │     │  (Real-time)│     │   Service   │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Job       │  │   Result    │  │   PostgreSQL        │  │
│  │   Service   │  │   Service   │  │   Database          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                              │                                │
│                              ▼                                │
│                    ┌─────────────────┐                       │
│                    │   Celery        │                       │
│                    │   Workers       │                       │
│                    └────────┬────────┘                       │
│                             │                                 │
│                             ▼                                 │
│                    ┌─────────────────┐                       │
│                    │   Selenium      │                       │
│                    │   Grid          │                       │
│                    └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### API Endpoints Integration

| Frontend Feature | Backend Endpoint | Method |
|-----------------|------------------|--------|
| Create Job | `/api/v1/jobs` | POST |
| List Jobs | `/api/v1/jobs` | GET |
| Job Details | `/api/v1/jobs/{id}` | GET |
| Cancel Job | `/api/v1/jobs/{id}` | DELETE |
| Get Results | `/api/v1/jobs/{id}/results` | GET |
| Export to File | `/api/v1/jobs/{id}/export` | POST |
| Ingest to DB | `/api/v1/jobs/{id}/ingest` | POST |
| Real-time Updates | `/ws/monitor/{job_id}` | WebSocket |
| Login | `/api/v1/auth/login` | POST |
| Health Check | `/health/live` | GET |

---

## Frontend Architecture

### Technology Stack

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| **Framework** | React | 18.x | Component-based, large ecosystem |
| **Language** | TypeScript | 5.x | Type safety, better DX |
| **Build Tool** | Vite | 5.x | Fast HMR, optimized builds |
| **Styling** | Tailwind CSS | 3.x | Utility-first, responsive |
| **UI Components** | shadcn/ui | Latest | Accessible, customizable |
| **State Management** | Zustand | 4.x | Lightweight, simple |
| **Data Fetching** | TanStack Query | 5.x | Caching, background updates |
| **WebSocket** | native WebSocket | - | Real-time communication |
| **Tables** | TanStack Table | 8.x | Powerful table utilities |
| **Charts** | Recharts | 2.x | React-native charts |
| **Forms** | React Hook Form | 7.x | Performance, validation |
| **Validation** | Zod | 3.x | Schema validation |
| **Routing** | React Router | 6.x | Standard routing |
| **HTTP Client** | Axios | 1.x | Interceptors, cancellation |
| **Testing** | Vitest + RTL | Latest | Fast testing |
| **E2E** | Playwright | Latest | Cross-browser testing |

### Project Structure

```
scraprrr-webapp/
├── 📁 public/                    # Static assets
│   ├── favicon.ico
│   ├── logo.svg
│   └── manifest.json
│
├── 📁 src/
│   ├── 📁 api/                   # API integration
│   │   ├── client.ts             # Axios instance
│   │   ├── endpoints.ts          # API endpoint definitions
│   │   ├── jobs.ts               # Job API calls
│   │   ├── results.ts            # Results API calls
│   │   ├── export.ts             # Export API calls
│   │   └── auth.ts               # Auth API calls
│   │
│   ├── 📁 components/            # Reusable components
│   │   ├── 📁 ui/                # Base UI components (shadcn)
│   │   │   ├── button.tsx
│   │   │   ├── table.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── form.tsx
│   │   │   └── ...
│   │   │
│   │   ├── 📁 layout/            # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── AppLayout.tsx
│   │   │
│   │   ├── 📁 jobs/              # Job-related components
│   │   │   ├── JobList.tsx
│   │   │   ├── JobCard.tsx
│   │   │   ├── JobStatus.tsx
│   │   │   ├── JobProgress.tsx
│   │   │   └── CreateJobForm.tsx
│   │   │
│   │   ├── 📁 results/           # Results components
│   │   │   ├── ResultsTable.tsx
│   │   │   ├── ResultsFilter.tsx
│   │   │   ├── ResultsSummary.tsx
│   │   │   └── AIExplanation.tsx
│   │   │
│   │   ├── 📁 export/            # Export components
│   │   │   ├── ExportDialog.tsx
│   │   │   ├── ExportFormatSelector.tsx
│   │   │   └── ExportHistory.tsx
│   │   │
│   │   └── 📁 common/            # Shared components
│   │       ├── Loading.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── StatusBadge.tsx
│   │       └── SearchInput.tsx
│   │
│   ├── 📁 pages/                 # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Jobs.tsx
│   │   ├── JobDetail.tsx
│   │   ├── Results.tsx
│   │   ├── Exports.tsx
│   │   ├── Settings.tsx
│   │   ├── Login.tsx
│   │   └── NotFound.tsx
│   │
│   ├── 📁 hooks/                 # Custom hooks
│   │   ├── useJobs.ts
│   │   ├── useJobMonitor.ts
│   │   ├── useResults.ts
│   │   ├── useExport.ts
│   │   └── useAuth.ts
│   │
│   ├── 📁 stores/                # Zustand stores
│   │   ├── authStore.ts
│   │   ├── jobStore.ts
│   │   └── settingsStore.ts
│   │
│   ├── 📁 types/                 # TypeScript types
│   │   ├── job.ts
│   │   ├── result.ts
│   │   ├── export.ts
│   │   └── api.ts
│   │
│   ├── 📁 utils/                 # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── helpers.ts
│   │
│   ├── 📁 lib/                   # Library configurations
│   │   ├── axios.ts
│   │   ├── queryClient.ts
│   │   └── websocket.ts
│   │
│   ├── App.tsx                   # Root component
│   ├── main.tsx                  # Entry point
│   └── index.css                 # Global styles
│
├── 📁 tests/                     # Test files
│   ├── components/
│   ├── pages/
│   └── e2e/
│
├── 📄 package.json
├── 📄 tsconfig.json
├── 📄 vite.config.ts
├── 📄 tailwind.config.js
├── 📄 eslint.config.js
├── 📄 .env.example
└── 📄 README.md
```

---

## Functional Requirements

### FR1: Authentication

#### FR1.1: Login
**Description:** Users can authenticate with email/password  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Login form with email and password fields
- [ ] Form validation (email format, password required)
- [ ] Display error messages for invalid credentials
- [ ] Store JWT token in memory (not localStorage for security)
- [ ] Redirect to dashboard after successful login
- [ ] "Remember me" option (optional)

---

#### FR1.2: Logout
**Description:** Users can log out securely  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Logout button in header/sidebar
- [ ] Clear authentication state
- [ ] Redirect to login page
- [ ] Invalidate JWT token on backend

---

### FR2: Dashboard

#### FR2.1: Dashboard Overview
**Description:** Main landing page showing system status and recent activity  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Display system health status (API, DB, Selenium)
- [ ] Show active jobs count
- [ ] Show recent jobs list (last 10)
- [ ] Display quick stats (total jobs, success rate)
- [ ] Quick action button to create new job
- [ ] Auto-refresh every 30 seconds

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│  Scraprrr Dashboard                              [User] ▼   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  System Status: ● All Systems Operational                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Active Jobs  │  │ Success Rate │  │ Total Jobs   │       │
│  │     5        │  │    94.2%     │  │    1,234     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  Recent Jobs                              [+ New Job]        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Job ID    │ Type    │ Status    │ Created    │ ... │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ abc123    │ Flight  │ Running   │ 2 min ago  │ ... │    │
│  │ def456    │ Hotel   │ Completed │ 15 min ago │ ... │    │
│  │ ghi789    │ Flight  │ Failed    │ 1 hour ago │ ... │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### FR3: Job Management

#### FR3.1: Create Job Wizard
**Description:** Step-by-step form to create new scraper job  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Step 1: Select scraper type (Flight/Hotel)
- [ ] Step 2: Enter search parameters
  - Flight: origin, destination, date (optional)
  - Hotel: location, check-in/out dates (optional)
- [ ] Step 3: Configure options (scroll, max results, output)
- [ ] Step 4: Review and confirm
- [ ] Form validation at each step
- [ ] Back/Next navigation
- [ ] Cancel option

**Flight Search Form:**
```
┌─────────────────────────────────────────┐
│  Create Flight Job                      │
├─────────────────────────────────────────┤
│                                          │
│  Origin *          Destination *         │
│  ┌────────────┐    ┌────────────────┐   │
│  │ CGK        │    │ DPS            │   │
│  │ Jakarta    │    │ Bali           │   │
│  └────────────┘    └────────────────┘   │
│                                          │
│  Departure Date                          │
│  ┌─────────────────────────────────┐     │
│  │ 2026-04-15                      │     │
│  └─────────────────────────────────┘     │
│                                          │
│  Advanced Options                         │
│  ☑ Enable scrolling                       │
│  ☐ Limit results: [____]                  │
│  ☑ Save to database                       │
│                                          │
│         [Cancel]     [Next →]            │
└─────────────────────────────────────────┘
```

---

#### FR3.2: Job List
**Description:** View and manage all jobs  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Table view with sortable columns
- [ ] Filter by status (All/Running/Completed/Failed)
- [ ] Filter by scraper type
- [ ] Search by job ID or parameters
- [ ] Pagination (25/50/100 per page)
- [ ] Bulk actions (cancel selected)
- [ ] Row click to view details

---

#### FR3.3: Job Detail & Monitoring
**Description:** Real-time monitoring of individual job  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Display job metadata (ID, type, created at, parameters)
- [ ] Show progress bar with percentage
- [ ] Display current step description
- [ ] Show items collected count
- [ ] Real-time status updates via WebSocket
- [ ] Cancel button for running jobs
- [ ] View results button when completed
- [ ] Error message display for failed jobs

**Monitoring View:**
```
┌─────────────────────────────────────────────────────────────┐
│  Job Details: abc123                           [← Back]     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Status: ● Running                                          │
│                                                              │
│  Progress: ████████████░░░░░░░░░ 45%                        │
│                                                              │
│  Current Step: Extracting flight data...                    │
│  Items Collected: 23 tickets                                │
│  Elapsed Time: 2m 34s                                       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Live Log                                             │    │
│  │ 10:00:00 - Job started                               │    │
│  │ 10:00:05 - Navigating to Traveloka                   │    │
│  │ 10:00:15 - Search executed: CGK → DPS                │    │
│  │ 10:00:25 - Waiting for results...                    │    │
│  │ 10:00:35 - Results loaded, scrolling...              │    │
│  │ 10:01:00 - Extracting data... (23 items)             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│                    [Cancel Job]  [View Results →]           │
└─────────────────────────────────────────────────────────────┘
```

---

### FR4: Results Viewer

#### FR4.1: Results Table
**Description:** Interactive table displaying scraping results  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Display results in sortable table
- [ ] Column visibility toggle
- [ ] Filter by any column
- [ ] Search across all fields
- [ ] Pagination with configurable page size
- [ ] Export current view button
- [ ] Copy row to clipboard
- [ ] Highlight important columns (price, etc.)

**Flight Results Table:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Results: Flight CGK → DPS                              [Export] [📊]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Search: [____________]  Airline: [▼ All]  Price: [___] - [___]        │
│                                                                          │
│  ┌───┬──────────────────┬─────────┬─────────┬─────────┬──────────────┐ │
│  │☐│ Airline            │ Depart  │ Arrive  │ Duration│ Price        │ │
│  ├───┼──────────────────┼─────────┼─────────┼─────────┼──────────────┤ │
│  │☐│ Garuda Indonesia   │ 08:00   │ 10:30   │ 2h 30m  │ Rp 1.500.000 │ │
│  │☐│ Lion Air           │ 09:15   │ 11:50   │ 2h 35m  │ Rp 1.200.000 │ │
│  │☐│ AirAsia            │ 10:00   │ 12:35   │ 2h 35m  │ Rp 1.100.000 │ │
│  │☐│ Citilink           │ 11:30   │ 14:00   │ 2h 30m  │ Rp 1.350.000 │ │
│  └───┴──────────────────┴─────────┴─────────┴─────────┴──────────────┘ │
│                                                                          │
│  Showing 1-25 of 150 results    [< Prev] [1] [2] [3] ... [6] [Next >]  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

#### FR4.2: Results Summary & Charts
**Description:** Visual summary of results with charts  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Display total results count
- [ ] Show price statistics (min, max, avg)
- [ ] Airline distribution pie chart
- [ ] Price range histogram
- [ ] Departure time distribution
- [ ] Toggle between summary and table view

---

#### FR4.3: AI Explanation
**Description:** AI-generated insights about the results  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Display AI-generated summary text
- [ ] Highlight best deals
- [ ] Point out price trends
- [ ] Suggest optimal booking times
- [ ] Explain anomalies or patterns
- [ ] Toggle to show/hide explanation

**Example AI Explanation:**
```
┌─────────────────────────────────────────────────────────────┐
│  📊 AI Insights                                      [▼]    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Based on 150 flights from CGK to DPS:                      │
│                                                              │
│  💡 Best Deal: AirAsia at Rp 1.100.000 (31% below avg)      │
│                                                              │
│  📈 Price Range: Rp 950.000 - Rp 3.500.000                  │
│     Average: Rp 1.850.000                                   │
│                                                              │
│  ⏰ Cheapest flights depart between 05:00-07:00             │
│                                                              │
│  ✈️ Most options: Garuda Indonesia (45 flights)             │
│                                                              │
│  🎯 Recommendation: Book morning flights for best prices    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### FR5: Export Management

#### FR5.1: Export Dialog
**Description:** Configure and initiate export  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Select export format (CSV, Excel, JSON)
- [ ] Choose columns to export
- [ ] Select rows (all, visible, selected)
- [ ] Configure format options (delimiter, encoding)
- [ ] Show estimated file size
- [ ] Download button
- [ ] Show export progress

---

#### FR5.2: Database Ingestion
**Description:** Export results directly to PostgreSQL  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Select target table (existing or new)
- [ ] Choose mode (append or upsert)
- [ ] Configure unique key for upsert
- [ ] Preview schema mapping
- [ ] Show ingestion progress
- [ ] Display ingestion statistics

---

#### FR5.3: Export History
**Description:** View past exports  
**Priority:** P2

**Acceptance Criteria:**
- [ ] List all exports with status
- [ ] Download expired exports (if available)
- [ ] Re-run export with same settings
- [ ] Delete export history

---

### FR6: Settings

#### FR6.1: User Preferences
**Description:** Configure user settings  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Default scraper options
- [ ] Table preferences (page size, columns)
- [ ] Notification preferences
- [ ] Theme selection (light/dark)

---

#### FR6.2: System Configuration
**Description:** Admin system settings  
**Priority:** P2

**Acceptance Criteria:**
- [ ] Selenium Grid configuration
- [ ] Database connection settings
- [ ] Export storage settings
- [ ] API key management

---

## User Interface Requirements

### Design Principles

1. **Clarity**: Information is easy to understand at a glance
2. **Efficiency**: Minimize clicks to complete tasks
3. **Consistency**: Uniform design patterns throughout
4. **Feedback**: Clear status indicators and notifications
5. **Accessibility**: WCAG 2.1 AA compliance

### Color Palette

```
Primary:     Blue       #3B82F6
Success:     Green      #10B981
Warning:     Yellow     #F59E0B
Error:       Red        #EF4444
Info:        Cyan       #06B6D4

Background:  Light      #F8FAFC
Surface:     White      #FFFFFF
Text:        Dark       #1E293B
Text Muted:  Gray       #64748B
```

### Typography

```
Headings:    Inter, sans-serif
Body:        Inter, sans-serif
Mono:        JetBrains Mono (for code/IDs)

Scale:
- xs:   12px
- sm:   14px
- base: 16px
- lg:   18px
- xl:   20px
- 2xl:  24px
- 3xl:  30px
```

### Responsive Breakpoints

```
sm:   640px   (small tablets)
md:   768px   (tablets)
lg:   1024px  (laptops)
xl:   1280px  (desktops)
2xl:  1536px  (large screens)
```

### Component States

All interactive components must have:
- **Default**: Normal state
- **Hover**: Mouse over state
- **Focus**: Keyboard focus state (visible outline)
- **Active**: Click/press state
- **Disabled**: Non-interactive state
- **Loading**: Processing state

---

## Non-Functional Requirements

### NFR1: Performance

| Metric | Target |
|--------|--------|
| Initial Page Load | < 2s |
| Time to Interactive | < 3s |
| API Response Display | < 500ms |
| WebSocket Update Latency | < 100ms |
| Table Render (100 rows) | < 200ms |
| Lighthouse Performance | > 90 |

---

### NFR2: Reliability

| Requirement | Target |
|-------------|--------|
| Error-free Session Rate | > 99% |
| WebSocket Reconnection | Auto, < 5s |
| Offline Detection | Immediate |
| Data Loss Prevention | Auto-save drafts |

---

### NFR3: Accessibility

| Requirement | Standard |
|-------------|----------|
| WCAG Compliance | Level AA |
| Keyboard Navigation | Full support |
| Screen Reader Support | Complete |
| Color Contrast | 4.5:1 minimum |
| Focus Indicators | Visible |

---

### NFR4: Browser Support

| Browser | Version |
|---------|---------|
| Chrome | Last 2 versions |
| Firefox | Last 2 versions |
| Safari | Last 2 versions |
| Edge | Last 2 versions |
| Mobile Safari | iOS 14+ |
| Chrome Mobile | Android 10+ |

---

### NFR5: Security

| Requirement | Description |
|-------------|-------------|
| XSS Prevention | Sanitize all user input |
| CSRF Protection | Token-based protection |
| Secure Token Storage | Memory only (no localStorage) |
| HTTPS Only | All API calls over HTTPS |
| Session Timeout | Auto-logout after 24h |

---

## Page Specifications

### Dashboard Page

**Route:** `/`  
**Layout:** Main with sidebar

**Components:**
- SystemStatusCard
- StatsOverview
- RecentJobsTable
- QuickActions

**Data Requirements:**
- System health from `/health/services`
- Job stats from `/jobs` with aggregation
- Recent jobs from `/jobs?limit=10`

---

### Jobs List Page

**Route:** `/jobs`  
**Layout:** Main with sidebar

**Components:**
- JobFilters
- JobTable
- Pagination
- BulkActions

**Data Requirements:**
- Jobs list from `/jobs` with filters
- Real-time updates via WebSocket

---

### Job Detail Page

**Route:** `/jobs/:jobId`  
**Layout:** Main with sidebar

**Components:**
- JobHeader
- JobProgress
- JobLog
- JobActions
- ResultsPreview

**Data Requirements:**
- Job details from `/jobs/:jobId`
- Real-time status via WebSocket `/ws/monitor/:jobId`

---

### Results Page

**Route:** `/jobs/:jobId/results`  
**Layout:** Full width

**Components:**
- ResultsHeader
- ResultsFilters
- ResultsTable (TanStack Table)
- ResultsSummary (charts)
- AIExplanation
- ExportButton

**Data Requirements:**
- Results from `/jobs/:jobId/results`
- Statistics from `/jobs/:jobId/results/stats`

---

### Create Job Page

**Route:** `/jobs/new`  
**Layout:** Centered modal/wizard

**Components:**
- StepIndicator
- ScraperTypeSelector
- FlightSearchForm / HotelSearchForm
- ConfigOptions
- ReviewSummary

**Validation:**
- Origin/Destination required for flights
- Location required for hotels
- IATA code validation
- Date format validation

---

### Settings Page

**Route:** `/settings`  
**Layout:** Main with sidebar

**Components:**
- SettingsTabs
- PreferencesForm
- SystemConfig (admin only)
- DangerZone

---

## Component Library

### Base Components (shadcn/ui)

| Component | File | Description |
|-----------|------|-------------|
| Button | `button.tsx` | Variants: default, outline, ghost |
| Input | `input.tsx` | Text input with label |
| Select | `select.tsx` | Dropdown selector |
| Table | `table.tsx` | Data table with sorting |
| Dialog | `dialog.tsx` | Modal dialogs |
| Form | `form.tsx` | Form wrapper with validation |
| Badge | `badge.tsx` | Status badges |
| Progress | `progress.tsx` | Progress bars |
| Card | `card.tsx` | Content cards |
| Tabs | `tabs.tsx` | Tab navigation |
| Toast | `toast.tsx` | Notifications |
| Avatar | `avatar.tsx` | User avatar |

### Custom Components

| Component | File | Description |
|-----------|------|-------------|
| JobCard | `jobs/JobCard.tsx` | Job summary card |
| JobStatus | `jobs/JobStatus.tsx` | Status indicator |
| JobProgress | `jobs/JobProgress.tsx` | Progress visualization |
| ResultsTable | `results/ResultsTable.tsx` | Interactive results table |
| AIExplanation | `results/AIExplanation.tsx` | AI insights display |
| ExportDialog | `export/ExportDialog.tsx` | Export configuration |
| SystemStatus | `common/SystemStatus.tsx` | Health indicator |
| SearchInput | `common/SearchInput.tsx` | Search with debounce |

---

## State Management

### Zustand Stores

#### Auth Store

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}
```

#### Job Store

```typescript
interface JobState {
  jobs: Job[];
  activeJob: Job | null;
  filters: JobFilters;
  fetchJobs: (params?: JobListParams) => Promise<void>;
  createJob: (data: CreateJobData) => Promise<Job>;
  cancelJob: (jobId: string) => Promise<void>;
  setFilters: (filters: JobFilters) => void;
}
```

#### WebSocket Store

```typescript
interface WebSocketState {
  connected: boolean;
  subscribe: (jobId: string) => void;
  unsubscribe: (jobId: string) => void;
  onJobUpdate: (callback: (update: JobUpdate) => void) => void;
}
```

### TanStack Query Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000, // 30 seconds
      retry: 2,
      refetchOnWindowFocus: true,
    },
  },
});

// Example query hooks
useQuery(['jobs', filters], () => fetchJobs(filters));
useQuery(['job', jobId], () => fetchJob(jobId));
useQuery(['results', jobId], () => fetchResults(jobId));
```

---

## API Integration

### Axios Configuration

```typescript
// src/lib/axios.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use((config) => {
  const token = authStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
```

### API Service Example

```typescript
// src/api/jobs.ts
import { apiClient } from '@/lib/axios';
import { Job, CreateJobData, JobListParams } from '@/types/job';

export const jobsApi = {
  list: async (params?: JobListParams) => {
    const { data } = await apiClient.get('/api/v1/jobs', { params });
    return data;
  },

  getById: async (jobId: string) => {
    const { data } = await apiClient.get(`/api/v1/jobs/${jobId}`);
    return data;
  },

  create: async (jobData: CreateJobData) => {
    const { data } = await apiClient.post('/api/v1/jobs', jobData);
    return data;
  },

  cancel: async (jobId: string) => {
    const { data } = await apiClient.delete(`/api/v1/jobs/${jobId}`);
    return data;
  },
};
```

### WebSocket Service

```typescript
// src/lib/websocket.ts
class WebSocketService {
  private ws: WebSocket | null = null;
  private subscribers: Map<string, Set<(data: any) => void>> = new Map();

  connect(token: string) {
    const wsUrl = `ws://localhost:8000/ws?token=${token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.notifySubscribers(message.job_id, message);
    };

    this.ws.onclose = () => {
      // Auto-reconnect
      setTimeout(() => this.connect(token), 5000);
    };
  }

  subscribe(jobId: string, callback: (data: any) => void) {
    if (!this.subscribers.has(jobId)) {
      this.subscribers.set(jobId, new Set());
    }
    this.subscribers.get(jobId)!.add(callback);
  }

  unsubscribe(jobId: string, callback: (data: any) => void) {
    this.subscribers.get(jobId)?.delete(callback);
  }

  private notifySubscribers(jobId: string, data: any) {
    this.subscribers.get(jobId)?.forEach((cb) => cb(data));
  }
}

export const wsService = new WebSocketService();
```

---

## Security Requirements

### Authentication Flow

```
┌──────────┐      ┌───────────┐      ┌──────────┐
│  Client  │      │  Frontend │      │  Backend │
└────┬─────┘      └─────┬─────┘      └────┬─────┘
     │                  │                  │
     │  Enter creds     │                  │
     │─────────────────►│                  │
     │                  │                  │
     │                  │  POST /auth/login│
     │                  │─────────────────►│
     │                  │                  │
     │                  │  JWT Token       │
     │                  │◄─────────────────│
     │                  │                  │
     │  Store in memory │                  │
     │◄─────────────────│                  │
     │                  │                  │
     │  API Request + JWT                   │
     │─────────────────────────────────────►│
     │                  │                  │
     │  Response        │                  │
     │◄─────────────────────────────────────│
     │                  │                  │
```

### Security Checklist

- [ ] JWT tokens stored in memory (not localStorage)
- [ ] HTTPS for all production API calls
- [ ] CSRF tokens for state-changing operations
- [ ] Input sanitization for all user inputs
- [ ] XSS prevention via React's built-in escaping
- [ ] Content Security Policy headers
- [ ] Session timeout after 24 hours
- [ ] Rate limiting on login attempts
- [ ] Password complexity requirements
- [ ] Secure password reset flow

---

## Deployment Strategy

### Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Access at http://localhost:5173
```

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Variables

```env
# .env.example
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_TITLE=Scraprrr
VITE_SENTRY_DSN=
```

---

## Milestones and Timeline

### Phase 1: Foundation (Weeks 1-3)

| Week | Deliverables |
|------|-------------|
| 1 | - Project setup (Vite, TypeScript)<br>- Basic routing<br>- Auth flow (login/logout) |
| 2 | - Dashboard page<br>- Job list page<br>- API integration layer |
| 3 | - Create job wizard<br>- Job detail page<br>- Basic styling |

**Milestone:** Basic job creation and viewing

---

### Phase 2: Real-time Features (Weeks 4-6)

| Week | Deliverables |
|------|-------------|
| 4 | - WebSocket integration<br>- Real-time job monitoring<br>- Progress visualization |
| 5 | - Results table<br>- Filtering and sorting<br>- Pagination |
| 6 | - Export dialog<br>- File download<br>- Database ingestion UI |

**Milestone:** Real-time monitoring and export

---

### Phase 3: Polish (Weeks 7-9)

| Week | Deliverables |
|------|-------------|
| 7 | - Results summary charts<br>- AI explanation component<br>- Settings page |
| 8 | - Responsive design<br>- Accessibility improvements<br>- Error handling |
| 9 | - Performance optimization<br>- Testing<br>- Documentation |

**Milestone:** Production-ready application

---

### Phase 4: Enhancements (Weeks 10-12)

| Week | Deliverables |
|------|-------------|
| 10-11 | - Advanced filtering<br>- Saved searches<br>- Notification system |
| 12 | - User feedback integration<br>- Bug fixes<br>- Launch preparation |

**Milestone:** Feature-complete v1.0

---

## Success Metrics

### User Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Task Completion Rate | > 90% | User testing |
| Time to First Job | < 2 min | Analytics |
| Error Rate | < 1% | Error tracking |
| User Satisfaction | > 4.5/5 | Surveys |

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Lighthouse Score | > 90 | Lighthouse CI |
| Bundle Size | < 500KB | Bundle analyzer |
| API Latency (p95) | < 500ms | Monitoring |
| WebSocket Uptime | > 99% | Connection tracking |

### Adoption Metrics (3 months)

| Metric | Target |
|--------|--------|
| Daily Active Users | 100+ |
| Jobs Created per Day | 500+ |
| Export Actions per Day | 200+ |
| Return User Rate | > 60% |

---

## Appendices

### Appendix A: API Response Examples

#### Job Creation Response

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "scraper_type": "flight",
  "parameters": {
    "origin": "CGK",
    "destination": "DPS",
    "departure_date": "2026-04-15"
  },
  "created_at": "2026-03-29T10:00:00Z",
  "estimated_start": "2026-03-29T10:00:30Z"
}
```

#### Results Response

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_results": 150,
  "page": 1,
  "page_size": 50,
  "results": [
    {
      "airline_name": "Garuda Indonesia",
      "departure_time": "08:00",
      "departure_airport": "CGK",
      "arrival_time": "10:30",
      "price": "Rp 1.500.000",
      "price_numeric": 1500000
    }
  ]
}
```

#### WebSocket Message

```json
{
  "type": "status_update",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-29T10:05:00Z",
  "data": {
    "status": "running",
    "progress": 67,
    "current_step": "Extracting flight data",
    "items_collected": 45
  }
}
```

---

### Appendix B: Component Props Examples

```typescript
// JobCard props
interface JobCardProps {
  job: Job;
  onStatusChange: (jobId: string, status: JobStatus) => void;
  onViewDetails: (jobId: string) => void;
}

// ResultsTable props
interface ResultsTableProps {
  data: Result[];
  columns: ColumnDef<Result>[];
  filters: ResultsFilters;
  onFilterChange: (filters: ResultsFilters) => void;
  onExport: (format: ExportFormat) => void;
}

// AIExplanation props
interface AIExplanationProps {
  results: Result[];
  statistics: ResultStatistics;
  isLoading?: boolean;
}
```

---

### Appendix C: Wireframes

See individual page specifications for ASCII wireframes. Full Figma designs to be created during implementation.

---

### Appendix D: Glossary

| Term | Definition |
|------|------------|
| **Job** | A single scraper execution task |
| **Scraper Type** | Type of scraper (flight, hotel, etc.) |
| **WebSocket** | Bidirectional real-time communication |
| **JWT** | JSON Web Token for authentication |
| **TanStack Query** | React library for data fetching |
| **Zustand** | Lightweight state management |
| **shadcn/ui** | Accessible UI component library |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-29 | Scraprrr Team | Initial draft |

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Tech Lead | | | |
| Design Lead | | | |
| Engineering Manager | | | |
