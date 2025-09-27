import React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { useAnalytics, useCoverageTrends, useTopIssues } from '@/hooks/useAnalytics';
import { mockApiResponse, mockApiError } from '@/tests/test-utils';

// Mock the API client
vi.mock('@/services/api', () => ({
  default: {
    getAnalyticsSummary: vi.fn(),
    getCoverageTrends: vi.fn(),
    getTopIssues: vi.fn(),
  },
}));

describe('useAnalytics', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches analytics data on mount', async () => {
    const mockGetAnalyticsSummary = vi.fn().mockResolvedValue({
      total_scans: 10,
      total_images_scanned: 100,
      total_images_with_alt: 70,
      total_images_missing_alt: 30,
      average_coverage_percentage: 70.0,
      most_common_issues: ['Missing alt text'],
    });

    const mockGetCoverageTrends = vi.fn().mockResolvedValue([
      { period: '2024-01-01', coverage_percentage: 65.0, total_images: 20, images_with_alt: 13, images_missing_alt: 7, scans: 2 },
    ]);

    const mockGetTopIssues = vi.fn().mockResolvedValue([
      { issue: 'Missing alt text', count: 15, severity: 'high', description: 'Images without alt text' },
    ]);

    const mockGetCoverageDistribution = vi.fn().mockResolvedValue({
      distribution: { '0-20%': 1, '21-40%': 2, '41-60%': 3, '61-80%': 2, '81-100%': 2 },
      total_scans: 10,
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.getAnalyticsSummary).mockImplementation(mockGetAnalyticsSummary);
    vi.mocked(require('@/services/api').default.getCoverageTrends).mockImplementation(mockGetCoverageTrends);
    vi.mocked(require('@/services/api').default.getTopIssues).mockImplementation(mockGetTopIssues);

    const { result } = renderHook(() => useAnalytics({ days: 30 }));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.summary).toEqual({
      total_scans: 10,
      total_images_scanned: 100,
      total_images_with_alt: 70,
      total_images_missing_alt: 30,
      average_coverage_percentage: 70.0,
      most_common_issues: ['Missing alt text'],
    });

    expect(result.current.trends).toHaveLength(1);
    expect(result.current.topIssues).toHaveLength(1);
    expect(result.current.distribution).toEqual({
      distribution: { '0-20%': 1, '21-40%': 2, '41-60%': 3, '61-80%': 2, '81-100%': 2 },
      total_scans: 10,
    });
  });

  it('handles API errors gracefully', async () => {
    const mockGetAnalyticsSummary = vi.fn().mockRejectedValue(new Error('API Error'));

    // Mock the API client
    vi.mocked(require('@/services/api').default.getAnalyticsSummary).mockImplementation(mockGetAnalyticsSummary);
    vi.mocked(require('@/services/api').default.getCoverageTrends).mockResolvedValue([]);
    vi.mocked(require('@/services/api').default.getTopIssues).mockResolvedValue([]);

    const { result } = renderHook(() => useAnalytics({ days: 30 }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to load analytics summary');
    expect(result.current.summary).toBeNull();
  });

  it('refreshes data when refresh is called', async () => {
    const mockGetAnalyticsSummary = vi.fn()
      .mockResolvedValueOnce({ total_scans: 5 })
      .mockResolvedValueOnce({ total_scans: 10 });

    // Mock the API client
    vi.mocked(require('@/services/api').default.getAnalyticsSummary).mockImplementation(mockGetAnalyticsSummary);
    vi.mocked(require('@/services/api').default.getCoverageTrends).mockResolvedValue([]);
    vi.mocked(require('@/services/api').default.getTopIssues).mockResolvedValue([]);

    const { result } = renderHook(() => useAnalytics({ days: 30 }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.summary?.total_scans).toBe(5);

    // Call refresh
    result.current.refresh();

    await waitFor(() => {
      expect(result.current.summary?.total_scans).toBe(10);
    });
  });

  it('updates when days parameter changes', async () => {
    const mockGetAnalyticsSummary = vi.fn().mockResolvedValue({ total_scans: 10 });

    // Mock the API client
    vi.mocked(require('@/services/api').default.getAnalyticsSummary).mockImplementation(mockGetAnalyticsSummary);
    vi.mocked(require('@/services/api').default.getCoverageTrends).mockResolvedValue([]);
    vi.mocked(require('@/services/api').default.getTopIssues).mockResolvedValue([]);

    const { result, rerender } = renderHook(
      ({ days }) => useAnalytics({ days }),
      { initialProps: { days: 30 } }
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockGetAnalyticsSummary).toHaveBeenCalledWith(30);

    // Change days parameter
    rerender({ days: 7 });

    await waitFor(() => {
      expect(mockGetAnalyticsSummary).toHaveBeenCalledWith(7);
    });
  });

  it('updates when groupBy parameter changes', async () => {
    const mockGetCoverageTrends = vi.fn().mockResolvedValue([]);

    // Mock the API client
    vi.mocked(require('@/services/api').default.getAnalyticsSummary).mockResolvedValue({ total_scans: 0 });
    vi.mocked(require('@/services/api').default.getCoverageTrends).mockImplementation(mockGetCoverageTrends);
    vi.mocked(require('@/services/api').default.getTopIssues).mockResolvedValue([]);

    const { result, rerender } = renderHook(
      ({ groupBy }) => useAnalytics({ days: 30, groupBy }),
      { initialProps: { groupBy: 'day' } }
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockGetCoverageTrends).toHaveBeenCalledWith(30, 'day');

    // Change groupBy parameter
    rerender({ groupBy: 'week' });

    await waitFor(() => {
      expect(mockGetCoverageTrends).toHaveBeenCalledWith(30, 'week');
    });
  });
});

describe('useCoverageTrends', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches coverage trends data', async () => {
    const mockGetCoverageTrends = vi.fn().mockResolvedValue([
      { period: '2024-01-01', coverage_percentage: 65.0, total_images: 20, images_with_alt: 13, images_missing_alt: 7, scans: 2 },
    ]);

    // Mock the API client
    vi.mocked(require('@/services/api').default.getCoverageTrends).mockImplementation(mockGetCoverageTrends);

    const { result } = renderHook(() => useCoverageTrends(30, 'day'));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toHaveLength(1);
    expect(result.current.data[0].coverage_percentage).toBe(65.0);
  });

  it('handles errors in coverage trends', async () => {
    const mockGetCoverageTrends = vi.fn().mockRejectedValue(new Error('API Error'));

    // Mock the API client
    vi.mocked(require('@/services/api').default.getCoverageTrends).mockImplementation(mockGetCoverageTrends);

    const { result } = renderHook(() => useCoverageTrends(30, 'day'));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to load coverage trends');
    expect(result.current.data).toEqual([]);
  });
});

describe('useTopIssues', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches top issues data', async () => {
    const mockGetTopIssues = vi.fn().mockResolvedValue([
      { issue: 'Missing alt text', count: 15, severity: 'high', description: 'Images without alt text' },
      { issue: 'Empty alt text', count: 8, severity: 'medium', description: 'Images with empty alt text' },
    ]);

    // Mock the API client
    vi.mocked(require('@/services/api').default.getTopIssues).mockImplementation(mockGetTopIssues);

    const { result } = renderHook(() => useTopIssues(30, 10));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data[0].issue).toBe('Missing alt text');
    expect(result.current.data[0].count).toBe(15);
  });

  it('handles errors in top issues', async () => {
    const mockGetTopIssues = vi.fn().mockRejectedValue(new Error('API Error'));

    // Mock the API client
    vi.mocked(require('@/services/api').default.getTopIssues).mockImplementation(mockGetTopIssues);

    const { result } = renderHook(() => useTopIssues(30, 10));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to load top issues');
    expect(result.current.data).toEqual([]);
  });
});
