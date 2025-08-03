import React, { useState } from 'react';
import type { ModelProvider } from '../services/feedminerApi';

interface ModelProviderSelectorProps {
  selectedProvider: ModelProvider;
  onProviderChange: (provider: ModelProvider) => void;
  disabled?: boolean;
  showComparison?: boolean;
  onToggleComparison?: (enabled: boolean) => void;
}

interface ModelOption {
  id: string;
  name: string;
  description: string;
  cost: string;
  performance: string;
  capabilities: string[];
  disabled?: boolean;
}

interface ModelFamily {
  name: string;
  color: string;
  description: string;
  models: ModelOption[];
}

const MODEL_FAMILIES: Record<'claude' | 'nova' | 'llama', ModelFamily> = {
  claude: {
    name: 'Anthropic Claude',
    color: 'orange',
    description: 'Advanced reasoning and multimodal capabilities',
    models: [
      {
        id: 'claude-3-5-sonnet-20241022',
        name: 'Claude 3.5 Sonnet',
        description: 'Most capable model for complex reasoning and analysis',
        cost: 'High',
        performance: '1200ms',
        capabilities: ['Text', 'Vision', 'Reasoning'],
      },
      {
        id: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        name: 'Claude 3.5 Sonnet (Bedrock)',
        description: 'Same model via AWS Bedrock for enterprise deployment',
        cost: 'High',
        performance: '1800ms',
        capabilities: ['Text', 'Vision', 'Reasoning'],
      },
    ],
  },
  nova: {
    name: 'Amazon Nova',
    color: 'blue',
    description: '75% cost savings with excellent performance',
    models: [
      {
        id: 'us.amazon.nova-micro-v1:0',
        name: 'Nova Micro',
        description: 'Ultra-fast, text-only model for rapid analysis',
        cost: 'Very Low',
        performance: '986ms',
        capabilities: ['Text'],
      },
      {
        id: 'us.amazon.nova-lite-v1:0',
        name: 'Nova Lite',
        description: 'Fast, multimodal model with great value',
        cost: 'Very Low',
        performance: '1200ms',
        capabilities: ['Text', 'Multimodal'],
      },
    ],
  },
  llama: {
    name: 'Meta Llama',
    color: 'green',
    description: 'Open-source efficiency with competitive performance',
    models: [
      {
        id: 'meta.llama3-1-8b-instruct-v1:0',
        name: 'Llama 3.1 8B',
        description: 'Efficient model with excellent speed',
        cost: 'Low',
        performance: '504ms',
        capabilities: ['Text'],
      },
      {
        id: 'meta.llama3-1-70b-instruct-v1:0',
        name: 'Llama 3.1 70B',
        description: 'More capable model with balanced performance',
        cost: 'Low',
        performance: '861ms',
        capabilities: ['Text'],
      },
    ],
  },
};

// Legacy structure for backward compatibility
const AVAILABLE_MODELS: Record<'anthropic' | 'bedrock' | 'nova' | 'llama', ModelOption[]> = {
  anthropic: MODEL_FAMILIES.claude.models.filter(m => m.id.includes('claude-3-5-sonnet-20241022')),
  bedrock: MODEL_FAMILIES.claude.models.filter(m => m.id.includes('anthropic.')),
  nova: MODEL_FAMILIES.nova.models,
  llama: MODEL_FAMILIES.llama.models,
};

