import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';

interface InterestData {
  category: string;
  percentage: number;
  goalPotential: 'High' | 'Medium' | 'Low';
}

interface InterestChartProps {
  data: InterestData[];
}

const COLORS = {
  'High': '#10b981',    // green-500
  'Medium': '#f59e0b',  // amber-500
  'Low': '#6b7280'      // gray-500
};

const InterestChart: React.FC<InterestChartProps> = ({ data }) => {
  const pieData = data.map(item => ({
    name: item.category.replace(' & ', ' &\n'),
    value: item.percentage,
    potential: item.goalPotential,
    fullName: item.category
  }));

  const barData = data.map(item => ({
    name: item.category.split(' ').slice(0, 2).join(' '),
    percentage: item.percentage,
    potential: item.goalPotential
  }));

  const renderCustomTooltip = (props: any) => {
    if (props.active && props.payload && props.payload.length) {
      const data = props.payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{data.fullName}</p>
          <p className="text-sm text-gray-600">{data.value}% of content</p>
          <p className="text-xs text-gray-500">
            <span className={`inline-block w-2 h-2 rounded-full mr-1 ${
              data.potential === 'High' ? 'bg-green-500' : 
              data.potential === 'Medium' ? 'bg-amber-500' : 'bg-gray-500'
            }`}></span>
            {data.potential} Goal Potential
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-8">
      {/* Pie Chart */}
      <div className="grid lg:grid-cols-2 gap-8">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Interest Distribution</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ value }) => `${value}%`}
                  labelLine={false}
                >
                  {pieData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[entry.potential]} 
                    />
                  ))}
                </Pie>
                <Tooltip content={renderCustomTooltip} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Goal Potential Analysis</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={11}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value: any) => [`${value}%`, 'Interest Level']}
                  labelFormatter={(label) => data.find(d => d.category.startsWith(label))?.category || label}
                />
                <Bar 
                  dataKey="percentage" 
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                >
                  {barData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.potential]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Legend and Analysis */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg">
          <div className="w-4 h-4 bg-green-500 rounded-full"></div>
          <div>
            <p className="font-medium text-green-900">High Potential</p>
            <p className="text-sm text-green-700">Ready for immediate goal setting</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-4 bg-amber-50 rounded-lg">
          <div className="w-4 h-4 bg-amber-500 rounded-full"></div>
          <div>
            <p className="font-medium text-amber-900">Medium Potential</p>
            <p className="text-sm text-amber-700">Explore and develop further</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
          <div className="w-4 h-4 bg-gray-500 rounded-full"></div>
          <div>
            <p className="font-medium text-gray-900">Low Potential</p>
            <p className="text-sm text-gray-700">Monitor for future opportunities</p>
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="bg-primary-50 rounded-lg p-6 border border-primary-200">
        <h4 className="font-semibold text-primary-900 mb-3">🎯 Key Insights</h4>
        <div className="space-y-2 text-sm text-primary-800">
          <p>
            • <strong>Fitness & Health</strong> dominates your interests at 38.2%, indicating this is your primary motivation area
          </p>
          <p>
            • <strong>Learning & Development</strong> at 20.6% suggests you actively seek skill improvement
          </p>
          <p>
            • The balanced distribution across creative and technology interests shows potential for integrated goals
          </p>
          <p>
            • Your <strong>high-potential categories (58.8%)</strong> provide multiple paths for meaningful personal development
          </p>
        </div>
      </div>
    </div>
  );
};

export default InterestChart;