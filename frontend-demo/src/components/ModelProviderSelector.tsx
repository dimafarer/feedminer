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
  disabled?: boolean;
}

const AVAILABLE_MODELS: Record<'anthropic' | 'bedrock', ModelOption[]> = {
  anthropic: [
    {
      id: 'claude-3-5-sonnet-20241022',
      name: 'Claude 3.5 Sonnet',
      description: 'Most capable model for complex reasoning and analysis',
      cost: 'Standard',
    },
  ],
  bedrock: [
    {
      id: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
      name: 'Claude 3.5 Sonnet (Bedrock)',
      description: 'Same model via AWS Bedrock for enterprise deployment',
      cost: 'Lower',
    },
    // Future models can be added here
    {
      id: 'anthropic.claude-3-haiku-20240307-v1:0',
      name: 'Claude 3 Haiku (Bedrock)',
      description: 'Faster, cost-effective model for simpler tasks',
      cost: 'Lowest',
      disabled: true, // Not yet implemented
    },
  ],
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

  const handleProviderSelect = (provider: 'anthropic' | 'bedrock', modelId: string) => {
    const newProvider: ModelProvider = {
      provider,
      model: modelId,
      temperature: selectedProvider.temperature || 0.7,
    };
    onProviderChange(newProvider);
  };

  const handleToggleComparison = (enabled: boolean) => {
    setComparisonEnabled(enabled);
    onToggleComparison?.(enabled);
  };

  const selectedModel = [...AVAILABLE_MODELS.anthropic, ...AVAILABLE_MODELS.bedrock]
    .find(model => model.id === selectedProvider.model);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">AI Model Selection</h3>
          <p className="text-sm text-gray-600">Choose your preferred AI provider and model</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500">v0.2.0</span>
          <div className="w-2 h-2 bg-green-400 rounded-full" title="Multi-Model AI Active"></div>
        </div>
      </div>

      {/* Current Selection Display */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              selectedProvider.provider === 'anthropic' ? 'bg-orange-400' : 'bg-blue-400'
            }`}></div>
            <div>
              <div className="font-medium text-gray-900">
                {selectedModel?.name || selectedProvider.model}
              </div>
              <div className="text-sm text-gray-600 capitalize">
                {selectedProvider.provider} • Temperature: {selectedProvider.temperature || 0.7}
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
          
          {/* Provider Tabs */}
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            {Object.keys(AVAILABLE_MODELS).map((provider) => (
              <button
                key={provider}
                onClick={() => {
                  const models = AVAILABLE_MODELS[provider as keyof typeof AVAILABLE_MODELS];
                  const firstModel = models.find(m => !m.disabled);
                  if (firstModel) {
                    handleProviderSelect(provider as 'anthropic' | 'bedrock', firstModel.id);
                  }
                }}
                disabled={disabled}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  selectedProvider.provider === provider
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 disabled:text-gray-400'
                }`}
              >
                <div className="flex items-center justify-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    provider === 'anthropic' ? 'bg-orange-400' : 'bg-blue-400'
                  }`}></div>
                  <span className="capitalize">{provider}</span>
                  {provider === 'bedrock' && (
                    <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">AWS</span>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Model Options */}
          <div className="space-y-2">
            {AVAILABLE_MODELS[selectedProvider.provider].map((model) => (
              <button
                key={model.id}
                onClick={() => handleProviderSelect(selectedProvider.provider, model.id)}
                disabled={disabled || model.disabled}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
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
                  </div>
                  <div className="text-right">
                    <div className={`text-xs font-medium ${
                      model.cost === 'Lowest' ? 'text-green-600' :
                      model.cost === 'Lower' ? 'text-blue-600' : 'text-gray-600'
                    }`}>
                      {model.cost} Cost
                    </div>
                  </div>
                </div>
              </button>
            ))}
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

      {/* Provider Comparison Toggle */}
      {showComparison && (
        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900">Compare Providers</div>
              <div className="text-xs text-gray-600">Run analysis with both Anthropic and Bedrock</div>
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
        </div>
      )}
    </div>
  );
};

export default ModelProviderSelector;