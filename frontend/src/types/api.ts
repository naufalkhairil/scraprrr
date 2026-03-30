// API Types

export interface AirportInfo {
  code: string;
  name: string;
}

export interface FlightTicket {
  airline_name: string;
  airline_logo?: string | null;
  departure_time: string;
  departure_airport: string;
  arrival_time: string;
  arrival_airport: string;
  duration: string;
  flight_type: string;
  price: string;
  original_price?: string | null;
  baggage: string;
  promos: string[];
  special_tag?: string | null;
  highlight_label?: string | null;
  extracted_at: string;
}

export interface FlightSearchResult {
  origin: AirportInfo;
  destination: AirportInfo;
  search_timestamp: string;
  status: string;
  total_results: number;
  tickets: FlightTicket[];
  error_message?: string | null;
}

export interface Hotel {
  hotel_name: string;
  location: string;
  star_rating?: number | null;
  rating_score?: string | null;
  review_count?: string | null;
  main_image_url?: string | null;
  supporting_images: string[];
  original_price?: string | null;
  price?: string | null;
  total_price?: string | null;
  booking_info?: string | null;
  hotel_type?: string | null;
  ranking?: string | null;
  features: string[];
  extracted_at: string;
}

export interface HotelSearchResult {
  location: string;
  search_timestamp: string;
  status: string;
  total_results: number;
  hotels: Hotel[];
  error_message?: string | null;
}

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface JobInfo {
  job_id: string;
  job_type: string;
  status: JobStatus;
  params: Record<string, unknown>;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  result?: unknown | null;
  error?: string | null;
  progress: number;
}

export interface JobListResponse {
  total: number;
  jobs: JobInfo[];
}

export interface JobStats {
  total_jobs: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
}

export interface HealthStatus {
  status: string;
  version: string;
  timestamp: string;
  selenium_connected: boolean;
  selenium_url: string;
}

// Search Request Types
export interface FlightSearchRequest {
  origin: string;
  destination: string;
  origin_name?: string;
  destination_name?: string;
  save_results?: boolean;
}

export interface HotelSearchRequest {
  location: string;
  save_results?: boolean;
}
