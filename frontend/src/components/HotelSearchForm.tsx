import React, { useState } from 'react';
import { Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { FaHotel, FaSearch, FaMapMarkerAlt } from 'react-icons/fa';
import type { HotelSearchRequest } from '@/types/api';

interface HotelSearchFormProps {
  onSubmit: (request: HotelSearchRequest) => void;
  isLoading: boolean;
}

const POPULAR_DESTINATIONS = [
  { id: 'jakarta', name: 'Jakarta, Indonesia' },
  { id: 'bali', name: 'Bali, Indonesia' },
  { id: 'bandung', name: 'Bandung, Indonesia' },
  { id: 'yogyakarta', name: 'Yogyakarta, Indonesia' },
  { id: 'surabaya', name: 'Surabaya, Indonesia' },
  { id: 'singapore', name: 'Singapore' },
  { id: 'kuala-lumpur', name: 'Kuala Lumpur, Malaysia' },
  { id: 'bangkok', name: 'Bangkok, Thailand' },
];

export const HotelSearchForm: React.FC<HotelSearchFormProps> = ({ onSubmit, isLoading }) => {
  const [location, setLocation] = useState('');
  const [saveResults, setSaveResults] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!location || location.trim().length === 0) {
      setError('Location cannot be empty');
      return;
    }

    onSubmit({
      location: location.trim(),
      save_results: saveResults,
    });
  };

  const handleQuickSelect = (destName: string) => {
    setLocation(destName);
    setError(null);
  };

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-success text-white">
        <FaHotel className="me-2" />
        Hotel Search
      </Card.Header>
      <Card.Body>
        <Form onSubmit={handleSubmit}>
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Form.Group className="mb-3">
            <Form.Label>
              <FaMapMarkerAlt className="me-2" />
              Location
            </Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter city, hotel, or place name"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              disabled={isLoading}
              isInvalid={!!error && !location.trim()}
            />
            <Form.Control.Feedback type="invalid">
              Please enter a location
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Quick Select (Popular Destinations)</Form.Label>
            <div className="d-flex flex-wrap gap-2">
              {POPULAR_DESTINATIONS.map((dest) => (
                <Button
                  key={dest.id}
                  variant="outline-success"
                  size="sm"
                  onClick={() => handleQuickSelect(dest.name)}
                  disabled={isLoading}
                >
                  {dest.name.split(',')[0]}
                </Button>
              ))}
            </div>
          </Form.Group>

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
            variant="success"
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
                Search Hotels
              </>
            )}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};
