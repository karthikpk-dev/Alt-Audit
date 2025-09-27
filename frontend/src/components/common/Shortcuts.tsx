import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

interface Shortcut {
  key: string;
  description: string;
  action: () => void;
  category: 'navigation' | 'actions' | 'modals';
}

export const useKeyboardShortcuts = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [showShortcuts, setShowShortcuts] = useState(false);

  const shortcuts: Shortcut[] = [
    // Navigation
    {
      key: 'g d',
      description: 'Go to Dashboard',
      action: () => navigate('/dashboard'),
      category: 'navigation'
    },
    {
      key: 'g a',
      description: 'Go to Analytics',
      action: () => navigate('/analytics'),
      category: 'navigation'
    },
    {
      key: 'g h',
      description: 'Go to Help',
      action: () => setShowShortcuts(true),
      category: 'navigation'
    },
    
    // Actions
    {
      key: 'n',
      description: 'New Scan',
      action: () => {
        const urlInput = document.querySelector('input[type="url"]') as HTMLInputElement;
        if (urlInput) {
          urlInput.focus();
        }
      },
      category: 'actions'
    },
    {
      key: 'r',
      description: 'Refresh Data',
      action: () => {
        const refreshButton = document.querySelector('[data-refresh]') as HTMLButtonElement;
        if (refreshButton) {
          refreshButton.click();
        }
      },
      category: 'actions'
    },
    
    // Modals
    {
      key: '?',
      description: 'Show Help',
      action: () => setShowShortcuts(true),
      category: 'modals'
    },
    {
      key: 'Escape',
      description: 'Close Modal',
      action: () => {
        const closeButton = document.querySelector('[data-close]') as HTMLButtonElement;
        if (closeButton) {
          closeButton.click();
        }
      },
      category: 'modals'
    }
  ];

  useEffect(() => {
    let keySequence = '';
    let sequenceTimeout: NodeJS.Timeout;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore if user is typing in an input
      if (event.target instanceof HTMLInputElement || 
          event.target instanceof HTMLTextAreaElement ||
          event.target instanceof HTMLSelectElement) {
        return;
      }

      // Handle single key shortcuts
      if (event.key === '?' || event.key === 'Escape') {
        const shortcut = shortcuts.find(s => s.key === event.key);
        if (shortcut) {
          event.preventDefault();
          shortcut.action();
        }
        return;
      }

      // Handle key sequences (like 'g d' for go to dashboard)
      if (event.key === 'g' || event.key === 'n' || event.key === 'r' || event.key === 'e' || event.key === 's') {
        keySequence += event.key;
        
        // Clear sequence after 1 second
        clearTimeout(sequenceTimeout);
        sequenceTimeout = setTimeout(() => {
          keySequence = '';
        }, 1000);

        // Check for exact matches
        const shortcut = shortcuts.find(s => s.key === keySequence);
        if (shortcut) {
          event.preventDefault();
          shortcut.action();
          keySequence = '';
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      clearTimeout(sequenceTimeout);
    };
  }, [shortcuts]);

  return {
    shortcuts,
    showShortcuts,
    setShowShortcuts
  };
};

export const ShortcutsModal: React.FC<{ 
  isOpen: boolean; 
  onClose: () => void; 
}> = ({ isOpen, onClose }) => {
  const { shortcuts } = useKeyboardShortcuts();

  if (!isOpen) {return null;}

  const shortcutsByCategory = shortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {} as Record<string, Shortcut[]>);

  const categoryLabels = {
    navigation: 'Navigation',
    actions: 'Actions',
    modals: 'Modals'
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900">Keyboard Shortcuts</h2>
          <button
            onClick={onClose}
            className="text-secondary-400 hover:text-secondary-600"
            data-close
          >
            ✕
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          <div className="space-y-6">
            {Object.entries(shortcutsByCategory).map(([category, categoryShortcuts]) => (
              <div key={category}>
                <h3 className="text-lg font-semibold text-secondary-900 mb-3">
                  {categoryLabels[category as keyof typeof categoryLabels]}
                </h3>
                <div className="space-y-2">
                  {categoryShortcuts.map((shortcut, index) => (
                    <div key={index} className="flex items-center justify-between py-2 px-3 bg-secondary-50 rounded-lg">
                      <span className="text-sm text-secondary-600">{shortcut.description}</span>
                      <kbd className="px-2 py-1 bg-secondary-200 text-secondary-700 rounded text-xs font-mono">
                        {shortcut.key}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="border-t border-secondary-200 p-4">
          <div className="text-sm text-secondary-600 text-center">
            Press <kbd className="px-1 py-0.5 bg-secondary-200 rounded text-xs">?</kbd> anytime to show this help
          </div>
        </div>
      </div>
    </div>
  );
};

export const ShortcutIndicator: React.FC<{ 
  shortcut: string; 
  className?: string; 
}> = ({ shortcut, className = '' }) => {
  return (
    <kbd className={`px-2 py-1 bg-secondary-200 text-secondary-700 rounded text-xs font-mono ${className}`}>
      {shortcut}
    </kbd>
  );
};
