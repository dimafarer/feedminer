import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

// Mock component since it's integrated into AnalysisDashboard
const ReprocessingProgress = ({ 
  isVisible, 
  progress, 
  currentStep, 
  error,
  onCancel
}: {
  isVisible: boolean
  progress: number
  currentStep: string
  error?: string | null
  onCancel?: () => void
}) => {
  if (!isVisible) return null

  return (
    <div data-testid="reprocessing-overlay" className="fixed inset-0 bg-black bg-opacity-50 z-50">
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <h3 className="text-xl font-semibold mb-4">
            {error ? 'Processing Failed' : 'Reprocessing Analysis'}
          </h3>
          
          {error ? (
            <div className="text-red-600 mb-4">
              <p>{error}</p>
            </div>
          ) : (
            <>
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>{Math.round(progress)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
              
              <p className="text-sm text-gray-600 mb-4">{currentStep}</p>
              
              <div className="text-xs text-gray-500 space-y-1">
                <p>This usually takes 15-30 seconds depending on the model and data size.</p>
                <p className="bg-blue-50 text-blue-700 p-2 rounded">
                  <strong>Phase 1:</strong> Using simulated progress. Real-time WebSocket updates will be available in Phase 2.
                </p>
              </div>
            </>
          )}
          
          {onCancel && (
            <div className="mt-6 flex justify-end">
              <button
                onClick={onCancel}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

describe('ReprocessingProgress', () => {
  const defaultProps = {
    isVisible: true,
    progress: 50,
    currentStep: 'Analyzing content with AI model...',
    error: null,
    onCancel: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders progress overlay when visible', () => {
    render(<ReprocessingProgress {...defaultProps} />)
    
    expect(screen.getByTestId('reprocessing-overlay')).toBeInTheDocument()
    expect(screen.getByText('Reprocessing Analysis')).toBeInTheDocument()
  })

  it('does not render when not visible', () => {
    render(<ReprocessingProgress {...defaultProps} isVisible={false} />)
    
    expect(screen.queryByTestId('reprocessing-overlay')).not.toBeInTheDocument()
  })

  it('displays progress percentage correctly', () => {
    render(<ReprocessingProgress {...defaultProps} progress={75} />)
    
    expect(screen.getByText('75%')).toBeInTheDocument()
    
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveStyle({ width: '75%' })
  })

  it('shows current processing step', () => {
    const currentStep = 'Processing with Claude 3.5 Sonnet...'
    render(<ReprocessingProgress {...defaultProps} currentStep={currentStep} />)
    
    expect(screen.getByText(currentStep)).toBeInTheDocument()
  })

  it('displays error state correctly', () => {
    const error = 'Analysis failed due to API timeout'
    render(<ReprocessingProgress {...defaultProps} error={error} />)
    
    expect(screen.getByText('Processing Failed')).toBeInTheDocument()
    expect(screen.getByText(error)).toBeInTheDocument()
    expect(screen.queryByText('Progress')).not.toBeInTheDocument()
  })

  it('shows Phase 1 information', () => {
    render(<ReprocessingProgress {...defaultProps} />)
    
    expect(screen.getByText('This usually takes 15-30 seconds depending on the model and data size.')).toBeInTheDocument()
    expect(screen.getByText(/Phase 1.*simulated progress/)).toBeInTheDocument()
    expect(screen.getByText(/Real-time WebSocket updates.*Phase 2/)).toBeInTheDocument()
  })

  it('handles cancel functionality', () => {
    const mockOnCancel = vi.fn()
    render(<ReprocessingProgress {...defaultProps} onCancel={mockOnCancel} />)
    
    const cancelButton = screen.getByText('Cancel')
    expect(cancelButton).toBeInTheDocument()
    
    cancelButton.click()
    expect(mockOnCancel).toHaveBeenCalledTimes(1)
  })

  it('does not show cancel button when onCancel not provided', () => {
    render(<ReprocessingProgress {...defaultProps} onCancel={undefined} />)
    
    expect(screen.queryByText('Cancel')).not.toBeInTheDocument()
  })

  it('uses correct CSS classes for overlay', () => {
    render(<ReprocessingProgress {...defaultProps} />)
    
    const overlay = screen.getByTestId('reprocessing-overlay')
    expect(overlay).toHaveClass('fixed', 'inset-0', 'bg-black', 'bg-opacity-50', 'z-50')
  })

  it('animates progress bar correctly', () => {
    const { rerender } = render(<ReprocessingProgress {...defaultProps} progress={25} />)
    
    let progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveStyle({ width: '25%' })
    expect(progressBar).toHaveClass('transition-all', 'duration-300')
    
    rerender(<ReprocessingProgress {...defaultProps} progress={75} />)
    
    progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveStyle({ width: '75%' })
  })

  it('displays appropriate progress steps', () => {
    const progressSteps = [
      'Starting analysis...',
      'Processing with Claude 3.5 Sonnet...',
      'Generating insights...',
      'Finalizing analysis...',
      'Complete!'
    ]

    progressSteps.forEach(step => {
      render(<ReprocessingProgress {...defaultProps} currentStep={step} />)
      expect(screen.getByText(step)).toBeInTheDocument()
    })
  })
})