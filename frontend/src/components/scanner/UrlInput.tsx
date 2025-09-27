import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Globe, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import apiClient from '@/services/api';
import toast from 'react-hot-toast';

const urlSchema = z.object({
  url: z
    .string()
    .min(1, 'URL is required')
    .url('Please enter a valid URL')
    .refine(
      (url) => url.startsWith('http://') || url.startsWith('https://'),
      'URL must start with http:// or https://'
    ),
});

type UrlFormData = z.infer<typeof urlSchema>;

interface UrlInputProps {
  onScanComplete?: (scanId: number) => void;
  onScanStart?: () => void;
}

const UrlInput: React.FC<UrlInputProps> = ({ onScanComplete, onScanStart }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState<'idle' | 'scanning' | 'completed' | 'error'>('idle');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<UrlFormData>({
    resolver: zodResolver(urlSchema),
  });

  const onSubmit = async (data: UrlFormData) => {
    try {
      setIsScanning(true);
      setScanStatus('scanning');
      onScanStart?.();

      // Create scan
      const scan = await apiClient.createScan({ url: data.url });
      
      setScanStatus('completed');
      toast.success('Scan started successfully!');
      
      // Reset form
      reset();
      
      // Notify parent component
      onScanComplete?.(scan.id);
      
    } catch (error) {
      setScanStatus('error');
      toast.error('Failed to start scan. Please try again.');
    } finally {
      setIsScanning(false);
    }
  };

  const getStatusIcon = () => {
    switch (scanStatus) {
      case 'scanning':
        return <Loader2 className="h-5 w-5 animate-spin text-primary-600" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success-600" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-error-600" />;
      default:
        return <Globe className="h-5 w-5 text-secondary-500" />;
    }
  };

  const getStatusMessage = () => {
    switch (scanStatus) {
      case 'scanning':
        return 'Scanning in progress...';
      case 'completed':
        return 'Scan completed successfully!';
      case 'error':
        return 'Scan failed. Please try again.';
      default:
        return 'Enter a URL to start scanning';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="card">
        <div className="card-header text-center">
          <h2 className="card-title">Scan Website for Accessibility</h2>
          <p className="card-description">
            Enter a URL to analyze images and their alt text attributes
          </p>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="card-content space-y-6">
          <div className="space-y-2">
            <label htmlFor="url" className="label">
              Website URL
            </label>
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 h-5 w-5" />
              <input
                {...register('url')}
                type="url"
                id="url"
                className="input pl-10 pr-4"
                placeholder="https://example.com"
                disabled={isSubmitting || isScanning}
              />
            </div>
            {errors.url && (
              <p className="text-sm text-error-600">{errors.url.message}</p>
            )}
          </div>

          {/* Status indicator */}
          <div className="flex items-center justify-center space-x-2 p-4 bg-secondary-50 rounded-lg">
            {getStatusIcon()}
            <span className="text-sm text-secondary-700">
              {getStatusMessage()}
            </span>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || isScanning}
            className="btn btn-primary btn-lg w-full"
          >
            {isSubmitting || isScanning ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                {isScanning ? 'Scanning...' : 'Starting Scan...'}
              </>
            ) : (
              <>
                <Globe className="mr-2 h-5 w-5" />
                Start Scan
              </>
            )}
          </button>
        </form>

        <div className="card-footer">
          <div className="text-sm text-secondary-600 text-center w-full">
            <p className="mb-2">
              <strong>What we scan:</strong>
            </p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>All images on the webpage</li>
              <li>Alt text presence and quality</li>
              <li>Decorative vs. content images</li>
              <li>Accessibility compliance metrics</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UrlInput;
