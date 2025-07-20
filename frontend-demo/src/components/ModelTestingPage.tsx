import React, { useState } from 'react';
import ModelProviderSelector from './ModelProviderSelector';
import AnalysisResultsCard from './AnalysisResultsCard';
import { useFeedMinerAPI } from '../services/feedminerApi';
import type { ModelProvider, AnalysisResponse, ComparisonResponse } from '../services/feedminerApi';

interface ModelTestingPageProps {
  onBack: () => void;
}

const ModelTestingPage: React.FC<ModelTestingPageProps> = ({ onBack }) => {
  const [selectedProvider, setSelectedProvider] = useState<ModelProvider>({
    provider: 'bedrock',
    model: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    temperature: 0.7,
  });
  
  const [comparisonMode, setComparisonMode] = useState(false);
  const [testPrompt, setTestPrompt] = useState('Analyze the benefits of using multiple AI providers in a content analysis system. Focus on performance, cost, and reliability aspects.');
  
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [comparisonResult, setComparisonResult] = useState<ComparisonResponse | null>(null);
  const [error, setError] = useState<string>('');

  const api = useFeedMinerAPI();

  const handleRunAnalysis = async () => {
    setIsLoading(true);
    setError('');
    setAnalysisResult(null);
    setComparisonResult(null);

    try {
      if (comparisonMode) {
        // For comparison, we'd need actual content. For now, we'll simulate
        // In a real app, this would use a real contentId with:
        // const comparisonRequest = {
        //   providers: [
        //     { provider: 'anthropic' as const, model: 'claude-3-5-sonnet-20241022', temperature: selectedProvider.temperature },
        //     { provider: 'bedrock' as const, model: 'anthropic.claude-3-5-sonnet-20241022-v2:0', temperature: selectedProvider.temperature },
        //   ],
        // };
        setError('Comparison mode requires uploaded content. Please upload content first or use single provider mode.');
        return;
      } else {
        // Run single provider analysis
        const response = await api.analyzeWithProvider('test', {
          provider: selectedProvider.provider,
          model: selectedProvider.model,
          temperature: selectedProvider.temperature,
          prompt: testPrompt,
        });
        
        setAnalysisResult(response);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickTest = async () => {
    setIsLoading(true);
    setError('');
    setAnalysisResult(null);
    setComparisonResult(null);

    try {
      const response = await api.testBedrockIntegration();
      setAnalysisResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Bedrock test failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <button 
                onClick={onBack}
                className="text-gray-600 hover:text-gray-900 flex items-center space-x-2"
              >
                <span>←</span>
                <span>Back to Demo</span>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Multi-Model AI Testing</h1>
                <p className="text-sm text-gray-600">
                  Test and compare AI providers • v0.2.0 Integration
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                🚀 Production Ready
              </span>
              <button
                onClick={handleQuickTest}
                disabled={isLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
              >
                Quick Bedrock Test
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Configuration */}
          <div className="space-y-6">
            {/* Model Provider Selector */}
            <ModelProviderSelector
              selectedProvider={selectedProvider}
              onProviderChange={setSelectedProvider}
              disabled={isLoading}
              showComparison={true}
              onToggleComparison={setComparisonMode}
            />

            {/* Test Prompt */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Test Prompt</h3>
                <p className="text-sm text-gray-600">Enter a custom prompt to test the AI model</p>
              </div>
              
              <textarea
                value={testPrompt}
                onChange={(e) => setTestPrompt(e.target.value)}
                disabled={isLoading}
                rows={4}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
                placeholder="Enter your test prompt here..."
              />

              <div className="flex space-x-3">
                <button
                  onClick={handleRunAnalysis}
                  disabled={isLoading || !testPrompt.trim()}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Analyzing...</span>
                    </div>
                  ) : comparisonMode ? (
                    'Compare Providers'
                  ) : (
                    'Run Analysis'
                  )}
                </button>
                
                {(analysisResult || comparisonResult) && (
                  <button
                    onClick={() => {
                      setAnalysisResult(null);
                      setComparisonResult(null);
                      setError('');
                    }}
                    className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Clear
                  </button>
                )}
              </div>

              {comparisonMode && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-yellow-600">⚠️</span>
                    <span className="text-sm text-yellow-800">
                      Comparison mode requires uploaded content. Upload content first or use single provider mode.
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Info Panel */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200 p-6">
              <h4 className="font-semibold text-indigo-900 mb-3">✨ What's New in v0.2.0</h4>
              <ul className="space-y-2 text-sm text-indigo-800">
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full"></span>
                  <span>Multi-provider AI support (Anthropic + AWS Bedrock)</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full"></span>
                  <span>Real-time performance metrics and comparison</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full"></span>
                  <span>Runtime model switching and temperature control</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full"></span>
                  <span>Enterprise-ready AWS Bedrock integration</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            <AnalysisResultsCard
              result={analysisResult}
              comparison={comparisonResult}
              isLoading={isLoading}
              error={error}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelTestingPage;