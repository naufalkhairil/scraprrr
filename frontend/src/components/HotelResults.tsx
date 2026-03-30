import React from 'react';
import { Table, Badge } from 'react-bootstrap';
import type { HotelSearchResult } from '@/types/api';

interface HotelResultsProps {
  result: HotelSearchResult;
}

export const HotelResults: React.FC<HotelResultsProps> = ({ result }) => {
  if (!result.hotels || result.hotels.length === 0) {
    return <div className="text-muted">No hotels found</div>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">{result.location}</h5>
        <Badge bg="success">{result.total_results} hotels found</Badge>
      </div>

      <div className="table-responsive" style={{ maxHeight: '400px', overflowY: 'auto' }}>
        <Table striped hover size="sm">
          <thead className="table-light sticky-top">
            <tr>
              <th>Hotel</th>
              <th>Location</th>
              <th>Stars</th>
              <th>Rating</th>
              <th>Price</th>
              <th>Features</th>
            </tr>
          </thead>
          <tbody>
            {result.hotels.map((hotel, index) => (
              <tr key={index}>
                <td>
                  <div className="fw-bold">{hotel.hotel_name}</div>
                  {hotel.hotel_type && (
                    <small className="text-muted">{hotel.hotel_type}</small>
                  )}
                </td>
                <td>
                  <small>{hotel.location}</small>
                </td>
                <td>
                  {hotel.star_rating && (
                    <div className="text-warning">
                      {'★'.repeat(hotel.star_rating)}
                      {'☆'.repeat(5 - hotel.star_rating)}
                    </div>
                  )}
                </td>
                <td>
                  {hotel.rating_score && (
                    <Badge bg={parseFloat(hotel.rating_score) >= 8 ? 'success' : 'secondary'}>
                      {hotel.rating_score}
                    </Badge>
                  )}
                </td>
                <td className="fw-bold">
                  {hotel.price && <div>{hotel.price}</div>}
                  {hotel.total_price && (
                    <small className="text-muted">{hotel.total_price}</small>
                  )}
                </td>
                <td>
                  <div className="d-flex flex-wrap gap-1">
                    {hotel.features?.slice(0, 3).map((feature, i) => (
                      <Badge key={i} bg="light" text="dark" className="small">
                        {feature}
                      </Badge>
                    ))}
                    {hotel.features && hotel.features.length > 3 && (
                      <Badge bg="secondary">+{hotel.features.length - 3}</Badge>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
    </div>
  );
};
