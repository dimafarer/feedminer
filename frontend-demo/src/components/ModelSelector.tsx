import React from 'react';

export interface ModelInfo {
  id: string;
  provider: 'anthropic' | 'bedrock' | 'nova' | 'llama';
  model: string;
  name: string;
  family: string;
  description: string;
  costTier: 'very_low' | 'low' | 'medium' | 'high';
  capabilities: string[];
  avgResponseTime: string;
  icon: string;
  recommended?: boolean;
  benefits: string[];
  limitations?: string[];
}

interface ModelSelectorProps {
  selectedModel: ModelInfo;
  onModelChange: (model: ModelInfo) => void;
  showDetails?: boolean;
  compact?: boolean;
  className?: string;
}

// Model configurations based on our analysis and production testing
export const AVAILABLE_MODELS: ModelInfo[] = [
  // Claude Family - Premium reasoning and multimodal
  {
    id: 'claude-sonnet',
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022',
    name: 'Claude 3.5 Sonnet',
    family: 'Anthropic Claude',
    description: 'Advanced reasoning with multimodal capabilities',
    costTier: 'high',
    capabilities: ['text', 'vision', 'reasoning'],
    avgResponseTime: '7.5s',
    icon: '🧠',
    benefits: [
      'Excellent reasoning and analysis',
      'Concise, actionable recommendations',
      'Strong goal-setting insights',
      'Professional business tone'
    ],
    limitations: ['Higher cost per analysis', 'Longer processing time']
  },
  {
    id: 'claude-bedrock',
    provider: 'bedrock',
    model: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    name: 'Claude 3.5 Sonnet (Bedrock)',
    family: 'Anthropic Claude',
    description: 'Enterprise Claude with AWS integration',
    costTier: 'high',
    capabilities: ['text', 'vision', 'reasoning'],
    avgResponseTime: '10s',
    icon: '🏢',
    benefits: [
      'Same quality as Claude API',
      'Enterprise security features',
      'AWS infrastructure reliability'
    ],
    limitations: ['Highest cost option', 'Slowest response time']
  },
  
  // Nova Family - Best cost/performance balance
  {
    id: 'nova-micro',
    provider: 'nova',
    model: 'us.amazon.nova-micro-v1:0',
    name: 'Nova Micro',
    family: 'Amazon Nova',
    description: '75% cost savings with excellent performance',
    costTier: 'very_low',
    capabilities: ['text', 'multimodal'],
    avgResponseTime: '2.8s',
    icon: '⚡',
    recommended: true,
    benefits: [
      '75% lower cost than Claude',
      'Fast 2.8s response time',
      'Detailed analysis output',
      'Great for experimentation'
    ],
    limitations: ['More verbose output', 'Academic tone']
  },
  {
    id: 'nova-lite',
    provider: 'nova',
    model: 'us.amazon.nova-lite-v1:0',
    name: 'Nova Lite',
    family: 'Amazon Nova',
    description: 'Enhanced Nova with better reasoning',
    costTier: 'very_low',
    capabilities: ['text', 'multimodal'],
    avgResponseTime: '5s',
    icon: '🔥',
    benefits: [
      'Still very cost-effective',
      'More sophisticated analysis',
      'Better structured output',
      'Good balance of detail'
    ],
    limitations: ['Slower than Nova Micro', 'Formal presentation style']
  },

  // Llama Family - Open source efficiency
  {
    id: 'llama-8b',
    provider: 'llama',
    model: 'meta.llama3-1-8b-instruct-v1:0',
    name: 'Llama 3.1 8B',
    family: 'Meta Llama',
    description: 'Fastest open-source model with competitive performance',
    costTier: 'low',
    capabilities: ['text'],
    avgResponseTime: '2.4s',
    icon: '🚀',
    benefits: [
      'Fastest response time (2.4s)',
      'Open-source efficiency',
      'Practical recommendations',
      'Good cost-performance ratio'
    ],
    limitations: ['Text-only capabilities', 'May need fallback parsing']
  },
  {
    id: 'llama-70b',
    provider: 'llama',
    model: 'meta.llama3-1-70b-instruct-v1:0',
    name: 'Llama 3.1 70B',
    family: 'Meta Llama',
    description: 'Larger Llama model with enhanced reasoning',
    costTier: 'low',
    capabilities: ['text'],
    avgResponseTime: '19s',
    icon: '🦙',
    benefits: [
      'Enhanced reasoning vs 8B',
      'Still cost-effective',
      'Well-structured analysis',
      'Open-source transparency'
    ],
    limitations: ['Much slower processing', 'Text-only capabilities']
  }
];

