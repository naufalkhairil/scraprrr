import React, { useState } from 'react';
import { Container, Row, Col, Tab, Nav, Alert, Button } from 'react-bootstrap';
import { FaPlane, FaHotel, FaBug } from 'react-icons/fa';
import { FlightSearchForm } from '@/components/FlightSearchForm';
import { HotelSearchForm } from '@/components/HotelSearchForm';
import { JobMonitor } from '@/components/JobMonitor';
import { SessionManager } from '@/services/api';
import { useScraper } from '@/hooks/useScraper';
import { useJobPolling } from '@/hooks/useJobPolling';
import type { FlightSearchRequest, HotelSearchRequest } from '@/types/api';

export const HomePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'flights' | 'hotels'>('flights');
  const [showDebug, setShowDebug] = useState(false);
  const { currentJob, isLoading, error, startFlightSearch, startHotelSearch, clearCurrentJob } =
    useScraper();

  const { job, cancelJob } = useJobPolling(currentJob);

  const sessionId = SessionManager.getId();

  const handleFlightSearch = async (request: FlightSearchRequest) => {
    try {
      console.log('[HomePage] Starting flight search:', request);
      await startFlightSearch(request);
      console.log('[HomePage] Flight search started, job:', currentJob);
    } catch (err) {
      console.error('[HomePage] Flight search failed:', err);
    }
  };

  const handleHotelSearch = async (request: HotelSearchRequest) => {
    try {
      console.log('[HomePage] Starting hotel search:', request);
      await startHotelSearch(request);
      console.log('[HomePage] Hotel search started, job:', currentJob);
    } catch (err) {
      console.error('[HomePage] Hotel search failed:', err);
    }
  };

  const handleCancelJob = async () => {
    if (job?.job_id) {
      await cancelJob();
    }
  };

  const handleClear = () => {
    clearCurrentJob();
  };

  const handleClearSession = () => {
    SessionManager.clear();
    window.location.reload();
  };

  return (
    <Container className="py-4">
      {/* Debug Panel */}
      {showDebug && (
        <Alert variant="dark" className="mb-4">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <FaBug className="me-2" />
              <strong>Debug Info</strong>
            </div>
            <Button variant="outline-light" size="sm" onClick={handleClearSession}>
              Clear Session & Reload
            </Button>
          </div>
          <Row className="mt-3 small">
            <Col md={6}>
              <strong>Session ID:</strong> {sessionId}
            </Col>
            <Col md={3}>
              <strong>Current Job:</strong> {currentJob ? 'Yes' : 'No'}
            </Col>
            <Col md={3}>
              <strong>Polling Job:</strong> {job ? 'Yes' : 'No'}
            </Col>
          </Row>
          {job && (
            <Row className="mt-2">
              <Col>
                <strong>Job Status:</strong> {job.status} | 
                <strong> Type:</strong> {job.job_type} | 
                <strong> Progress:</strong> {job.progress}%
              </Col>
            </Row>
          )}
          {error && (
            <Row className="mt-2">
              <Col>
                <strong className="text-danger">Error:</strong> {error}
              </Col>
            </Row>
          )}
        </Alert>
      )}

      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1>
                <FaPlane className="me-2" />
                Scraprrr
              </h1>
              <p className="text-muted">
                Traveloka Flight & Hotel Scraper - Monitor scraping in real-time via Selenium Grid
              </p>
            </div>
            <Button 
              variant="outline-secondary" 
              size="sm"
              onClick={() => setShowDebug(!showDebug)}
            >
              <FaBug className="me-2" />
              {showDebug ? 'Hide Debug' : 'Show Debug'}
            </Button>
          </div>
          <div className="text-muted small">
            <strong>Session:</strong> {sessionId.slice(0, 8)}...{sessionId.slice(-8)}
          </div>
        </Col>
      </Row>

      {/* Current Job Monitor - Shows immediately when job starts */}
      {job && (
        <Row className="mb-4">
          <Col>
            <JobMonitor
              job={job}
              onCancel={handleCancelJob}
              onClear={handleClear}
              autoOpenVnc
            />
          </Col>
        </Row>
      )}

      {/* Search Forms - Always visible */}
      <Row>
        <Col lg={6} className="mb-4">
          <Tab.Container activeKey={activeTab} onSelect={(k) => setActiveTab(k as 'flights' | 'hotels')}>
            <Nav variant="tabs" className="mb-3">
              <Nav.Item>
                <Nav.Link eventKey="flights">
                  <FaPlane className="me-2" />
                  Flights
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="hotels">
                  <FaHotel className="me-2" />
                  Hotels
                </Nav.Link>
              </Nav.Item>
            </Nav>

            <Tab.Content>
              <Tab.Pane eventKey="flights">
                <FlightSearchForm
                  onSubmit={handleFlightSearch}
                  isLoading={isLoading}
                />
              </Tab.Pane>
              <Tab.Pane eventKey="hotels">
                <HotelSearchForm
                  onSubmit={handleHotelSearch}
                  isLoading={isLoading}
                />
              </Tab.Pane>
            </Tab.Content>
          </Tab.Container>
        </Col>

        <Col lg={6}>
          <div className="bg-light p-4 rounded h-100">
            <h5>How to Use</h5>
            <ol className="text-muted">
              <li>Enter your search parameters (origin/destination for flights, location for hotels)</li>
              <li>Click "Search" to start the scraping job</li>
              <li>
                <strong>Job Monitor appears immediately</strong> - Watch the progress in real-time
              </li>
              <li>
                The <strong>Live View (VNC)</strong> tab opens automatically - Watch the browser automation live!
              </li>
              <li>View results in the <strong>Results</strong> tab when complete</li>
            </ol>

            <h6 className="mt-4">What You'll See</h6>
            <div className="text-muted small">
              <p>When you click Search, the Job Monitor will show:</p>
              <ul>
                <li>📊 <strong>Status Tab:</strong> Job ID, progress bar, timestamps</li>
                <li>🖥️ <strong>Live View (VNC):</strong> Real-time browser view (opens automatically)</li>
                <li>📋 <strong>Results Tab:</strong> Scraped data table when complete</li>
              </ul>
            </div>

            <h6 className="mt-4">Quick Links</h6>
            <div className="d-flex flex-wrap gap-2">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-sm btn-outline-primary"
              >
                API Docs
              </a>
              <a
                href="http://localhost:7900"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-sm btn-outline-secondary"
              >
                VNC Viewer
              </a>
              <a
                href="http://localhost:4444"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-sm btn-outline-info"
              >
                Selenium Hub
              </a>
              <a
                href="/jobs"
                className="btn btn-sm btn-outline-success"
              >
                View All Jobs
              </a>
            </div>
          </div>
        </Col>
      </Row>
    </Container>
  );
};
