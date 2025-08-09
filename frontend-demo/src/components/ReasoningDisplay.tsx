import React, { useEffect, useRef } from 'react';
import type { ReasoningStep } from '../services/feedminerApi';

interface ReasoningDisplayProps {
  reasoningSteps: ReasoningStep[];
  isActive: boolean;
  className?: string;
}

const ReasoningDisplay: React.FC<ReasoningDisplayProps> = ({ 
  reasoningSteps, 
  isActive, 
  className = '' 
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new reasoning steps arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [reasoningSteps]);

  const getStepIcon = (step: string) => {
    const stepIcons: Record<string, string> = {
      'data_extraction': '📥',
      'post_extraction_complete': '✅',
      'ai_analysis_starting': '🤖',
      'ai_processing': '⚡',
      'analysis_complete': '🎉',
      'multi_type_analysis_start': '🔄',
      'data_sampling_strategy': '📊',
      'processing_saved_posts': '💾',
      'processing_liked_posts': '❤️',
      'processing_comments': '💬',
      'processing_user_posts': '📝',
      'processing_following': '👥',
      'data_extraction_complete': '📋',
      'ai_analysis_preparation': '🎯',
      'ai_deep_analysis': '🧠',
      'analysis_finalization': '🏁',
      'analysis_error': '❌'
    };
    
    return stepIcons[step] || '🔍';
  };

  const getStepTitle = (step: string) => {
    const stepTitles: Record<string, string> = {
      'data_extraction': 'Data Extraction',
      'post_extraction_complete': 'Extraction Complete',
      'ai_analysis_starting': 'AI Analysis Starting',
      'ai_processing': 'Processing Content',
      'analysis_complete': 'Analysis Complete',
      'multi_type_analysis_start': 'Multi-Type Analysis',
      'data_sampling_strategy': 'Smart Sampling',
      'processing_saved_posts': 'Processing Saved Posts',
      'processing_liked_posts': 'Processing Liked Posts',
      'processing_comments': 'Processing Comments',
      'processing_user_posts': 'Processing Your Posts',
      'processing_following': 'Processing Following',
      'data_extraction_complete': 'Data Ready',
      'ai_analysis_preparation': 'Preparing Analysis',
      'ai_deep_analysis': 'Deep Analysis',
      'analysis_finalization': 'Finalizing',
      'analysis_error': 'Error Occurred'
    };
    
    return stepTitles[step] || step.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  if (!isActive && reasoningSteps.length === 0) {
    return null;
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <span>🤖</span>
            <span>AI Model Thinking Process</span>
          </h3>
          <div className="flex items-center space-x-2">
            {isActive && (
              <div className="flex items-center space-x-2">
                <div className="animate-pulse w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600 font-medium">Live</span>
              </div>
            )}
            <span className="text-sm text-gray-500">
              {reasoningSteps.length} step{reasoningSteps.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Watch the AI model's reasoning process in real-time as it analyzes your data
        </p>
      </div>
      
      <div 
        ref={scrollRef}
        className="max-h-96 overflow-y-auto p-4 space-y-3"
      >
        {reasoningSteps.length === 0 && isActive && (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-3"></div>
              <p className="text-gray-600">Connecting to AI model...</p>
            </div>
          </div>
        )}

        {reasoningSteps.map((step, index) => (
          <div 
            key={`${step.step}-${index}`} 
            className={`flex items-start space-x-3 p-3 rounded-lg transition-all duration-300 ${
              index === reasoningSteps.length - 1 && isActive
                ? 'bg-primary-50 border border-primary-200'
                : 'bg-gray-50 hover:bg-gray-100'
            }`}
          >
            <div className="flex-shrink-0">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                step.step.includes('error') 
                  ? 'bg-red-100 text-red-600' 
                  : step.step.includes('complete')
                    ? 'bg-green-100 text-green-600'
                    : 'bg-blue-100 text-blue-600'
              }`}>
                {getStepIcon(step.step)}
              </div>
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <h4 className={`text-sm font-medium ${
                  step.step.includes('error') ? 'text-red-900' : 'text-gray-900'
                }`}>
                  {getStepTitle(step.step)}
                </h4>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">
                    {formatTime(step.timestamp)}
                  </span>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    step.progress === 1.0 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {Math.round(step.progress * 100)}%
                  </div>
                </div>
              </div>
              
              <p className={`text-sm ${
                step.step.includes('error') ? 'text-red-700' : 'text-gray-700'
              } leading-relaxed`}>
                {step.reasoning}
              </p>

              {/* Progress bar for current step */}
              {index === reasoningSteps.length - 1 && isActive && step.progress < 1.0 && (
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-1">
                    <div 
                      className="bg-primary-600 h-1 rounded-full transition-all duration-500"
                      style={{ width: `${step.progress * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Metadata display for debugging */}
              {step.metadata && Object.keys(step.metadata).length > 0 && (
                <details className="mt-2">
                  <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                    Technical details
                  </summary>
                  <pre className="text-xs text-gray-600 mt-1 bg-gray-100 p-2 rounded overflow-x-auto">
                    {JSON.stringify(step.metadata, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer with summary */}
      {!isActive && reasoningSteps.length > 0 && (
        <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              Analysis completed in {reasoningSteps.length} steps
            </span>
            {reasoningSteps.length > 0 && (
              <span className="text-gray-500">
                Duration: {Math.round(
                  (new Date(reasoningSteps[reasoningSteps.length - 1].timestamp).getTime() - 
                   new Date(reasoningSteps[0].timestamp).getTime()) / 1000
                )}s
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReasoningDisplay;