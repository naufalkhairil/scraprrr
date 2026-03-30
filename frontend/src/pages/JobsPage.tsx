import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Alert, Button, Badge } from 'react-bootstrap';
import { FaList, FaChartBar, FaTrash, FaSync, FaCheckCircle, FaInfoCircle } from 'react-icons/fa';
import { jobApi, SessionManager } from '@/services/api';
import { JobList } from '@/components/JobList';
import { JobMonitor } from '@/components/JobMonitor';
import type { JobInfo, JobStats } from '@/types/api';

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [stats, setStats] = useState<JobStats | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [sessionId, setSessionId] = useState<string>('');

  const fetchJobs = async (showLoadingIndicator = false) => {
    try {
      if (showLoadingIndicator) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      
      const currentSessionId = SessionManager.getId();
      setSessionId(currentSessionId);
      console.log('[JobsPage] Fetching jobs for session:', currentSessionId);
      
      const [jobsResponse, statsResponse] = await Promise.all([
        jobApi.list(),
        jobApi.getStats(),
      ]);
      
      console.log('[JobsPage] Jobs response:', jobsResponse);
      console.log('[JobsPage] Stats response:', statsResponse);
      
      setJobs(jobsResponse.jobs);
      setStats(statsResponse);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('[JobsPage] Failed to fetch jobs:', err);
      setError('Failed to load jobs. Please refresh.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    const sid = SessionManager.getId();
    setSessionId(sid);
    console.log('[JobsPage] Initial session ID:', sid);
    fetchJobs();
    // Poll every 2 seconds for near real-time updates
    const interval = setInterval(() => fetchJobs(false), 2000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    await fetchJobs(true);
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await jobApi.cancel(jobId);
      await fetchJobs();
      if (selectedJob?.job_id === jobId) {
        setSelectedJob(null);
      }
    } catch (err) {
      setError('Failed to cancel job');
    }
  };

  const handleCleanup = async () => {
    try {
      await jobApi.cleanup(0); // Clean up all old jobs
      await fetchJobs();
    } catch (err) {
      setError('Failed to cleanup jobs');
    }
  };

  const handleSelectJob = (job: JobInfo) => {
    setSelectedJob(job);
  };

  const handleClearSession = () => {
    SessionManager.clear();
    const newSessionId = SessionManager.getId();
    setSessionId(newSessionId);
    fetchJobs();
  };

  return (
    <Container className="py-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
            <div>
              <h1 className="d-inline-flex align-items-center gap-2">
                <FaList />
                Job History
              </h1>
              {lastUpdated && (
                <div className="text-muted small mt-1">
                  <FaCheckCircle className="me-1 text-success" />
                  Updated: {lastUpdated.toLocaleTimeString()}
                </div>
              )}
              {sessionId && (
                <div className="text-muted small mt-1" style={{ fontSize: '0.75rem' }}>
                  <FaInfoCircle className="me-1" />
                  Session: {sessionId.slice(0, 8)}...{sessionId.slice(-8)}
                </div>
              )}
            </div>
            <div className="d-flex gap-2">
              <Button 
                variant="outline-primary" 
                onClick={handleRefresh} 
                disabled={isRefreshing}
              >
                <FaSync className={`me-2 ${isRefreshing ? 'spin' : ''}`} />
                Refresh
              </Button>
              <Button variant="outline-secondary" onClick={handleClearSession}>
                <FaTrash className="me-2" />
                Clear Session
              </Button>
              <Button variant="outline-danger" onClick={handleCleanup}>
                <FaTrash className="me-2" />
                Cleanup Old
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Row className="mb-4">
          <Col>
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          </Col>
        </Row>
      )}

      {/* Session Info Alert */}
      {!isLoading && jobs.length === 0 && (
        <Row className="mb-4">
          <Col>
            <Alert variant="info">
              <div className="d-flex align-items-start">
                <FaInfoCircle className="me-2 mt-1" />
                <div>
                  <strong>No jobs found for this session</strong>
                  <div className="mt-2 small">
                    <p className="mb-1">
                      Jobs are isolated by browser session. This could mean:
                    </p>
                    <ul className="mb-2">
                      <li>You haven't created any jobs yet in this session</li>
                      <li>You're using a different browser or incognito mode</li>
                      <li>Jobs were cleaned up (older than 1 hour)</li>
                    </ul>
                    <p className="mb-1">
                      <strong>To test:</strong> Go to the home page and start a new search.
                    </p>
                    <Button 
                      variant="outline-primary" 
                      size="sm" 
                      onClick={() => window.location.href = '/'}
                    >
                      Go to Home Page
                    </Button>
                    {' '}
                    <Button 
                      variant="outline-secondary" 
                      size="sm" 
                      onClick={handleClearSession}
                    >
                      Clear Session & Reload
                    </Button>
                  </div>
                </div>
              </div>
            </Alert>
          </Col>
        </Row>
      )}

      {/* Stats Cards */}
      {stats && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center shadow-sm">
              <Card.Body>
                <Card.Title className="text-muted">
                  <FaChartBar className="me-2" />
                  Total Jobs
                </Card.Title>
                <h2 className="mb-0">{stats.total_jobs}</h2>
              </Card.Body>
            </Card>
          </Col>
          {Object.entries(stats.by_status).map(([status, count]) => (
            <Col md={2} key={status}>
              <Card className="text-center shadow-sm">
                <Card.Body>
                  <Card.Title className="text-muted small">
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </Card.Title>
                  <h3 className="mb-0">
                    <Badge
                      bg={
                        status === 'completed'
                          ? 'success'
                          : status === 'running'
                          ? 'primary'
                          : status === 'failed'
                          ? 'danger'
                          : status === 'cancelled'
                          ? 'warning'
                          : 'secondary'
                      }
                      pill
                    >
                      {count}
                    </Badge>
                  </h3>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Row>
        <Col lg={8}>
          <JobList
            jobs={jobs}
            stats={stats}
            isLoading={isLoading}
            onSelectJob={handleSelectJob}
            onCancelJob={handleCancelJob}
          />
        </Col>
        <Col lg={4}>
          {selectedJob ? (
            <JobMonitor
              job={selectedJob}
              onCancel={() => handleCancelJob(selectedJob.job_id)}
              onClear={() => setSelectedJob(null)}
              autoOpenVnc={selectedJob.status === 'running' || selectedJob.status === 'pending'}
            />
          ) : (
            <Card className="shadow-sm">
              <Card.Body className="text-center text-muted py-5">
                <FaList size={48} className="mb-3 opacity-25" />
                <p>Select a job from the list to view details</p>
                <small className="text-muted">
                  Jobs are filtered by your browser session
                </small>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </Container>
  );
};
