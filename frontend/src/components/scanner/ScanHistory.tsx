import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  Trash2, 
  Eye,
  ExternalLink,
  Calendar,
  Filter,
  Search
} from 'lucide-react';
import { ScanResultSummary, ScanFilters, ScanStatus } from '@/types';
import apiClient from '@/services/api';
import toast from 'react-hot-toast';

interface ScanHistoryProps {
  onScanSelect?: (scanId: number) => void;
  refreshTrigger?: number;
}

const ScanHistory: React.FC<ScanHistoryProps> = ({ onScanSelect, refreshTrigger }) => {
  const [scans, setScans] = useState<ScanResultSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [filters, setFilters] = useState<ScanFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const pageSize = 10;

  useEffect(() => {
    fetchScans();
  }, [currentPage, filters, refreshTrigger]);

  const fetchScans = async () => {
    try {
      setIsLoading(true);
      const scanData = await apiClient.getScans({
        skip: currentPage * pageSize,
        limit: pageSize,
      }, filters);
      
      if (currentPage === 0) {
        setScans(scanData);
      } else {
        setScans(prev => [...prev, ...scanData]);
      }
      
      setHasMore(scanData.length === pageSize);
    } catch (error) {
      toast.error('Failed to load scan history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (scanId: number) => {
    if (!window.confirm('Are you sure you want to delete this scan?')) {
      return;
    }

    try {
      await apiClient.deleteScan(scanId);
      setScans(prev => prev.filter(scan => scan.id !== scanId));
      toast.success('Scan deleted successfully');
    } catch (error) {
      toast.error('Failed to delete scan');
    }
  };

  const handleFilterChange = (newFilters: Partial<ScanFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setCurrentPage(0);
  };

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    setCurrentPage(0);
  };

  const loadMore = () => {
    setCurrentPage(prev => prev + 1);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success-600" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-error-600" />;
      case 'running':
        return <RefreshCw className="h-5 w-5 text-primary-600 animate-spin" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-warning-600" />;
      default:
        return <Clock className="h-5 w-5 text-secondary-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success-700 bg-success-100';
      case 'failed':
        return 'text-error-700 bg-error-100';
      case 'running':
        return 'text-primary-700 bg-primary-100';
      case 'pending':
        return 'text-warning-700 bg-warning-100';
      default:
        return 'text-secondary-700 bg-secondary-100';
    }
  };

  const filteredScans = scans.filter(scan => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return scan.url.toLowerCase().includes(searchLower);
    }
    return true;
  });

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="card-title">Scan History</h3>
            <p className="card-description">
              Your recent accessibility scans
            </p>
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn btn-outline btn-sm"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="card-content border-b border-secondary-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 h-4 w-4" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="input pl-10"
                  placeholder="Search URLs..."
                />
              </div>
            </div>
            
            <div>
              <label className="label">Status</label>
              <select
                value={filters.status || ''}
                onChange={(e) => {
                  handleFilterChange({
                    status: e.target.value as ScanStatus || undefined
                  });
                }}
                className="input"
              >
                <option value="">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="running">Running</option>
                <option value="pending">Pending</option>
              </select>
            </div>
            
            <div>
              <label className="label">Date Range</label>
              <select
                onChange={(e) => {
                  const value = e.target.value;
                  let startDate: string | undefined;
                  
                  if (value === '7') {
                    startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
                  } else if (value === '30') {
                    startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
                  } else if (value === '90') {
                    startDate = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString();
                  }
                  
                  handleFilterChange({
                    start_date: startDate
                  });
                }}
                className="input"
              >
                <option value="">All Time</option>
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
              </select>
            </div>
          </div>
        </div>
      )}

      <div className="card-content">
        {isLoading && scans.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary-600 border-t-transparent mr-2" />
            <span>Loading scans...</span>
          </div>
        ) : filteredScans.length === 0 ? (
          <div className="text-center py-8">
            <Calendar className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
            <p className="text-secondary-600">
              {searchTerm ? 'No scans match your search' : 'No scans yet'}
            </p>
            <p className="text-sm text-secondary-500 mt-2">
              Start by scanning a URL above
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredScans.map((scan) => (
              <div
                key={scan.id}
                className="border border-secondary-200 rounded-lg p-4 hover:bg-secondary-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(scan.scan_status)}
                      <span className={`badge ${getStatusColor(scan.scan_status)}`}>
                        {scan.scan_status.toUpperCase()}
                      </span>
                      {scan.scan_status === 'completed' && (
                        <span className="text-sm text-secondary-600">
                          {scan.alt_text_coverage_percentage}% coverage
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-secondary-600 break-all mb-2">
                      {scan.url}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-xs text-secondary-500">
                      <span>{scan.total_images} images</span>
                      {scan.scan_status === 'completed' && (
                        <>
                          <span className="text-success-600">{scan.images_with_alt} with alt</span>
                          <span className="text-error-600">{scan.images_missing_alt} missing</span>
                        </>
                      )}
                      <span>{new Date(scan.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    {scan.scan_status === 'completed' && (
                      <button
                        onClick={() => onScanSelect?.(scan.id)}
                        className="btn btn-ghost btn-sm"
                        title="View details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    )}
                    
                    <a
                      href={scan.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-ghost btn-sm"
                      title="Open URL"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                    
                    <button
                      onClick={() => handleDelete(scan.id)}
                      className="btn btn-ghost btn-sm text-error-600 hover:text-error-700"
                      title="Delete scan"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Load More Button */}
            {hasMore && (
              <div className="text-center pt-4">
                <button
                  onClick={loadMore}
                  disabled={isLoading}
                  className="btn btn-outline btn-md"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-600 border-t-transparent mr-2" />
                      Loading...
                    </>
                  ) : (
                    'Load More Scans'
                  )}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ScanHistory;
