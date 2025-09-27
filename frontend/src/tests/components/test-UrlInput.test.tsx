import React from 'react';
import { render, screen, fireEvent, waitFor } from '@/tests/test-utils';
import UrlInput from '@/components/scanner/UrlInput';
import { mockApiResponse, mockApiError } from '@/tests/test-utils';

// Mock the API client
vi.mock('@/services/api', () => ({
  default: {
    createScan: vi.fn(),
  },
}));

describe('UrlInput', () => {
  const mockOnScanComplete = vi.fn();
  const mockOnScanStart = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders URL input form', () => {
    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    expect(screen.getByLabelText('Website URL')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start scan/i })).toBeInTheDocument();
    expect(screen.getByText(/enter a website url to scan/i)).toBeInTheDocument();
  });

  it('shows validation error for empty URL', async () => {
    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('URL is required')).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid URL format', async () => {
    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    fireEvent.change(urlInput, { target: { value: 'not-a-valid-url' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid URL')).toBeInTheDocument();
    });
  });

  it('shows validation error for URL without protocol', async () => {
    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    fireEvent.change(urlInput, { target: { value: 'example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('URL must start with http:// or https://')).toBeInTheDocument();
    });
  });

  it('submits form with valid URL', async () => {
    const mockCreateScan = vi.fn().mockResolvedValue({
      id: 1,
      url: 'https://example.com',
      status: 'pending',
      created_at: '2024-01-01T00:00:00Z',
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.createScan).mockImplementation(mockCreateScan);

    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockCreateScan).toHaveBeenCalledWith('https://example.com');
      expect(mockOnScanStart).toHaveBeenCalled();
    });
  });

  it('shows loading state during scan creation', async () => {
    const mockCreateScan = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    // Mock the API client
    vi.mocked(require('@/services/api').default.createScan).mockImplementation(mockCreateScan);

    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://example.com' } });
    fireEvent.click(submitButton);
    
    // Check loading state
    expect(screen.getByText('Starting scan...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    
    await waitFor(() => {
      expect(screen.queryByText('Starting scan...')).not.toBeInTheDocument();
    });
  });

  it('shows error message on scan creation failure', async () => {
    const mockCreateScan = vi.fn().mockRejectedValue({
      response: {
        data: { detail: 'Failed to create scan' },
        status: 400,
      },
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.createScan).mockImplementation(mockCreateScan);

    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to create scan')).toBeInTheDocument();
    });
  });

  it('calls onScanComplete when scan is successfully created', async () => {
    const mockCreateScan = vi.fn().mockResolvedValue({
      id: 1,
      url: 'https://example.com',
      status: 'pending',
      created_at: '2024-01-01T00:00:00Z',
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.createScan).mockImplementation(mockCreateScan);

    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnScanComplete).toHaveBeenCalledWith(1);
    });
  });

  it('clears form after successful submission', async () => {
    const mockCreateScan = vi.fn().mockResolvedValue({
      id: 1,
      url: 'https://example.com',
      status: 'pending',
      created_at: '2024-01-01T00:00:00Z',
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.createScan).mockImplementation(mockCreateScan);

    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(urlInput).toHaveValue('');
    });
  });

  it('handles keyboard submission', async () => {
    const mockCreateScan = vi.fn().mockResolvedValue({
      id: 1,
      url: 'https://example.com',
      status: 'pending',
      created_at: '2024-01-01T00:00:00Z',
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.createScan).mockImplementation(mockCreateScan);

    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    
    fireEvent.change(urlInput, { target: { value: 'https://example.com' } });
    fireEvent.keyDown(urlInput, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(mockCreateScan).toHaveBeenCalledWith('https://example.com');
    });
  });

  it('shows example URLs', () => {
    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    expect(screen.getByText('https://example.com')).toBeInTheDocument();
    expect(screen.getByText('https://github.com')).toBeInTheDocument();
  });

  it('clicking example URL fills the input', () => {
    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const exampleLink = screen.getByText('https://example.com');
    
    fireEvent.click(exampleLink);
    
    expect(urlInput).toHaveValue('https://example.com');
  });

  it('shows scan tips', () => {
    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    expect(screen.getByText(/make sure the website is accessible/i)).toBeInTheDocument();
    expect(screen.getByText(/scanning may take a few moments/i)).toBeInTheDocument();
  });

  it('handles network error gracefully', async () => {
    const mockCreateScan = vi.fn().mockRejectedValue(new Error('Network error'));

    // Mock the API client
    vi.mocked(require('@/services/api').default.createScan).mockImplementation(mockCreateScan);

    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('validates URL format correctly', async () => {
    render(
      <UrlInput 
        onScanComplete={mockOnScanComplete} 
        onScanStart={mockOnScanStart} 
      />
    );
    
    const urlInput = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /start scan/i });
    
    const invalidUrls = [
      'not-a-url',
      'ftp://example.com',
      'javascript:alert(1)',
      'data:text/html,<script>alert(1)</script>',
    ];
    
    for (const invalidUrl of invalidUrls) {
      fireEvent.change(urlInput, { target: { value: invalidUrl } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/please enter a valid url/i)).toBeInTheDocument();
      });
      
      // Clear the error for next test
      fireEvent.change(urlInput, { target: { value: '' } });
    }
  });
});
