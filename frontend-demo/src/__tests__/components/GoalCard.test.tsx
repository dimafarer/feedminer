import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import GoalCard from '../../components/GoalCard'
import { realAnalysisResults } from '../../data/analysisResults'

describe('GoalCard', () => {
  const fitnessGoal = realAnalysisResults.goalAreas[0] // Physical Fitness goal

  it('renders goal information correctly', () => {
    render(<GoalCard goal={fitnessGoal} />)
    
    expect(screen.getByText('🏋️ Physical Fitness')).toBeInTheDocument()
    expect(screen.getByText('HIGH EVIDENCE')).toBeInTheDocument()
    expect(screen.getByText('38.2% interest')).toBeInTheDocument()
    expect(screen.getByText(/Strong evidence of fitness goals through consistent saving/)).toBeInTheDocument()
  })

  it('displays evidence data correctly', () => {
    render(<GoalCard goal={fitnessGoal} />)
    
    expect(screen.getByText('📊 Evidence from Your Data')).toBeInTheDocument()
    expect(screen.getByText('Content saves:')).toBeInTheDocument()
    expect(screen.getByText('12 posts')).toBeInTheDocument()
    expect(screen.getByText('Key accounts:')).toBeInTheDocument()
    expect(screen.getByText('@rishfits')).toBeInTheDocument()
    expect(screen.getByText('@fitfight_')).toBeInTheDocument()
  })

  it('shows timeframe selector with default 30-day selection', () => {
    render(<GoalCard goal={fitnessGoal} />)
    
    expect(screen.getByText('30-day')).toBeInTheDocument()
    expect(screen.getByText('90-day')).toBeInTheDocument()
    expect(screen.getByText('1-year')).toBeInTheDocument()
    
    // 30-day should be selected by default
    const thirtyDayButton = screen.getByRole('button', { name: '30-day' })
    expect(thirtyDayButton).toHaveClass('bg-white', 'text-primary-600')
  })

  it('switches timeframes correctly', () => {
    render(<GoalCard goal={fitnessGoal} />)
    
    // Click 90-day tab
    const ninetyDayButton = screen.getByRole('button', { name: '90-day' })
    fireEvent.click(ninetyDayButton)
    
    expect(ninetyDayButton).toHaveClass('bg-white', 'text-primary-600')
    expect(screen.getByText('🎯 90-day Goal:')).toBeInTheDocument()
  })

  it('displays 30-day goal content correctly', () => {
    render(<GoalCard goal={fitnessGoal} />)
    
    expect(screen.getByText('🎯 30-day Goal: Establish Consistent Workout Routine')).toBeInTheDocument()
    expect(screen.getByText(/Start 3x\/week workout schedule leveraging saved fitness content/)).toBeInTheDocument()
    expect(screen.getByText('Action Steps:')).toBeInTheDocument()
    expect(screen.getByText(/Week 1-2: Follow @rishfits routine 3x\/week/)).toBeInTheDocument()
  })

  it('displays success probability correctly', () => {
    render(<GoalCard goal={fitnessGoal} />)
    
    expect(screen.getByText('Success Probability:')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText(/Based on your content engagement patterns/)).toBeInTheDocument()
  })

  it('shows different content for 1-year timeframe', () => {
    render(<GoalCard goal={fitnessGoal} />)
    
    // Click 1-year tab
    const oneYearButton = screen.getByRole('button', { name: '1-year' })
    fireEvent.click(oneYearButton)
    
    expect(screen.getByText('🎯 1-year Goal:')).toBeInTheDocument()
    expect(screen.getByText(/Achieve expertise level in chosen domain/)).toBeInTheDocument()
    expect(screen.getByText(/Integrate multiple interests into unified project/)).toBeInTheDocument()
  })

  it('renders learning goal with different evidence level', () => {
    const learningGoal = realAnalysisResults.goalAreas[1] // Continuous Learning goal
    render(<GoalCard goal={learningGoal} />)
    
    expect(screen.getByText('📚 Continuous Learning')).toBeInTheDocument()
    expect(screen.getByText('HIGH EVIDENCE')).toBeInTheDocument()
    expect(screen.getByText('20.6% interest')).toBeInTheDocument()
    expect(screen.getByText('@shuffleacademy')).toBeInTheDocument()
    expect(screen.getByText('@brilliantorg')).toBeInTheDocument()
  })

  it('renders business goal with medium evidence', () => {
    const businessGoal = realAnalysisResults.goalAreas[2] // Business goal
    render(<GoalCard goal={businessGoal} />)
    
    expect(screen.getByText('💼 Business & Personal Brand')).toBeInTheDocument()
    expect(screen.getByText('MEDIUM EVIDENCE')).toBeInTheDocument()
    expect(screen.getByText('5.9% interest')).toBeInTheDocument()
    expect(screen.getByText('65%')).toBeInTheDocument() // Different success probability for medium evidence
  })

  it('shows appropriate action steps for learning goals', () => {
    const learningGoal = realAnalysisResults.goalAreas[1]
    render(<GoalCard goal={learningGoal} />)
    
    expect(screen.getByText(/Choose one @brilliantorg course to complete/)).toBeInTheDocument()
    expect(screen.getByText(/Practice @jd_dance_tutorial moves 15min daily/)).toBeInTheDocument()
  })
})