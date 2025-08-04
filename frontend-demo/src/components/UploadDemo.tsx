import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import JSZip from 'jszip';
import { sampleInstagramData } from '../data/analysisResults';
import { smallTestDataset } from '../data/smallTestDataset';
import { useFeedMinerAPI } from '../services/feedminerApi';
import ModelSelector, { type ModelInfo, AVAILABLE_MODELS } from './ModelSelector';

interface UploadDemoProps {
  onUploadComplete: (contentId?: string) => void;
  onBack: () => void;
}

interface InstagramDataType {
  id: string;
  name: string;
  description: string;
  filePath: string;
  found: boolean;
  count?: number;
  lastActivity?: string;
}

interface ZipAnalysis {
  isInstagramExport: boolean;
  exportFolder?: string;
  availableDataTypes: InstagramDataType[];
  totalFiles: number;
  estimatedSize: string;
}

const UploadDemo: React.FC<UploadDemoProps> = ({ onUploadComplete, onBack }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [step, setStep] = useState<'upload' | 'preview' | 'data-selection' | 'confirm'>('upload');
  const [zipAnalysis, setZipAnalysis] = useState<ZipAnalysis | null>(null);
  const [selectedDataTypes, setSelectedDataTypes] = useState<string[]>(['saved_posts']);
  const [extractionProgress, setExtractionProgress] = useState(0);
  const [selectedModel, setSelectedModel] = useState<ModelInfo>(
    AVAILABLE_MODELS.find(m => m.recommended) || AVAILABLE_MODELS[2] // Default to Nova Micro
  );

  const api = useFeedMinerAPI();

  // Analyze ZIP file for Instagram export structure
  const analyzeInstagramZip = async (file: File): Promise<ZipAnalysis> => {
    const zip = await JSZip.loadAsync(file);
    const files = Object.keys(zip.files);
    
    // Look for Instagram export folder pattern (can be nested under meta-* folder)
    // Pattern matches: meta-*/instagram-username-YYYY-MM-DD-hash/ or instagram-username-YYYY-MM-DD-hash/
    const instagramFolderPattern = /(?:meta-[^/]+\/)?instagram-[^/]+-\d{4}-\d{2}-\d{2}-[^/]+\//;
    let exportFolder = '';
    
    for (const filePath of files) {
      const match = filePath.match(instagramFolderPattern);
      if (match) {
        exportFolder = match[0];
        break;
      }
    }
    
    if (!exportFolder) {
      return {
        isInstagramExport: false,
        availableDataTypes: [],
        totalFiles: files.length,
        estimatedSize: (file.size / 1024 / 1024).toFixed(1) + ' MB'
      };
    }
    
    // Define Instagram data types to look for
    const dataTypeMap: Record<string, InstagramDataType> = {
      saved_posts: {
        id: 'saved_posts',
        name: 'Saved Posts',
        description: 'Posts you saved on Instagram',
        filePath: `${exportFolder}your_instagram_activity/saved/saved_posts.json`,
        found: false
      },
      liked_posts: {
        id: 'liked_posts', 
        name: 'Liked Posts',
        description: 'Posts you liked on Instagram',
        filePath: `${exportFolder}your_instagram_activity/likes/liked_posts.json`,
        found: false
      },
      comments: {
        id: 'comments',
        name: 'Comments',
        description: 'Comments you made on posts',
        filePath: `${exportFolder}your_instagram_activity/comments/post_comments_1.json`,
        found: false
      },
      user_posts: {
        id: 'user_posts',
        name: 'Your Posts',
        description: 'Posts you created and shared',
        filePath: `${exportFolder}your_instagram_activity/media/posts_1.json`,
        found: false
      },
      following: {
        id: 'following',
        name: 'Following',
        description: 'Accounts you follow',
        filePath: `${exportFolder}connections/followers_and_following/following.json`,
        found: false
      }
    };
    
    // Check which data types are available
    const availableDataTypes: InstagramDataType[] = [];
    
    for (const [key, dataType] of Object.entries(dataTypeMap)) {
      if (zip.files[dataType.filePath]) {
        try {
          const fileContent = await zip.files[dataType.filePath].async('text');
          const jsonData = JSON.parse(fileContent);
          
          // Count items based on data type
          let count = 0;
          if (key === 'saved_posts' && jsonData.saved_saved_media) {
            count = jsonData.saved_saved_media.length;
          } else if (key === 'liked_posts' && jsonData.likes_media_likes) {
            count = jsonData.likes_media_likes.length;
          } else if (key === 'comments' && jsonData.comments_media_comments) {
            count = jsonData.comments_media_comments.length;
          } else if (key === 'user_posts' && Array.isArray(jsonData)) {
            count = jsonData.length;
          } else if (key === 'following' && jsonData.relationships_following) {
            count = jsonData.relationships_following.length;
          }
          
          dataType.found = true;
          dataType.count = count;
          availableDataTypes.push(dataType);
        } catch (error) {
          console.warn(`Failed to parse ${dataType.filePath}:`, error);
        }
      }
    }
    
    return {
      isInstagramExport: availableDataTypes.length > 0,
      exportFolder,
      availableDataTypes,
      totalFiles: files.length,
      estimatedSize: (file.size / 1024 / 1024).toFixed(1) + ' MB'
    };
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      
      // Check if it's a ZIP file
      if (file.type === 'application/zip' || file.name.endsWith('.zip')) {
        setIsProcessing(true);
        setExtractionProgress(0);
        
        try {
          // Simulate progress for UX
          const progressInterval = setInterval(() => {
            setExtractionProgress(prev => Math.min(prev + 10, 90));
          }, 100);
          
          const analysis = await analyzeInstagramZip(file);
          
          clearInterval(progressInterval);
          setExtractionProgress(100);
          
          setZipAnalysis(analysis);
          
          if (analysis.isInstagramExport) {
            // Set default selection to saved posts if available
            const savedPostsAvailable = analysis.availableDataTypes.find(dt => dt.id === 'saved_posts');
            if (savedPostsAvailable) {
              setSelectedDataTypes(['saved_posts']);
            } else {
              setSelectedDataTypes([analysis.availableDataTypes[0]?.id || '']);
            }
            setStep('data-selection');
          } else {
            setStep('preview');
          }
        } catch (error) {
          console.error('ZIP analysis failed:', error);
          alert('Failed to analyze ZIP file. Please ensure it\'s a valid Instagram export.');
          setUploadedFile(null);
        } finally {
          setIsProcessing(false);
          setExtractionProgress(0);
        }
      } else {
        setStep('preview');
      }
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

  const handleUseSmallTestData = () => {
    setStep('preview');
    setUploadedFile(new File([JSON.stringify(smallTestDataset, null, 2)], 'small-test-data.json', { type: 'application/json' }));
    // Set up for multi-upload test
    setZipAnalysis({
      isInstagramExport: true,
      exportFolder: smallTestDataset.exportInfo.exportFolder,
      availableDataTypes: [
        {
          id: 'saved_posts',
          name: 'Saved Posts',
          description: 'Posts you saved on Instagram',
          filePath: 'saved_posts.json',
          found: true,
          count: 3
        },
        {
          id: 'liked_posts',
          name: 'Liked Posts', 
          description: 'Posts you liked on Instagram',
          filePath: 'liked_posts.json',
          found: true,
          count: 2
        }
      ],
      totalFiles: 2,
      estimatedSize: '2.1 KB'
    });
    setSelectedDataTypes(['saved_posts', 'liked_posts']);
  };

  const extractDataFromZip = async (file: File, dataTypeId: string): Promise<any> => {
    if (!zipAnalysis || !zipAnalysis.isInstagramExport) {
      throw new Error('Invalid Instagram export');
    }
    
    const zip = await JSZip.loadAsync(file);
    const dataType = zipAnalysis.availableDataTypes.find(dt => dt.id === dataTypeId);
    
    if (!dataType) {
      throw new Error(`Data type ${dataTypeId} not found`);
    }
    
    const zipFile = zip.files[dataType.filePath];
    if (!zipFile) {
      throw new Error(`File ${dataType.filePath} not found in ZIP`);
    }
    
    const fileContent = await zipFile.async('text');
    return JSON.parse(fileContent);
  };

  const handleConfirmUpload = async () => {
    setIsProcessing(true);
    setStep('confirm');
    
    try {
      let contentToUpload;
      let uploadType = 'instagram_saved';
      
      if (uploadedFile && uploadedFile.name.includes('sample')) {
        // Use sample data
        contentToUpload = sampleInstagramData;
      } else if (uploadedFile && uploadedFile.name.includes('small-test-data')) {
        // Use small test data - already in the right format
        contentToUpload = smallTestDataset;
        uploadType = 'instagram_export';
      } else if (uploadedFile) {
        // Check if it's a ZIP file
        if (uploadedFile.type === 'application/zip' || uploadedFile.name.endsWith('.zip')) {
          if (!zipAnalysis?.isInstagramExport) {
            throw new Error('This ZIP file does not appear to be a valid Instagram export.');
          }
          
          // Extract selected data types from ZIP - always use consolidated structure for ZIP files
          const consolidatedData: any = {
            exportInfo: {
              dataTypes: selectedDataTypes,
              extractedAt: new Date().toISOString(),
              exportFolder: zipAnalysis.exportFolder
            }
          };
          
          for (const dataTypeId of selectedDataTypes) {
            try {
              const data = await extractDataFromZip(uploadedFile, dataTypeId);
              consolidatedData[dataTypeId] = data;
            } catch (error) {
              console.warn(`Failed to extract ${dataTypeId}:`, error);
            }
          }
          
          contentToUpload = consolidatedData;
          uploadType = 'instagram_export';
        } else {
          // Regular JSON file
          const fileContent = await uploadedFile.text();
          
          try {
            contentToUpload = JSON.parse(fileContent);
          } catch (parseError) {
            throw new Error('Invalid JSON file. Please upload a valid Instagram export JSON file.');
          }
        }
      } else {
        throw new Error('No file selected');
      }

      console.log('Uploading content to backend...', { 
        type: uploadType, 
        size: JSON.stringify(contentToUpload).length,
        dataTypes: selectedDataTypes
      });
      
      const response = await api.uploadContent(
        contentToUpload, 
        uploadType, 
        'demo-user',
        {
          provider: selectedModel.provider,
          model: selectedModel.model,
          temperature: 0.7
        }
      );
      
      console.log('Upload successful:', response);
      onUploadComplete(response.contentId);
      
    } catch (err) {
      console.error('Upload failed:', err);
      alert('Upload failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
      setIsProcessing(false);
      setStep(zipAnalysis?.isInstagramExport ? 'data-selection' : 'preview'); // Go back to appropriate step
    }
  };

  const handleStartOver = () => {
    setUploadedFile(null);
    setZipAnalysis(null);
    setSelectedDataTypes(['saved_posts']);
    setSelectedModel(AVAILABLE_MODELS.find(m => m.recommended) || AVAILABLE_MODELS[2]);
    setStep('upload');
    setIsProcessing(false);
  };

  const handleDataTypeToggle = (dataTypeId: string) => {
    setSelectedDataTypes(prev => {
      if (prev.includes(dataTypeId)) {
        return prev.filter(id => id !== dataTypeId);
      } else {
        return [...prev, dataTypeId];
      }
    });
  };

  const handleProceedWithSelection = () => {
    if (selectedDataTypes.length === 0) {
      alert('Please select at least one data type to analyze.');
      return;
    }
    setStep('preview');
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
                step === 'upload' ? 'bg-primary-600 text-white' : 
                ['data-selection', 'preview', 'confirm'].includes(step) ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                1
              </div>
              <div className="w-8 h-1 bg-gray-300"></div>
              {zipAnalysis?.isInstagramExport && (
                <>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step === 'data-selection' ? 'bg-primary-600 text-white' : 
                    ['preview', 'confirm'].includes(step) ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
                  }`}>
                    2
                  </div>
                  <div className="w-8 h-1 bg-gray-300"></div>
                </>
              )}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'preview' ? 'bg-primary-600 text-white' : 
                step === 'confirm' ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                {zipAnalysis?.isInstagramExport ? '3' : '2'}
              </div>
              <div className="w-8 h-1 bg-gray-300"></div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'confirm' ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                {zipAnalysis?.isInstagramExport ? '4' : '3'}
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
                  <p>Select "Your Activity" and any data you want to analyze → Request Download</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-primary-100 text-primary-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">3</span>
                  <p>Upload the entire ZIP file here - we'll extract and analyze your selected data types</p>
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
                        Drag & drop your Instagram export file here
                      </p>
                      <p className="text-gray-500">or click to browse</p>
                    </>
                  )}
                  <p className="text-xs text-gray-400">Supports: Complete ZIP exports (recommended) or individual .json files</p>
                </div>
              </div>

              {/* Demo Option */}
              <div className="text-center">
                <div className="inline-flex items-center space-x-4">
                  <div className="h-px bg-gray-300 flex-1"></div>
                  <span className="text-gray-500 text-sm">or</span>
                  <div className="h-px bg-gray-300 flex-1"></div>
                </div>
                <div className="mt-4 space-y-3">
                  <button 
                    onClick={handleUseSampleData}
                    className="btn-secondary"
                  >
                    Use Sample Data for Demo
                  </button>
                  <p className="text-xs text-gray-500 mt-1">
                    See how FeedMiner works with real analysis results (177 Instagram saves)
                  </p>
                  
                  <button 
                    onClick={handleUseSmallTestData}
                    className="btn-secondary bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100"
                  >
                    🧪 Use Small Test Dataset
                  </button>
                  <p className="text-xs text-blue-600 mt-1">
                    Debug multi-upload with minimal data (5 items, 2KB) - Perfect for testing!
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 'data-selection' && zipAnalysis && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Select Data to Analyze
              </h2>
              <p className="text-lg text-gray-600">
                We found multiple data types in your Instagram export. Choose what you'd like to analyze.
              </p>
            </div>

            {/* ZIP Analysis Summary */}
            <div className="card">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">📦</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">Instagram Export Detected</h3>
                  <p className="text-sm text-gray-600">
                    {zipAnalysis.totalFiles} files • {zipAnalysis.estimatedSize} • {zipAnalysis.availableDataTypes.length} data types found
                  </p>
                </div>
              </div>
              
              {extractionProgress > 0 && extractionProgress < 100 && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Analyzing export structure...</span>
                    <span>{extractionProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${extractionProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>

            {/* Data Type Selection */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">📊 Available Data Types</h3>
              <div className="space-y-3">
                {zipAnalysis.availableDataTypes.map((dataType) => (
                  <label 
                    key={dataType.id}
                    className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedDataTypes.includes(dataType.id)}
                      onChange={() => handleDataTypeToggle(dataType.id)}
                      className="mt-1 w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-gray-900">{dataType.name}</h4>
                        <span className="text-sm text-primary-600 font-medium">
                          {dataType.count?.toLocaleString()} items
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{dataType.description}</p>
                      {dataType.lastActivity && (
                        <p className="text-xs text-gray-500 mt-1">
                          Last activity: {dataType.lastActivity}
                        </p>
                      )}
                    </div>
                  </label>
                ))}
              </div>
              
              {selectedDataTypes.length > 0 && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Analysis Preview</h4>
                  <p className="text-sm text-blue-800">
                    Selected {selectedDataTypes.length} data type{selectedDataTypes.length > 1 ? 's' : ''} for analysis:
                  </p>
                  <ul className="text-sm text-blue-700 mt-1">
                    {selectedDataTypes.map(typeId => {
                      const dataType = zipAnalysis.availableDataTypes.find(dt => dt.id === typeId);
                      return (
                        <li key={typeId} className="flex justify-between">
                          <span>• {dataType?.name}</span>
                          <span>{dataType?.count?.toLocaleString()} items</span>
                        </li>
                      );
                    })}
                  </ul>
                  <div className="mt-2 text-sm text-blue-800">
                    <strong>Total items to analyze: {selectedDataTypes.reduce((total, typeId) => {
                      const dataType = zipAnalysis.availableDataTypes.find(dt => dt.id === typeId);
                      return total + (dataType?.count || 0);
                    }, 0).toLocaleString()}</strong>
                  </div>
                </div>
              )}
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
                onClick={handleProceedWithSelection}
                disabled={selectedDataTypes.length === 0}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue to Preview
              </button>
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
                {zipAnalysis?.isInstagramExport 
                  ? `Ready to analyze ${selectedDataTypes.length} data type${selectedDataTypes.length > 1 ? 's' : ''} from your Instagram export.`
                  : "We've detected your Instagram data. Review before processing."
                }
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
                    File size: {(uploadedFile.size / 1024 / 1024).toFixed(1)} MB • Format: {zipAnalysis?.isInstagramExport ? 'Instagram Export (ZIP)' : 'JSON'}
                  </p>
                  {zipAnalysis?.isInstagramExport && (
                    <p className="text-sm text-green-600 mt-1">
                      ✓ {selectedDataTypes.length} data type{selectedDataTypes.length > 1 ? 's' : ''} selected for analysis
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Data Preview */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">📊 What We'll Analyze</h3>
              {zipAnalysis?.isInstagramExport ? (
                <div className="space-y-3">
                  {selectedDataTypes.map(typeId => {
                    const dataType = zipAnalysis.availableDataTypes.find(dt => dt.id === typeId);
                    if (!dataType) return null;
                    return (
                      <div key={typeId} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900">{dataType.name}</h4>
                          <p className="text-sm text-gray-600">{dataType.description}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-xl font-bold text-primary-600">{dataType.count?.toLocaleString()}</div>
                          <div className="text-sm text-gray-600">items</div>
                        </div>
                      </div>
                    );
                  })}
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600 mb-1">
                        {selectedDataTypes.reduce((total, typeId) => {
                          const dataType = zipAnalysis.availableDataTypes.find(dt => dt.id === typeId);
                          return total + (dataType?.count || 0);
                        }, 0).toLocaleString()}
                      </div>
                      <div className="text-sm text-blue-800">Total Items for Analysis</div>
                    </div>
                  </div>
                </div>
              ) : (
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
              )}
            </div>

            {/* Model Selection */}
            <div className="card">
              <ModelSelector
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
                showDetails={true}
              />
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
                  ? `${selectedModel.name} is analyzing your Instagram behavior patterns and generating personalized goals.`
                  : 'Your analysis is ready! Redirecting to results...'
                }
              </p>
              
              {isProcessing && (
                <div className="text-sm text-gray-500 space-y-1">
                  <p>Using: {selectedModel.name} ({selectedModel.family})</p>
                  <p>Expected processing time: ~{selectedModel.avgResponseTime}</p>
                </div>
              )}
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