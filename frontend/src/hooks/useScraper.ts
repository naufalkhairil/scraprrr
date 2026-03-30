import { useState, useCallback } from 'react';
import { flightApi, hotelApi } from '@/services/api';
import type { FlightSearchRequest, HotelSearchRequest, JobInfo } from '@/types/api';
import axios from 'axios';

export function useScraper() {
  const [currentJob, setCurrentJob] = useState<JobInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startFlightSearch = useCallback(async (request: FlightSearchRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const job = await flightApi.searchAsync(request);
      setCurrentJob(job);
      return job;
    } catch (err) {
      const message = axios.isAxiosError(err) ? err.message : 'Failed to start flight search';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const startHotelSearch = useCallback(async (request: HotelSearchRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const job = await hotelApi.searchAsync(request);
      setCurrentJob(job);
      return job;
    } catch (err) {
      const message = axios.isAxiosError(err) ? err.message : 'Failed to start hotel search';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearCurrentJob = useCallback(() => {
    setCurrentJob(null);
    setError(null);
  }, []);

  return {
    currentJob,
    isLoading,
    error,
    startFlightSearch,
    startHotelSearch,
    clearCurrentJob,
  };
}
