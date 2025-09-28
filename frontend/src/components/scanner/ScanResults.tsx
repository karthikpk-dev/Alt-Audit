import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  Image, 
  RefreshCw,
  Trash2,
  Download,
  Eye,
  BarChart3
} from 'lucide-react';
import { ScanResult, ScanResultSummary } from '@/types';
import apiClient from '@/services/api';
import toast from 'react-hot-toast';
import ImageList from './ImageList';
import ScanChartModal from './ScanChartModal';

interface ScanResultsProps {
  scanId: number;
  onScanUpdate?: (scan: ScanResult) => void;
  onScanDelete?: (scanId: number) => void;
}

const ScanResults: React.FC<ScanResultsProps> = ({ 
  scanId, 
  onScanUpdate, 
  onScanDelete 
}) => {
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRetrying, setIsRetrying] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showImages, setShowImages] = useState(false);
  const [showChartModal, setShowChartModal] = useState(false);

  useEffect(() => {
    fetchScanDetails();
  }, [scanId]);

  const fetchScanDetails = async () => {
    try {
      setIsLoading(true);
      const scanData = await apiClient.getScan(scanId);
      setScan(scanData);
      onScanUpdate?.(scanData);
    } catch (error) {
      toast.error('Failed to load scan details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = async () => {
    try {
      setIsRetrying(true);
      const updatedScan = await apiClient.retryScan(scanId);
      setScan(updatedScan);
      onScanUpdate?.(updatedScan);
      toast.success('Scan retried successfully');
    } catch (error) {
      toast.error('Failed to retry scan');
    } finally {
      setIsRetrying(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this scan?')) {
      return;
    }

    try {
      setIsDeleting(true);
      await apiClient.deleteScan(scanId);
      onScanDelete?.(scanId);
      toast.success('Scan deleted successfully');
    } catch (error) {
      toast.error('Failed to delete scan');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await apiClient.exportScanDetailsCSV(scanId);
      const filename = `scan_${scanId}_${scan?.url.replace(/[^a-zA-Z0-9]/g, '_')}.csv`;
      apiClient.downloadBlob(blob, filename);
      toast.success('Export started');
    } catch (error) {
      toast.error('Failed to export scan data');
    }
  };

  const handleShowChart = () => {
    setShowChartModal(true);
  };

  const handleCloseChart = () => {
    setShowChartModal(false);
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
        return <AlertTriangle className="h-5 w-5 text-secondary-600" />;
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

  if (isLoading) {
    return (
      <div className="card">
        <div className="card-content">
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-primary-600 mr-2" />
            <span>Loading scan details...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!scan) {
    return (
      <div className="card">
        <div className="card-content">
          <div className="text-center py-8">
            <XCircle className="h-12 w-12 text-error-500 mx-auto mb-4" />
            <p className="text-error-600">Failed to load scan details</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Scan Header */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getStatusIcon(scan.scan_status)}
              <div>
                <h3 className="card-title text-lg">Scan Results</h3>
                <p className="text-sm text-secondary-600 break-all">
                  {scan.url}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`badge ${getStatusColor(scan.scan_status)}`}>
                {scan.scan_status.toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        <div className="card-content">
          {/* Error Message */}
          {scan.error_message && (
            <div className="mb-4 p-4 bg-error-50 border border-error-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <AlertTriangle className="h-5 w-5 text-error-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-error-800">Scan Error</p>
                  <p className="text-sm text-error-700 mt-1">{scan.error_message}</p>
                </div>
              </div>
            </div>
          )}

          {/* Scan Statistics */}
          {scan.scan_status === 'completed' && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-secondary-50 rounded-lg">
                <Image className="h-8 w-8 text-primary-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-secondary-900">{scan.total_images}</p>
                <p className="text-sm text-secondary-600">Total Images</p>
              </div>
              
              <div className="text-center p-4 bg-success-50 rounded-lg">
                <CheckCircle className="h-8 w-8 text-success-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-success-900">{scan.images_with_alt}</p>
                <p className="text-sm text-success-600">With Alt Text</p>
              </div>
              
              <div className="text-center p-4 bg-error-50 rounded-lg">
                <XCircle className="h-8 w-8 text-error-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-error-900">{scan.images_missing_alt}</p>
                <p className="text-sm text-error-600">Missing Alt Text</p>
              </div>
              
              <div className="text-center p-4 bg-primary-50 rounded-lg">
                <div className="h-8 w-8 text-primary-600 mx-auto mb-2 flex items-center justify-center">
                  <span className="text-lg font-bold">{scan.alt_text_coverage_percentage}%</span>
                </div>
                <p className="text-sm text-primary-600">Coverage</p>
              </div>
            </div>
          )}

          {/* Progress Bar */}
          {scan.scan_status === 'completed' && (
            <div className="mb-6">
              <div className="flex justify-between text-sm text-secondary-600 mb-2">
                <span>Accessibility Coverage</span>
                <span>{scan.alt_text_coverage_percentage}%</span>
              </div>
              <div className="w-full bg-secondary-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${scan.alt_text_coverage_percentage}%` }}
                />
              </div>
            </div>
          )}

          {/* Scan Metadata */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-secondary-600">
            <div>
              <span className="font-medium">Created:</span> {new Date(scan.created_at).toLocaleString()}
            </div>
            {scan.scan_duration_ms && (
              <div>
                <span className="font-medium">Duration:</span> {scan.scan_duration_ms}ms
              </div>
            )}
          </div>
        </div>

        <div className="card-footer">
          <div className="flex flex-wrap gap-2">
            {scan.scan_status === 'completed' && (
              <>
                <button
                  onClick={() => setShowImages(!showImages)}
                  className="btn btn-outline btn-sm"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  {showImages ? 'Hide' : 'View'} Images
                </button>
                <button
                  onClick={handleShowChart}
                  className="btn btn-outline btn-sm"
                  title="View charts and analytics for this scan"
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Scan Charts
                </button>
                <button
                  onClick={handleExport}
                  className="btn btn-outline btn-sm"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </button>
              </>
            )}
            
            {scan.scan_status === 'failed' && (
              <button
                onClick={handleRetry}
                disabled={isRetrying}
                className="btn btn-primary btn-sm"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isRetrying ? 'animate-spin' : ''}`} />
                Retry Scan
              </button>
            )}
            
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="btn btn-ghost btn-sm text-error-600 hover:text-error-700"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Image List */}
      {showImages && scan.scan_status === 'completed' && (
        <ImageList scanId={scanId} />
      )}

      {/* Chart Modal */}
      {scan && (
        <ScanChartModal
          isOpen={showChartModal}
          onClose={handleCloseChart}
          scan={scan}
        />
      )}
    </div>
  );
};

export default ScanResults;
