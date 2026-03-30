import React from 'react';
import { Card, Badge, Spinner, Table, Button } from 'react-bootstrap';
import { format } from 'date-fns';
import { FaList, FaCheckCircle, FaTimesCircle, FaClock, FaPlay, FaStopCircle } from 'react-icons/fa';
import type { JobInfo, JobStats } from '@/types/api';

interface JobListProps {
  jobs: JobInfo[];
  stats: JobStats | null;
  isLoading: boolean;
  onSelectJob: (job: JobInfo) => void;
  onCancelJob: (jobId: string) => void;
}

const statusIcons: Record<string, React.ReactNode> = {
  pending: <FaClock />,
  running: <FaPlay />,
  completed: <FaCheckCircle />,
  failed: <FaTimesCircle />,
  cancelled: <FaStopCircle />,
};

const statusVariants: Record<string, string> = {
  pending: 'secondary',
  running: 'primary',
  completed: 'success',
  failed: 'danger',
  cancelled: 'warning',
};

export const JobList: React.FC<JobListProps> = ({
  jobs,
  stats,
  isLoading,
  onSelectJob,
  onCancelJob,
}) => {
  if (isLoading) {
    return (
      <Card className="shadow-sm">
        <Card.Body className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <div className="mt-2">Loading jobs...</div>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-secondary text-white">
        <FaList className="me-2" />
        Recent Jobs
        {stats && (
          <Badge bg="light" text="dark" className="ms-2">
            {stats.total_jobs} total
          </Badge>
        )}
      </Card.Header>
      <Card.Body>
        {jobs.length === 0 ? (
          <div className="text-muted text-center py-4">No recent jobs</div>
        ) : (
          <div className="table-responsive" style={{ maxHeight: '400px', overflowY: 'auto' }}>
            <Table striped hover size="sm">
              <thead className="table-light sticky-top">
                <tr>
                  <th>Status</th>
                  <th>Type</th>
                  <th>Parameters</th>
                  <th>Created</th>
                  <th>Progress</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.slice(0, 20).map((job) => (
                  <tr key={job.job_id} onClick={() => onSelectJob(job)} style={{ cursor: 'pointer' }}>
                    <td>
                      <Badge bg={statusVariants[job.status]}>
                        {statusIcons[job.status]}
                        <span className="ms-1">{job.status}</span>
                      </Badge>
                    </td>
                    <td>
                      <Badge bg={job.job_type === 'flight_search' ? 'primary' : 'success'}>
                        {job.job_type === 'flight_search' ? 'Flight' : 'Hotel'}
                      </Badge>
                    </td>
                    <td>
                      <small>
                        {job.job_type === 'flight_search'
                          ? `${job.params.origin} → ${job.params.destination}`
                          : `${job.params.location}`}
                      </small>
                    </td>
                    <td>
                      <small>{format(new Date(job.created_at), 'HH:mm:ss')}</small>
                    </td>
                    <td>
                      <div style={{ width: '100px' }}>
                        <div className="progress" style={{ height: '8px' }}>
                          <div
                            className="progress-bar"
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                        <small>{job.progress}%</small>
                      </div>
                    </td>
                    <td>
                      {(job.status === 'running' || job.status === 'pending') && (
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onCancelJob(job.job_id);
                          }}
                        >
                          Cancel
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};
