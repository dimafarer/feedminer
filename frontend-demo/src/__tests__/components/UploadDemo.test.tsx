import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UploadDemo from '../../components/UploadDemo'

describe('UploadDemo', () => {
  const mockOnUploadComplete = vi.fn()
  const mockOnBack = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders upload instructions correctly', () => {
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    expect(screen.getByText('Upload Your Instagram Data Export')).toBeInTheDocument()
    expect(screen.getByText('📱 How to Export Your Instagram Data')).toBeInTheDocument()
    expect(screen.getByText(/Go to Instagram.*Settings.*Privacy and Security/)).toBeInTheDocument()
  })

  it('shows upload area with proper messaging', () => {
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    expect(screen.getByText('Drag & drop your Instagram JSON file here')).toBeInTheDocument()
    expect(screen.getByText('or click to browse')).toBeInTheDocument()
    expect(screen.getByText('Supports: .json, .zip files')).toBeInTheDocument()
  })

  it('provides sample data option', () => {
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    expect(screen.getByText('Use Sample Data for Demo')).toBeInTheDocument()
    expect(screen.getByText(/See how FeedMiner works with real analysis results.*177 Instagram saves/)).toBeInTheDocument()
  })

  it('calls onBack when back button is clicked', () => {
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    const backButton = screen.getByText('← Back')
    fireEvent.click(backButton)
    
    expect(mockOnBack).toHaveBeenCalledTimes(1)
  })

  it('advances to preview step when sample data is used', async () => {
    const user = userEvent.setup()
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    const sampleDataButton = screen.getByText('Use Sample Data for Demo')
    await user.click(sampleDataButton)
    
    await waitFor(() => {
      expect(screen.getByText('Preview Your Data')).toBeInTheDocument()
    })
  })

  it('shows preview data when in preview step', async () => {
    const user = userEvent.setup()
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    const sampleDataButton = screen.getByText('Use Sample Data for Demo')
    await user.click(sampleDataButton)
    
    await waitFor(() => {
      expect(screen.getByText('177')).toBeInTheDocument()
      expect(screen.getByText('Saved Posts')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('Interest Areas')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('Goal Opportunities')).toBeInTheDocument()
    })
  })

  it('shows analysis features in preview', async () => {
    const user = userEvent.setup()
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    const sampleDataButton = screen.getByText('Use Sample Data for Demo')
    await user.click(sampleDataButton)
    
    await waitFor(() => {
      expect(screen.getByText('🔍 Analysis Features')).toBeInTheDocument()
      expect(screen.getByText('Interest Classification')).toBeInTheDocument()
      expect(screen.getByText('Behavioral Pattern Detection')).toBeInTheDocument()
      expect(screen.getByText('Goal Recommendation')).toBeInTheDocument()
      expect(screen.getByText('Evidence-Based Insights')).toBeInTheDocument()
    })
  })

  it('starts analysis when confirmed', async () => {
    const user = userEvent.setup()
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    // Go to preview
    const sampleDataButton = screen.getByText('Use Sample Data for Demo')
    await user.click(sampleDataButton)
    
    // Start analysis
    await waitFor(() => {
      const startButton = screen.getByText('Start AI Analysis')
      return user.click(startButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText('Processing Your Data...')).toBeInTheDocument()
    })
  })

  it('shows step indicators correctly', () => {
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    // Should show step 1 as active
    const stepIndicators = screen.getAllByText(/[123]/)
    expect(stepIndicators[0]).toHaveClass('bg-primary-600')
  })

  it('allows going back to file selection from preview', async () => {
    const user = userEvent.setup()
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    // Go to preview
    const sampleDataButton = screen.getByText('Use Sample Data for Demo')
    await user.click(sampleDataButton)
    
    // Go back to upload
    await waitFor(async () => {
      const chooseFileButton = screen.getByText('Choose Different File')
      await user.click(chooseFileButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText('Upload Your Instagram Data Export')).toBeInTheDocument()
    })
  })
})