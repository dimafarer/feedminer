import { useState } from 'react';
import LandingPage from './components/LandingPage';
import UploadDemo from './components/UploadDemo';
import AnalysisDashboard from './components/AnalysisDashboard';
import ModelTestingPage from './components/ModelTestingPage';
import { realAnalysisResults } from './data/analysisResults';

type AppState = 'landing' | 'upload' | 'processing' | 'results' | 'model-testing';

function App() {
  const [currentView, setCurrentView] = useState<AppState>('landing');

  const handleStartDemo = () => {
    setCurrentView('upload');
  };

  const handleUploadComplete = () => {
    setCurrentView('processing');
    // Simulate processing time
    setTimeout(() => {
      setCurrentView('results');
    }, 3000);
  };

  const handleViewDemo = () => {
    setCurrentView('results');
  };

  const handleBackToLanding = () => {
    setCurrentView('landing');
  };

  const handleModelTesting = () => {
    setCurrentView('model-testing');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {currentView === 'landing' && (
        <LandingPage 
          onStartDemo={handleStartDemo}
          onViewDemo={handleViewDemo}
          onModelTesting={handleModelTesting}
        />
      )}
      
      {currentView === 'upload' && (
        <UploadDemo 
          onUploadComplete={handleUploadComplete}
          onBack={handleBackToLanding}
        />
      )}
      
      {currentView === 'processing' && (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center space-y-6">
            <div className="w-16 h-16 mx-auto">
              <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-gray-900">Analyzing Your Content</h2>
              <p className="text-gray-600">AI is discovering your behavioral patterns and goal opportunities...</p>
            </div>
            <div className="w-80 bg-gray-200 rounded-full h-3 mx-auto">
              <div className="processing-animation h-3 rounded-full"></div>
            </div>
          </div>
        </div>
      )}
      
      {currentView === 'results' && (
        <AnalysisDashboard 
          results={realAnalysisResults}
          onBack={handleBackToLanding}
        />
      )}
      
      {currentView === 'model-testing' && (
        <ModelTestingPage 
          onBack={handleBackToLanding}
        />
      )}
    </div>
  );
}

export default App;
