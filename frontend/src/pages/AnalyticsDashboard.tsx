import React, { useState } from 'react';
import { 
  BarChart3, 
  Calendar, 
  Download, 
  RefreshCw, 
  Filter,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowLeft
} from 'lucide-react';
import { useAnalytics } from '@/hooks/useAnalytics';
import {
  SummaryCards,
  CoverageTrendChart,
  ImageCountChart,
  TopIssuesChart,
  ScanFrequencyChart
} from '@/components/analytics/Charts';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import apiClient from '@/services/api';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const AnalyticsDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [days, setDays] = useState(30);
  const [groupBy, setGroupBy] = useState<'day' | 'week' | 'month'>('day');

  const {
    summary,
    trends,
    topIssues,
    isLoading,
    error,
    refresh
  } = useAnalytics({ days, groupBy, autoRefresh: false });


  const handleRefresh = () => {
    refresh();
    toast.success('Analytics data refreshed');
  };

  if (isLoading && !summary) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading analytics..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-secondary-900 mb-2">Error Loading Analytics</h2>
          <p className="text-secondary-600 mb-4">{error}</p>
          <button onClick={handleRefresh} className="btn btn-primary" data-refresh>
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-secondary-900 flex items-center">
                <BarChart3 className="h-6 w-6 mr-2" />
                Analytics Dashboard
              </h1>
              <p className="text-secondary-600 mt-1">
                Track your accessibility improvements and insights
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="btn btn-ghost btn-sm"
                title="Back to Dashboard"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </button>
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="btn btn-outline btn-sm"
                data-refresh
                title="Refresh data"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="card mb-6">
          <div className="card-content py-4">
            <div className="flex flex-wrap items-center gap-6">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-secondary-500" />
                <span className="text-sm font-medium text-secondary-700">Filters:</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <label className="text-sm font-medium text-secondary-600 whitespace-nowrap">Time Period:</label>
                <select
                  value={days}
                  onChange={(e) => setDays(Number(e.target.value))}
                  className="input min-w-[140px]"
                >
                  <option value={7}>Last 7 days</option>
                  <option value={30}>Last 30 days</option>
                  <option value={90}>Last 90 days</option>
                  <option value={365}>Last year</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-3">
                <label className="text-sm font-medium text-secondary-600 whitespace-nowrap">Group By:</label>
                <select
                  value={groupBy}
                  onChange={(e) => setGroupBy(e.target.value as 'day' | 'week' | 'month')}
                  className="input min-w-[100px]"
                >
                  <option value="day">Day</option>
                  <option value="week">Week</option>
                  <option value="month">Month</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        {summary && <SummaryCards data={summary} />}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Coverage Trends */}
          {trends.length > 0 && (
            <div className="lg:col-span-2">
              <CoverageTrendChart data={trends} groupBy={groupBy} />
            </div>
          )}

          {/* Image Count Chart */}
          {trends.length > 0 && (
            <div className="lg:col-span-2">
              <ImageCountChart data={trends} groupBy={groupBy} />
            </div>
          )}

          {/* Scan Frequency */}
          {trends.length > 0 && (
            <div className="lg:col-span-2">
              <ScanFrequencyChart data={trends} groupBy={groupBy} />
            </div>
          )}

        </div>

        {/* Top Issues */}
        {topIssues.length > 0 && (
          <div className="mt-6">
            <TopIssuesChart data={topIssues} />
          </div>
        )}

        {/* Insights Section */}
        {summary && (
          <div className="mt-6">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Key Insights</h3>
                <p className="card-description">
                  Automated insights based on your scan data
                </p>
              </div>
              <div className="card-content">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {summary.average_coverage_percentage >= 80 && (
                    <div className="flex items-start space-x-3 p-4 bg-success-50 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-success-900">Excellent Coverage</h4>
                        <p className="text-sm text-success-700">
                          Your average coverage of {summary.average_coverage_percentage}% is excellent!
                        </p>
                      </div>
                    </div>
                  )}

                  {summary.average_coverage_percentage < 50 && (
                    <div className="flex items-start space-x-3 p-4 bg-error-50 rounded-lg">
                      <AlertTriangle className="h-5 w-5 text-error-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-error-900">Needs Improvement</h4>
                        <p className="text-sm text-error-700">
                          Your coverage of {summary.average_coverage_percentage}% needs attention.
                        </p>
                      </div>
                    </div>
                  )}

                  {summary.total_scans > 0 && (
                    <div className="flex items-start space-x-3 p-4 bg-primary-50 rounded-lg">
                      <TrendingUp className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-primary-900">Active Scanning</h4>
                        <p className="text-sm text-primary-700">
                          You've completed {summary.total_scans} scans in the last {days} days.
                        </p>
                      </div>
                    </div>
                  )}

                  {summary.total_images_missing_alt > 0 && (
                    <div className="flex items-start space-x-3 p-4 bg-warning-50 rounded-lg">
                      <Clock className="h-5 w-5 text-warning-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-warning-900">Action Required</h4>
                        <p className="text-sm text-warning-700">
                          {summary.total_images_missing_alt} images need alt text.
                        </p>
                      </div>
                    </div>
                  )}

                  {summary.most_common_issues.length > 0 && (
                    <div className="flex items-start space-x-3 p-4 bg-secondary-50 rounded-lg">
                      <BarChart3 className="h-5 w-5 text-secondary-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-secondary-900">Common Issues</h4>
                        <p className="text-sm text-secondary-700">
                          Top issue: {summary.most_common_issues[0]}
                        </p>
                      </div>
                    </div>
                  )}

                  {summary.total_images_scanned > 1000 && (
                    <div className="flex items-start space-x-3 p-4 bg-primary-50 rounded-lg">
                      <BarChart3 className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-primary-900">High Volume</h4>
                        <p className="text-sm text-primary-700">
                          You've analyzed {summary.total_images_scanned} images - great dedication!
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {summary && summary.total_scans === 0 && (
          <div className="mt-6">
            <div className="card">
              <div className="card-content">
                <div className="text-center py-12">
                  <BarChart3 className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">No Data Yet</h3>
                  <p className="text-secondary-600 mb-4">
                    Start scanning URLs to see your analytics data here.
                  </p>
                  <button className="btn btn-primary">
                    Start Your First Scan
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
