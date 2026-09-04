/**
 * SafeSlope-NER — Generic polling hook
 * Calls `fetcher` immediately on mount and then every `intervalMs` milliseconds.
 * Returns { data, error, isLoading, refetch }.
 */
import { useCallback, useEffect, useRef, useState } from 'react';

interface UsePollingResult<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  refetch: () => void;
}

export function usePolling<T>(
  fetcher: () => Promise<T>,
  intervalMs: number = 30_000,
  enabled: boolean = true
): UsePollingResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const fetcherRef = useRef(fetcher);

  // Keep the ref in sync so we always call the latest version
  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  const doFetch = useCallback(async () => {
    try {
      setError(null);
      const result = await fetcherRef.current();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!enabled) return;

    doFetch();
    const id = setInterval(doFetch, intervalMs);
    return () => clearInterval(id);
  }, [enabled, intervalMs, doFetch]);

  return { data, error, isLoading, refetch: doFetch };
}
