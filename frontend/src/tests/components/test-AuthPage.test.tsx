import React from 'react';
import { render, screen, fireEvent, waitFor } from '@/tests/test-utils';
import AuthPage from '@/components/auth/AuthPage';
import { mockApiResponse, mockApiError } from '@/tests/test-utils';

// Mock the API client
vi.mock('@/services/api', () => ({
  default: {
    login: vi.fn(),
    register: vi.fn(),
  },
}));

describe('AuthPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form by default', () => {
    render(<AuthPage />);
    
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('switches to register form when clicking register link', () => {
    render(<AuthPage />);
    
    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);
    
    expect(screen.getByText('Create Account')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  it('switches back to login form when clicking sign in link', () => {
    render(<AuthPage />);
    
    // Switch to register
    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);
    
    // Switch back to login
    const signInLink = screen.getByText(/already have an account/i);
    fireEvent.click(signInLink);
    
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    render(<AuthPage />);
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeInTheDocument();
      expect(screen.getByText('Password is required')).toBeInTheDocument();
    });
  });

  it('shows validation errors for invalid email in register form', async () => {
    render(<AuthPage />);
    
    // Switch to register
    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);
    
    const emailInput = screen.getByLabelText('Email');
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    
    const submitButton = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });
  });

  it('shows validation error for password mismatch in register form', async () => {
    render(<AuthPage />);
    
    // Switch to register
    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);
    
    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'different123' } });
    
    const submitButton = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
    });
  });

  it('shows validation error for weak password', async () => {
    render(<AuthPage />);
    
    // Switch to register
    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);
    
    const passwordInput = screen.getByLabelText('Password');
    fireEvent.change(passwordInput, { target: { value: '123' } });
    
    const submitButton = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument();
    });
  });

  it('submits login form with valid data', async () => {
    const mockLogin = vi.fn().mockResolvedValue({
      access_token: 'mock-token',
      token_type: 'bearer',
      expires_in: 3600,
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.login).mockImplementation(mockLogin);

    render(<AuthPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  it('submits register form with valid data', async () => {
    const mockRegister = vi.fn().mockResolvedValue({
      id: 1,
      username: 'newuser',
      email: 'newuser@example.com',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.register).mockImplementation(mockRegister);

    render(<AuthPage />);
    
    // Switch to register
    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);
    
    const usernameInput = screen.getByLabelText('Username');
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    const submitButton = screen.getByRole('button', { name: /create account/i });
    
    fireEvent.change(usernameInput, { target: { value: 'newuser' } });
    fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123',
      });
    });
  });

  it('shows error message on login failure', async () => {
    const mockLogin = vi.fn().mockRejectedValue({
      response: {
        data: { detail: 'Invalid credentials' },
        status: 401,
      },
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.login).mockImplementation(mockLogin);

    render(<AuthPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  it('shows error message on register failure', async () => {
    const mockRegister = vi.fn().mockRejectedValue({
      response: {
        data: { detail: 'Username already exists' },
        status: 400,
      },
    });

    // Mock the API client
    vi.mocked(require('@/services/api').default.register).mockImplementation(mockRegister);

    render(<AuthPage />);
    
    // Switch to register
    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);
    
    const usernameInput = screen.getByLabelText('Username');
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    const submitButton = screen.getByRole('button', { name: /create account/i });
    
    fireEvent.change(usernameInput, { target: { value: 'existinguser' } });
    fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Username already exists')).toBeInTheDocument();
    });
  });

  it('shows loading state during form submission', async () => {
    const mockLogin = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    // Mock the API client
    vi.mocked(require('@/services/api').default.login).mockImplementation(mockLogin);

    render(<AuthPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    // Check loading state
    expect(screen.getByText('Signing in...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    
    await waitFor(() => {
      expect(screen.queryByText('Signing in...')).not.toBeInTheDocument();
    });
  });

  it('clears form errors when switching between login and register', async () => {
    render(<AuthPage />);
    
    // Trigger validation error in login form
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeInTheDocument();
    });
    
    // Switch to register form
    const registerLink = screen.getByText(/don't have an account/i);
    fireEvent.click(registerLink);
    
    // Switch back to login form
    const signInLink = screen.getByText(/already have an account/i);
    fireEvent.click(signInLink);
    
    // Error should be cleared
    expect(screen.queryByText('Username is required')).not.toBeInTheDocument();
  });
});
