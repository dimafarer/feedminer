import { useState } from 'react';
import LandingPage from './components/LandingPage';
import UploadDemo from './components/UploadDemo';
import AnalysisDashboard from './components/AnalysisDashboard';
import ModelTestingPage from './components/ModelTestingPage';
import { realAnalysisResults, type AnalysisResult } from './data/analysisResults';
import { useFeedMinerAPI } from './services/feedminerApi';

type AppState = 'landing' | 'upload' | 'processing' | 'results' | 'model-testing';

function App() {
  const [currentView, setCurrentView] = useState<AppState>('landing');
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult>(realAnalysisResults);
  const [, setCurrentContentId] = useState<string | null>(null);
  
  const api = useFeedMinerAPI();

  const handleStartDemo = () => {
    setCurrentView('upload');
  };

  const handleUploadComplete = async (contentId?: string) => {
    setCurrentView('processing');
    
    if (contentId) {
      setCurrentContentId(contentId);
      
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
