import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';
import { 
  User, 
  Token, 
  ScanResult, 
  ScanResultSummary, 
  ImageDetail, 
  AnalyticsSummary, 
  CoverageTrend, 
  TopIssue, 
  LoginForm,
  RegisterForm,
  UserUpdateForm,
  ScanForm,
  ScanFilters,
  ImageFilters,
  PaginationParams,
  ApiError,
  ValidationError
} from '@/types';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage
    this.token = localStorage.getItem('access_token');
    if (this.token) {
      this.setAuthToken(this.token);
    }

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }

  private handleError(error: any) {
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          this.clearAuth();
          toast.error('Session expired. Please log in again.');
          break;
        case 403:
          toast.error('Access denied. You do not have permission to perform this action.');
          break;
        case 404:
          toast.error('Resource not found.');
          break;
        case 422:
          if (data.detail && Array.isArray(data.detail)) {
            // Validation errors
            const validationError = data as ValidationError;
            const errorMessages = validationError.detail.map(err => 
              `${err.loc.join('.')}: ${err.msg}`
            ).join(', ');
            toast.error(`Validation error: ${errorMessages}`);
          } else {
            toast.error('Invalid data provided.');
          }
          break;
        case 429:
          toast.error('Too many requests. Please try again later.');
          break;
        case 500:
          toast.error('Server error. Please try again later.');
          break;
        default:
          const apiError = data as ApiError;
          toast.error(apiError.detail || 'An unexpected error occurred.');
      }
    } else if (error.request) {
      toast.error('Network error. Please check your connection.');
    } else {
      toast.error('An unexpected error occurred.');
    }
  }

  setAuthToken(token: string) {
    this.token = token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('access_token', token);
  }

  clearAuth() {
    this.token = null;
    delete this.client.defaults.headers.common['Authorization'];
    localStorage.removeItem('access_token');
  }

  // Auth endpoints
  async login(credentials: LoginForm): Promise<Token> {
    const response = await this.client.post<Token>('/auth/login-json', credentials);
    const token = response.data;
    this.setAuthToken(token.access_token);
    return token;
  }

  async register(userData: RegisterForm): Promise<User> {
    const response = await this.client.post<User>('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  async updateUser(userData: UserUpdateForm): Promise<User> {
    const response = await this.client.put<User>('/auth/me', userData);
    return response.data;
  }

  async refreshToken(): Promise<Token> {
    const response = await this.client.post<Token>('/auth/refresh');
    const token = response.data;
    this.setAuthToken(token.access_token);
    return token;
  }

  async logout(): Promise<void> {
    this.clearAuth();
  }

  // Scan endpoints
  async createScan(scanData: ScanForm): Promise<ScanResult> {
    const response = await this.client.post<ScanResult>('/scans/', scanData);
    return response.data;
  }

  async getScans(
    pagination: PaginationParams = { skip: 0, limit: 10 },
    filters: ScanFilters = {}
  ): Promise<ScanResultSummary[]> {
    const params = new URLSearchParams();
    params.append('skip', pagination.skip.toString());
    params.append('limit', pagination.limit.toString());
    
    if (filters.status) {params.append('status_filter', filters.status);}
    if (filters.start_date) {params.append('start_date', filters.start_date);}
    if (filters.end_date) {params.append('end_date', filters.end_date);}

    const response = await this.client.get<ScanResultSummary[]>(`/scans/?${params}`);
    return response.data;
  }

  async getScan(scanId: number): Promise<ScanResult> {
    const response = await this.client.get<ScanResult>(`/scans/${scanId}`);
    return response.data;
  }

  async getScanImages(
    scanId: number,
    pagination: PaginationParams = { skip: 0, limit: 50 },
    filters: ImageFilters = {}
  ): Promise<ImageDetail[]> {
    const params = new URLSearchParams();
    params.append('skip', pagination.skip.toString());
    params.append('limit', pagination.limit.toString());
    
    if (filters.has_alt_only !== undefined) {params.append('has_alt_only', filters.has_alt_only.toString());}

    const response = await this.client.get<ImageDetail[]>(`/scans/${scanId}/images?${params}`);
    return response.data;
  }

  async deleteScan(scanId: number): Promise<void> {
    await this.client.delete(`/scans/${scanId}`);
  }

  async retryScan(scanId: number): Promise<ScanResult> {
    const response = await this.client.post<ScanResult>(`/scans/${scanId}/retry`);
    return response.data;
  }

  // Analytics endpoints
  async getAnalyticsSummary(days: number = 30): Promise<AnalyticsSummary> {
    const response = await this.client.get<AnalyticsSummary>(`/analytics/summary?days=${days}`);
    return response.data;
  }

  async getCoverageTrends(days: number = 30, groupBy: 'day' | 'week' | 'month' = 'day'): Promise<CoverageTrend[]> {
    const response = await this.client.get<CoverageTrend[]>(`/analytics/trends?days=${days}&group_by=${groupBy}`);
    return response.data;
  }

  async getTopIssues(days: number = 30, limit: number = 10): Promise<TopIssue[]> {
    const response = await this.client.get<TopIssue[]>(`/analytics/top-issues?days=${days}&limit=${limit}`);
    return response.data;
  }


  // Export endpoints
  async exportScanDetailsCSV(scanId: number): Promise<Blob> {
    const response = await this.client.get(`/export/scans/${scanId}/details/csv`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; version: string }> {
    const response = await this.client.get('/health/');
    return response.data;
  }

  // Utility methods
  downloadBlob(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  getToken(): string | null {
    return this.token;
  }
}

// Create singleton instance
export const apiClient = new ApiClient();
export default apiClient;
