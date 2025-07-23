import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { sampleInstagramData } from '../data/analysisResults';
import { useFeedMinerAPI } from '../services/feedminerApi';

interface UploadDemoProps {
  onUploadComplete: () => void;
  onBack: () => void;
}

const UploadDemo: React.FC<UploadDemoProps> = ({ onUploadComplete, onBack }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [step, setStep] = useState<'upload' | 'preview' | 'confirm'>('upload');

  const api = useFeedMinerAPI();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      setStep('preview');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'application/zip': ['.zip']
    },
    maxFiles: 1
  });

  const handleUseSampleData = () => {
    setStep('preview');
    setUploadedFile(new File([JSON.stringify(sampleInstagramData, null, 2)], 'sample-instagram-data.json', { type: 'application/json' }));
  };

  const handleConfirmUpload = async () => {
    setIsProcessing(true);
    setStep('confirm');
    
    try {
      let contentToUpload;
      
      if (uploadedFile && uploadedFile.name.includes('sample')) {
        // Use sample data
        contentToUpload = sampleInstagramData;
      } else if (uploadedFile) {
        // Read actual file content
        const fileContent = await uploadedFile.text();
        contentToUpload = JSON.parse(fileContent);
      } else {
        throw new Error('No file selected');
      }

      console.log('Uploading content to backend...', { type: 'instagram_saved', size: JSON.stringify(contentToUpload).length });
      
      const response = await api.uploadContent(
        contentToUpload, 
        'instagram_saved', 
        'demo-user'
      );
      
      console.log('Upload successful:', response);
      onUploadComplete();
      
    } catch (err) {
      console.error('Upload failed:', err);
      alert('Upload failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
      setIsProcessing(false);
      setStep('preview'); // Go back to preview to allow retry
    }
  };

  const handleStartOver = () => {
    setUploadedFile(null);
    setStep('upload');
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <button 
                onClick={onBack}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Upload Instagram Data</h1>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'upload' ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                1
              </div>
              <div className="w-8 h-1 bg-gray-300"></div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'preview' ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                2
              </div>
              <div className="w-8 h-1 bg-gray-300"></div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'confirm' ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                3
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {step === 'upload' && (
          <div className="space-y-8">
            {/* Instructions */}
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Upload Your Instagram Data Export
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                FeedMiner analyzes your saved posts to discover your interests and generate personalized goals. 
                Your data stays secure and is processed privately.
              </p>
            </div>

            {/* How to Export Guide */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">📱 How to Export Your Instagram Data</h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start space-x-3">
                  <span className="bg-primary-100 text-primary-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">1</span>
                  <p>Go to Instagram → Settings → Privacy and Security → Download Your Information</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-primary-100 text-primary-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">2</span>
                  <p>Select "Your Activity" → Include "Saved Posts" → Request Download</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-primary-100 text-primary-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">3</span>
                  <p>Download the ZIP file and upload the "saved_posts.json" file here</p>
                </div>
              </div>
            </div>

            {/* Upload Area */}
            <div className="space-y-6">
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
                  isDragActive 
                    ? 'border-primary-400 bg-primary-50' 
                    : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                }`}
              >
                <input {...getInputProps()} />
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-3xl">📁</span>
                  </div>
                  {isDragActive ? (
                    <p className="text-lg text-primary-600 font-medium">Drop your file here...</p>
                  ) : (
                    <>
                      <p className="text-lg text-gray-700 font-medium">
                        Drag & drop your Instagram JSON file here
                      </p>
                      <p className="text-gray-500">or click to browse</p>
                    </>
                  )}
                  <p className="text-xs text-gray-400">Supports: .json, .zip files</p>
                </div>
              </div>

              {/* Demo Option */}
              <div className="text-center">
                <div className="inline-flex items-center space-x-4">
                  <div className="h-px bg-gray-300 flex-1"></div>
                  <span className="text-gray-500 text-sm">or</span>
                  <div className="h-px bg-gray-300 flex-1"></div>
                </div>
                <div className="mt-4">
                  <button 
                    onClick={handleUseSampleData}
                    className="btn-secondary"
                  >
                    Use Sample Data for Demo
                  </button>
                  <p className="text-xs text-gray-500 mt-2">
                    See how FeedMiner works with real analysis results (177 Instagram saves)
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 'preview' && uploadedFile && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Preview Your Data
              </h2>
              <p className="text-lg text-gray-600">
                We've detected your Instagram saved posts. Review the data before processing.
              </p>
            </div>

            {/* File Info */}
            <div className="card">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">✅</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{uploadedFile.name}</h3>
                  <p className="text-sm text-gray-600">
                    File size: {(uploadedFile.size / 1024).toFixed(1)} KB • Format: JSON
                  </p>
                </div>
              </div>
            </div>

            {/* Data Preview */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">📊 What We'll Analyze</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="metric-card">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600 mb-1">177</div>
                    <div className="text-sm text-gray-600">Saved Posts</div>
                  </div>
                </div>
                <div className="metric-card">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-accent-600 mb-1">5</div>
                    <div className="text-sm text-gray-600">Interest Areas</div>
                  </div>
                </div>
                <div className="metric-card">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 mb-1">3</div>
                    <div className="text-sm text-gray-600">Goal Opportunities</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Features */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">🔍 Analysis Features</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-start space-x-3">
                  <span className="text-green-600 mt-1">✓</span>
                  <div>
                    <p className="font-medium text-gray-900">Interest Classification</p>
                    <p className="text-sm text-gray-600">Categorize content by fitness, learning, business, etc.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-green-600 mt-1">✓</span>
                  <div>
                    <p className="font-medium text-gray-900">Behavioral Pattern Detection</p>
                    <p className="text-sm text-gray-600">Identify learning style and motivation cycles</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-green-600 mt-1">✓</span>
                  <div>
                    <p className="font-medium text-gray-900">Goal Recommendation</p>
                    <p className="text-sm text-gray-600">Generate 30/90/365-day actionable goals</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-green-600 mt-1">✓</span>
                  <div>
                    <p className="font-medium text-gray-900">Evidence-Based Insights</p>
                    <p className="text-sm text-gray-600">Each recommendation backed by your data</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center space-x-4">
              <button 
                onClick={handleStartOver}
                className="btn-secondary"
              >
                Choose Different File
              </button>
              <button 
                onClick={handleConfirmUpload}
                className="btn-primary"
              >
                Start AI Analysis
              </button>
            </div>
          </div>
        )}

        {step === 'confirm' && (
          <div className="text-center space-y-8">
            <div className="w-20 h-20 mx-auto">
              {isProcessing ? (
                <div className="w-20 h-20 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
              ) : (
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-4xl">🚀</span>
                </div>
              )}
            </div>
            
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                {isProcessing ? 'Processing Your Data...' : 'Upload Complete!'}
              </h2>
              <p className="text-lg text-gray-600">
                {isProcessing 
                  ? 'AI is analyzing your Instagram behavior patterns and generating personalized goals.'
                  : 'Your analysis is ready! Redirecting to results...'
                }
              </p>
            </div>

            {isProcessing && (
              <div className="max-w-md mx-auto">
                <div className="bg-gray-200 rounded-full h-3">
                  <div className="processing-animation h-3 rounded-full"></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>Analyzing patterns...</span>
                  <span>Generating goals...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default UploadDemo;