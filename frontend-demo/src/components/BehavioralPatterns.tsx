import React from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, PieChart, Pie, Cell } from 'recharts';
import type { BehavioralPattern } from '../data/analysisResults';

interface BehavioralPatternsProps {
  patterns: BehavioralPattern[];
}

const BehavioralPatterns: React.FC<BehavioralPatternsProps> = ({ patterns }) => {
  // Mock temporal data for visualization
  const temporalData = [
    { month: 'Oct 2023', saves: 25, motivation: 'High' },
    { month: 'Nov 2023', saves: 32, motivation: 'High' },
    { month: 'Dec 2023', saves: 28, motivation: 'High' },
    { month: 'Jan 2024', saves: 35, motivation: 'Peak' },
    { month: 'Feb 2024', saves: 18, motivation: 'Medium' },
    { month: 'Mar 2024', saves: 15, motivation: 'Medium' },
    { month: 'Apr 2024', saves: 8, motivation: 'Low' },
    { month: 'May 2024', saves: 6, motivation: 'Low' },
    { month: 'Jun 2024', saves: 4, motivation: 'Low' },
    { month: 'Jul 2024', saves: 2, motivation: 'Low' }
  ];

  const contentPreferenceData = [
    { name: 'Reels', value: 80.8, color: '#3b82f6' },
    { name: 'Posts', value: 19.2, color: '#8b5cf6' }
  ];

  const learningStylePattern = patterns.find(p => p.type === 'learning_style');
  const contentPreferencePattern = patterns.find(p => p.type === 'content_preference');
  const temporalPattern = patterns.find(p => p.type === 'temporal');
  const qualityPattern = patterns.find(p => p.type === 'quality_focus');

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Behavioral Pattern Analysis</h2>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Understanding your digital behavior patterns to optimize goal-setting strategies and 
          predict success probability for different types of personal development activities.
        </p>
      </div>

      {/* Content Preference Analysis */}
      {contentPreferencePattern && (
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">🎥 Content Consumption Patterns</h3>
          <div className="grid lg:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-4">Reels vs Posts Preference</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={contentPreferenceData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {contentPreferenceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: any) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h5 className="font-medium text-blue-900 mb-2">Visual Learning Preference</h5>
                <p className="text-blue-800 text-sm">
                  {contentPreferencePattern.insight}
                </p>
              </div>
              <div className="space-y-3">
                <h5 className="font-medium text-gray-900">Optimization Strategies:</h5>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-blue-600 rounded-full"></span>
                    <span>Choose video-based courses and tutorials</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-blue-600 rounded-full"></span>
                    <span>Prefer hands-on, demonstration-style learning</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-blue-600 rounded-full"></span>
                    <span>Use visual progress tracking methods</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Temporal Pattern Analysis */}
      {temporalPattern && (
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">📅 Motivation Cycle Analysis</h3>
          <div className="grid lg:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-4">Saving Activity Over Time</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={temporalData}>
                    <XAxis 
                      dataKey="month" 
                      angle={-45}
                      textAnchor="end"
                      height={60}
                      fontSize={10}
                    />
                    <YAxis />
                    <Tooltip 
                      formatter={(value: any) => [value, 'Saves']}
                      labelFormatter={(label) => `Month: ${label}`}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="saves" 
                      stroke="#3b82f6" 
                      strokeWidth={3}
                      dot={{ fill: '#3b82f6', strokeWidth: 2, r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-orange-50 p-4 rounded-lg">
                <h5 className="font-medium text-orange-900 mb-2">Seasonal Motivation Pattern</h5>
                <p className="text-orange-800 text-sm">
                  {temporalPattern.insight}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-green-100 p-3 rounded-lg text-center">
                  <div className="text-lg font-bold text-green-800">Peak Periods</div>
                  <div className="text-sm text-green-700">Oct-Dec, Jan</div>
                </div>
                <div className="bg-red-100 p-3 rounded-lg text-center">
                  <div className="text-lg font-bold text-red-800">Low Activity</div>
                  <div className="text-sm text-red-700">Apr-Jul</div>
                </div>
              </div>
              <div className="bg-yellow-50 p-3 rounded-lg">
                <p className="text-yellow-800 text-sm font-medium">
                  💡 Recommendation: Schedule goal launches during Oct-Jan for maximum success probability
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quality Focus Pattern */}
      {qualityPattern && (
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">⭐ Content Curation Quality</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="metric-card">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 mb-2">0.4</div>
                <div className="text-sm font-medium text-gray-900">Saves per Week</div>
                <div className="text-xs text-gray-600 mt-1">Highly selective</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 mb-2">High</div>
                <div className="text-sm font-medium text-gray-900">Quality Score</div>
                <div className="text-xs text-gray-600 mt-1">Curated content</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 mb-2">85%</div>
                <div className="text-sm font-medium text-gray-900">Goal Commitment</div>
                <div className="text-xs text-gray-600 mt-1">Predicted success</div>
              </div>
            </div>
          </div>
          <div className="mt-4 bg-green-50 p-4 rounded-lg">
            <p className="text-green-800 text-sm">
              <strong>Quality-Focused Approach:</strong> {qualityPattern.insight}
            </p>
          </div>
        </div>
      )}

      {/* Multi-Modal Learning Pattern */}
      {learningStylePattern && (
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">🧠 Learning Style Analysis</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-4">Interest Domain Distribution</h4>
              <div className="space-y-3">
                {learningStylePattern.data.domains.map((domain: string, index: number) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                      <span className="text-white text-xs font-medium">{index + 1}</span>
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900 capitalize">{domain}</div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div 
                          className="bg-gradient-to-r from-primary-500 to-accent-500 h-2 rounded-full"
                          style={{ width: `${Math.random() * 40 + 60}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-purple-50 p-4 rounded-lg">
                <h5 className="font-medium text-purple-900 mb-2">Multi-Modal Learning Style</h5>
                <p className="text-purple-800 text-sm">
                  {learningStylePattern.insight}
                </p>
              </div>
              <div>
                <h5 className="font-medium text-gray-900 mb-2">Recommended Goal Strategies:</h5>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-purple-600 rounded-full"></span>
                    <span>Combine physical and intellectual goals</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-purple-600 rounded-full"></span>
                    <span>Include creative outlets as rewards</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-purple-600 rounded-full"></span>
                    <span>Use technology tools for integration</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success Prediction Model */}
      <div className="card bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
        <h3 className="text-xl font-semibold mb-4">🎯 Goal Success Prediction Model</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-4">Success Factors Analysis</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Content Engagement Quality</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '90%' }}></div>
                  </div>
                  <span className="text-sm font-medium">90%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Interest Consistency</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                  <span className="text-sm font-medium">85%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Learning Style Match</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '95%' }}></div>
                  </div>
                  <span className="text-sm font-medium">95%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Motivation Timing</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                  </div>
                  <span className="text-sm font-medium">60%</span>
                </div>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="text-center p-6 bg-white rounded-lg border-2 border-green-200">
              <div className="text-4xl font-bold text-green-600 mb-2">82%</div>
              <div className="text-lg font-semibold text-gray-900">Overall Success Probability</div>
              <div className="text-sm text-gray-600 mt-2">For recommended goals during optimal timing</div>
            </div>
            <div className="bg-green-100 p-4 rounded-lg">
              <h5 className="font-medium text-green-900 mb-2">Key Success Drivers</h5>
              <ul className="text-sm text-green-800 space-y-1">
                <li>• High-quality content curation indicates commitment</li>
                <li>• Visual learning preference aligns with available resources</li>
                <li>• Multi-domain interests enable integrated goal approaches</li>
                <li>• Seasonal patterns suggest optimal launch timing</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BehavioralPatterns;