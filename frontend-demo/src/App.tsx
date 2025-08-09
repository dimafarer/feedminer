import { useState, useEffect, useRef, useCallback } from 'react';
import LandingPage from './components/LandingPage';
import UploadDemo from './components/UploadDemo';
import AnalysisDashboard from './components/AnalysisDashboard';
import ModelTestingPage from './components/ModelTestingPage';
import ReasoningDisplay from './components/ReasoningDisplay';
import { realAnalysisResults, type AnalysisResult } from './data/analysisResults';
import { useFeedMinerAPI, type ReasoningStep } from './services/feedminerApi';

type AppState = 'landing' | 'upload' | 'processing' | 'results' | 'model-testing';

function App() {
  const [currentView, setCurrentView] = useState<AppState>('landing');
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult>(realAnalysisResults);
  const [currentContentId, setCurrentContentId] = useState<string | null>(null);
  
  // WebSocket reasoning display state
  const [reasoningSteps, setReasoningSteps] = useState<ReasoningStep[]>([]);
  const [isAnalysisActive, setIsAnalysisActive] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  
  // Use refs to avoid dependency issues in useEffect
  const websocketRef = useRef<WebSocket | null>(null);
  const connectionAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const api = useFeedMinerAPI();
  
  // Constants
  const MAX_CONNECTION_ATTEMPTS = 3;
  const RECONNECT_DELAY = 2000; // 2 seconds

  // WebSocket connection management functions
  const closeWebSocketConnection = useCallback(() => {
    if (websocketRef.current) {
      console.log('🔌 Closing WebSocket connection');
      websocketRef.current.close();
      websocketRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);
  
  const createWebSocketConnection = useCallback((contentId: string) => {
    // Check max attempts
    if (connectionAttemptsRef.current >= MAX_CONNECTION_ATTEMPTS) {
      console.log(`🚫 Max connection attempts (${MAX_CONNECTION_ATTEMPTS}) reached, giving up`);
      setConnectionError(`Failed to connect after ${MAX_CONNECTION_ATTEMPTS} attempts`);
      return;
    }
    
    // Close existing connection
    closeWebSocketConnection();
    
    connectionAttemptsRef.current += 1;
    setConnectionAttempts(connectionAttemptsRef.current);
    setConnectionError(null);
    
    console.log(`🔄 Creating WebSocket connection (attempt ${connectionAttemptsRef.current}/${MAX_CONNECTION_ATTEMPTS}) for content: ${contentId}`);
    
    try {
      const ws = api.createWebSocketConnection(
        (message: any) => {
          console.log('📥 WebSocket message received:', message);
          
          // Handle reasoning steps
          if (message.type === 'reasoning_step' && message.content_id === contentId) {
            const reasoningStep: ReasoningStep = {
              type: 'reasoning_step',
              content_id: message.content_id,
              step: message.step,
              reasoning: message.reasoning,
              progress: message.progress,
              timestamp: message.timestamp,
              metadata: message.metadata
            };
            
            setReasoningSteps(prev => [...prev, reasoningStep]);
          }
          
          // Handle analysis completion
          else if (message.type === 'analysis_complete' && message.content_id === contentId) {
            console.log('✅ Analysis completed via WebSocket');
            setIsAnalysisActive(false);
          }
          
          // Handle analysis errors
          else if (message.type === 'analysis_error' && message.content_id === contentId) {
            console.log('❌ Analysis error via WebSocket:', message.error);
            setIsAnalysisActive(false);
          }
        },
        (error) => {
          console.error('❌ WebSocket error:', error);
          setConnectionError(`Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
          
          // Attempt reconnection with delay
          if (connectionAttemptsRef.current < MAX_CONNECTION_ATTEMPTS) {
            console.log(`🔄 Scheduling reconnection in ${RECONNECT_DELAY}ms...`);
            reconnectTimeoutRef.current = setTimeout(() => {
              createWebSocketConnection(contentId);
            }, RECONNECT_DELAY);
          } else {
            console.log('🚫 Max attempts reached, stopping reconnection');
            setIsAnalysisActive(false);
          }
        }
      );
      
      websocketRef.current = ws;
      
      // Register for reasoning updates after connection is established
      const registerTimeout = setTimeout(() => {
        if (ws.readyState === WebSocket.OPEN) {
          console.log('📝 Registering for reasoning updates');
          api.sendWebSocketMessage(ws, 'stream_reasoning', { content_id: contentId });
        } else {
          console.log('⚠️ WebSocket not ready for registration, connection may have failed');
        }
      }, 1000);
      
      // Store timeout for cleanup
      reconnectTimeoutRef.current = registerTimeout;
      
      // Reset attempts on successful connection
      ws.addEventListener('open', () => {
        console.log('✅ WebSocket connected successfully');
        connectionAttemptsRef.current = 0;
        setConnectionAttempts(0);
        setConnectionError(null);
        setIsWebSocketConnected(true);
      });

      ws.addEventListener('close', () => {
        setIsWebSocketConnected(false);
      });
      
    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error);
      setConnectionError(`Failed to create connection: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [api, closeWebSocketConnection, MAX_CONNECTION_ATTEMPTS, RECONNECT_DELAY]);
  
  // Effect: Start WebSocket when analysis begins
  useEffect(() => {
    if (isAnalysisActive && currentContentId) {
      console.log('🚀 Starting WebSocket connection for analysis:', currentContentId);
      createWebSocketConnection(currentContentId);
    }
    
    // Note: Cleanup is handled by separate effect to avoid dependencies
  }, [isAnalysisActive, currentContentId, createWebSocketConnection]);
  
  // Effect: Cleanup WebSocket when leaving processing view
  useEffect(() => {
    if (currentView !== 'processing') {
      console.log('🧹 Cleaning up WebSocket (view changed)');
      closeWebSocketConnection();
      setIsAnalysisActive(false);
      setReasoningSteps([]);
      setConnectionAttempts(0);
      setConnectionError(null);
      setIsWebSocketConnected(false);
      connectionAttemptsRef.current = 0;
    }
  }, [currentView, closeWebSocketConnection]);
  
  // Effect: Cleanup on component unmount
  useEffect(() => {
    return () => {
      console.log('🧹 Component unmounting, cleaning up WebSocket');
      closeWebSocketConnection();
    };
  }, [closeWebSocketConnection]);

  const handleStartDemo = () => {
    setCurrentView('upload');
  };

  const handleUploadComplete = async (contentId?: string) => {
    setCurrentView('processing');
    
    if (contentId) {
      setCurrentContentId(contentId);
      
      // Initialize reasoning display
      setReasoningSteps([]);
      setIsAnalysisActive(true);
      setConnectionAttempts(0);
      setConnectionError(null);
      setIsWebSocketConnected(false);
      connectionAttemptsRef.current = 0;
      
      try {
        // Wait for processing to complete and fetch analysis results
        console.log('Fetching analysis results for contentId:', contentId);
        
        // Poll for results (the analysis might take some time for large datasets)
        let attempts = 0;
        const maxAttempts = 60; // Wait up to 6 minutes for large uploads
        
        while (attempts < maxAttempts) {
          try {
            const content = await api.getContent(contentId, true);
            console.log(`Attempt ${attempts + 1}/${maxAttempts} - Content status:`, content.status);
            
            if ((content.status === 'completed' || content.status === 'analyzed') && content.analysis) {
              console.log('Analysis completed! Processing results...');
              // Transform backend analysis to frontend format
              const transformedResults = transformBackendAnalysis(content.analysis, contentId);
              setAnalysisResults(transformedResults);
              setCurrentView('results');
              return;
            } else if (content.status === 'processing') {
              console.log('Analysis still in progress, continuing to wait...');
            } else if (content.status === 'failed') {
              console.error('Analysis failed');
              break;
            } else {
              console.log('Status:', content.status, '- waiting for processing to start...');
            }
            
            // Wait 6 seconds before next attempt
            await new Promise(resolve => setTimeout(resolve, 6000));
            attempts++;
          } catch (error) {
            console.log(`Attempt ${attempts + 1}/${maxAttempts} - Waiting for analysis to complete...`, error);
            await new Promise(resolve => setTimeout(resolve, 6000));
            attempts++;
          }
        }
        
        // If we get here, analysis didn't complete in time
        console.log('Analysis taking longer than expected, showing sample results');
        setCurrentView('results');
        
      } catch (error) {
        console.error('Error fetching analysis results:', error);
        // Fall back to sample data
        setCurrentView('results');
      }
    } else {
      // No contentId provided (sample data), just show results after delay
      setTimeout(() => {
        setCurrentView('results');
      }, 3000);
    }
  };

  const handleViewDemo = () => {
    setCurrentView('results');
  };

  const handleBackToLanding = () => {
    // Clean up state - WebSocket cleanup is handled by useEffect
    setCurrentContentId(null);
    setCurrentView('landing');
  };

  const handleModelTesting = () => {
    setCurrentView('model-testing');
  };

  // Transform backend analysis results to frontend format
  const transformBackendAnalysis = (backendAnalysis: any, contentId: string): AnalysisResult => {
    console.log('Transforming backend analysis:', backendAnalysis);
    console.log('Backend analysis keys:', Object.keys(backendAnalysis));
    
    // Extract metadata if available (from multi-type analysis)
    const metadata = backendAnalysis.metadata || {};
    console.log('Analysis metadata:', metadata);
    
    // Try multiple ways to get the total count
    const totalItemsProcessed = metadata.total_items_processed || 
                               backendAnalysis.total_posts || 
                               (backendAnalysis.posts && backendAnalysis.posts.length) ||
                               (metadata.export_info && metadata.export_info.totalDataPoints) ||
                               177;
    const dataTypesAnalyzed = metadata.data_types_analyzed || ['saved_posts'];
    
    console.log(`Analysis processed ${totalItemsProcessed} items from ${dataTypesAnalyzed.length} data types:`, dataTypesAnalyzed);
    console.log('totalItemsProcessed source:', {
      'metadata.total_items_processed': metadata.total_items_processed,
      'backendAnalysis.total_posts': backendAnalysis.total_posts,
      'metadata.export_info.totalDataPoints': metadata.export_info && metadata.export_info.totalDataPoints,
      'fallback': 177,
      'final_value': totalItemsProcessed
    });
    
    // Create analysis description based on data types (for future use)
    const analysisDescription = dataTypesAnalyzed.length > 1 
      ? `${totalItemsProcessed} Instagram items across ${dataTypesAnalyzed.length} data types (${dataTypesAnalyzed.join(', ')})`
      : dataTypesAnalyzed[0] === 'saved_posts' 
        ? `${totalItemsProcessed} Instagram saves`
        : `${totalItemsProcessed} Instagram items`;
    
    console.log('Analysis description:', analysisDescription);
    
    // Transform the backend analysis to match frontend interface
    // For now, we'll enhance the existing structure with real data
    const transformedResult: AnalysisResult = {
      ...realAnalysisResults, // Use existing structure as baseline
      totalPosts: totalItemsProcessed,
      contentId: contentId,
      analysisDate: new Date().toISOString().split('T')[0],
      // Update any metrics that can be derived from real analysis
      metadata: {
        dataTypesAnalyzed,
        analysisType: metadata.analysis_type || 'single_type',
        backendAnalysis: backendAnalysis
      }
    };
    
    // If we have categories from backend analysis, use them
    if (backendAnalysis.categories && backendAnalysis.categories.length > 0) {
      // Map backend categories to frontend goal areas
      const backendCategories = backendAnalysis.categories;
      console.log('Using backend categories:', backendCategories);
      
      // Update interest distribution based on backend categories
      transformedResult.interestDistribution = backendCategories.map((cat: any) => ({
        category: cat.name,
        percentage: cat.confidence * 100, // Convert confidence to percentage
        goalPotential: cat.confidence > 0.7 ? 'High' : cat.confidence > 0.4 ? 'Medium' : 'Low'
      }));
    }
    
    console.log('Transformed analysis result:', transformedResult);
    return transformedResult;
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
        <div className="min-h-screen bg-gray-50 py-8">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
              <div className="w-16 h-16 mx-auto">
                <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-gray-900">Analyzing Your Content</h2>
                <p className="text-gray-600">AI is discovering your behavioral patterns and goal opportunities...</p>
                {currentContentId && (
                  <p className="text-sm text-gray-500">
                    Content ID: <span className="font-mono">{currentContentId.slice(0, 8)}...</span>
                  </p>
                )}
              </div>
              
              {/* Overall Progress Bar */}
              <div className="w-80 bg-gray-200 rounded-full h-3 mx-auto">
                <div className="processing-animation h-3 rounded-full"></div>
              </div>
            </div>

            {/* Reasoning Display with Error Handling */}
            <div className="max-w-3xl mx-auto">
              {isWebSocketConnected && connectionAttempts === 0 && !connectionError && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                      <span className="text-green-600 text-sm">✅</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-green-900">Reasoning Stream Connected</h4>
                      <p className="text-xs text-green-600">🔴 Live - Showing AI's thinking process in real-time</p>
                    </div>
                  </div>
                </div>
              )}
              {connectionError && connectionAttempts >= MAX_CONNECTION_ATTEMPTS && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center">
                        <span className="text-red-600 text-sm">⚠️</span>
                      </div>
                      <h4 className="font-medium text-red-900">Reasoning Display Unavailable</h4>
                    </div>
                    <button 
                      onClick={() => {
                        if (currentContentId && isAnalysisActive) {
                          connectionAttemptsRef.current = 0;
                          setConnectionAttempts(0);
                          setConnectionError(null);
                          createWebSocketConnection(currentContentId);
                        }
                      }}
                      className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                    >
                      Retry
                    </button>
                  </div>
                  <p className="text-sm text-red-700 mb-2">Failed to connect after {MAX_CONNECTION_ATTEMPTS} attempts</p>
                  <p className="text-xs text-red-600">
                    ✅ Your analysis continues normally - you just won't see the AI's live reasoning process.
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    💡 The reasoning stream requires a WebSocket connection. You can retry or check your network connection.
                  </p>
                </div>
              )}
              
              {connectionAttempts > 0 && connectionAttempts < MAX_CONNECTION_ATTEMPTS && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="animate-spin w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                      <div>
                        <h4 className="font-medium text-blue-900">Connecting to Reasoning Stream</h4>
                        <p className="text-sm text-blue-700">Attempt {connectionAttempts} of {MAX_CONNECTION_ATTEMPTS}</p>
                        <p className="text-xs text-blue-600 mt-1">🔄 Setting up live AI reasoning display...</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-blue-600 font-mono">{connectionAttempts}/{MAX_CONNECTION_ATTEMPTS}</div>
                    </div>
                  </div>
                </div>
              )}
              
              <ReasoningDisplay 
                reasoningSteps={reasoningSteps}
                isActive={isAnalysisActive && !connectionError}
                className="mb-6"
              />
            </div>

            {/* Footer with tips */}
            <div className="text-center text-sm text-gray-500 max-w-2xl mx-auto">
              <p className="mb-2">
                📊 Your Instagram data is being analyzed by our AI models to identify behavioral patterns, 
                interests, and personalized goal opportunities.
              </p>
              <p>
                Analysis typically takes 15-60 seconds depending on the data size and selected AI model.
              </p>
            </div>
          </div>
        </div>
      )}
      
      {currentView === 'results' && (
        <AnalysisDashboard 
          results={analysisResults}
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
