import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import type { JobInfo } from '@/types/api';
import { jobApi } from '@/services/api';

export function useJobPolling(initialJob: JobInfo | null, pollInterval: number = 2000) {
  const [job, setJob] = useState<JobInfo | null>(initialJob);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const jobId = initialJob?.job_id || null;

  const fetchJob = useCallback(async () => {
    if (!jobId) return;

    try {
      setIsLoading(true);
      const data = await jobApi.get(jobId);
      setJob(data);
      setError(null);

      // Stop polling if job is completed, failed, or cancelled
      if (['completed', 'failed', 'cancelled'].includes(data.status)) {
        stopPolling();
      }
    } catch (err) {
      console.error('Polling error:', err);
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 404) {
          setError('Job not found');
          stopPolling();
        } else if (err.response?.status === 202) {
          // Job is still running - get job data from response
          const runningJob = err.response?.data as JobInfo;
          if (runningJob) {
            setJob(runningJob);
          }
        } else {
          setError(err.message);
        }
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  }, [jobId]);

  const startPolling = useCallback(() => {
    if (intervalRef.current) return;
    fetchJob(); // Fetch immediately
    intervalRef.current = setInterval(fetchJob, pollInterval);
  }, [fetchJob, pollInterval]);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Start polling when jobId changes
  useEffect(() => {
    if (jobId) {
      startPolling();
    }
    return () => stopPolling();
  }, [jobId]);

  // Update job state when initialJob changes
  useEffect(() => {
    if (initialJob) {
      setJob(initialJob);
      // Start polling for the new job
      if (!intervalRef.current) {
        startPolling();
      }
    }
  }, [initialJob]);

  const cancelJob = useCallback(async () => {
    if (!jobId) return;
    try {
      await jobApi.cancel(jobId);
      await fetchJob();
    } catch (err) {
      setError('Failed to cancel job');
    }
  }, [jobId, fetchJob]);

  return {
    job,
    isLoading,
    error,
    isPolling: intervalRef.current !== null,
    startPolling,
    stopPolling,
    cancelJob,
    refresh: fetchJob,
  };
}
