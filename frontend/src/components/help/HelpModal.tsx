import React, { useState } from 'react';
import { X, HelpCircle, Book, Video, MessageCircle, ExternalLink, ChevronRight } from 'lucide-react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const HelpModal: React.FC<HelpModalProps> = ({ isOpen, onClose }) => {
  const [activeSection, setActiveSection] = useState('getting-started');

  if (!isOpen) {return null;}

  const sections = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: <HelpCircle className="h-5 w-5" />,
      content: (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-lg mb-2">Welcome to Alt Audit</h3>
            <p className="text-secondary-600 mb-4">
              Alt Audit helps you scan websites for image accessibility compliance. 
              Here's how to get started:
            </p>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                1
              </div>
              <div>
                <h4 className="font-medium">Enter a URL</h4>
                <p className="text-sm text-secondary-600">
                  Enter any website URL in the scan form. Make sure it starts with http:// or https://
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                2
              </div>
              <div>
                <h4 className="font-medium">Start the Scan</h4>
                <p className="text-sm text-secondary-600">
                  Click "Start Scan" to begin analyzing the website for images and alt text
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                3
              </div>
              <div>
                <h4 className="font-medium">Review Results</h4>
                <p className="text-sm text-secondary-600">
                  View detailed analysis of images, alt text coverage, and accessibility issues
                </p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'understanding-results',
      title: 'Understanding Results',
      icon: <Book className="h-5 w-5" />,
      content: (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-lg mb-2">Reading Your Scan Results</h3>
            <p className="text-secondary-600 mb-4">
              Here's what each metric means in your scan results:
            </p>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-secondary-50 rounded-lg">
              <h4 className="font-medium mb-2">Coverage Percentage</h4>
              <p className="text-sm text-secondary-600">
                The percentage of images that have alt text. Higher is better for accessibility.
              </p>
            </div>
            
            <div className="p-4 bg-secondary-50 rounded-lg">
              <h4 className="font-medium mb-2">Images with Alt Text</h4>
              <p className="text-sm text-secondary-600">
                Count of images that have alt text attributes (including empty alt="" for decorative images).
              </p>
            </div>
            
            <div className="p-4 bg-secondary-50 rounded-lg">
              <h4 className="font-medium mb-2">Images Missing Alt Text</h4>
              <p className="text-sm text-secondary-600">
                Count of images that don't have alt text attributes and need attention.
              </p>
            </div>
            
            <div className="p-4 bg-secondary-50 rounded-lg">
              <h4 className="font-medium mb-2">Decorative Images</h4>
              <p className="text-sm text-secondary-600">
                Images marked as decorative with alt="" - these are correctly implemented.
              </p>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'best-practices',
      title: 'Best Practices',
      icon: <Book className="h-5 w-5" />,
      content: (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-lg mb-2">Accessibility Best Practices</h3>
            <p className="text-secondary-600 mb-4">
              Follow these guidelines to improve your website's accessibility:
            </p>
          </div>
          
          <div className="space-y-4">
            <div className="border-l-4 border-success-500 pl-4">
              <h4 className="font-medium text-success-900">Do's</h4>
              <ul className="text-sm text-secondary-600 mt-2 space-y-1">
                <li>• Write descriptive alt text that conveys the image's purpose</li>
                <li>• Use alt="" for decorative images that don't add meaning</li>
                <li>• Keep alt text concise but informative (under 125 characters)</li>
                <li>• Test with screen readers to ensure alt text makes sense</li>
                <li>• Include important text that appears in images in the alt text</li>
              </ul>
            </div>
            
            <div className="border-l-4 border-error-500 pl-4">
              <h4 className="font-medium text-error-900">Don'ts</h4>
              <ul className="text-sm text-secondary-600 mt-2 space-y-1">
                <li>• Don't use "image of" or "picture of" in alt text</li>
                <li>• Don't leave alt attributes empty for meaningful images</li>
                <li>• Don't use file names as alt text</li>
                <li>• Don't make alt text too long or verbose</li>
                <li>• Don't use alt text to stuff keywords</li>
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'troubleshooting',
      title: 'Troubleshooting',
      icon: <MessageCircle className="h-5 w-5" />,
      content: (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-lg mb-2">Common Issues & Solutions</h3>
            <p className="text-secondary-600 mb-4">
              Here are solutions to common problems you might encounter:
            </p>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-warning-50 border border-warning-200 rounded-lg">
              <h4 className="font-medium text-warning-900 mb-2">Scan Failed</h4>
              <p className="text-sm text-warning-700 mb-2">
                If a scan fails, it might be due to:
              </p>
              <ul className="text-sm text-warning-700 space-y-1">
                <li>• Website is down or unreachable</li>
                <li>• Website blocks automated requests</li>
                <li>• Invalid URL format</li>
                <li>• Network connectivity issues</li>
              </ul>
              <p className="text-sm text-warning-700 mt-2">
                Try again later or check the URL format.
              </p>
            </div>
            
            <div className="p-4 bg-info-50 border border-info-200 rounded-lg">
              <h4 className="font-medium text-info-900 mb-2">Low Coverage Percentage</h4>
              <p className="text-sm text-info-700 mb-2">
                If your coverage is low:
              </p>
              <ul className="text-sm text-info-700 space-y-1">
                <li>• Add alt text to meaningful images</li>
                <li>• Use alt="" for decorative images</li>
                <li>• Review images that might be missing alt attributes</li>
                <li>• Check for images loaded via JavaScript</li>
              </ul>
            </div>
            
            <div className="p-4 bg-secondary-50 border border-secondary-200 rounded-lg">
              <h4 className="font-medium text-secondary-900 mb-2">Slow Scans</h4>
              <p className="text-sm text-secondary-700">
                Large websites with many images may take longer to scan. 
                This is normal and ensures thorough analysis.
              </p>
            </div>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900">Help & Documentation</h2>
          <button
            onClick={onClose}
            className="text-secondary-400 hover:text-secondary-600"
            data-close
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <div className="w-64 bg-secondary-50 border-r border-secondary-200 p-4 overflow-y-auto">
            <nav className="space-y-2">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    activeSection === section.id
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-secondary-600 hover:bg-secondary-100'
                  }`}
                >
                  {section.icon}
                  <span className="font-medium">{section.title}</span>
                  <ChevronRight className="h-4 w-4 ml-auto" />
                </button>
              ))}
            </nav>
          </div>
          
          {/* Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {sections.find(s => s.id === activeSection)?.content}
          </div>
        </div>
        
        {/* Footer */}
        <div className="border-t border-secondary-200 p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-secondary-600">
              Need more help? Contact support or check our documentation.
            </div>
            <div className="flex space-x-2">
              <button className="btn btn-outline btn-sm">
                <ExternalLink className="h-4 w-4 mr-2" />
                Documentation
              </button>
              <button className="btn btn-primary btn-sm">
                <MessageCircle className="h-4 w-4 mr-2" />
                Contact Support
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpModal;
