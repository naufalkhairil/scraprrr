import React from 'react';
import { Table, Badge } from 'react-bootstrap';
import type { FlightSearchResult } from '@/types/api';

interface FlightResultsProps {
  result: FlightSearchResult;
}

export const FlightResults: React.FC<FlightResultsProps> = ({ result }) => {
  if (!result.tickets || result.tickets.length === 0) {
    return <div className="text-muted">No flights found</div>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">
          {result.origin.code} → {result.destination.code}
        </h5>
        <Badge bg="success">{result.total_results} flights found</Badge>
      </div>

      <div className="table-responsive" style={{ maxHeight: '400px', overflowY: 'auto' }}>
        <Table striped hover size="sm">
          <thead className="table-light sticky-top">
            <tr>
              <th>Airline</th>
              <th>Departure</th>
              <th>Arrival</th>
              <th>Duration</th>
              <th>Type</th>
              <th>Price</th>
              <th>Baggage</th>
            </tr>
          </thead>
          <tbody>
            {result.tickets.map((ticket, index) => (
              <tr key={index}>
                <td>
                  {ticket.airline_logo && (
                    <img
                      src={ticket.airline_logo}
                      alt={ticket.airline_name}
                      style={{ width: '30px', height: '30px', marginRight: '8px' }}
                    />
                  )}
                  {ticket.airline_name}
                  {ticket.highlight_label && (
                    <Badge bg="warning" text="dark" className="ms-2">
                      {ticket.highlight_label}
                    </Badge>
                  )}
                </td>
                <td>
                  <div>{ticket.departure_time}</div>
                  <small className="text-muted">{ticket.departure_airport}</small>
                </td>
                <td>
                  <div>{ticket.arrival_time}</div>
                  <small className="text-muted">{ticket.arrival_airport}</small>
                </td>
                <td>{ticket.duration}</td>
                <td>
                  <Badge bg={ticket.flight_type === 'Direct' ? 'success' : 'info'}>
                    {ticket.flight_type}
                  </Badge>
                </td>
                <td className="fw-bold">{ticket.price}</td>
                <td>{ticket.baggage}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
    </div>
  );
};
