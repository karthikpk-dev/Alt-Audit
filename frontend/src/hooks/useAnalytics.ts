import { useState, useEffect, useCallback } from 'react';
import { 
  AnalyticsSummary, 
  CoverageTrend, 
  TopIssue, 
} from '@/types';
import apiClient from '@/services/api';
import toast from 'react-hot-toast';

interface UseAnalyticsOptions {
  days?: number;
  groupBy?: 'day' | 'week' | 'month';
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const useAnalytics = (options: UseAnalyticsOptions = {}) => {
  const {
    days = 30,
    groupBy = 'day',
    autoRefresh = false,
    refreshInterval = 30000 // 30 seconds
  } = options;

  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [trends, setTrends] = useState<CoverageTrend[]>([]);
  const [topIssues, setTopIssues] = useState<TopIssue[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    try {
      const data = await apiClient.getAnalyticsSummary(days);
      setSummary(data);
    } catch (err) {
      // Error handled by toast notification
      setError('Failed to load analytics summary');
    }
  }, [days]);

  const fetchTrends = useCallback(async () => {
    try {
      const data = await apiClient.getCoverageTrends(days, groupBy);
      setTrends(data);
    } catch (err) {
      // Error handled by toast notification
      setError('Failed to load coverage trends');
    }
  }, [days, groupBy]);

  const fetchTopIssues = useCallback(async () => {
    try {
      const data = await apiClient.getTopIssues(days, 10);
      setTopIssues(data);
    } catch (err) {
      // Error handled by toast notification
      setError('Failed to load top issues');
    }
  }, [days]);


  const fetchAll = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        fetchSummary(),
        fetchTrends(),
        fetchTopIssues()
      ]);
    } catch (err) {
      // Error handled by toast notification
      setError('Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  }, [days, groupBy]);

  const refresh = useCallback(() => {
    fetchAll();
  }, [fetchAll]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(fetchAll, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, fetchAll]);

  return {
    summary,
    trends,
    topIssues,
    isLoading,
    error,
    refresh,
    fetchSummary,
    fetchTrends,
    fetchTopIssues
  };
};

export const useCoverageTrends = (days: number = 30, groupBy: 'day' | 'week' | 'month' = 'day') => {
  const [data, setData] = useState<CoverageTrend[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const trends = await apiClient.getCoverageTrends(days, groupBy);
      setData(trends);
    } catch (err) {
      // Error handled by toast notification
      setError('Failed to load coverage trends');
    } finally {
      setIsLoading(false);
    }
  }, [days, groupBy]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    refresh: fetchData
  };
};

export const useTopIssues = (days: number = 30, limit: number = 10) => {
  const [data, setData] = useState<TopIssue[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const issues = await apiClient.getTopIssues(days, limit);
      setData(issues);
    } catch (err) {
      // Error handled by toast notification
      setError('Failed to load top issues');
    } finally {
      setIsLoading(false);
    }
  }, [days, limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    refresh: fetchData
  };
};


export const useAnalyticsSummary = (days: number = 30) => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const summary = await apiClient.getAnalyticsSummary(days);
      setData(summary);
    } catch (err) {
      // Error handled by toast notification
      setError('Failed to load analytics summary');
    } finally {
      setIsLoading(false);
    }
  }, [days]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    refresh: fetchData
  };
};
