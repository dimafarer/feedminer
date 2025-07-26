// Real analysis results from July 14, 2025 - 177 Instagram posts
export interface GoalArea {
  id: string;
  name: string;
  icon: string;
  evidence: 'HIGH' | 'MEDIUM' | 'LOW';
  percentage: number;
  saveCount: number;
  keyAccounts: string[];
  description: string;
  goals: {
    term: '30-day' | '90-day' | '1-year';
    title: string;
    description: string;
  }[];
}

export interface BehavioralPattern {
  type: 'content_preference' | 'temporal' | 'quality_focus' | 'learning_style';
  title: string;
  description: string;
  data: any;
  insight: string;
}

export interface AnalysisResult {
  totalPosts: number;
  analysisDate: string;
  contentId: string;
  goalAreas: GoalArea[];
  behavioralPatterns: BehavioralPattern[];
  interestDistribution: {
    category: string;
    percentage: number;
    goalPotential: 'High' | 'Medium' | 'Low';
  }[];
  metadata?: {
    dataTypesAnalyzed: string[];
    analysisType: string;
    backendAnalysis: any;
  };
}

// Real data from our successful analysis
export const realAnalysisResults: AnalysisResult = {
  totalPosts: 177,
  analysisDate: '2025-07-14',
  contentId: '27d6ca17-eea8-404a-a05c-d53bdbdda10f',
  goalAreas: [
    {
      id: 'fitness',
      name: '🏋️ Physical Fitness',
      icon: '💪',
      evidence: 'HIGH',
      percentage: 38.2,
      saveCount: 12,
      keyAccounts: ['rishfits', 'fitfight_', 'joexfitness', 'tryspartan_us', 'jalalsamfit'],
      description: 'Strong evidence of fitness goals through consistent saving of workout content and trainer accounts',
      goals: [
        {
          term: '30-day',
          title: 'Establish Consistent Workout Routine',
          description: 'Start 3x/week workout schedule leveraging saved fitness content from top trainers'
        },
        {
          term: '90-day',
          title: 'Implement Progress Tracking',
          description: 'Build measurement system for strength and endurance gains using proven methods'
        },
        {
          term: '1-year',
          title: 'Fitness Community Leadership',
          description: 'Become recognized contributor in fitness communities you follow'
        }
      ]
    },
    {
      id: 'learning',
      name: '📚 Continuous Learning',
      icon: '🎓',
      evidence: 'HIGH',
      percentage: 20.6,
      saveCount: 7,
      keyAccounts: ['shuffleacademy', 'jd_dance_tutorial', 'brilliantorg'],
      description: 'Clear focus on skill development and educational content across multiple domains',
      goals: [
        {
          term: '30-day',
          title: 'Complete Online Course',
          description: 'Finish one course from saved learning accounts (Brilliant, Shuffle Academy)'
        },
        {
          term: '90-day',
          title: 'Build Skill Portfolio',
          description: 'Develop proficiency in 2-3 skills from saved educational content'
        },
        {
          term: '1-year',
          title: 'Expertise Development',
          description: 'Achieve recognized expertise in chosen learning domain'
        }
      ]
    },
    {
      id: 'business',
      name: '💼 Business & Personal Brand',
      icon: '🚀',
      evidence: 'MEDIUM',
      percentage: 5.9,
      saveCount: 2,
      keyAccounts: ['personalbrandlaunch', 'brandoperezl'],
      description: 'Emerging interest in personal branding and business development',
      goals: [
        {
          term: '30-day',
          title: 'Brand Strategy Development',
          description: 'Create personal brand strategy using saved insights and frameworks'
        },
        {
          term: '90-day',
          title: 'Professional Network Building',
          description: 'Establish connections with creators from most-saved business accounts'
        },
        {
          term: '1-year',
          title: 'Integrated Business Project',
          description: 'Launch project combining fitness + technology interests for business growth'
        }
      ]
    }
  ],
  behavioralPatterns: [
    {
      type: 'content_preference',
      title: 'Visual Learning Preference',
      description: 'Strong preference for video content over static posts',
      data: { reels: 143, posts: 34, reelsPercentage: 80.8 },
      insight: 'Kinesthetic learner who prefers visual demonstration over text-based content'
    },
    {
      type: 'quality_focus',
      title: 'Quality-Focused Curation',
      description: 'Selective approach to content saving',
      data: { savesPerWeek: 0.4, selectivityScore: 'High' },
      insight: 'Focused interests with quality over quantity approach to content consumption'
    },
    {
      type: 'temporal',
      title: 'Seasonal Motivation Cycles',
      description: 'Peak activity during specific periods',
      data: { peakPeriods: ['Oct-Dec 2023', 'Jan 2024'], recentActivity: 2 },
      insight: 'Seasonal motivation pattern with recent low engagement suggesting need for re-engagement'
    },
    {
      type: 'learning_style',
      title: 'Multi-Modal Interest Pattern',
      description: 'Diverse interests across physical, intellectual, and creative domains',
      data: { domains: ['fitness', 'technology', 'dance', 'nutrition', 'music'] },
      insight: 'Well-rounded personal development approach with potential for integrated goals'
    }
  ],
  interestDistribution: [
    { category: 'Fitness & Health Goals', percentage: 38.2, goalPotential: 'High' },
    { category: 'Learning & Skill Development', percentage: 20.6, goalPotential: 'High' },
    { category: 'Creative & Artistic Pursuits', percentage: 17.6, goalPotential: 'Medium' },
    { category: 'Technology & Innovation', percentage: 17.6, goalPotential: 'Medium' },
    { category: 'Business & Entrepreneurship', percentage: 5.9, goalPotential: 'Medium' }
  ]
};

// Sample Instagram data structure for demo upload
export const sampleInstagramData = {
  "saved_saved_media": [
    {
      "title": "rishfits",
      "string_map_data": {
        "Saved on": {
          "href": "https://www.instagram.com/reel/DDXmi2qRUUD/",
          "timestamp": 1733969519
        }
      }
    },
    {
      "title": "brilliantorg",
      "string_map_data": {
        "Saved on": {
          "href": "https://www.instagram.com/p/ABC123/",
          "timestamp": 1731234567
        }
      }
    }
  ]
};