const ModelSelector: React.FC<ModelSelectorProps> = ({
  selectedModel,
  onModelChange,
  showDetails = true,
  compact = false,
  className = ''
}) => {
  const getCostBadge = (costTier: string) => {
    const configs = {
      very_low: { label: 'Very Low Cost', color: 'bg-green-100 text-green-800', icon: '💰' },
      low: { label: 'Low Cost', color: 'bg-blue-100 text-blue-800', icon: '💰💰' },
      medium: { label: 'Medium Cost', color: 'bg-yellow-100 text-yellow-800', icon: '💰💰💰' },
      high: { label: 'High Cost', color: 'bg-red-100 text-red-800', icon: '💰💰💰💰' }
    };
    const config = configs[costTier as keyof typeof configs] || configs.medium;
    return (
      <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        <span>{config.icon}</span>
        <span>{config.label}</span>
      </span>
    );
  };

  const getSpeedBadge = (responseTime: string) => {
    const timeInSeconds = parseFloat(responseTime);
    if (timeInSeconds < 3) {
      return <span className="text-green-600 text-xs">⚡ Very Fast</span>;
    } else if (timeInSeconds < 8) {
      return <span className="text-yellow-600 text-xs">⚡ Fast</span>;
    } else {
      return <span className="text-orange-600 text-xs">⚡ Slower</span>;
    }
  };

  if (compact) {
    return (
      <div className={`space-y-2 ${className}`}>
        <label className="block text-sm font-medium text-gray-700">
          AI Model
        </label>
        <select
          value={selectedModel.id}
          onChange={(e) => {
            const model = AVAILABLE_MODELS.find(m => m.id === e.target.value);
            if (model) onModelChange(model);
          }}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          {AVAILABLE_MODELS.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name} - {model.costTier === 'very_low' ? 'Very Low Cost' : 
                           model.costTier === 'low' ? 'Low Cost' :
                           model.costTier === 'medium' ? 'Medium Cost' : 'High Cost'} 
              ({model.avgResponseTime})
            </option>
          ))}
        </select>
      </div>
    );
  }

  // Group models by family
  const modelFamilies = AVAILABLE_MODELS.reduce((acc, model) => {
    if (!acc[model.family]) {
      acc[model.family] = [];
    }
    acc[model.family].push(model);
    return acc;
  }, {} as Record<string, ModelInfo[]>);

  return (
    <div className={`space-y-6 ${className}`}>
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Choose Your AI Model
        </h3>
        <p className="text-sm text-gray-600">
          Each AI family has different strengths. Choose based on your priorities: cost, speed, or analysis depth.
        </p>
      </div>

      <div className="space-y-4">
        {Object.entries(modelFamilies).map(([familyName, models]) => (
          <div key={familyName} className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
              <h4 className="font-medium text-gray-900">{familyName}</h4>
            </div>
            <div className="p-4 space-y-3">
              {models.map((model) => (
                <label
                  key={model.id}
                  className={`relative flex items-start space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedModel.id === model.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="model"
                    value={model.id}
                    checked={selectedModel.id === model.id}
                    onChange={() => onModelChange(model)}
                    className="mt-1 w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{model.icon}</span>
                        <h5 className="font-medium text-gray-900">{model.name}</h5>
                        {model.recommended && (
                          <span className="bg-primary-100 text-primary-800 text-xs font-medium px-2 py-1 rounded-full">
                            Recommended
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        {getCostBadge(model.costTier)}
                        {getSpeedBadge(model.avgResponseTime)}
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">{model.description}</p>
                    
                    {showDetails && (
                      <div className="space-y-2">
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>Response Time: {model.avgResponseTime}</span>
                          <span>•</span>
                          <span>Capabilities: {model.capabilities.join(', ')}</span>
                        </div>
                        
                        <div className="grid md:grid-cols-2 gap-3 text-xs">
                          <div>
                            <h6 className="font-medium text-green-700 mb-1">✓ Benefits:</h6>
                            <ul className="text-gray-600 space-y-1">
                              {model.benefits.slice(0, 2).map((benefit, index) => (
                                <li key={index}>• {benefit}</li>
                              ))}
                            </ul>
                          </div>
                          {model.limitations && (
                            <div>
                              <h6 className="font-medium text-orange-700 mb-1">⚠ Considerations:</h6>
                              <ul className="text-gray-600 space-y-1">
                                {model.limitations.slice(0, 2).map((limitation, index) => (
                                  <li key={index}>• {limitation}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      {showDetails && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">💡 Model Selection Tips</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• <strong>First time?</strong> Try Nova Micro for fast, cost-effective analysis</li>
            <li>• <strong>Detailed insights?</strong> Use Claude Sonnet for premium reasoning</li>
            <li>• <strong>Speed priority?</strong> Llama 8B provides fastest results</li>
            <li>• <strong>Experimenting?</strong> Nova family offers best value for testing</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;