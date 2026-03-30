import React from 'react';
import { Card, Badge, ProgressBar, Button, Alert, Spinner, Row, Col, Nav, Tab } from 'react-bootstrap';
import { format } from 'date-fns';
import {
  FaPlay,
  FaCheckCircle,
  FaTimesCircle,
  FaStopCircle,
  FaClock,
  FaExclamationTriangle,
  FaDesktop,
  FaList,
} from 'react-icons/fa';
import type { JobInfo, JobStatus } from '@/types/api';
import { FlightResults } from './FlightResults';
import { HotelResults } from './HotelResults';

interface JobMonitorProps {
  job: JobInfo;
  onCancel: () => void;
  onClear: () => void;
  autoOpenVnc?: boolean;
}

const statusConfig: Record<JobStatus, { variant: string; icon: React.ReactNode; label: string }> = {
  pending: {
    variant: 'secondary',
    icon: <FaClock />,
    label: 'Pending',
  },
  running: {
    variant: 'primary',
    icon: <FaPlay />,
    label: 'Running',
  },
  completed: {
    variant: 'success',
    icon: <FaCheckCircle />,
    label: 'Completed',
  },
  failed: {
    variant: 'danger',
    icon: <FaTimesCircle />,
    label: 'Failed',
  },
  cancelled: {
    variant: 'warning',
    icon: <FaStopCircle />,
    label: 'Cancelled',
  },
};

