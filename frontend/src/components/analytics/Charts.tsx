import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
  Legend
} from 'recharts';
import { 
  CoverageTrend, 
  TopIssue, 
  AnalyticsSummary 
} from '@/types';

interface CoverageTrendChartProps {
  data: CoverageTrend[];
  groupBy: 'day' | 'week' | 'month';
}

export const CoverageTrendChart: React.FC<CoverageTrendChartProps> = ({ data, groupBy }) => {
  const formatXAxisLabel = (period: string) => {
    if (groupBy === 'day') {
      return new Date(period).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else if (groupBy === 'week') {
      return `Week ${period.split('-')[1]}`;
    } else {
      return new Date(`${period  }-01`).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Coverage Trends</h3>
        <p className="card-description">
          Accessibility coverage over time
        </p>
      </div>
      <div className="card-content">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="period" 
                tickFormatter={formatXAxisLabel}
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                domain={[0, 100]}
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip 
                formatter={(value: number, name: string) => [
                  `${value.toFixed(1)}%`, 
                  name === 'coverage_percentage' ? 'Coverage' : name
                ]}
                labelFormatter={(period) => `Period: ${formatXAxisLabel(period)}`}
              />
              <Area
                type="monotone"
                dataKey="coverage_percentage"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.2}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

interface ImageCountChartProps {
  data: CoverageTrend[];
  groupBy: 'day' | 'week' | 'month';
}

export const ImageCountChart: React.FC<ImageCountChartProps> = ({ data, groupBy }) => {
  const formatXAxisLabel = (period: string) => {
    if (groupBy === 'day') {
      return new Date(period).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else if (groupBy === 'week') {
      return `Week ${period.split('-')[1]}`;
    } else {
      return new Date(`${period  }-01`).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Image Analysis</h3>
        <p className="card-description">
          Images scanned and accessibility status over time
        </p>
      </div>
      <div className="card-content">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="period" 
                tickFormatter={formatXAxisLabel}
                tick={{ fontSize: 12 }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                formatter={(value: number, name: string) => [
                  value, 
                  name === 'total_images' ? 'Total Images' : 
                  name === 'images_with_alt' ? 'With Alt Text' : 'Missing Alt Text'
                ]}
                labelFormatter={(period) => `Period: ${formatXAxisLabel(period)}`}
              />
              <Legend />
              <Bar dataKey="total_images" fill="#6b7280" name="Total Images" />
              <Bar dataKey="images_with_alt" fill="#22c55e" name="With Alt Text" />
              <Bar dataKey="images_missing_alt" fill="#ef4444" name="Missing Alt Text" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};


interface TopIssuesChartProps {
  data: TopIssue[];
}

export const TopIssuesChart: React.FC<TopIssuesChartProps> = ({ data }) => {
  const COLORS = {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#22c55e'
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Top Accessibility Issues</h3>
        <p className="card-description">
          Most common accessibility problems found
        </p>
      </div>
      <div className="card-content">
        <div className="space-y-4">
          {data.map((issue, index) => (
            <div key={issue.issue} className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <span className="text-lg font-bold text-secondary-600">#{index + 1}</span>
                </div>
                <div>
                  <h4 className="font-medium text-secondary-900">{issue.issue}</h4>
                  <p className="text-sm text-secondary-600">{issue.description}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`badge ${
                  issue.severity === 'high' ? 'badge-error' :
                  issue.severity === 'medium' ? 'badge-warning' : 'badge-success'
                }`}>
                  {issue.severity.toUpperCase()}
                </span>
                <span className="text-2xl font-bold text-secondary-900">{issue.count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

interface SummaryCardsProps {
  data: AnalyticsSummary;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ data }) => {
  const cards = [
    {
      title: 'Total Scans',
      value: data.total_scans,
      icon: '📊',
      color: 'text-primary-600 bg-primary-50',
      description: 'Scans completed'
    },
    {
      title: 'Images Scanned',
      value: data.total_images_scanned,
      icon: '🖼️',
      color: 'text-secondary-600 bg-secondary-50',
      description: 'Total images analyzed'
    },
    {
      title: 'With Alt Text',
      value: data.total_images_with_alt,
      icon: '✅',
      color: 'text-success-600 bg-success-50',
      description: 'Accessible images'
    },
    {
      title: 'Missing Alt Text',
      value: data.total_images_missing_alt,
      icon: '❌',
      color: 'text-error-600 bg-error-50',
      description: 'Images needing attention'
    },
    {
      title: 'Average Coverage',
      value: `${data.average_coverage_percentage}%`,
      icon: '📈',
      color: 'text-primary-600 bg-primary-50',
      description: 'Overall accessibility score'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {cards.map((card, index) => (
        <div key={index} className="card h-full">
          <div className="card-content h-full">
            <div className="flex flex-col h-full pt-2">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-medium text-secondary-600">{card.title}</p>
                <div className={`w-10 h-10 rounded-lg ${card.color} flex items-center justify-center text-lg`}>
                  {card.icon}
                </div>
              </div>
              <div className="flex-1 flex flex-col justify-center">
                <p className="text-2xl font-bold text-secondary-900 mb-1">{card.value}</p>
                <p className="text-xs text-secondary-500">{card.description}</p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

interface ScanFrequencyChartProps {
  data: CoverageTrend[];
  groupBy: 'day' | 'week' | 'month';
}

export const ScanFrequencyChart: React.FC<ScanFrequencyChartProps> = ({ data, groupBy }) => {
  const formatXAxisLabel = (period: string) => {
    if (groupBy === 'day') {
      return new Date(period).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else if (groupBy === 'week') {
      return `Week ${period.split('-')[1]}`;
    } else {
      return new Date(`${period  }-01`).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Scan Activity</h3>
        <p className="card-description">
          Number of scans performed over time
        </p>
      </div>
      <div className="card-content">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="period" 
                tickFormatter={formatXAxisLabel}
                tick={{ fontSize: 12 }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                formatter={(value: number) => [value, 'Scans']}
                labelFormatter={(period) => `Period: ${formatXAxisLabel(period)}`}
              />
              <Line
                type="monotone"
                dataKey="scans"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
