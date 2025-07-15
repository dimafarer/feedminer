import React from 'react';

interface LandingPageProps {
  onStartDemo: () => void;
  onViewDemo: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onStartDemo, onViewDemo }) => {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">FM</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">FeedMiner</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={onViewDemo}
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                View Demo
              </button>
              <button 
                onClick={onStartDemo}
                className="btn-primary"
              >
                Try Demo
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-20 text-center">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-5xl font-bold text-gray-900 mb-6">
              Transform Your 
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-accent-600"> Social Media Data </span>
              Into Personal Goals
            </h2>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              FeedMiner uses AI to analyze your saved Instagram content and discover your hidden interests, 
              motivations, and behavioral patterns to generate personalized, actionable self-help goals.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={onStartDemo}
                className="btn-primary text-lg px-8 py-4"
              >
                Upload Your Instagram Data
              </button>
              <button 
                onClick={onViewDemo}
                className="btn-secondary text-lg px-8 py-4"
              >
                See Real Analysis Results
              </button>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="py-20">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Real Analysis. Real Results. Real Goals.
            </h3>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              We successfully analyzed 177 real Instagram saves to extract specific goal recommendations. 
              Here's what makes FeedMiner different:
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">🧠</span>
              </div>
              <h4 className="text-xl font-semibold mb-4">AI-Powered Behavioral Analysis</h4>
              <p className="text-gray-600">
                Advanced pattern recognition identifies your interests, learning style, and motivation cycles 
                from your saved content behavior.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">🎯</span>
              </div>
              <h4 className="text-xl font-semibold mb-4">Evidence-Based Goal Setting</h4>
              <p className="text-gray-600">
                Each goal recommendation comes with evidence strength, specific metrics, and actionable 
                30/90/365-day implementation plans.
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">📊</span>
              </div>
              <h4 className="text-xl font-semibold mb-4">Real-World Validation</h4>
              <p className="text-gray-600">
                Tested with actual Instagram exports. Successfully identified fitness goals (38.2% interest), 
                learning objectives (20.6%), and business development opportunities.
              </p>
            </div>
          </div>
        </div>

        {/* Demo Preview */}
        <div className="py-20 bg-gradient-to-br from-gray-50 to-white rounded-2xl">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              See What We Discovered from Real Data
            </h3>
            <p className="text-lg text-gray-600">
              177 Instagram saves analyzed • 3 high-evidence goal areas identified • Specific action plans generated
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="metric-card">
              <div className="text-center">
                <div className="text-4xl font-bold text-primary-600 mb-2">38.2%</div>
                <div className="text-sm font-semibold text-gray-900 mb-2">🏋️ FITNESS GOALS</div>
                <div className="text-xs text-gray-600">12 fitness-related saves from top trainers → Specific workout routine recommendations</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="text-center">
                <div className="text-4xl font-bold text-accent-600 mb-2">20.6%</div>
                <div className="text-sm font-semibold text-gray-900 mb-2">📚 LEARNING GOALS</div>
                <div className="text-xs text-gray-600">Educational content focus → Course completion and skill development plans</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">80.8%</div>
                <div className="text-sm font-semibold text-gray-900 mb-2">🎥 VISUAL LEARNER</div>
                <div className="text-xs text-gray-600">Reels vs Posts preference → Kinesthetic learning style identified</div>
              </div>
            </div>
          </div>

          <div className="text-center mt-8">
            <button 
              onClick={onViewDemo}
              className="btn-primary"
            >
              Explore Full Analysis Results
            </button>
          </div>
        </div>

        {/* CTA Section */}
        <div className="py-20 text-center">
          <div className="max-w-3xl mx-auto">
            <h3 className="text-3xl font-bold text-gray-900 mb-6">
              Ready to Discover Your Hidden Goals?
            </h3>
            <p className="text-lg text-gray-600 mb-8">
              Upload your Instagram data export and let AI transform your digital behavior into 
              personalized self-improvement goals that actually align with your interests.
            </p>
            <button 
              onClick={onStartDemo}
              className="btn-primary text-lg px-8 py-4"
            >
              Start Your Analysis
            </button>
            <p className="text-sm text-gray-500 mt-4">
              Demo uses sample data • Your privacy is protected • Results in under 30 seconds
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">FM</span>
              </div>
              <span className="text-xl font-bold">FeedMiner</span>
            </div>
            <p className="text-gray-400 mb-4">
              AI-powered social media analysis for personal development
            </p>
            <div className="flex justify-center space-x-6 text-sm text-gray-400">
              <span>Built with React + TypeScript</span>
              <span>•</span>
              <span>Powered by AWS Serverless</span>
              <span>•</span>
              <span>Claude AI Analysis</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;