export const JobMonitor: React.FC<JobMonitorProps> = ({ 
  job, 
  onCancel, 
  onClear,
  autoOpenVnc = false,
}) => {
  // Always start on VNC tab if autoOpenVnc is true
  const [activeTab, setActiveTab] = React.useState<'status' | 'vnc' | 'results'>(() => {
    if (autoOpenVnc) return 'vnc';
    return 'status';
  });
  const config = statusConfig[job.status];

  const isRunning = job.status === 'running' || job.status === 'pending';
  const isCompleted = job.status === 'completed';

  // Keep VNC tab active while job is running if autoOpenVnc was set
  React.useEffect(() => {
    if (autoOpenVnc && isRunning) {
      setActiveTab('vnc');
    }
  }, [job.status, autoOpenVnc, isRunning]);

  const getResult = () => {
    if (!job.result) return null;
    return job.result as import('@/types/api').FlightSearchResult | import('@/types/api').HotelSearchResult;
  };

  const result = getResult();

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-dark text-white d-flex justify-content-between align-items-center">
        <span>
          <FaDesktop className="me-2" />
          Job Monitor
        </span>
        <Badge bg={config.variant} className="d-flex align-items-center gap-1">
          {config.icon}
          {config.label}
        </Badge>
      </Card.Header>
      <Card.Body>
        {/* Job Info */}
        <Row className="mb-3">
          <Col md={6}>
            <small className="text-muted">Job ID</small>
            <div className="font-monospace small">{job.job_id}</div>
          </Col>
          <Col md={6}>
            <small className="text-muted">Job Type</small>
            <div>
              <Badge bg={job.job_type === 'flight_search' ? 'primary' : 'success'}>
                {job.job_type === 'flight_search' ? 'Flight Search' : 'Hotel Search'}
              </Badge>
            </div>
          </Col>
        </Row>

        {/* Search Parameters */}
        <div className="mb-3">
          <small className="text-muted">Search Parameters</small>
          <div className="bg-light p-2 rounded">
            {job.job_type === 'flight_search' ? (
              <span>
                {job.params.origin as string} → {job.params.destination as string}
              </span>
            ) : (
              <span>{job.params.location as string}</span>
            )}
          </div>
        </div>

        {/* Progress */}
        {isRunning && (
          <div className="mb-3">
            <div className="d-flex justify-content-between mb-1">
              <span>Progress</span>
              <span>{job.progress}%</span>
            </div>
            <ProgressBar now={job.progress} animated={isRunning} variant="primary" />
            <small className="text-muted">
              {job.status === 'pending' ? 'Starting scraper...' : 'Scraping in progress...'}
            </small>
          </div>
        )}

        {/* Timestamps */}
        <Row className="mb-3 small">
          <Col>
            <span className="text-muted">Created: </span>
            {format(new Date(job.created_at), 'HH:mm:ss')}
          </Col>
          {job.started_at && (
            <Col>
              <span className="text-muted">Started: </span>
              {format(new Date(job.started_at), 'HH:mm:ss')}
            </Col>
          )}
          {job.completed_at && (
            <Col>
              <span className="text-muted">Completed: </span>
              {format(new Date(job.completed_at), 'HH:mm:ss')}
            </Col>
          )}
        </Row>

        {/* Error Message */}
        {job.error && (
          <Alert variant="danger" className="mb-3">
            <FaExclamationTriangle className="me-2" />
            {job.error}
          </Alert>
        )}

        {/* Status Alert */}
        {isRunning && (
          <Alert variant="info" className="mb-3">
            <div className="d-flex align-items-center">
              <Spinner animation="border" size="sm" className="me-2" />
              <div>
                <strong>Scraping in progress...</strong>
                <div className="small">
                  Watch the live browser in the <strong>Live View (VNC)</strong> tab
                </div>
              </div>
            </div>
          </Alert>
        )}

        {/* Result Summary */}
        {isCompleted && result && (
          <Alert variant="success" className="mb-3">
            <FaCheckCircle className="me-2" />
            Found {(result as import('@/types/api').FlightSearchResult).total_results || 
                   (result as import('@/types/api').HotelSearchResult).total_results}{' '}
            {job.job_type === 'flight_search' ? 'flights' : 'hotels'}
          </Alert>
        )}

        {/* Action Buttons */}
        <div className="d-flex gap-2 mb-3">
          {isRunning && (
            <Button variant="danger" onClick={onCancel} size="sm">
              <FaStopCircle className="me-2" />
              Cancel Job
            </Button>
          )}
          {isCompleted && (
            <Button variant="secondary" onClick={onClear} size="sm">
              Clear
            </Button>
          )}
        </div>

        {/* Tabs for Status, VNC, Results */}
        <Tab.Container activeKey={activeTab} onSelect={(k) => setActiveTab(k as 'status' | 'vnc' | 'results')}>
          <Nav variant="tabs" className="mb-3">
            <Nav.Item>
              <Nav.Link eventKey="status">
                Status
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link 
                eventKey="vnc" 
                disabled={false}  // Always enabled now
                className={isRunning ? 'bg-primary text-white rounded' : ''}
              >
                <FaDesktop className="me-2" />
                Live View (VNC)
                {isRunning && <Spinner animation="border" size="sm" className="ms-2" />}
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link 
                eventKey="results" 
                disabled={!isCompleted || !result}
              >
                <FaList className="me-2" />
                Results
                {isCompleted && result && (
                  <Badge bg="success" className="ms-2">
                    {job.job_type === 'flight_search' 
                      ? (result as import('@/types/api').FlightSearchResult).total_results
                      : (result as import('@/types/api').HotelSearchResult).total_results
                    }
                  </Badge>
                )}
              </Nav.Link>
            </Nav.Item>
          </Nav>

          {/* Tab Content */}
          <Tab.Content>
            <Tab.Pane eventKey="status">
              <h6 className="mb-3">Job Status Details</h6>
              <pre className="bg-light p-3 rounded small" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {JSON.stringify(job, null, 2)}
              </pre>
            </Tab.Pane>

            <Tab.Pane eventKey="vnc">
              <h6 className="mb-3">
                <FaDesktop className="me-2" />
                Selenium Live View
              </h6>
              <Alert variant="info" className="mb-3">
                <div className="d-flex align-items-center">
                  <Spinner animation="border" size="sm" className="me-2" />
                  <div>
                    <strong>Watching live browser automation</strong>
                    <div className="small">
                      Password: <strong>secret</strong> | 
                      Watch the scraper navigate Traveloka, search, and extract data in real-time.
                    </div>
                  </div>
                </div>
              </Alert>
              <div className="ratio ratio-16x9 border rounded" style={{ backgroundColor: '#000' }}>
                <iframe
                  src="http://localhost:7900/?autoconnect=1&resize=scale&password=secret&view_only=1"
                  title="Selenium VNC Viewer"
                  allow="clipboard-write"
                  style={{ border: 'none' }}
                />
              </div>
              <div className="mt-2 text-center">
                <small className="text-muted">
                  Having issues?{' '}
                  <a href="http://localhost:7900" target="_blank" rel="noopener noreferrer">
                    Open VNC in new tab
                  </a>
                </small>
              </div>
            </Tab.Pane>

            <Tab.Pane eventKey="results">
              {result && (
                job.job_type === 'flight_search' ? (
                  <FlightResults result={result as import('@/types/api').FlightSearchResult} />
                ) : (
                  <HotelResults result={result as import('@/types/api').HotelSearchResult} />
                )
              )}
            </Tab.Pane>
          </Tab.Content>
        </Tab.Container>
      </Card.Body>
    </Card>
  );
};
