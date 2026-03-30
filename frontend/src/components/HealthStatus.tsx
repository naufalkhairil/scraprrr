import React from 'react';
import { Alert, Badge } from 'react-bootstrap';
import { FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';
import type { HealthStatus } from '@/types/api';

interface HealthStatusProps {
  health: HealthStatus | null;
  isLoading: boolean;
  error: string | null;
}

export const HealthStatusIndicator: React.FC<HealthStatusProps> = ({
  health,
  isLoading,
  error,
}) => {
  if (isLoading) {
    return (
      <Alert variant="info">
        Checking system status...
      </Alert>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <FaExclamationTriangle className="me-2" />
        Unable to connect to API server: {error}
      </Alert>
    );
  }

  if (!health) {
    return null;
  }

  return (
    <Alert variant={health.selenium_connected ? 'success' : 'warning'}>
      <div className="d-flex justify-content-between align-items-center">
        <div>
          <FaCheckCircle className="me-2" />
          <strong>System Status: </strong>
          {health.status === 'healthy' ? 'All systems operational' : 'Degraded'}
          {' | '}
          <small>API v{health.version}</small>
        </div>
        <div>
          <Badge bg={health.selenium_connected ? 'success' : 'danger'}>
            Selenium: {health.selenium_connected ? 'Connected' : 'Disconnected'}
          </Badge>
        </div>
      </div>
      {!health.selenium_connected && (
        <div className="mt-2">
          <small>
            ⚠️ Selenium Grid is not connected. Please start the Docker container:
            <code className="ms-2">docker-compose -f docker/selenium-grid/docker-compose.yml up -d</code>
          </small>
        </div>
      )}
    </Alert>
  );
};
