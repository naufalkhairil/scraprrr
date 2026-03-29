# Product Requirements Document (PRD)
# Scraprrr Web Platform - Backend API

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
5. [Current Architecture](#current-architecture)
6. [Proposed Architecture](#proposed-architecture)
7. [Functional Requirements](#functional-requirements)
8. [Non-Functional Requirements](#non-functional-requirements)
9. [API Specification](#api-specification)
10. [Database Schema](#database-schema)
11. [Security Requirements](#security-requirements)
12. [Integration Points](#integration-points)
13. [Monitoring & Observability](#monitoring--observability)
14. [Deployment Strategy](#deployment-strategy)
15. [Milestones and Timeline](#milestones-and-timeline)
16. [Success Metrics](#success-metrics)
17. [Risks and Mitigations](#risks-and-mitigations)
18. [Appendices](#appendices)

---

## Executive Summary

Scraprrr is evolving from a CLI-based web scraping tool to a comprehensive web platform that enables users to monitor, manage, and export e-commerce ticket scraping operations (flights, hotels, etc.) from platforms like Traveloka, Booking.com, and Agoda. This PRD outlines the backend architecture and API requirements to support real-time scraper monitoring, result retrieval, data export, and database integration.

### Key Value Propositions

- **Real-time Monitoring**: Dashboard API to track running scraper jobs
- **Centralized Results**: Unified API to retrieve scraping results in tabular format
- **Flexible Export**: Multiple export formats (CSV, JSON, Excel) and direct database ingestion
- **Scalable Architecture**: Support for concurrent scraping operations with job queuing
- **Enterprise Integration**: PostgreSQL integration for persistent storage and analytics

---

## Product Overview

### Problem Statement

The current Scraprrr CLI tool is effective for individual scraping tasks but lacks:
- Real-time visibility into running scrapers
- Centralized result management
- Easy data export and integration capabilities
- Multi-user access and job scheduling
- Historical data tracking and analysis

### Solution

A RESTful API backend that:
1. Manages scraper jobs via a task queue (Celery + Redis)
2. Provides WebSocket connections for real-time monitoring
3. Stores results in PostgreSQL for persistence and querying
4. Offers multiple export mechanisms (file download, direct DB insert, API streaming)
5. Integrates with existing Selenium Grid infrastructure

### Scope

**In Scope:**
- REST API for scraper management
- WebSocket API for real-time updates
- PostgreSQL database integration
- Export functionality (CSV, JSON, Excel, direct DB)
- Job queue management
- Authentication and authorization
- Admin dashboard API

**Out of Scope (Phase 1):**
- Frontend web application (API-only)
- Multi-tenant support
- Payment/billing integration
- Mobile application
- Third-party platform expansion beyond Traveloka (Phase 2)

---

## Goals and Objectives

### Primary Goals

| Goal | Description | Success Metric |
|------|-------------|----------------|
| **G1: Real-time Monitoring** | Enable users to monitor scraper progress in real-time | < 500ms latency for status updates |
| **G2: Data Accessibility** | Provide easy access to scraping results in multiple formats | Support 4+ export formats |
| **G3: Scalability** | Support concurrent scraping operations | Handle 50+ concurrent jobs |
| **G4: Persistence** | Store historical scraping data for analysis | 99.9% data durability |
| **G5: Integration** | Enable seamless integration with external systems | PostgreSQL + REST API + Webhooks |

### Key Objectives

1. **O1**: Migrate from CLI-only to API-first architecture
2. **O2**: Implement job queuing for asynchronous scraper execution
3. **O3**: Build robust result storage and retrieval system
4. **O4**: Create extensible architecture for future scraper types
5. **O5**: Ensure production-ready security and monitoring

---

## Target Users

### User Personas

#### 1. Data Analyst (Primary)
- **Needs**: Easy access to scraping results, export to analysis tools
- **Use Cases**: 
  - Monitor flight price trends
  - Export hotel data to Excel/CSV
  - Query historical data via SQL

#### 2. Developer (Primary)
- **Needs**: API integration, webhooks, custom workflows
- **Use Cases**:
  - Integrate scraping results into internal systems
  - Build custom dashboards
  - Automate data pipelines

#### 3. Operations Manager (Secondary)
- **Needs**: Monitor scraper health, manage jobs
- **Use Cases**:
  - View running jobs dashboard
  - Cancel failed jobs
  - Review success/failure rates

#### 4. System Administrator (Secondary)
- **Needs**: System health, resource management
- **Use Cases**:
  - Monitor Selenium Grid utilization
  - Manage database storage
  - Configure alerts

---

## Current Architecture

### Existing Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Scraprrr v2.0                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   CLI Layer  │  │   Core       │  │   Modules    │       │
│  │              │  │              │  │              │       │
│  │ - main.py    │  │ - base.py    │  │ - flight/    │       │
│  │ - commands/  │  │ - driver.py  │  │ - hotel/     │       │
│  │ - parsers/   │  │ - utils.py   │  │   models.py  │       │
│  │              │  │              │  │   scraper.py │       │
│  │              │  │              │  │   page.py    │       │
│  │              │  │              │  │   extractor.py│      │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  Dependencies: Selenium, Pandas, Pydantic, Requests         │
│  Infrastructure: Docker Selenium Grid                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Current Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.9+ |
| Browser Automation | Selenium | 4.15.0+ |
| Data Processing | Pandas | 2.0.0+ |
| Validation | Pydantic | 2.0.0+ |
| Containerization | Docker | Latest |
| Selenium Grid | Docker Selenium | Latest |

### Current Project Structure

```
scraprrr/
├── src/scraprrr/
│   ├── __init__.py              # Public API exports
│   ├── cli/                     # Command-line interface
│   │   ├── main.py
│   │   ├── commands/
│   │   └── parsers/
│   ├── core/                    # Shared infrastructure
│   │   ├── base.py
│   │   ├── driver.py
│   │   └── utils.py
│   └── modules/                 # Domain-specific scrapers
│       ├── flight/
│       └── hotel/
├── tests/
├── docker/selenium-grid/
└── results/
```

---

## Proposed Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Scraprrr Web Platform                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         API Gateway                               │   │
│  │                    (FastAPI Application)                          │   │
│  │                                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │   │
│  │  │   REST API  │  │  WebSocket  │  │      Background         │   │   │
│  │  │  Endpoints  │  │   Server    │  │       Tasks             │   │   │
│  │  │             │  │             │  │      (Celery)           │   │   │
│  │  │ - /jobs     │  │ - /ws/      │  │                         │   │   │
│  │  │ - /results  │  │   monitor/  │  │  - Scraper tasks        │   │   │
│  │  │ - /export   │  │   {job_id}  │  │  - Export tasks         │   │   │
│  │  │ - /health   │  │             │  │  - DB ingestion         │   │   │
│  │  └─────────────┘  └─────────────┘  └───────────┬─────────────┘   │   │
│  └─────────────────────────────────────────────────┼─────────────────┘   │
│                                                     │                      │
│                    ┌────────────────────────────────┼────────────────┐    │
│                    │                 │              │                │    │
│                    ▼                 ▼              ▼                ▼    │
│           ┌─────────────┐   ┌─────────────┐  ┌──────────┐   ┌──────────┐ │
│           │   Redis     │   │  PostgreSQL │  │ Selenium │   │   File   │ │
│           │   (Broker   │   │  (Results   │  │   Grid   │   │  Storage │ │
│           │    + Cache) │   │   + Meta)   │  │ (Docker) │   │  (S3/    │ │
│           │             │   │             │  │          │   │   Local) │ │
│           └─────────────┘   └─────────────┘  └──────────┘   └──────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
scraprrr/
├── src/scraprrr/
│   ├── __init__.py
│   │
│   ├── api/                          # NEW: API Layer
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application
│   │   ├── config.py                 # API configuration
│   │   │
│   │   ├── routes/                   # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py               # Job management endpoints
│   │   │   ├── results.py            # Results retrieval endpoints
│   │   │   ├── export.py             # Export functionality
│   │   │   ├── health.py             # Health check endpoints
│   │   │   └── admin.py              # Admin operations
│   │   │
│   │   ├── websocket/                # WebSocket handlers
│   │   │   ├── __init__.py
│   │   │   ├── manager.py            # Connection manager
│   │   │   └── handlers.py           # Message handlers
│   │   │
│   │   ├── middleware/               # Custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication
│   │   │   ├── logging.py            # Request logging
│   │   │   └── cors.py               # CORS configuration
│   │   │
│   │   └── schemas/                  # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── job.py                # Job request/response schemas
│   │       ├── result.py             # Result schemas
│   │       └── export.py             # Export schemas
│   │
│   ├── services/                     # NEW: Business Logic Layer
│   │   ├── __init__.py
│   │   ├── job_service.py            # Job management logic
│   │   ├── result_service.py         # Result retrieval logic
│   │   ├── export_service.py         # Export logic
│   │   ├── scraper_service.py        # Scraper orchestration
│   │   └── database_service.py       # Database operations
│   │
│   ├── tasks/                        # NEW: Background Tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py             # Celery configuration
│   │   ├── scraper_tasks.py          # Scraper Celery tasks
│   │   ├── export_tasks.py           # Export Celery tasks
│   │   └── db_tasks.py               # Database ingestion tasks
│   │
│   ├── models/                       # NEW: Database Models
│   │   ├── __init__.py
│   │   ├── base.py                   # Base model class
│   │   ├── job.py                    # Job model
│   │   ├── result.py                 # Result model
│   │   └── user.py                   # User model (future)
│   │
│   ├── db/                           # NEW: Database Layer
│   │   ├── __init__.py
│   │   ├── session.py                # DB session management
│   │   ├── crud.py                   # CRUD operations
│   │   └── migrations/               # Alembic migrations
│   │
│   ├── core/                         # EXISTING: Enhanced
│   │   ├── __init__.py
│   │   ├── base.py                   # Base scraper class
│   │   ├── driver.py                 # WebDriver management
│   │   ├── utils.py                  # Common utilities
│   │   └── config.py                 # Core configuration
│   │
│   ├── modules/                      # EXISTING: Scraper modules
│   │   ├── __init__.py
│   │   ├── flight/
│   │   └── hotel/
│   │
│   └── cli/                          # EXISTING: CLI (backward compatible)
│       ├── __init__.py
│       ├── main.py
│       ├── commands/
│       └── parsers/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/                     # NEW: API tests
│   ├── test_services/                # NEW: Service tests
│   ├── test_tasks/                   # NEW: Task tests
│   └── test_models/                  # NEW: Model tests
│
├── docker/
│   ├── selenium-grid/
│   ├── api/                          # NEW: API Dockerfile
│   ├── worker/                       # NEW: Worker Dockerfile
│   └── docker-compose.yml            # NEW: Full stack compose
│
├── alembic.ini                       # NEW: Migration config
└── pyproject.toml                    # UPDATED: New dependencies
```

### Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **API Framework** | FastAPI | Async support, auto docs, Pydantic integration |
| **Task Queue** | Celery + Redis | Mature, scalable, Python-native |
| **Database** | PostgreSQL 15+ | Robust, ACID-compliant, JSON support |
| **ORM** | SQLAlchemy 2.0 | Async support, type hints, mature |
| **Migrations** | Alembic | SQLAlchemy-native migration tool |
| **WebSocket** | FastAPI WebSocket | Native async support |
| **Authentication** | JWT + OAuth2 | Industry standard, stateless |
| **Caching** | Redis | Fast, supports pub/sub for WebSocket |
| **Containerization** | Docker + Compose | Consistent environments |
| **Monitoring** | Prometheus + Grafana | Industry standard metrics |

### New Dependencies

```python
# API & Web
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0

# Task Queue
celery>=5.3.0
redis>=5.0.0

# Database
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.12.0
psycopg2-binary>=2.9.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# Export
openpyxl>=3.1.0  # Excel support

# Monitoring
prometheus-client>=0.19.0

# Testing (enhanced)
pytest-asyncio>=0.21.0
httpx>=0.25.0  # Async HTTP client for API tests
```

---

## Functional Requirements

### FR1: Job Management

#### FR1.1: Create Scraper Job
**Description:** Users can create new scraper jobs via API  
**Priority:** P0

**Acceptance Criteria:**
- [ ] POST `/api/v1/jobs` endpoint accepts scraper parameters
- [ ] Job is queued to Celery with unique job ID
- [ ] Response includes job ID, status, and estimated start time
- [ ] Job parameters are validated before queuing
- [ ] Duplicate job detection (optional deduplication)

**API Example:**
```http
POST /api/v1/jobs
Content-Type: application/json

{
  "scraper_type": "flight",
  "parameters": {
    "origin": "CGK",
    "destination": "DPS",
    "departure_date": "2026-04-15"
  },
  "config": {
    "save_to_db": true,
    "export_format": ["csv", "json"]
  }
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "scraper_type": "flight",
  "created_at": "2026-03-29T10:00:00Z",
  "estimated_start": "2026-03-29T10:00:30Z"
}
```

---

#### FR1.2: Get Job Status
**Description:** Users can retrieve the status of a scraper job  
**Priority:** P0

**Acceptance Criteria:**
- [ ] GET `/api/v1/jobs/{job_id}` returns current job status
- [ ] Status includes: queued, running, completed, failed, cancelled
- [ ] Response includes progress percentage for running jobs
- [ ] Response includes error message for failed jobs
- [ ] Response includes result summary for completed jobs

**Response Example:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 45,
  "scraper_type": "flight",
  "created_at": "2026-03-29T10:00:00Z",
  "started_at": "2026-03-29T10:00:25Z",
  "current_step": "Extracting flight data",
  "items_collected": 23
}
```

---

#### FR1.3: List Jobs
**Description:** Users can list all jobs with filtering and pagination  
**Priority:** P1

**Acceptance Criteria:**
- [ ] GET `/api/v1/jobs` supports pagination (page, page_size)
- [ ] Filter by status: `?status=running`
- [ ] Filter by scraper type: `?scraper_type=flight`
- [ ] Filter by date range: `?from=2026-03-01&to=2026-03-31`
- [ ] Sort by created_at, status, or scraper_type
- [ ] Response includes total count and page info

---

#### FR1.4: Cancel Job
**Description:** Users can cancel a running or queued job  
**Priority:** P1

**Acceptance Criteria:**
- [ ] DELETE `/api/v1/jobs/{job_id}` cancels the job
- [ ] Cancellation is graceful (cleanup resources)
- [ ] Cannot cancel completed/failed jobs
- [ ] WebSocket notifies clients of cancellation
- [ ] Job status updates to "cancelled"

---

### FR2: Real-time Monitoring

#### FR2.1: WebSocket Connection
**Description:** Clients can connect via WebSocket for real-time updates  
**Priority:** P0

**Acceptance Criteria:**
- [ ] WebSocket endpoint: `ws://api/ws/monitor/{job_id}`
- [ ] Connection authentication via JWT token
- [ ] Automatic reconnection on disconnect
- [ ] Heartbeat/ping-pong for connection health
- [ ] Connection manager tracks active connections

**Connection Example:**
```javascript
const ws = new WebSocket(
  'ws://api/ws/monitor/550e8400-e29b-41d4-a716-446655440000?token=eyJ...'
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

---

#### FR2.2: Real-time Status Updates
**Description:** WebSocket pushes status updates to connected clients  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Push update on status change (queued → running → completed)
- [ ] Push progress updates every 5 seconds for running jobs
- [ ] Push error notifications immediately on failure
- [ ] Include job metadata in each update
- [ ] Support broadcast to multiple clients

**Message Format:**
```json
{
  "type": "status_update",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-29T10:05:00Z",
  "data": {
    "status": "running",
    "progress": 67,
    "current_step": "Saving results to database",
    "items_collected": 45
  }
}
```

---

#### FR2.3: Job Metrics Streaming
**Description:** Stream real-time metrics during job execution  
**Priority:** P2

**Acceptance Criteria:**
- [ ] Stream items/sec rate
- [ ] Stream success/failure counts
- [ ] Stream Selenium Grid utilization
- [ ] Stream memory/CPU usage (if available)

---

### FR3: Results Retrieval

#### FR3.1: Get Job Results
**Description:** Retrieve results for a completed job  
**Priority:** P0

**Acceptance Criteria:**
- [ ] GET `/api/v1/jobs/{job_id}/results` returns results
- [ ] Support pagination for large result sets
- [ ] Return results in JSON format by default
- [ ] Include metadata (total count, job info)
- [ ] Return 404 if job not found or not completed

**Response Example:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_results": 150,
  "page": 1,
  "page_size": 50,
  "total_pages": 3,
  "results": [
    {
      "airline_name": "Garuda Indonesia",
      "departure_time": "08:00",
      "departure_airport": "CGK",
      "arrival_time": "10:30",
      "arrival_airport": "DPS",
      "duration": "2h 30m",
      "price": "Rp 1.500.000",
      "price_numeric": 1500000,
      "extracted_at": "2026-03-29T10:05:00Z"
    }
    // ... more results
  ]
}
```

---

#### FR3.2: Results Filtering and Sorting
**Description:** Filter and sort results via query parameters  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Filter by price range: `?min_price=1000000&max_price=3000000`
- [ ] Filter by airline: `?airline=Garuda Indonesia`
- [ ] Filter by departure time: `?departure_after=06:00`
- [ ] Sort by price, duration, departure_time
- [ ] Support multiple sort fields

**Example:**
```http
GET /api/v1/jobs/{job_id}/results?min_price=1000000&max_price=3000000&sort=price&order=asc
```

---

#### FR3.3: Results Aggregation
**Description:** Get aggregated statistics for job results  
**Priority:** P2

**Acceptance Criteria:**
- [ ] GET `/api/v1/jobs/{job_id}/results/stats` returns statistics
- [ ] Include: min/max/avg price, total count, airline distribution
- [ ] Include: price trends over time (for historical jobs)
- [ ] Cache aggregation results for performance

**Response Example:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "statistics": {
    "total_results": 150,
    "price": {
      "min": 950000,
      "max": 3500000,
      "avg": 1850000,
      "median": 1750000
    },
    "airlines": {
      "Garuda Indonesia": 45,
      "Lion Air": 38,
      "AirAsia": 32,
      "Citilink": 35
    },
    "duration": {
      "min_minutes": 150,
      "max_minutes": 300,
      "avg_minutes": 185
    }
  }
}
```

---

### FR4: Export Functionality

#### FR4.1: Export to File
**Description:** Export job results to downloadable files  
**Priority:** P0

**Acceptance Criteria:**
- [ ] POST `/api/v1/jobs/{job_id}/export` initiates export
- [ ] Support formats: CSV, JSON, Excel (XLSX)
- [ ] Export runs asynchronously (Celery task)
- [ ] File stored in configurable storage (local/S3)
- [ ] GET `/api/v1/jobs/{job_id}/export/{export_id}` downloads file
- [ ] Files expire after configurable TTL (default: 7 days)

**Export Request:**
```json
{
  "format": "csv",
  "options": {
    "include_headers": true,
    "delimiter": ",",
    "encoding": "utf-8"
  }
}
```

**Export Response:**
```json
{
  "export_id": "exp_550e8400-e29b-41d4-a716-446655440001",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "format": "csv",
  "status": "processing",
  "created_at": "2026-03-29T10:10:00Z",
  "expires_at": "2026-04-05T10:10:00Z"
}
```

---

#### FR4.2: Export to PostgreSQL
**Description:** Ingest job results directly into PostgreSQL database  
**Priority:** P0

**Acceptance Criteria:**
- [ ] POST `/api/v1/jobs/{job_id}/ingest` initiates database ingestion
- [ ] Configurable table name (default: auto-generated)
- [ ] Support upsert (update existing records by unique key)
- [ ] Support append (always insert new records)
- [ ] Validate schema before ingestion
- [ ] Return ingestion statistics (inserted, updated, failed)
- [ ] Track ingestion history in `ingestion_logs` table

**Ingest Request:**
```json
{
  "table_name": "flight_prices_cgk_dps",
  "mode": "upsert",
  "unique_key": ["airline_name", "departure_time", "price"],
  "create_if_not_exists": true
}
```

**Ingest Response:**
```json
{
  "ingestion_id": "ing_550e8400-e29b-41d4-a716-446655440001",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "table_name": "flight_prices_cgk_dps",
  "status": "completed",
  "statistics": {
    "inserted": 145,
    "updated": 5,
    "failed": 0,
    "total": 150
  },
  "completed_at": "2026-03-29T10:12:00Z"
}
```

---

#### FR4.3: Scheduled Exports
**Description:** Configure automatic periodic exports  
**Priority:** P2

**Acceptance Criteria:**
- [ ] POST `/api/v1/jobs/{job_id}/exports/schedule` creates schedule
- [ ] Support cron-like scheduling (e.g., "0 9 * * *" for daily at 9 AM)
- [ ] Support multiple export targets (file + DB)
- [ ] Pause/resume schedules
- [ ] Track execution history

---

### FR5: Database Integration

#### FR5.1: PostgreSQL Schema Management
**Description:** Manage database schema for scraped data  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Auto-create tables based on scraper type
- [ ] Support custom table schemas via API
- [ ] Track schema versions
- [ ] Migration support via Alembic

**Default Tables:**
```sql
-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    scraper_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    parameters JSONB,
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Results table (generic)
CREATE TABLE results (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Ingestion logs
CREATE TABLE ingestion_logs (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    table_name VARCHAR(255),
    mode VARCHAR(20),
    status VARCHAR(20),
    statistics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

#### FR5.2: Query API for Database Results
**Description:** Query ingested data via SQL-like API  
**Priority:** P1

**Acceptance Criteria:**
- [ ] POST `/api/v1/data/query` accepts SQL queries
- [ ] Whitelist allowed tables
- [ ] Limit query complexity (max rows, no DROP/DELETE)
- [ ] Return results in JSON format
- [ ] Support parameterized queries (prevent SQL injection)

**Query Example:**
```json
{
  "table": "flight_prices_cgk_dps",
  "select": ["airline_name", "AVG(price) as avg_price"],
  "where": {
    "departure_date": {"gte": "2026-04-01"}
  },
  "group_by": ["airline_name"],
  "limit": 100
}
```

---

#### FR5.3: Data Retention Policies
**Description:** Configure automatic data cleanup  
**Priority:** P2

**Acceptance Criteria:**
- [ ] Configure retention period per table
- [ ] Automatic deletion of old data
- [ ] Archive option (move to cold storage)
- [ ] Manual cleanup API endpoint

---

### FR6: Authentication & Authorization

#### FR6.1: User Authentication
**Description:** Authenticate users via JWT  
**Priority:** P0

**Acceptance Criteria:**
- [ ] POST `/api/v1/auth/login` returns JWT token
- [ ] Token expiration (default: 24 hours)
- [ ] Refresh token support
- [ ] API key authentication for service accounts

---

#### FR6.2: Role-Based Access Control
**Description:** Restrict access based on user roles  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Roles: admin, user, readonly
- [ ] Admin: full access to all endpoints
- [ ] User: create/manage own jobs
- [ ] Readonly: view jobs and results only
- [ ] Endpoint-level permission checks

---

### FR7: Health & Monitoring

#### FR7.1: Health Check Endpoints
**Description:** Monitor API and service health  
**Priority:** P0

**Acceptance Criteria:**
- [ ] GET `/health/live` - liveness probe (always returns 200 if running)
- [ ] GET `/health/ready` - readiness probe (checks dependencies)
- [ ] GET `/health/services` - detailed service status
- [ ] Include: DB connection, Redis, Celery workers, Selenium Grid

**Response Example:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-29T10:15:00Z",
  "services": {
    "database": {"status": "up", "latency_ms": 12},
    "redis": {"status": "up", "latency_ms": 3},
    "celery_workers": {"status": "up", "active_workers": 4},
    "selenium_grid": {"status": "up", "available_nodes": 5}
  }
}
```

---

#### FR7.2: Metrics Endpoint
**Description:** Expose Prometheus-compatible metrics  
**Priority:** P1

**Acceptance Criteria:**
- [ ] GET `/metrics` returns Prometheus format metrics
- [ ] Track: request count, latency, error rate
- [ ] Track: job queue length, processing time
- [ ] Track: Selenium Grid utilization
- [ ] Track: database connection pool stats

---

## Non-Functional Requirements

### NFR1: Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | < 200ms | All endpoints except export |
| WebSocket Latency | < 100ms | Status update delivery |
| Job Queue Throughput | 100 jobs/min | Celery task processing |
| Database Query Time (p95) | < 500ms | Result retrieval queries |
| Export Generation Time | < 30s | For 10K results |
| Concurrent Users | 100+ | Simultaneous API clients |
| Concurrent Jobs | 50+ | Parallel scraper execution |

---

### NFR2: Scalability

| Requirement | Description |
|-------------|-------------|
| Horizontal Scaling | API can scale horizontally behind load balancer |
| Worker Scaling | Celery workers can auto-scale based on queue length |
| Database Scaling | Support read replicas for query-heavy workloads |
| Selenium Grid Scaling | Support 20+ concurrent browser instances |

---

### NFR3: Reliability

| Requirement | Target |
|-------------|--------|
| API Uptime | 99.9% (excluding scheduled maintenance) |
| Job Success Rate | > 95% (excluding website changes) |
| Data Durability | 99.99% (no data loss) |
| Recovery Time Objective (RTO) | < 1 hour |
| Recovery Point Objective (RPO) | < 5 minutes |

---

### NFR4: Security

| Requirement | Description |
|-------------|-------------|
| Authentication | JWT-based authentication for all endpoints |
| Authorization | RBAC with least-privilege principle |
| Data Encryption | TLS 1.3 for data in transit |
| Secrets Management | Environment variables + Docker secrets |
| Input Validation | Pydantic validation for all inputs |
| SQL Injection Prevention | Parameterized queries, ORM usage |
| Rate Limiting | Configurable rate limits per endpoint |
| Audit Logging | Log all authentication and data modification events |

---

### NFR5: Maintainability

| Requirement | Description |
|-------------|-------------|
| Code Coverage | > 80% test coverage |
| API Documentation | Auto-generated OpenAPI/Swagger docs |
| Logging | Structured JSON logging with correlation IDs |
| Monitoring | Prometheus metrics + Grafana dashboards |
| CI/CD | Automated testing and deployment pipeline |
| Documentation | Comprehensive API docs and runbooks |

---

### NFR6: Compliance

| Requirement | Description |
|-------------|-------------|
| GDPR | Support data deletion requests |
| Robots.txt | Respect target website robots.txt |
| Terms of Service | Comply with Traveloka ToS |
| Rate Limiting | Implement respectful scraping rates |

---

## API Specification

### Base URL

```
Production: https://api.scraprrr.com/v1
Staging: https://api-staging.scraprrr.com/v1
Local: http://localhost:8000/v1
```

### Authentication

All endpoints (except health checks) require authentication via:
- **Bearer Token**: `Authorization: Bearer <jwt_token>`
- **API Key**: `X-API-Key: <api_key>` (for service accounts)

### Endpoints Summary

#### Jobs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/jobs` | Create new job | Yes |
| GET | `/jobs` | List jobs | Yes |
| GET | `/jobs/{job_id}` | Get job details | Yes |
| DELETE | `/jobs/{job_id}` | Cancel job | Yes |
| GET | `/jobs/{job_id}/status` | Get job status | Yes |

#### Results

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/jobs/{job_id}/results` | Get job results | Yes |
| GET | `/jobs/{job_id}/results/stats` | Get result statistics | Yes |
| POST | `/jobs/{job_id}/results/query` | Query results | Yes |

#### Export

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/jobs/{job_id}/export` | Export to file | Yes |
| GET | `/exports/{export_id}` | Get export status | Yes |
| GET | `/exports/{export_id}/download` | Download file | Yes |
| POST | `/jobs/{job_id}/ingest` | Ingest to database | Yes |
| GET | `/ingestions/{ingestion_id}` | Get ingestion status | Yes |

#### WebSocket

| Endpoint | Description | Auth Required |
|----------|-------------|---------------|
| `ws://api/ws/monitor/{job_id}` | Real-time job monitoring | Yes |
| `ws://api/ws/jobs` | Job list updates | Yes |

#### Health & Monitoring

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health/live` | Liveness probe | No |
| GET | `/health/ready` | Readiness probe | No |
| GET | `/health/services` | Service health | Yes |
| GET | `/metrics` | Prometheus metrics | No (internal only) |

#### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | Get JWT token | No |
| POST | `/auth/refresh` | Refresh token | Yes |
| POST | `/auth/logout` | Invalidate token | Yes |

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│       jobs          │       │       users         │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ user_id (FK)        │◄──────│ email               │
│ scraper_type        │       │ password_hash       │
│ status              │       │ role                │
│ parameters (JSONB)  │       │ created_at          │
│ config (JSONB)      │       │ updated_at          │
│ created_at          │       └─────────────────────┘
│ started_at          │
│ completed_at        │              │
│ error_message       │              │
└─────────────────────┘              │
          │                          │
          │                          │
          ▼                          ▼
┌─────────────────────┐       ┌─────────────────────┐
│      results        │       │    api_keys         │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ job_id (FK)         │       │ user_id (FK)        │
│ data (JSONB)        │       │ key_hash            │
│ created_at          │       │ name                │
└─────────────────────┘       │ expires_at          │
          │                   │ created_at          │
          │                   └─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   ingestion_logs    │
├─────────────────────┤
│ id (PK)             │
│ job_id (FK)         │
│ table_name          │
│ mode                │
│ status              │
│ statistics (JSONB)  │
│ created_at          │
└─────────────────────┘
```

### Table Definitions

See Appendix A for complete DDL statements.

---

## Security Requirements

### Authentication Flow

```
┌──────────┐      ┌───────────┐      ┌──────────┐
│  Client  │      │  Auth API │      │  Redis   │
└────┬─────┘      └─────┬─────┘      └────┬─────┘
     │                  │                  │
     │  POST /auth/login│                  │
     │─────────────────►│                  │
     │  {email, pass}   │                  │
     │                  │                  │
     │                  │  Validate creds   │
     │                  │─────────────────►│
     │                  │                  │
     │                  │  Generate JWT     │
     │                  │◄─────────────────│
     │                  │                  │
     │  JWT Token       │                  │
     │◄─────────────────│                  │
     │                  │                  │
     │  Request + JWT   │                  │
     │─────────────────►│                  │
     │                  │                  │
     │                  │  Verify JWT       │
     │                  │─────────────────►│
     │                  │                  │
     │  Response        │                  │
     │◄─────────────────│                  │
     │                  │                  │
```

### Security Checklist

- [ ] JWT tokens with short expiration (24h)
- [ ] Refresh token rotation
- [ ] Password hashing with bcrypt (cost factor 12)
- [ ] HTTPS everywhere (TLS 1.3)
- [ ] CORS configuration for allowed origins
- [ ] Rate limiting (100 req/min default)
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (ORM + parameterized queries)
- [ ] XSS prevention (Content-Security-Policy headers)
- [ ] CSRF protection for state-changing operations
- [ ] Secrets in environment variables (not in code)
- [ ] Audit logging for sensitive operations
- [ ] Regular security dependency updates

---

## Integration Points

### External Systems

```
┌─────────────────────────────────────────────────────────────┐
│                     Scraprrr Platform                        │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │  Selenium Grid  │ │  External APIs  │
│   (Database)    │ │  (Browsers)     │ │  (Webhooks)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  BI Tools       │ │  Docker         │  │  Client Apps   │
│  (Tableau,      │ │  Compose        │ │  (Frontend,    │
│   PowerBI)      │ │  Kubernetes     │ │   Mobile)      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Webhook Integration

**Priority:** P2

Support outbound webhooks for job completion:

```json
{
  "event": "job.completed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-29T10:15:00Z",
  "data": {
    "status": "completed",
    "total_results": 150,
    "result_url": "/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/results"
  }
}
```

---

## Monitoring & Observability

### Logging Strategy

| Level | Description | Example |
|-------|-------------|---------|
| ERROR | System errors, failures | "Database connection failed" |
| WARN | Recoverable issues | "Job retry attempt 2/3" |
| INFO | Business events | "Job created", "Export completed" |
| DEBUG | Detailed debugging | "WebDriver initialized" |

**Log Format:**
```json
{
  "timestamp": "2026-03-29T10:00:00Z",
  "level": "INFO",
  "service": "scraprrr-api",
  "trace_id": "abc123",
  "span_id": "def456",
  "message": "Job created successfully",
  "context": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_123",
    "scraper_type": "flight"
  }
}
```

### Metrics Dashboard

**Key Dashboards:**

1. **API Performance**
   - Request rate (req/s)
   - Response time (p50, p95, p99)
   - Error rate (%)
   - Endpoint breakdown

2. **Job Processing**
   - Queue length
   - Processing time distribution
   - Success/failure rate
   - Worker utilization

3. **Selenium Grid**
   - Active sessions
   - Node utilization
   - Browser errors
   - Session duration

4. **Database**
   - Connection pool usage
   - Query latency
   - Transaction rate
   - Storage growth

### Alerting Rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| API Down | Health check fails | Critical | Page on-call |
| High Error Rate | > 5% errors in 5min | High | Investigate logs |
| Queue Backlog | Queue > 100 jobs | Medium | Scale workers |
| Selenium Grid Full | No available nodes | Medium | Scale grid |
| Database Slow | Query p95 > 1s | Medium | Optimize queries |
| Disk Space Low | > 80% usage | Low | Cleanup/expand |

---

## Deployment Strategy

### Environment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Production                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   API       │  │   Worker    │  │   Worker    │         │
│  │  (x3 pods)  │  │  (x4 pods)  │  │  (x4 pods)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│         ┌────────────────┼────────────────┐                 │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Redis     │  │  PostgreSQL │  │ Selenium    │         │
│  │  (Cluster)  │  │  (Primary + │  │   Grid      │         │
│  │             │  │   Replica)  │  │  (10 nodes) │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Options

#### Option 1: Docker Compose (Development/Small Scale)

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./docker/api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/scraprrr
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  worker:
    build: ./docker/worker
    deploy:
      replicas: 4
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/scraprrr
      - REDIS_URL=redis://redis:6379
      - SELENIUM_URL=http://selenium-hub:4444/wd/hub

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  selenium-hub:
    image: selenium/hub:latest
    ports:
      - "4444:4444"

  selenium-node:
    image: selenium/node-chrome:latest
    deploy:
      replicas: 5
```

#### Option 2: Kubernetes (Production)

See Appendix B for Kubernetes manifests.

### CI/CD Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Push   │───►│  Build   │───►│   Test   │───►│  Deploy  │
│  (Git)   │    │  (Docker)│    │ (pytest) │    │ (K8s)    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │               │               │               │
     ▼               ▼               ▼               ▼
  GitHub        Docker Hub      Coverage       Staging
  Actions         Registry        Report        (Auto)
                                                      │
                                                      │ Manual
                                                      ▼
                                                 Production
```

---

## Milestones and Timeline

### Phase 1: Foundation (Weeks 1-4)

| Week | Deliverables |
|------|-------------|
| 1 | - Project scaffolding<br>- FastAPI setup<br>- Basic job endpoints |
| 2 | - Celery integration<br>- Redis setup<br>- Scraper task implementation |
| 3 | - PostgreSQL integration<br>- SQLAlchemy models<br>- Result storage |
| 4 | - WebSocket implementation<br>- Real-time status updates<br>- Basic monitoring |

**Milestone:** MVP with job creation, monitoring, and result retrieval

---

### Phase 2: Export & Integration (Weeks 5-7)

| Week | Deliverables |
|------|-------------|
| 5 | - File export (CSV, JSON, Excel)<br>- Download endpoints |
| 6 | - PostgreSQL ingestion<br>- Schema management<br>- Query API |
| 7 | - Authentication (JWT)<br>- RBAC<br>- API documentation |

**Milestone:** Full export functionality with database integration

---

### Phase 3: Production Readiness (Weeks 8-10)

| Week | Deliverables |
|------|-------------|
| 8 | - Health checks<br>- Prometheus metrics<br>- Logging improvements |
| 9 | - Docker Compose setup<br>- Kubernetes manifests<br>- CI/CD pipeline |
| 10 | - Load testing<br>- Security audit<br>- Documentation |

**Milestone:** Production-ready deployment

---

### Phase 4: Enhancements (Weeks 11-14)

| Week | Deliverables |
|------|-------------|
| 11-12 | - Scheduled exports<br>- Webhook integration<br>- Advanced filtering |
| 13-14 | - Performance optimization<br>- Caching layer<br>- Admin dashboard API |

**Milestone:** Feature-complete platform

---

## Success Metrics

### Key Performance Indicators (KPIs)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| API Uptime | N/A | 99.9% | Uptime monitoring |
| Job Success Rate | N/A | > 95% | Job completion tracking |
| Average Response Time | N/A | < 200ms | Prometheus metrics |
| User Satisfaction | N/A | > 4.5/5 | User surveys |
| Time to First Job | N/A | < 5 min | Onboarding metrics |

### Adoption Metrics

| Metric | Target (3 months) |
|--------|-------------------|
| Daily Active Users | 50+ |
| Jobs per Day | 500+ |
| API Calls per Day | 10,000+ |
| Data Exported per Day | 100 MB+ |

---

## Risks and Mitigations

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Website structure changes break scrapers | High | High | - Modular scraper architecture<br>- Automated detection<br>- Quick update process |
| Selenium Grid performance issues | Medium | Medium | - Horizontal scaling<br>- Connection pooling<br>- Fallback mechanisms |
| Database performance degradation | Medium | High | - Query optimization<br>- Indexing strategy<br>- Read replicas |
| Security vulnerabilities | Low | High | - Regular audits<br>- Dependency updates<br>- Penetration testing |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Insufficient monitoring | Medium | Medium | - Comprehensive metrics<br>- Alerting setup<br>- Runbook documentation |
| Scaling challenges | Medium | Medium | - Load testing<br>- Auto-scaling configuration<br>- Capacity planning |
| Data loss | Low | High | - Regular backups<br>- Point-in-time recovery<br>- Replication |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Terms of Service violations | Medium | High | - Legal review<br>- Respectful scraping<br>- Rate limiting |
| Low adoption | Medium | Medium | - User feedback loops<br>- Documentation<br>- Support channels |

---

## Appendices

### Appendix A: Database DDL

```sql
-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    scraper_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    parameters JSONB NOT NULL,
    config JSONB,
    progress INTEGER DEFAULT 0,
    current_step VARCHAR(255),
    items_collected INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_user_id ON jobs(user_id);

-- Results table
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_results_job_id ON results(job_id);
CREATE INDEX idx_results_data ON results USING GIN(data);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- Ingestion logs table
CREATE TABLE ingestion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    table_name VARCHAR(255) NOT NULL,
    mode VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    statistics JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Export logs table
CREATE TABLE export_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    format VARCHAR(20) NOT NULL,
    storage_path VARCHAR(500),
    status VARCHAR(20) NOT NULL,
    file_size_bytes BIGINT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

### Appendix B: Kubernetes Manifests (Sample)

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scraprrr-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: scraprrr-api
  template:
    metadata:
      labels:
        app: scraprrr-api
    spec:
      containers:
      - name: api
        image: scraprrr/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: scraprrr-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis:6379"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
# api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: scraprrr-api
spec:
  selector:
    app: scraprrr-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

### Appendix C: API Usage Examples

#### Python Client Example

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000/v1"

async def create_and_monitor_job():
    async with httpx.AsyncClient() as client:
        # Login
        auth_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "user@example.com", "password": "password"}
        )
        token = auth_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create job
        job_response = await client.post(
            f"{BASE_URL}/jobs",
            headers=headers,
            json={
                "scraper_type": "flight",
                "parameters": {
                    "origin": "CGK",
                    "destination": "DPS",
                    "departure_date": "2026-04-15"
                }
            }
        )
        job_id = job_response.json()["job_id"]
        
        # Monitor via polling
        while True:
            status_response = await client.get(
                f"{BASE_URL}/jobs/{job_id}",
                headers=headers
            )
            status = status_response.json()
            
            if status["status"] == "completed":
                # Get results
                results_response = await client.get(
                    f"{BASE_URL}/jobs/{job_id}/results",
                    headers=headers
                )
                results = results_response.json()
                print(f"Found {results['total_results']} flights")
                break
            
            await asyncio.sleep(2)

asyncio.run(create_and_monitor_job())
```

---

### Appendix D: Glossary

| Term | Definition |
|------|------------|
| **Job** | A single scraper execution task |
| **Scraper Type** | Type of scraper (flight, hotel, etc.) |
| **Celery** | Distributed task queue system |
| **WebSocket** | Bidirectional communication protocol |
| **RBAC** | Role-Based Access Control |
| **JWT** | JSON Web Token |
| **JSONB** | PostgreSQL binary JSON type |
| **RTO** | Recovery Time Objective |
| **RPO** | Recovery Point Objective |

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
| Engineering Manager | | | |
