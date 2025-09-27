import React, { useState } from 'react';
import { CheckCircle, Globe, Shield, BarChart3 } from 'lucide-react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  const switchToLogin = () => setIsLogin(true);
  const switchToRegister = () => setIsLogin(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex">
      {/* Left side - Features */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 to-primary-800 text-white p-12 flex-col justify-center">
        <div className="max-w-md">
          <h1 className="text-4xl font-bold mb-6">
            Alt Audit
          </h1>
          <p className="text-xl text-primary-100 mb-8">
            Scan web pages for images and analyze their alt text attributes for accessibility compliance.
          </p>
          
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <Globe className="h-6 w-6 text-primary-200" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">URL Scanning</h3>
                <p className="text-primary-200">
                  Enter any URL to scan for images and analyze their accessibility
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <Shield className="h-6 w-6 text-primary-200" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Security First</h3>
                <p className="text-primary-200">
                  Built with SSRF protection and secure scanning practices
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <BarChart3 className="h-6 w-6 text-primary-200" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Analytics & Reports</h3>
                <p className="text-primary-200">
                  Track your accessibility improvements with detailed analytics
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Auth forms */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile header */}
          <div className="lg:hidden text-center mb-8">
            <h1 className="text-3xl font-bold text-primary-600 mb-2">
              Alt Audit
            </h1>
            <p className="text-secondary-600">
              Image Alt Text Scanner
            </p>
          </div>

          {/* Auth form */}
          {isLogin ? (
            <LoginForm onSwitchToRegister={switchToRegister} />
          ) : (
            <RegisterForm onSwitchToLogin={switchToLogin} />
          )}

          {/* Features for mobile */}
          <div className="lg:hidden mt-8 space-y-4">
            <div className="text-center">
              <h3 className="font-semibold text-lg mb-4">Why Alt Audit?</h3>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
              <div className="flex items-center space-x-3 p-3 bg-white rounded-lg shadow-sm">
                <CheckCircle className="h-5 w-5 text-success-500 flex-shrink-0" />
                <div>
                  <p className="font-medium text-sm">Comprehensive Analysis</p>
                  <p className="text-xs text-secondary-600">Scan all images and check alt text</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-3 bg-white rounded-lg shadow-sm">
                <CheckCircle className="h-5 w-5 text-success-500 flex-shrink-0" />
                <div>
                  <p className="font-medium text-sm">Secure Scanning</p>
                  <p className="text-xs text-secondary-600">SSRF protection and safe practices</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-3 bg-white rounded-lg shadow-sm">
                <CheckCircle className="h-5 w-5 text-success-500 flex-shrink-0" />
                <div>
                  <p className="font-medium text-sm">Detailed Reports</p>
                  <p className="text-xs text-secondary-600">Export data and track progress</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
