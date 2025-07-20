import React from 'react';
import type { AnalysisResponse, ComparisonResponse } from '../services/feedminerApi';

interface AnalysisResultsCardProps {
  result: AnalysisResponse | null;
  comparison: ComparisonResponse | null;
  isLoading?: boolean;
  error?: string;
}

const AnalysisResultsCard: React.FC<AnalysisResultsCardProps> = ({
  result,
  comparison,
  isLoading = false,
  error,
}) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 bg-gray-300 rounded-full"></div>
            <div className="h-4 bg-gray-300 rounded w-32"></div>
          </div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-300 rounded w-full"></div>
            <div className="h-4 bg-gray-300 rounded w-3/4"></div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="h-16 bg-gray-300 rounded"></div>
            <div className="h-16 bg-gray-300 rounded"></div>
            <div className="h-16 bg-gray-300 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 bg-red-400 rounded-full flex items-center justify-center">
            <span className="text-white text-sm">!</span>
          </div>
          <div>
            <h3 className="text-red-800 font-medium">Analysis Failed</h3>
            <p className="text-red-600 text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!result && !comparison) {
    return (
      <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <div className="text-gray-500">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Analyze</h3>
          <p className="text-sm">Select a model provider and start your analysis</p>
        </div>
      </div>
    );
  }

  // Single Analysis Result
  if (result && !comparison) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                result.provider === 'anthropic' ? 'bg-orange-400' : 'bg-blue-400'
              }`}></div>
              <div>
                <h3 className="font-semibold text-gray-900 capitalize">
                  {result.provider} Analysis
                </h3>
                <p className="text-sm text-gray-600">{result.model}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-semibold text-green-600">
                {result.response.latency_ms}ms
              </div>
              <div className="text-xs text-gray-500">Response Time</div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* AI Response */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Analysis Result</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-900 whitespace-pre-wrap">{result.response.content}</p>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {result.response.usage.input_tokens}
              </div>
              <div className="text-xs text-blue-700 font-medium">Input Tokens</div>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {result.response.usage.output_tokens}
              </div>
              <div className="text-xs text-green-700 font-medium">Output Tokens</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {result.response.usage.total_tokens}
              </div>
              <div className="text-xs text-purple-700 font-medium">Total Tokens</div>
            </div>
          </div>

          {/* Test Mode Badge */}
          {result.test_mode && (
            <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              🧪 Test Mode
            </div>
          )}
        </div>
      </div>
    );
  }

  // Comparison Results
  if (comparison) {
    const results = comparison.comparison.results;
    const summary = comparison.comparison.summary;
    
    return (
      <div className="space-y-6">
        {/* Comparison Header */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Provider Comparison</h3>
              <p className="text-sm text-gray-600">
                Comparing {comparison.comparison.providers.length} AI providers
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                Multi-Model Analysis
              </span>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-sm text-green-700 font-medium mb-1">Fastest Response</div>
              <div className="text-lg font-semibold text-green-900 capitalize">
                {summary.fastest_provider}
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-blue-700 font-medium mb-1">Most Cost Effective</div>
              <div className="text-lg font-semibold text-blue-900 capitalize">
                {summary.most_cost_effective}
              </div>
            </div>
          </div>
        </div>

        {/* Individual Results */}
        <div className="space-y-4">
          {Object.entries(results).map(([provider, result]) => (
            <div key={provider} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className={`px-6 py-3 border-b border-gray-200 ${
                provider === summary.fastest_provider ? 'bg-green-50' : 'bg-gray-50'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      provider === 'anthropic' ? 'bg-orange-400' : 'bg-blue-400'
                    }`}></div>
                    <span className="font-medium text-gray-900 capitalize">{provider}</span>
                    {provider === summary.fastest_provider && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        ⚡ Fastest
                      </span>
                    )}
                  </div>
                  <div className="text-sm font-medium text-gray-600">
                    {result.latency_ms}ms
                  </div>
                </div>
              </div>
              <div className="p-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-900 text-sm">{result.content}</p>
                </div>
                {result.usage && (
                  <div className="mt-3 flex space-x-4 text-xs text-gray-500">
                    <span>Tokens: {result.usage.total_tokens || 'N/A'}</span>
                    <span>Input: {result.usage.input_tokens || 'N/A'}</span>
                    <span>Output: {result.usage.output_tokens || 'N/A'}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return null;
};

export default AnalysisResultsCard;