const ModelProviderSelector: React.FC<ModelProviderSelectorProps> = ({
  selectedProvider,
  onProviderChange,
  disabled = false,
  showComparison = false,
  onToggleComparison,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [comparisonEnabled, setComparisonEnabled] = useState(false);

  const handleProviderSelect = (provider: 'anthropic' | 'bedrock' | 'nova' | 'llama', modelId: string) => {
    const newProvider: ModelProvider = {
      provider,
      model: modelId,
      temperature: selectedProvider.temperature || 0.7,
    };
    onProviderChange(newProvider);
  };

  const handleFamilySelect = (family: 'claude' | 'nova' | 'llama') => {
    const firstModel = MODEL_FAMILIES[family].models[0];
    const provider = family === 'claude' ? 'anthropic' : family;
    handleProviderSelect(provider as any, firstModel.id);
  };

  const handleToggleComparison = (enabled: boolean) => {
    setComparisonEnabled(enabled);
    onToggleComparison?.(enabled);
  };

  const selectedModel = [
    ...AVAILABLE_MODELS.anthropic, 
    ...AVAILABLE_MODELS.bedrock,
    ...AVAILABLE_MODELS.nova,
    ...AVAILABLE_MODELS.llama
  ].find(model => model.id === selectedProvider.model);

  const getModelFamily = (modelId: string): 'claude' | 'nova' | 'llama' => {
    if (modelId.includes('nova')) return 'nova';
    if (modelId.includes('llama')) return 'llama';
    return 'claude';
  };

  const currentFamily = getModelFamily(selectedProvider.model);
  const familyColor = MODEL_FAMILIES[currentFamily].color;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">AI Model Selection</h3>
          <p className="text-sm text-gray-600">Choose from 6 models across 3 AI families</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500">v0.4.0+</span>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-orange-400 rounded-full" title="Claude Family"></div>
            <div className="w-2 h-2 bg-blue-400 rounded-full" title="Nova Family"></div>
            <div className="w-2 h-2 bg-green-400 rounded-full" title="Llama Family"></div>
          </div>
        </div>
      </div>

      {/* Current Selection Display */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              familyColor === 'orange' ? 'bg-orange-400' : 
              familyColor === 'blue' ? 'bg-blue-400' : 'bg-green-400'
            }`}></div>
            <div>
              <div className="font-medium text-gray-900">
                {selectedModel?.name || selectedProvider.model}
              </div>
              <div className="text-sm text-gray-600 flex items-center space-x-2">
                <span className="capitalize">{MODEL_FAMILIES[currentFamily].name}</span>
                <span>•</span>
                <span>Temp: {selectedProvider.temperature || 0.7}</span>
                {selectedModel && (
                  <>
                    <span>•</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      selectedModel.cost === 'Very Low' ? 'bg-green-100 text-green-700' :
                      selectedModel.cost === 'Low' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {selectedModel.cost} Cost
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            disabled={disabled}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium disabled:text-gray-400"
          >
            {isExpanded ? 'Collapse' : 'Change Model'}
          </button>
        </div>
      </div>

      {/* Expanded Model Selection */}
      {isExpanded && (
        <div className="space-y-4 border-t border-gray-200 pt-4">
          
          {/* Model Family Tabs */}
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            {(Object.keys(MODEL_FAMILIES) as Array<keyof typeof MODEL_FAMILIES>).map((family) => (
              <button
                key={family}
                onClick={() => handleFamilySelect(family)}
                disabled={disabled}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  currentFamily === family
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 disabled:text-gray-400'
                }`}
              >
                <div className="flex items-center justify-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    MODEL_FAMILIES[family].color === 'orange' ? 'bg-orange-400' : 
                    MODEL_FAMILIES[family].color === 'blue' ? 'bg-blue-400' : 'bg-green-400'
                  }`}></div>
                  <span>{family === 'claude' ? 'Claude' : family === 'nova' ? 'Nova' : 'Llama'}</span>
                  {family === 'nova' && (
                    <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">75% Savings</span>
                  )}
                  {family === 'llama' && (
                    <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">Fastest</span>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Family Description */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm font-medium text-gray-900">{MODEL_FAMILIES[currentFamily].name}</div>
            <div className="text-xs text-gray-600 mt-1">{MODEL_FAMILIES[currentFamily].description}</div>
          </div>

          {/* Model Options for Current Family */}
          <div className="space-y-3">
            {MODEL_FAMILIES[currentFamily].models.map((model) => {
              const provider = currentFamily === 'claude' 
                ? (model.id.includes('anthropic.') ? 'bedrock' : 'anthropic')
                : currentFamily;
              
              return (
                <button
                  key={model.id}
                  onClick={() => handleProviderSelect(provider as any, model.id)}
                  disabled={disabled || model.disabled}
                  className={`w-full text-left p-4 rounded-lg border transition-colors ${
                    selectedProvider.model === model.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  } ${(disabled || model.disabled) ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <div className="font-medium text-gray-900">{model.name}</div>
                        {model.disabled && (
                          <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                            Coming Soon
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">{model.description}</div>
                      <div className="flex items-center space-x-3 mt-2">
                        <div className="flex items-center space-x-1">
                          <span className="text-xs text-gray-500">Performance:</span>
                          <span className="text-xs font-medium text-gray-700">{model.performance}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <span className="text-xs text-gray-500">Capabilities:</span>
                          <div className="flex space-x-1">
                            {model.capabilities.map((cap, idx) => (
                              <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                                {cap}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <div className={`text-sm font-medium px-2 py-1 rounded ${
                        model.cost === 'Very Low' ? 'bg-green-100 text-green-700' :
                        model.cost === 'Low' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {model.cost}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">Cost</div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Temperature Control */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Temperature: {selectedProvider.temperature || 0.7}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={selectedProvider.temperature || 0.7}
              onChange={(e) => onProviderChange({
                ...selectedProvider,
                temperature: parseFloat(e.target.value)
              })}
              disabled={disabled}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:cursor-not-allowed"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>More Focused</span>
              <span>More Creative</span>
            </div>
          </div>
        </div>
      )}

      {/* Model Family Comparison Toggle */}
      {showComparison && (
        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900">Compare AI Families</div>
              <div className="text-xs text-gray-600">Run analysis with Claude vs Nova vs Llama</div>
            </div>
            <button
              onClick={() => handleToggleComparison(!comparisonEnabled)}
              disabled={disabled}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                comparisonEnabled ? 'bg-blue-600' : 'bg-gray-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  comparisonEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          {comparisonEnabled && (
            <div className="mt-3 p-3 bg-blue-50 rounded-lg">
              <div className="text-xs text-blue-800 font-medium mb-2">Comparison will include:</div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                  <span>Claude 3.5 Sonnet</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                  <span>Nova Micro</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>Llama 3.1 8B</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ModelProviderSelector;