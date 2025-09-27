import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';

// Mock API client
export const mockApiClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn(),
};

// Mock user data
export const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
};

// Mock scan result data
export const mockScanResult = {
  id: 1,
  url: 'https://example.com',
  user_id: 1,
  total_images: 10,
  images_with_alt: 7,
  images_missing_alt: 3,
  coverage_percentage: 70.0,
  status: 'completed',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

// Mock image detail data
export const mockImageDetails = [
  {
    id: 1,
    scan_id: 1,
    image_url: 'https://example.com/image1.jpg',
    alt_text: 'Test image 1',
    has_alt: true,
    is_decorative: false,
    width: 100,
    height: 100,
  },
  {
    id: 2,
    scan_id: 1,
    image_url: 'https://example.com/image2.jpg',
    alt_text: '',
    has_alt: true,
    is_decorative: true,
    width: 200,
    height: 200,
  },
  {
    id: 3,
    scan_id: 1,
    image_url: 'https://example.com/image3.jpg',
    alt_text: null,
    has_alt: false,
    is_decorative: false,
    width: 300,
    height: 300,
  },
];

// Mock analytics data
export const mockAnalyticsSummary = {
  total_scans: 10,
  total_images_scanned: 100,
  total_images_with_alt: 70,
  total_images_missing_alt: 30,
  average_coverage_percentage: 70.0,
  most_common_issues: ['Missing alt text', 'Empty alt text'],
};

export const mockCoverageTrends = [
  {
    period: '2024-01-01',
    coverage_percentage: 65.0,
    total_images: 20,
    images_with_alt: 13,
    images_missing_alt: 7,
    scans: 2,
  },
  {
    period: '2024-01-02',
    coverage_percentage: 75.0,
    total_images: 30,
    images_with_alt: 22,
    images_missing_alt: 8,
    scans: 3,
  },
];

export const mockTopIssues = [
  {
    issue: 'Missing alt text',
    count: 15,
    severity: 'high',
    description: 'Images without alt text attributes',
  },
  {
    issue: 'Empty alt text',
    count: 8,
    severity: 'medium',
    description: 'Images with empty alt text that should be descriptive',
  },
];


// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialAuthState?: {
    isAuthenticated: boolean;
    user?: typeof mockUser | null;
  };
  initialRoute?: string;
}

const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <BrowserRouter>
      <AuthProvider>
        {children}
      </AuthProvider>
    </BrowserRouter>
  );
};

export const customRender = (
  ui: ReactElement,
  options: CustomRenderOptions = {}
) => {
  const { initialAuthState, initialRoute, ...renderOptions } = options;

  // Mock the auth context if needed
  if (initialAuthState) {
    // This would need to be implemented based on your auth context structure
    // For now, we'll just render with the default providers
  }

  // Set initial route if provided
  if (initialRoute) {
    window.history.pushState({}, '', initialRoute);
  }

  return render(ui, {
    wrapper: AllTheProviders,
    ...renderOptions,
  });
};

// Re-export everything from testing library
export * from '@testing-library/react';
export { customRender as render };

// Mock functions for common API calls
export const mockApiResponses = {
  login: {
    success: {
      access_token: 'mock-jwt-token',
      token_type: 'bearer',
      expires_in: 3600,
    },
    error: {
      detail: 'Invalid credentials',
    },
  },
  register: {
    success: mockUser,
    error: {
      detail: 'Username already exists',
    },
  },
  me: {
    success: mockUser,
    error: {
      detail: 'Not authenticated',
    },
  },
  scans: {
    list: {
      scans: [mockScanResult],
      total: 1,
      page: 1,
      per_page: 10,
    },
    detail: mockScanResult,
    images: {
      images: mockImageDetails,
      total: 3,
      page: 1,
      per_page: 10,
    },
  },
  analytics: {
    summary: mockAnalyticsSummary,
    trends: mockCoverageTrends,
    topIssues: mockTopIssues,
  },
};

// Helper function to mock API responses
export const mockApiResponse = (endpoint: string, response: any, status = 200) => {
  const mockResponse = {
    data: response,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: {},
    config: {},
  };

  if (endpoint.includes('GET')) {
    mockApiClient.get.mockResolvedValueOnce(mockResponse);
  } else if (endpoint.includes('POST')) {
    mockApiClient.post.mockResolvedValueOnce(mockResponse);
  } else if (endpoint.includes('PUT')) {
    mockApiClient.put.mockResolvedValueOnce(mockResponse);
  } else if (endpoint.includes('DELETE')) {
    mockApiClient.delete.mockResolvedValueOnce(mockResponse);
  }
};

// Helper function to mock API errors
export const mockApiError = (endpoint: string, error: any, status = 400) => {
  const mockError = {
    response: {
      data: error,
      status,
      statusText: 'Error',
    },
    message: error.detail || 'API Error',
  };

  if (endpoint.includes('GET')) {
    mockApiClient.get.mockRejectedValueOnce(mockError);
  } else if (endpoint.includes('POST')) {
    mockApiClient.post.mockRejectedValueOnce(mockError);
  } else if (endpoint.includes('PUT')) {
    mockApiClient.put.mockRejectedValueOnce(mockError);
  } else if (endpoint.includes('DELETE')) {
    mockApiClient.delete.mockRejectedValueOnce(mockError);
  }
};

// Helper function to wait for async operations
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function to create mock event
export const createMockEvent = (type: string, target?: any) => ({
  type,
  target: target || { value: '' },
  preventDefault: vi.fn(),
  stopPropagation: vi.fn(),
});

// Helper function to create mock form event
export const createMockFormEvent = (values: Record<string, any>) => ({
  preventDefault: vi.fn(),
  target: {
    elements: Object.keys(values).reduce((acc, key) => {
      acc[key] = { value: values[key] };
      return acc;
    }, {} as Record<string, { value: any }>),
  },
});

// Mock IntersectionObserver
export const mockIntersectionObserver = () => {
  const mockObserver = {
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  };
  
  global.IntersectionObserver = vi.fn().mockImplementation(() => mockObserver);
  return mockObserver;
};

// Mock ResizeObserver
export const mockResizeObserver = () => {
  const mockObserver = {
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  };
  
  global.ResizeObserver = vi.fn().mockImplementation(() => mockObserver);
  return mockObserver;
};

// Mock window.matchMedia
export const mockMatchMedia = (matches: boolean = false) => {
  global.matchMedia = vi.fn().mockImplementation(query => ({
    matches,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
};

// Mock localStorage
export const mockLocalStorage = () => {
  const store: Record<string, string> = {};
  
  global.localStorage = {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
  };
  
  return store;
};

// Mock sessionStorage
export const mockSessionStorage = () => {
  const store: Record<string, string> = {};
  
  global.sessionStorage = {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
  };
  
  return store;
};
