import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { LogOut, User, Globe, History, BarChart3, HelpCircle } from 'lucide-react';
import UrlInput from '@/components/scanner/UrlInput';
import ScanResults from '@/components/scanner/ScanResults';
import ScanHistory from '@/components/scanner/ScanHistory';
import HelpModal from '@/components/help/HelpModal';
import { useKeyboardShortcuts, ShortcutsModal } from '@/components/common/Shortcuts';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [selectedScanId, setSelectedScanId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'scan' | 'history'>('scan');
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [showHelpModal, setShowHelpModal] = useState(false);
  
  const { showShortcuts, setShowShortcuts } = useKeyboardShortcuts();

  const handleLogout = async () => {
    await logout();
  };

  const handleScanComplete = (scanId: number) => {
    setSelectedScanId(scanId);
    setActiveTab('history');
    setRefreshTrigger(prev => prev + 1);
  };

  const handleScanSelect = (scanId: number) => {
    setSelectedScanId(scanId);
    setActiveTab('scan');
  };

  const handleScanUpdate = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleScanDelete = (scanId: number) => {
    if (selectedScanId === scanId) {
      setSelectedScanId(null);
    }
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-secondary-900">
                Alt Audit
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-secondary-500" />
                <span className="text-sm text-secondary-700">
                  {user?.username}
                </span>
              </div>
              
              <button
                onClick={() => setShowHelpModal(true)}
                className="btn btn-ghost btn-sm"
                data-help
                title="Help (?)"
              >
                <HelpCircle className="h-4 w-4" />
              </button>
              
              
              <button
                onClick={handleLogout}
                className="btn btn-ghost btn-sm"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-secondary-900 mb-4">
              Welcome to Alt Audit
            </h2>
            <p className="text-lg text-secondary-600 max-w-2xl mx-auto">
              Scan web pages for images and analyze their alt text attributes for accessibility compliance.
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex justify-center">
            <div className="bg-white rounded-lg p-1 shadow-sm border border-secondary-200">
              <button
                onClick={() => setActiveTab('scan')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'scan'
                    ? 'bg-primary-600 text-white'
                    : 'text-secondary-600 hover:text-secondary-900'
                }`}
              >
                <Globe className="h-4 w-4 mr-2 inline" />
                New Scan
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'history'
                    ? 'bg-primary-600 text-white'
                    : 'text-secondary-600 hover:text-secondary-900'
                }`}
              >
                <History className="h-4 w-4 mr-2 inline" />
                Scan History
              </button>
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === 'scan' ? (
            <div className="space-y-8">
              {/* URL Input */}
              <UrlInput 
                onScanComplete={handleScanComplete}
                onScanStart={() => setSelectedScanId(null)}
              />
              
              {/* Scan Results */}
              {selectedScanId && (
                <ScanResults
                  scanId={selectedScanId}
                  onScanUpdate={handleScanUpdate}
                  onScanDelete={handleScanDelete}
                />
              )}
            </div>
          ) : (
            <div className="space-y-8">
              {/* Scan History */}
              <ScanHistory
                onScanSelect={handleScanSelect}
                refreshTrigger={refreshTrigger}
              />
            </div>
          )}

          {/* Quick Actions */}
          <div className="w-full max-w-2xl mx-auto">
            <div className="card">
              <div className="card-header text-center">
                <h3 className="card-title text-lg">View Analytics</h3>
                <p className="card-description">
                  Track your accessibility improvements
                </p>
              </div>
              <div className="card-content">
                <button 
                  onClick={() => navigate('/analytics')}
                  className="btn btn-secondary btn-md w-full"
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  View Reports
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Modals */}
      
      <HelpModal
        isOpen={showHelpModal}
        onClose={() => setShowHelpModal(false)}
      />
      
      
      <ShortcutsModal
        isOpen={showShortcuts}
        onClose={() => setShowShortcuts(false)}
      />
    </div>
  );
};

export default Dashboard;
