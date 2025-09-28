import React, { useState, useEffect } from 'react';
import { X, BarChart3, PieChart, TrendingUp } from 'lucide-react';
import { ScanResultSummary } from '@/types';
import apiClient from '@/services/api';
import toast from 'react-hot-toast';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

interface ScanChartModalProps {
  isOpen: boolean;
  onClose: () => void;
  scan: ScanResultSummary | null;
}

const ScanChartModal: React.FC<ScanChartModalProps> = ({ isOpen, onClose, scan }) => {
  const [chartType, setChartType] = useState<'bar' | 'pie'>('bar');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen || !scan) return null;

  // Prepare data for charts
  const chartData = [
    {
      name: 'With Alt Text',
      value: scan.images_with_alt,
      color: '#22c55e'
    },
    {
      name: 'Missing Alt Text',
      value: scan.images_missing_alt,
      color: '#ef4444'
    }
  ];

  const barChartData = [
    {
      category: 'Accessibility Status',
      'With Alt Text': scan.images_with_alt,
      'Missing Alt Text': scan.images_missing_alt
    }
  ];

  const COLORS = ['#22c55e', '#ef4444'];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-secondary-200">
          <div className="flex items-center space-x-3">
            <BarChart3 className="h-6 w-6 text-primary-600" />
            <div>
              <h2 className="text-xl font-semibold text-secondary-900">Scan Analytics</h2>
              <p className="text-sm text-secondary-600 truncate max-w-md" title={scan.url}>
                {scan.url}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-secondary-400 hover:text-secondary-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-primary-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-primary-600">Total Images</p>
                  <p className="text-2xl font-bold text-primary-900">{scan.total_images}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-primary-600" />
              </div>
            </div>
            
            <div className="bg-success-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-success-600">With Alt Text</p>
                  <p className="text-2xl font-bold text-success-900">{scan.images_with_alt}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-success-600" />
              </div>
            </div>
            
            <div className="bg-error-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-error-600">Missing Alt Text</p>
                  <p className="text-2xl font-bold text-error-900">{scan.images_missing_alt}</p>
                </div>
                <X className="h-8 w-8 text-error-600" />
              </div>
            </div>
            
            <div className="bg-secondary-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-secondary-600">Coverage</p>
                  <p className="text-2xl font-bold text-secondary-900">{scan.alt_text_coverage_percentage}%</p>
                </div>
                <PieChart className="h-8 w-8 text-secondary-600" />
              </div>
            </div>
          </div>

          {/* Chart Type Toggle */}
          <div className="flex items-center justify-center mb-6">
            <div className="bg-secondary-100 p-1 rounded-lg">
              <button
                onClick={() => setChartType('bar')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  chartType === 'bar'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-secondary-600 hover:text-secondary-900'
                }`}
              >
                Bar Chart
              </button>
              <button
                onClick={() => setChartType('pie')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  chartType === 'pie'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-secondary-600 hover:text-secondary-900'
                }`}
              >
                Pie Chart
              </button>
            </div>
          </div>

          {/* Chart */}
          <div className="bg-white border border-secondary-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4 text-center">
              Image Accessibility Distribution
            </h3>
            
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                {chartType === 'bar' ? (
                  <BarChart data={barChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="category" 
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip 
                      formatter={(value: number, name: string) => [
                        value, 
                        name === 'With Alt Text' ? 'With Alt Text' : 'Missing Alt Text'
                      ]}
                    />
                    <Legend />
                    <Bar dataKey="With Alt Text" fill="#22c55e" />
                    <Bar dataKey="Missing Alt Text" fill="#ef4444" />
                  </BarChart>
                ) : (
                  <RechartsPieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value: number) => [value, 'Images']}
                    />
                    <Legend />
                  </RechartsPieChart>
                )}
              </ResponsiveContainer>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-secondary-50 p-4 rounded-lg">
              <h4 className="font-semibold text-secondary-900 mb-2">Scan Details</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-secondary-600">Status:</span>
                  <span className={`font-medium ${
                    scan.scan_status === 'completed' ? 'text-success-600' : 'text-error-600'
                  }`}>
                    {scan.scan_status.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Scanned:</span>
                  <span className="text-secondary-900">
                    {new Date(scan.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Coverage:</span>
                  <span className="text-secondary-900">
                    {scan.alt_text_coverage_percentage}%
                  </span>
                </div>
              </div>
            </div>
            
            <div className="bg-secondary-50 p-4 rounded-lg">
              <h4 className="font-semibold text-secondary-900 mb-2">Accessibility Score</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-secondary-600">Overall Score</span>
                  <span className={`text-lg font-bold ${
                    scan.alt_text_coverage_percentage >= 80 ? 'text-success-600' :
                    scan.alt_text_coverage_percentage >= 60 ? 'text-warning-600' : 'text-error-600'
                  }`}>
                    {scan.alt_text_coverage_percentage}%
                  </span>
                </div>
                <div className="w-full bg-secondary-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      scan.alt_text_coverage_percentage >= 80 ? 'bg-success-500' :
                      scan.alt_text_coverage_percentage >= 60 ? 'bg-warning-500' : 'bg-error-500'
                    }`}
                    style={{ width: `${scan.alt_text_coverage_percentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-secondary-500">
                  {scan.alt_text_coverage_percentage >= 80 ? 'Excellent accessibility' :
                   scan.alt_text_coverage_percentage >= 60 ? 'Good accessibility' : 'Needs improvement'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-secondary-200 bg-secondary-50">
          <button
            onClick={onClose}
            className="btn btn-outline btn-md"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ScanChartModal;
