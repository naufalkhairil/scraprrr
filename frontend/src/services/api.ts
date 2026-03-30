import axios from 'axios';
import type {
  FlightSearchRequest,
  FlightSearchResult,
  HotelSearchRequest,
  HotelSearchResult,
  JobInfo,
  JobListResponse,
  JobStats,
  HealthStatus,
} from '@/types/api';

const API_BASE_URL = '/api/v1';

/**
 * Session ID manager for job isolation.
 * Uses localStorage to persist across page refreshes.
 */
export const SessionManager = {
  STORAGE_KEY: 'scraprrr_session_id',

  /**
   * Get or create session ID.
   * Persists to localStorage for cross-refresh consistency.
   */
  getId: (): string => {
    let sessionId = localStorage.getItem(SessionManager.STORAGE_KEY);
    
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      localStorage.setItem(SessionManager.STORAGE_KEY, sessionId);
      console.log('[SessionManager] Created new session:', sessionId);
    } else {
      console.log('[SessionManager] Using existing session:', sessionId);
    }
    
    return sessionId;
  },

  /**
   * Get current session ID without creating a new one.
   */
  getCurrent: (): string | null => {
    return localStorage.getItem(SessionManager.STORAGE_KEY);
  },

  /**
   * Clear session (for testing/debugging).
   */
  clear: () => {
    localStorage.removeItem(SessionManager.STORAGE_KEY);
    console.log('[SessionManager] Session cleared');
  },

  /**
   * Get headers for API requests.
   */
  getHeaders: () => ({
    'X-Session-ID': SessionManager.getId(),
  }),
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add session ID to all requests
apiClient.interceptors.request.use((config) => {
  const sessionId = SessionManager.getId();
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId;
  }
  return config;
});

// Flight API
export const flightApi = {
  search: async (request: FlightSearchRequest): Promise<FlightSearchResult> => {
    const response = await apiClient.post<FlightSearchResult>('/flights/search', request);
    return response.data;
  },

  searchAsync: async (request: FlightSearchRequest): Promise<JobInfo> => {
    const response = await apiClient.post<JobInfo>('/flights/search/async', request);
    return response.data;
  },

  getJob: async (jobId: string): Promise<JobInfo> => {
    const response = await apiClient.get<JobInfo>(`/flights/job/${jobId}`);
    return response.data;
  },

  cancelJob: async (jobId: string): Promise<void> => {
    await apiClient.delete(`/flights/job/${jobId}`);
  },

  getAirports: async (): Promise<Record<string, string>> => {
    const response = await apiClient.get<Record<string, string>>('/flights/airports');
    return response.data;
  },
};

// Hotel API
export const hotelApi = {
  search: async (request: HotelSearchRequest): Promise<HotelSearchResult> => {
    const response = await apiClient.post<HotelSearchResult>('/hotels/search', request);
    return response.data;
  },

  searchAsync: async (request: HotelSearchRequest): Promise<JobInfo> => {
    const response = await apiClient.post<JobInfo>('/hotels/search/async', request);
    return response.data;
  },

  getJob: async (jobId: string): Promise<JobInfo> => {
    const response = await apiClient.get<JobInfo>(`/hotels/job/${jobId}`);
    return response.data;
  },

  cancelJob: async (jobId: string): Promise<void> => {
    await apiClient.delete(`/hotels/job/${jobId}`);
  },

  getPopularDestinations: async (): Promise<Record<string, string>> => {
    const response = await apiClient.get<Record<string, string>>('/hotels/popular-destinations');
    return response.data;
  },
};

// Job Management API
export const jobApi = {
  list: async (): Promise<JobListResponse> => {
    const response = await apiClient.get<JobListResponse>('/jobs');
    console.log('[jobApi.list] Response:', response.data);
    return response.data;
  },

  get: async (jobId: string): Promise<JobInfo> => {
    const response = await apiClient.get<JobInfo>(`/jobs/${jobId}`);
    return response.data;
  },

  cancel: async (jobId: string): Promise<void> => {
    await apiClient.delete(`/jobs/${jobId}`);
  },

  cleanup: async (maxAgeSeconds: number = 3600): Promise<{ message: string; deleted_count: number }> => {
    const response = await apiClient.post(`/jobs/cleanup?max_age_seconds=${maxAgeSeconds}`, null);
    return response.data;
  },

  getStats: async (): Promise<JobStats> => {
    const response = await apiClient.get<JobStats>('/jobs/stats');
    return response.data;
  },
};

// Health API
export const healthApi = {
  check: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },
};

export default apiClient;
