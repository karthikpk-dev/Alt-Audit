// API Response Types
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ScanResult {
  id: number;
  url: string;
  total_images: number;
  images_with_alt: number;
  images_missing_alt: number;
  scan_status: 'pending' | 'running' | 'completed' | 'failed';
  error_message?: string;
  scan_duration_ms?: number;
  alt_text_coverage_percentage: number;
  missing_alt_percentage: number;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export interface ScanResultSummary {
  id: number;
  url: string;
  total_images: number;
  images_with_alt: number;
  images_missing_alt: number;
  scan_status: 'pending' | 'running' | 'completed' | 'failed';
  alt_text_coverage_percentage: number;
  created_at: string;
}

export interface ImageDetail {
  id: number;
  scan_result_id: number;
  image_url: string;
  alt_text?: string;
  has_alt_text: boolean;
  alt_text_length?: number;
  image_width?: number;
  image_height?: number;
  is_decorative: boolean;
  created_at: string;
}

export interface AnalyticsSummary {
  total_scans: number;
  total_images_scanned: number;
  total_images_with_alt: number;
  total_images_missing_alt: number;
  average_coverage_percentage: number;
  most_common_issues: string[];
}

export interface CoverageTrend {
  period: string;
  scans: number;
  total_images: number;
  images_with_alt: number;
  images_missing_alt: number;
  coverage_percentage: number;
}

export interface TopIssue {
  issue: string;
  count: number;
  severity: 'high' | 'medium' | 'low';
  description: string;
}


// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
}

export interface ScanForm {
  url: string;
}

export interface UserUpdateForm {
  email?: string;
  username?: string;
}

// API Error Types
export interface ApiError {
  detail: string;
  error_code?: string;
  timestamp?: string;
}

export interface ValidationError {
  detail: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
  error_code: string;
  timestamp: string;
}

// Component Props Types
export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterForm) => Promise<void>;
  logout: () => void;
  updateUser: (data: UserUpdateForm) => Promise<void>;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
}

// Utility Types
export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed';

// Severity type removed - not used

// Chart Data Types - removed unused types

// Pagination Types
export interface PaginationParams {
  skip: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Filter Types
export interface ScanFilters {
  status?: ScanStatus;
  start_date?: string;
  end_date?: string;
  search?: string;
}

export interface ImageFilters {
  has_alt_only?: boolean;
  is_decorative?: boolean;
  min_width?: number;
  max_width?: number;
  min_height?: number;
  max_height?: number;
}
