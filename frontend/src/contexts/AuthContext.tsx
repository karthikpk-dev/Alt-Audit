import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, LoginForm, RegisterForm, UserUpdateForm, AuthContextType } from '@/types';
import apiClient from '@/services/api';
import toast from 'react-hot-toast';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('access_token');
      if (storedToken) {
        setToken(storedToken);
        try {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
        } catch (error) {
          // Token is invalid, clear it
          localStorage.removeItem('access_token');
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const loginData: LoginForm = { email, password };
      const tokenData = await apiClient.login(loginData);
      
      setToken(tokenData.access_token);
      
      // Get user data
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      
      toast.success('Login successful!');
    } catch (error) {
      toast.error('Login failed. Please check your credentials.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterForm) => {
    try {
      setIsLoading(true);
      await apiClient.register(data);
      toast.success('Registration successful! Please log in.');
    } catch (error) {
      toast.error('Registration failed. Please try again.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient.logout();
      setUser(null);
      setToken(null);
      toast.success('Logged out successfully!');
    } catch (error) {
      // Even if logout fails on server, clear local state
      setUser(null);
      setToken(null);
      localStorage.removeItem('access_token');
    }
  };

  const updateUser = async (data: UserUpdateForm) => {
    try {
      setIsLoading(true);
      const updatedUser = await apiClient.updateUser(data);
      setUser(updatedUser);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile. Please try again.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    updateUser,
    isLoading,
    isAuthenticated: !!user && !!token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
