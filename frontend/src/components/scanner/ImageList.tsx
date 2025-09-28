import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Image as ImageIcon,
  ExternalLink,
  Filter,
  Search,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { ImageDetail, ImageFilters } from '@/types';
import apiClient from '@/services/api';
import toast from 'react-hot-toast';

interface ImageListProps {
  scanId: number;
}

const ImageList: React.FC<ImageListProps> = ({ scanId }) => {
  const [images, setImages] = useState<ImageDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<ImageFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const pageSize = 20;

  useEffect(() => {
    fetchImages();
  }, [scanId, filters, currentPage]);

  const fetchImages = async () => {
    try {
      setIsLoading(true);
      const imageData = await apiClient.getScanImages(scanId, {
        skip: currentPage * pageSize,
        limit: pageSize,
      }, filters);
      
      if (currentPage === 0) {
        setImages(imageData);
      } else {
        setImages(prev => [...prev, ...imageData]);
      }
      
      setHasMore(imageData.length === pageSize);
    } catch (error) {
      toast.error('Failed to load images');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (newFilters: Partial<ImageFilters>) => {
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

  const getAltTextQuality = (image: ImageDetail) => {
    if (!image.has_alt_text) {return 'missing';}
    if (image.is_decorative) {return 'decorative';}
    if (!image.alt_text_length || image.alt_text_length < 5) {return 'poor';}
    if (image.alt_text_length > 125) {return 'too-long';}
    return 'good';
  };

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'missing':
        return 'text-error-600 bg-error-100';
      case 'decorative':
        return 'text-secondary-600 bg-secondary-100';
      case 'poor':
        return 'text-warning-600 bg-warning-100';
      case 'too-long':
        return 'text-warning-600 bg-warning-100';
      case 'good':
        return 'text-success-600 bg-success-100';
      default:
        return 'text-secondary-600 bg-secondary-100';
    }
  };

  const getQualityIcon = (quality: string) => {
    switch (quality) {
      case 'missing':
        return <XCircle className="h-4 w-4" />;
      case 'decorative':
        return <ImageIcon className="h-4 w-4" />;
      case 'poor':
      case 'too-long':
        return <AlertTriangle className="h-4 w-4" />;
      case 'good':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <ImageIcon className="h-4 w-4" />;
    }
  };

  const filteredImages = images.filter(image => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        image.image_url.toLowerCase().includes(searchLower) ||
        (image.alt_text && image.alt_text.toLowerCase().includes(searchLower))
      );
    }
    return true;
  });

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="card-title">Image Analysis</h3>
            <p className="card-description">
              Detailed analysis of each image found on the page
            </p>
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn btn-outline btn-sm"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
            {showFilters ? <ChevronUp className="h-4 w-4 ml-2" /> : <ChevronDown className="h-4 w-4 ml-2" />}
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
                  placeholder="Search images or alt text..."
                />
              </div>
            </div>
            
            <div>
              <label className="label">Alt Text</label>
              <select
                value={filters.has_alt_only ? 'true' : filters.has_alt_only === false ? 'false' : ''}
                onChange={(e) => {
                  const value = e.target.value;
                  handleFilterChange({
                    has_alt_only: value === '' ? undefined : value === 'true'
                  });
                }}
                className="input"
              >
                <option value="">All Images</option>
                <option value="true">With Alt Text</option>
                <option value="false">Missing Alt Text</option>
              </select>
            </div>
            
          </div>
        </div>
      )}

      <div className="card-content">
        {isLoading && images.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary-600 border-t-transparent mr-2" />
            <span>Loading images...</span>
          </div>
        ) : filteredImages.length === 0 ? (
          <div className="text-center py-8">
            <ImageIcon className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
            <p className="text-secondary-600">
              {searchTerm ? 'No images match your search' : 'No images found'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredImages.map((image) => {
              const quality = getAltTextQuality(image);
              return (
                <div
                  key={image.id}
                  className="border border-secondary-200 rounded-lg p-4 hover:bg-secondary-50 transition-colors"
                >
                  <div className="flex items-start space-x-4">
                    {/* Image Preview */}
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 bg-secondary-100 rounded-lg flex items-center justify-center overflow-hidden">
                        <img
                          src={image.image_url}
                          alt=""
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            target.nextElementSibling?.classList.remove('hidden');
                          }}
                        />
                        <div className="hidden text-secondary-400">
                          <ImageIcon className="h-6 w-6" />
                        </div>
                      </div>
                    </div>

                    {/* Image Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className={`badge ${getQualityColor(quality)}`}>
                              {getQualityIcon(quality)}
                              <span className="ml-1 capitalize">{quality.replace('-', ' ')}</span>
                            </span>
                            {image.is_decorative && (
                              <span className="badge badge-secondary">Decorative</span>
                            )}
                          </div>
                          
                          <p className="text-sm text-secondary-600 break-all mb-2">
                            {image.image_url}
                          </p>
                          
                          {image.alt_text && (
                            <div className="bg-secondary-50 rounded p-2 mb-2">
                              <p className="text-sm font-medium text-secondary-700 mb-1">Alt Text:</p>
                              <p className="text-sm text-secondary-600">"{image.alt_text}"</p>
                              {image.alt_text_length && (
                                <p className="text-xs text-secondary-500 mt-1">
                                  {image.alt_text_length} characters
                                </p>
                              )}
                            </div>
                          )}
                          
                          <div className="flex items-center space-x-4 text-xs text-secondary-500">
                            {image.image_width && image.image_height && (
                              <span>{image.image_width} × {image.image_height}px</span>
                            )}
                            <span>
                              {new Date(image.created_at).toLocaleString()}
                            </span>
                          </div>
                        </div>
                        
                        <a
                          href={image.image_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-ghost btn-sm"
                          title="Open image in new tab"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
            
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
                    'Load More Images'
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

export default ImageList;
