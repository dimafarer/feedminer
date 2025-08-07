import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import AnalysisDashboard from '../../components/AnalysisDashboard'
import { realAnalysisResults } from '../../data/analysisResults'

// Mock the API hook
const mockReprocessContent = vi.fn()
const mockCreateWebSocketConnection = vi.fn()

vi.mock('../../services/feedminerApi', () => ({
  useFeedMinerAPI: () => ({
    reprocessContent: mockReprocessContent,
    createWebSocketConnection: mockCreateWebSocketConnection
  })
}))

describe('Model Switching Integration Flow', () => {
  const mockOnBack = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockReprocessContent.mockClear()
    mockCreateWebSocketConnection.mockClear()
  })

  it('displays current model badge in analysis header', async () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Should show current model information (wait for useEffect to set initial model)
    await waitFor(() => {
      expect(screen.getByText(/Claude 3.5 Sonnet/)).toBeInTheDocument()
    })
  })

  it('opens model selector when current model badge is clicked', async () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Wait for initial model to be set
    await waitFor(() => {
      expect(screen.getByText(/Claude 3.5 Sonnet/)).toBeInTheDocument()
    })
    
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model for Reanalysis')).toBeInTheDocument()
    })
  })

  it('shows only Phase 1 models in selector', async () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Wait for initial model to be set
    await waitFor(() => {
      expect(screen.getByText(/Claude 3.5 Sonnet/)).toBeInTheDocument()
    })
    
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      // Should show Claude models (Phase 1) - 3 total: header + 2 in modal  
      expect(screen.getAllByText(/Claude 3.5 Sonnet/)).toHaveLength(3)
      expect(screen.getByText(/Claude 3.5 Sonnet \(Bedrock\)/)).toBeInTheDocument()
      
      // Should NOT show Phase 2+ models in the modal
      expect(screen.queryByText(/Nova/)).not.toBeInTheDocument()
      expect(screen.queryByText(/Llama/)).not.toBeInTheDocument()
    })
  })

  it('initiates reprocessing when different model is selected', async () => {
    mockReprocessContent.mockResolvedValue({
      message: 'Reprocessing started successfully',
      jobId: 'test-job-123',
      estimatedCost: 0.015,
      estimatedTime: 20
    })

    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model')).toBeInTheDocument()
    })
    
    // Click on Bedrock model (different from current Anthropic API)
    const bedrockModelCards = screen.getAllByText(/AWS Bedrock/)
    expect(bedrockModelCards).toHaveLength(1)
    const bedrockModelCard = bedrockModelCards[0].closest('button') || bedrockModelCards[0].closest('[role="button"]')
    if (bedrockModelCard) {
      fireEvent.click(bedrockModelCard)
    }
    
    await waitFor(() => {
      expect(mockReprocessContent).toHaveBeenCalledWith(
        realAnalysisResults.contentId,
        expect.objectContaining({
          model_provider: 'bedrock',
          model_name: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
          force: false
        })
      )
    })
  })

  it('shows reprocessing progress overlay during processing', async () => {
    mockReprocessContent.mockResolvedValue({
      message: 'Reprocessing started successfully',
      jobId: 'test-job-456'
    })

    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Open model selector and switch models
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model')).toBeInTheDocument()
    })
    
    const bedrockModelCard = screen.getByTestId('model-card-bedrock-claude')
    fireEvent.click(bedrockModelCard)
    
    // Should show progress overlay
    await waitFor(() => {
      expect(screen.getByText('Reprocessing Analysis')).toBeInTheDocument()
      expect(screen.getByText(/Processing with/)).toBeInTheDocument()
      expect(screen.getByText(/Phase 1.*simulated progress/)).toBeInTheDocument()
    })
  })

  it('simulates progress steps during reprocessing', async () => {
    mockReprocessContent.mockResolvedValue({
      message: 'Reprocessing started successfully',
      jobId: 'test-job-789'
    })

    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Initiate reprocessing
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model')).toBeInTheDocument()
    })
    
    const bedrockModelCard = screen.getByTestId('model-card-bedrock-claude')
    fireEvent.click(bedrockModelCard)
    
    // Check initial progress step
    await waitFor(() => {
      expect(screen.getByText(/Processing with.*Bedrock/)).toBeInTheDocument()
    })
    
    // Wait for progress simulation steps
    await waitFor(() => {
      expect(screen.getByText(/Analyzing content structure/)).toBeInTheDocument()
    }, { timeout: 3000 })
    
    await waitFor(() => {
      expect(screen.getByText(/Applying AI model/)).toBeInTheDocument()
    }, { timeout: 5000 })
  })

  it('closes model selector after successful reprocessing', async () => {
    mockReprocessContent.mockResolvedValue({
      message: 'Reprocessing started successfully',
      jobId: 'test-job-complete'
    })

    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Initiate and complete reprocessing flow
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model')).toBeInTheDocument()
    })
    
    const bedrockModelCard = screen.getByTestId('model-card-bedrock-claude')
    fireEvent.click(bedrockModelCard)
    
    // Wait for completion (simulated progress finishes)
    await waitFor(() => {
      expect(screen.getByText('Complete!')).toBeInTheDocument()
    }, { timeout: 12000 })
    
    // Model selector should close
    await waitFor(() => {
      expect(screen.queryByText('Choose AI Model')).not.toBeInTheDocument()
    }, { timeout: 2000 })
  })

  it('handles reprocessing errors gracefully', async () => {
    mockReprocessContent.mockRejectedValue(new Error('API timeout'))

    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model')).toBeInTheDocument()
    })
    
    const bedrockModelCard = screen.getByTestId('model-card-bedrock-claude')
    fireEvent.click(bedrockModelCard)
    
    // Should show error state
    await waitFor(() => {
      expect(screen.getByText(/Error.*reprocessing failed/)).toBeInTheDocument()
    })
  })

  it('prevents model selection during reprocessing', async () => {
    mockReprocessContent.mockImplementation(() => {
      // Return a promise that doesn't resolve immediately
      return new Promise(resolve => {
        setTimeout(() => resolve({ message: 'Success', jobId: 'slow-job' }), 1000)
      })
    })

    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Start reprocessing
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model')).toBeInTheDocument()
    })
    
    const bedrockModelCard = screen.getByTestId('model-card-bedrock-claude')
    fireEvent.click(bedrockModelCard)
    
    // Try to open model selector again while processing
    await waitFor(() => {
      expect(screen.getByText('Reprocessing Analysis')).toBeInTheDocument()
    })
    
    // Model badge should be disabled/not clickable during processing
    const processingModelBadge = screen.queryByText(/Claude 3.5 Sonnet/)
    if (processingModelBadge) {
      fireEvent.click(processingModelBadge)
      // Should not open model selector
      expect(screen.queryAllByText('Choose AI Model')).toHaveLength(0)
    }
  })

  it('shows cost and time estimates for different models', async () => {
    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model')).toBeInTheDocument()
      
      // Should show cost estimates
      expect(screen.getAllByText(/\$0\.015/)).toHaveLength(2) // Both Claude models
      expect(screen.getAllByText(/15-25s/)).toHaveLength(2) // Time estimates
      
      // Should show capabilities
      expect(screen.getByText('High Quality')).toBeInTheDocument()
      expect(screen.getByText('Complex Reasoning')).toBeInTheDocument()
    })
  })

  it('maintains analysis view state during model switching', async () => {
    mockReprocessContent.mockResolvedValue({
      message: 'Success',
      jobId: 'maintain-state-job'
    })

    render(<AnalysisDashboard results={realAnalysisResults} onBack={mockOnBack} />)
    
    // Switch to goals tab first
    const goalsTab = screen.getByText('Goal Recommendations')
    fireEvent.click(goalsTab)
    
    await waitFor(() => {
      expect(screen.getByText('Your Personalized Goal Recommendations')).toBeInTheDocument()
    })
    
    // Now switch models
    const modelBadge = screen.getByText(/Claude 3.5 Sonnet/)
    fireEvent.click(modelBadge)
    
    await waitFor(() => {
      expect(screen.getByText('Choose AI Model')).toBeInTheDocument()
    })
    
    const bedrockModelCard = screen.getByTestId('model-card-bedrock-claude')
    fireEvent.click(bedrockModelCard)
    
    // After reprocessing completes, should still be on goals tab
    await waitFor(() => {
      expect(screen.getByText('Complete!')).toBeInTheDocument()
    }, { timeout: 12000 })
    
    await waitFor(() => {
      expect(screen.getByText('Your Personalized Goal Recommendations')).toBeInTheDocument()
    }, { timeout: 2000 })
  })
})