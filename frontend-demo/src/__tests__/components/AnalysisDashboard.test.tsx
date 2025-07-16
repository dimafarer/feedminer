import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import AnalysisDashboard from '../../components/AnalysisDashboard'
import { realAnalysisResults } from '../../data/analysisResults'

describe('AnalysisDashboard', () => {
  const mockOnBack = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard header with analysis info', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    expect(screen.getByText('Your Personal Analysis')).toBeInTheDocument()
    expect(screen.getByText(/Based on 177 Instagram saves.*Analyzed 2025-07-14/)).toBeInTheDocument()
    expect(screen.getByText(/27d6ca17/)).toBeInTheDocument()
  })

  it('displays all navigation tabs', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    expect(screen.getByText('📊')).toBeInTheDocument()
    expect(screen.getByText('Overview')).toBeInTheDocument()
    expect(screen.getByText('🎯')).toBeInTheDocument()
    expect(screen.getByText('Goal Recommendations')).toBeInTheDocument()
    expect(screen.getByText('🧠')).toBeInTheDocument()
    expect(screen.getByText('Behavioral Patterns')).toBeInTheDocument()
    expect(screen.getByText('💡')).toBeInTheDocument()
    expect(screen.getByText('Deep Insights')).toBeInTheDocument()
  })

  it('shows overview metrics correctly', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    expect(screen.getByText('177')).toBeInTheDocument()
    expect(screen.getByText('Posts Analyzed')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('Goal Areas Found')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument() // High evidence goals
    expect(screen.getByText('High-Evidence Goals')).toBeInTheDocument()
    expect(screen.getByText('4')).toBeInTheDocument() // Behavioral patterns
    expect(screen.getByText('Behavioral Insights')).toBeInTheDocument()
  })

  it('displays interest distribution section', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    expect(screen.getByText('Interest Distribution Analysis')).toBeInTheDocument()
    expect(screen.getByText(/fitness and health goals.*38.2%/)).toBeInTheDocument()
    expect(screen.getByText(/continuous learning.*20.6%/)).toBeInTheDocument()
  })

  it('shows top goal opportunities preview', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    expect(screen.getByText('Top Goal Opportunities')).toBeInTheDocument()
    expect(screen.getByText('View All Goals')).toBeInTheDocument()
    expect(screen.getByText('🏋️ Physical Fitness')).toBeInTheDocument()
    expect(screen.getByText('📚 Continuous Learning')).toBeInTheDocument()
  })

  it('switches to goals tab when clicking View All Goals', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    const viewAllGoalsButton = screen.getByText('View All Goals')
    fireEvent.click(viewAllGoalsButton)
    
    expect(screen.getByText('Your Personalized Goal Recommendations')).toBeInTheDocument()
    expect(screen.getByText(/Each goal is backed by evidence from your saved content/)).toBeInTheDocument()
  })

  it('switches tabs correctly', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Switch to patterns tab
    const patternsTab = screen.getByText('Behavioral Patterns')
    fireEvent.click(patternsTab)
    
    expect(screen.getByText('Behavioral Pattern Analysis')).toBeInTheDocument()
    
    // Switch to insights tab
    const insightsTab = screen.getByText('Deep Insights')
    fireEvent.click(insightsTab)
    
    expect(screen.getByText('Deep Behavioral Insights')).toBeInTheDocument()
    expect(screen.getByText('🎓 Learning Style Profile')).toBeInTheDocument()
  })

  it('shows insights tab content correctly', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Switch to insights tab
    const insightsTab = screen.getByText('Deep Insights')
    fireEvent.click(insightsTab)
    
    expect(screen.getByText('Visual/Kinesthetic Learner')).toBeInTheDocument()
    expect(screen.getByText('Quality-Focused Approach')).toBeInTheDocument()
    expect(screen.getByText('📅 Motivation Pattern Analysis')).toBeInTheDocument()
    expect(screen.getByText('🔍 Unexpected Pattern Discoveries')).toBeInTheDocument()
    expect(screen.getByText('🚀 Your Personalized Action Plan')).toBeInTheDocument()
  })

  it('calls onBack when back button is clicked', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    const backButton = screen.getByText('← Back to Demo')
    fireEvent.click(backButton)
    
    expect(mockOnBack).toHaveBeenCalledTimes(1)
  })

  it('displays evidence-based recommendations in insights', () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Switch to insights tab
    const insightsTab = screen.getByText('Deep Insights')
    fireEvent.click(insightsTab)
    
    expect(screen.getByText(/80.8% of your saves are Reels/)).toBeInTheDocument()
    expect(screen.getByText(/Choose courses with video content/)).toBeInTheDocument()
    expect(screen.getByText(/Your discerning taste means you're likely to commit/)).toBeInTheDocument()
  })
})