import React, { useState } from 'react';
import { Card, Form, Button, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { FaPlaneDeparture, FaPlaneArrival, FaExchangeAlt, FaSearch } from 'react-icons/fa';
import type { FlightSearchRequest } from '@/types/api';

interface FlightSearchFormProps {
  onSubmit: (request: FlightSearchRequest) => void;
  isLoading: boolean;
}

export const FlightSearchForm: React.FC<FlightSearchFormProps> = ({ onSubmit, isLoading }) => {
  const [origin, setOrigin] = useState('CGK');
  const [destination, setDestination] = useState('DPS');
  const [originName, setOriginName] = useState('');
  const [destinationName, setDestinationName] = useState('');
  const [saveResults, setSaveResults] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!origin || origin.length !== 3) {
      setError('Origin must be a 3-letter airport code');
      return;
    }

    if (!destination || destination.length !== 3) {
      setError('Destination must be a 3-letter airport code');
      return;
    }

    if (origin === destination) {
      setError('Origin and destination cannot be the same');
      return;
    }

    onSubmit({
      origin: origin.toUpperCase(),
      destination: destination.toUpperCase(),
      origin_name: originName || undefined,
      destination_name: destinationName || undefined,
      save_results: saveResults,
    });
  };

  const swapLocations = () => {
    setOrigin(destination);
    setDestination(origin);
    setOriginName(destinationName);
    setDestinationName(originName);
  };

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-primary text-white">
        <FaPlaneDeparture className="me-2" />
        Flight Search
      </Card.Header>
      <Card.Body>
        <Form onSubmit={handleSubmit}>
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Row className="mb-3 align-items-center">
            <Col md={5}>
              <Form.Group>
                <Form.Label>
                  <FaPlaneDeparture className="me-2" />
                  Origin (Airport Code)
                </Form.Label>
                <Form.Control
                  type="text"
                  placeholder="e.g., CGK"
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value.toUpperCase())}
                  maxLength={3}
                  disabled={isLoading}
                  isInvalid={!!error && origin.length !== 3}
                />
                <Form.Control.Feedback type="invalid">
                  Must be 3 letters
                </Form.Control.Feedback>
              </Form.Group>
            </Col>

            <Col md={2} className="text-center">
              <Button
                variant="outline-secondary"
                type="button"
                onClick={swapLocations}
                disabled={isLoading}
                className="mt-4"
              >
                <FaExchangeAlt />
              </Button>
            </Col>

            <Col md={5}>
              <Form.Group>
                <Form.Label>
                  <FaPlaneArrival className="me-2" />
                  Destination (Airport Code)
                </Form.Label>
                <Form.Control
                  type="text"
                  placeholder="e.g., DPS"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value.toUpperCase())}
                  maxLength={3}
                  disabled={isLoading}
                  isInvalid={!!error && destination.length !== 3}
                />
                <Form.Control.Feedback type="invalid">
                  Must be 3 letters
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>

          <Row className="mb-3">
            <Col md={6}>
              <Form.Group>
                <Form.Label>Origin Name (Optional)</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="e.g., Jakarta"
                  value={originName}
                  onChange={(e) => setOriginName(e.target.value)}
                  disabled={isLoading}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group>
                <Form.Label>Destination Name (Optional)</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="e.g., Bali"
                  value={destinationName}
                  onChange={(e) => setDestinationName(e.target.value)}
                  disabled={isLoading}
                />
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Save results to files (CSV/JSON)"
              checked={saveResults}
              onChange={(e) => setSaveResults(e.target.checked)}
              disabled={isLoading}
            />
          </Form.Group>

          <Button
            variant="primary"
            type="submit"
            disabled={isLoading}
            className="w-100"
          >
            {isLoading ? (
              <>
                <Spinner as="span" animation="border" size="sm" className="me-2" />
                Starting Search...
              </>
            ) : (
              <>
                <FaSearch className="me-2" />
                Search Flights
              </>
            )}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};
