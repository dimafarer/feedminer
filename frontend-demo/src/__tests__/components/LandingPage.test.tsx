import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import LandingPage from '../../components/LandingPage'

describe('LandingPage', () => {
  const mockOnStartDemo = vi.fn()
  const mockOnViewDemo = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the main heading correctly', () => {
    render(<LandingPage onStartDemo={mockOnStartDemo} onViewDemo={mockOnViewDemo} />)
    
    expect(screen.getByText('Transform Your')).toBeInTheDocument()
    expect(screen.getByText('Social Media Data')).toBeInTheDocument()
    expect(screen.getByText('Into Personal Goals')).toBeInTheDocument()
  })

  it('displays real analysis metrics', () => {
    render(<LandingPage onStartDemo={mockOnStartDemo} onViewDemo={mockOnViewDemo} />)
    
    expect(screen.getByText('38.2%')).toBeInTheDocument()
    expect(screen.getByText('🏋️ FITNESS GOALS')).toBeInTheDocument()
    expect(screen.getByText('20.6%')).toBeInTheDocument()
    expect(screen.getByText('📚 LEARNING GOALS')).toBeInTheDocument()
    expect(screen.getByText('80.8%')).toBeInTheDocument()
    expect(screen.getByText('🎥 VISUAL LEARNER')).toBeInTheDocument()
  })

  it('calls onStartDemo when Try Demo button is clicked', () => {
    render(<LandingPage onStartDemo={mockOnStartDemo} onViewDemo={mockOnViewDemo} />)
    
    const tryDemoButtons = screen.getAllByText(/Try Demo|Upload Your Instagram Data|Start Your Analysis/)
    fireEvent.click(tryDemoButtons[0])
    
    expect(mockOnStartDemo).toHaveBeenCalledTimes(1)
  })

  it('calls onViewDemo when View Demo button is clicked', () => {
    render(<LandingPage onStartDemo={mockOnStartDemo} onViewDemo={mockOnViewDemo} />)
    
    const viewDemoButtons = screen.getAllByText(/View Demo|See Real Analysis Results|Explore Full Analysis Results/)
    fireEvent.click(viewDemoButtons[0])
    
    expect(mockOnViewDemo).toHaveBeenCalledTimes(1)
  })

  it('displays feature cards correctly', () => {
    render(<LandingPage onStartDemo={mockOnStartDemo} onViewDemo={mockOnViewDemo} />)
    
    expect(screen.getByText('AI-Powered Behavioral Analysis')).toBeInTheDocument()
    expect(screen.getByText('Evidence-Based Goal Setting')).toBeInTheDocument()
    expect(screen.getByText('Real-World Validation')).toBeInTheDocument()
  })

  it('has proper navigation structure', () => {
    render(<LandingPage onStartDemo={mockOnStartDemo} onViewDemo={mockOnViewDemo} />)
    
    expect(screen.getByText('FeedMiner')).toBeInTheDocument()
    expect(screen.getByText('AI-powered social media analysis for personal development')).toBeInTheDocument()
  })

  it('displays real analysis validation text', () => {
    render(<LandingPage onStartDemo={mockOnStartDemo} onViewDemo={mockOnViewDemo} />)
    
    expect(screen.getByText(/Successfully identified fitness goals.*38.2% interest/)).toBeInTheDocument()
    expect(screen.getByText(/177 Instagram saves analyzed/)).toBeInTheDocument()
  })
})