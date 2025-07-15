import React, { useState } from 'react';
import type { AnalysisResult } from '../data/analysisResults';
import GoalCard from './GoalCard';
import BehavioralPatterns from './BehavioralPatterns';
import InterestChart from './InterestChart';

interface AnalysisDashboardProps {
  results: AnalysisResult;
  onBack: () => void;
}

const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({ results, onBack }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'goals' | 'patterns' | 'insights'>('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'goals', label: 'Goal Recommendations', icon: '🎯' },
    { id: 'patterns', label: 'Behavioral Patterns', icon: '🧠' },
    { id: 'insights', label: 'Deep Insights', icon: '💡' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <button 
                onClick={onBack}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back to Demo
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Your Personal Analysis</h1>
                <p className="text-sm text-gray-600">
                  Based on {results.totalPosts} Instagram saves • Analyzed {results.analysisDate}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">Analysis ID</div>
                <div className="text-xs text-gray-500 font-mono">{results.contentId.slice(0, 8)}...</div>
              </div>
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 text-sm">✓</span>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex space-x-8 border-b border-gray-200">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Key Metrics */}
            <div className="grid lg:grid-cols-4 md:grid-cols-2 gap-6">
              <div className="metric-card">
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary-600 mb-2">{results.totalPosts}</div>
                  <div className="text-sm font-medium text-gray-900">Posts Analyzed</div>
                  <div className="text-xs text-gray-600 mt-1">Complete dataset processed</div>
                </div>
              </div>
              
              <div className="metric-card">
                <div className="text-center">
                  <div className="text-3xl font-bold text-accent-600 mb-2">{results.goalAreas.length}</div>
                  <div className="text-sm font-medium text-gray-900">Goal Areas Found</div>
                  <div className="text-xs text-gray-600 mt-1">High-evidence opportunities</div>
                </div>
              </div>
              
              <div className="metric-card">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {results.goalAreas.filter(g => g.evidence === 'HIGH').length}
                  </div>
                  <div className="text-sm font-medium text-gray-900">High-Evidence Goals</div>
                  <div className="text-xs text-gray-600 mt-1">Ready for implementation</div>
                </div>
              </div>
              
              <div className="metric-card">
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600 mb-2">{results.behavioralPatterns.length}</div>
                  <div className="text-sm font-medium text-gray-900">Behavioral Insights</div>
                  <div className="text-xs text-gray-600 mt-1">Patterns discovered</div>
                </div>
              </div>
            </div>

            {/* Interest Distribution */}
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Interest Distribution Analysis</h2>
              <InterestChart data={results.interestDistribution} />
              <div className="mt-6">
                <p className="text-gray-600">
                  Your content reveals a strong focus on <strong>fitness and health goals</strong> (38.2% of saves), 
                  followed by continuous learning (20.6%). This pattern suggests you're actively seeking personal 
                  improvement in both physical and intellectual domains.
                </p>
              </div>
            </div>

            {/* Top Goal Areas Preview */}
            <div className="card">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Top Goal Opportunities</h2>
                <button 
                  onClick={() => setActiveTab('goals')}
                  className="btn-primary"
                >
                  View All Goals
                </button>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                {results.goalAreas.slice(0, 2).map((goal) => (
                  <div key={goal.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">{goal.name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        goal.evidence === 'HIGH' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {goal.evidence} EVIDENCE
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{goal.description}</p>
                    <div className="text-xs text-gray-500">
                      {goal.saveCount} saves • {goal.keyAccounts.slice(0, 2).join(', ')} +{goal.keyAccounts.length - 2} more
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'goals' && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Your Personalized Goal Recommendations</h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Each goal is backed by evidence from your saved content and includes specific action plans 
                for 30-day, 90-day, and 1-year timeframes.
              </p>
            </div>
            
            <div className="grid lg:grid-cols-2 gap-8">
              {results.goalAreas.map((goal) => (
                <GoalCard key={goal.id} goal={goal} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'patterns' && (
          <BehavioralPatterns patterns={results.behavioralPatterns} />
        )}

        {activeTab === 'insights' && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Deep Behavioral Insights</h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Advanced analysis of your digital behavior patterns and what they reveal about your 
                personal development journey.
              </p>
            </div>

            {/* Learning Style Analysis */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">🎓 Learning Style Profile</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Visual/Kinesthetic Learner</h4>
                  <p className="text-gray-600 text-sm mb-4">
                    80.8% of your saves are Reels vs Posts, indicating you prefer dynamic, demonstration-based 
                    learning over static text content.
                  </p>
                  <div className="bg-primary-50 p-3 rounded-lg">
                    <p className="text-primary-800 text-sm font-medium">
                      💡 Recommendation: Choose courses with video content, hands-on practice, and visual demonstrations
                    </p>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Quality-Focused Approach</h4>
                  <p className="text-gray-600 text-sm mb-4">
                    Your selective saving pattern (0.4 saves/week) suggests you curate high-quality content 
                    rather than consuming everything.
                  </p>
                  <div className="bg-green-50 p-3 rounded-lg">
                    <p className="text-green-800 text-sm font-medium">
                      💡 Strength: Your discerning taste means you're likely to commit to well-chosen goals
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Motivation Cycles */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">📅 Motivation Pattern Analysis</h3>
              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-orange-600 text-sm">📈</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Seasonal Motivation Peaks</h4>
                    <p className="text-gray-600 text-sm">
                      High activity during Oct-Dec 2023 and Jan 2024 suggests New Year resolution periods 
                      and end-of-year reflection times are your peak motivation windows.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-red-600 text-sm">⚠️</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Current Low Engagement</h4>
                    <p className="text-gray-600 text-sm">
                      Only 2 saves in the last 30 days indicates you may be in a motivation valley. 
                      This analysis could be the catalyst to re-engage with your goals.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Unexpected Discoveries */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">🔍 Unexpected Pattern Discoveries</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Multi-Modal Learning Interest</h4>
                    <p className="text-gray-600 text-sm">
                      Your saves span dance tutorials, fitness content, technology tools, and creative pursuits - 
                      suggesting you thrive on integrated, cross-domain learning experiences.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Health-Conscious Lifestyle</h4>
                    <p className="text-gray-600 text-sm">
                      Food and nutrition accounts align perfectly with fitness goals, indicating a 
                      holistic approach to health and wellness.
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Creative Expression Desire</h4>
                    <p className="text-gray-600 text-sm">
                      Music and art content suggests a need for creative outlets alongside your 
                      fitness and learning goals.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Technology Integration</h4>
                    <p className="text-gray-600 text-sm">
                      Interest in digital tools and innovation indicates you'd benefit from 
                      tech-enabled goal tracking and achievement systems.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Plan */}
            <div className="card bg-gradient-to-r from-primary-50 to-accent-50 border-primary-200">
              <h3 className="text-xl font-semibold mb-4">🚀 Your Personalized Action Plan</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <span className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">1</span>
                  <p className="text-gray-800">Start with fitness goals during your next motivation peak (likely seasonal transition)</p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">2</span>
                  <p className="text-gray-800">Choose video-based learning courses that align with your visual learning style</p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">3</span>
                  <p className="text-gray-800">Integrate creative activities as reward systems for achieving fitness/learning milestones</p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">4</span>
                  <p className="text-gray-800">Use technology tools to track progress and maintain motivation between peak periods</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AnalysisDashboard;