import React, { useState } from 'react';
import type { GoalArea } from '../data/analysisResults';

interface GoalCardProps {
  goal: GoalArea;
}

const GoalCard: React.FC<GoalCardProps> = ({ goal }) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState<'30-day' | '90-day' | '1-year'>('30-day');

  const selectedGoal = goal.goals.find(g => g.term === selectedTimeframe);

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <span className="text-2xl">{goal.icon}</span>
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">{goal.name}</h3>
            <div className="flex items-center space-x-2 mt-1">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                goal.evidence === 'HIGH' 
                  ? 'bg-green-100 text-green-800' 
                  : goal.evidence === 'MEDIUM'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {goal.evidence} EVIDENCE
              </span>
              <span className="text-sm text-gray-500">
                {goal.percentage}% interest
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-600 mb-4">{goal.description}</p>

      {/* Evidence */}
      <div className="bg-gray-50 rounded-lg p-4 mb-4">
        <h4 className="font-medium text-gray-900 mb-2">📊 Evidence from Your Data</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Content saves:</span>
            <span className="font-medium text-gray-900">{goal.saveCount} posts</span>
          </div>
          <div>
            <span className="text-gray-600">Key accounts:</span>
            <div className="mt-1 flex flex-wrap gap-1">
              {goal.keyAccounts.map((account, index) => (
                <span 
                  key={index}
                  className="bg-white px-2 py-1 rounded text-xs text-gray-700 border"
                >
                  @{account}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Timeframe Selector */}
      <div className="mb-4">
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {(['30-day', '90-day', '1-year'] as const).map((timeframe) => (
            <button
              key={timeframe}
              onClick={() => setSelectedTimeframe(timeframe)}
              className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                selectedTimeframe === timeframe
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {timeframe}
            </button>
          ))}
        </div>
      </div>

      {/* Selected Goal */}
      {selectedGoal && (
        <div className="bg-primary-50 rounded-lg p-4">
          <h4 className="font-semibold text-primary-900 mb-2">
            🎯 {selectedTimeframe} Goal: {selectedGoal.title}
          </h4>
          <p className="text-primary-800 text-sm mb-3">
            {selectedGoal.description}
          </p>
          
          {/* Action Steps based on timeframe */}
          <div className="space-y-2">
            <h5 className="text-sm font-medium text-primary-900">Action Steps:</h5>
            <div className="space-y-1 text-xs text-primary-700">
              {selectedTimeframe === '30-day' && goal.id === 'fitness' && (
                <>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Week 1-2: Follow @rishfits routine 3x/week</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Week 3-4: Add @tryspartan_us challenges</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Track progress weekly with measurements</span>
                  </div>
                </>
              )}
              
              {selectedTimeframe === '30-day' && goal.id === 'learning' && (
                <>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Choose one @brilliantorg course to complete</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Practice @jd_dance_tutorial moves 15min daily</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Document learning progress weekly</span>
                  </div>
                </>
              )}
              
              {selectedTimeframe === '90-day' && (
                <>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Establish measurement systems and tracking</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Build consistency through habit stacking</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Connect with community from saved accounts</span>
                  </div>
                </>
              )}
              
              {selectedTimeframe === '1-year' && (
                <>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Achieve expertise level in chosen domain</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Contribute back to communities you follow</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-1 h-1 bg-primary-600 rounded-full"></span>
                    <span>Integrate multiple interests into unified project</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Success Probability */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Success Probability:</span>
          <div className="flex items-center space-x-2">
            <div className="w-20 bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  goal.evidence === 'HIGH' ? 'bg-green-500' : 'bg-yellow-500'
                }`}
                style={{ 
                  width: goal.evidence === 'HIGH' ? '85%' : '65%' 
                }}
              ></div>
            </div>
            <span className="font-medium text-gray-900">
              {goal.evidence === 'HIGH' ? '85%' : '65%'}
            </span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Based on your content engagement patterns and behavioral consistency
        </p>
      </div>
    </div>
  );
};

export default GoalCard;