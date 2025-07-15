import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../../App'

// Mock the API to avoid actual network calls in tests
vi.mock('../../services/feedminerApi', () => ({
  useFeedMinerAPI: () => ({
    uploadContent: vi.fn().mockResolvedValue({
      contentId: 'test-123',
      message: 'Upload successful',
      s3Key: 'test-key',
      status: 'uploaded',
      type: 'instagram_saved'
    }),
    listContent: vi.fn().mockResolvedValue({
      items: [],
      count: 0,
      hasMore: false
    }),
    getContent: vi.fn().mockResolvedValue({
      contentId: 'test-123',
      type: 'instagram_saved',
      status: 'analyzed'
    }),
    createWebSocketConnection: vi.fn().mockReturnValue({
      readyState: 1,
      send: vi.fn(),
      close: vi.fn()
    }),
    sendWebSocketMessage: vi.fn()
  }),
  demoMode: {
    enabled: true,
    simulateUpload: vi.fn().mockResolvedValue({
      contentId: 'demo-123',
      message: 'Demo upload',
      s3Key: 'demo-key',
      status: 'uploaded',
      type: 'instagram_saved'
    }),
    simulateProcessing: vi.fn().mockImplementation((onUpdate) => {
      return new Promise((resolve) => {
        setTimeout(() => {
          onUpdate(1.0, 'Complete')
          resolve(undefined)
        }, 100)
      })
    })
  }
}))

describe('App Integration Tests', () => {
  it('renders landing page by default', () => {
    render(<App />)
    
    expect(screen.getByText('Transform Your')).toBeInTheDocument()
    expect(screen.getByText('Social Media Data')).toBeInTheDocument()
    expect(screen.getByText('Into Personal Goals')).toBeInTheDocument()
  })

  it('navigates to upload demo when Try Demo is clicked', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    const tryDemoButton = screen.getAllByText(/Try Demo|Upload Your Instagram Data/)[0]
    await user.click(tryDemoButton)
    
    await waitFor(() => {
      expect(screen.getByText('Upload Your Instagram Data Export')).toBeInTheDocument()
    })
  })

  it('navigates directly to results when View Demo is clicked', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    const viewDemoButton = screen.getAllByText(/View Demo|See Real Analysis Results/)[0]
    await user.click(viewDemoButton)
    
    await waitFor(() => {
      expect(screen.getByText('Your Personal Analysis')).toBeInTheDocument()
    })
  })

  it('completes full upload flow to results', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    // Start demo
    const tryDemoButton = screen.getAllByText(/Try Demo/)[0]
    await user.click(tryDemoButton)
    
    // Use sample data
    await waitFor(() => {
      const sampleDataButton = screen.getByText('Use Sample Data for Demo')
      return user.click(sampleDataButton)
    })
    
    // Start analysis
    await waitFor(() => {
      const startButton = screen.getByText('Start AI Analysis')
      return user.click(startButton)
    })
    
    // Should show processing
    await waitFor(() => {
      expect(screen.getByText('Analyzing Your Content')).toBeInTheDocument()
    })
    
    // Should eventually show results
    await waitFor(() => {
      expect(screen.getByText('Your Personal Analysis')).toBeInTheDocument()
    }, { timeout: 5000 })
  })

  it('allows navigation back to landing from any view', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    // Go to upload
    const tryDemoButton = screen.getAllByText(/Try Demo/)[0]
    await user.click(tryDemoButton)
    
    // Go back to landing
    await waitFor(() => {
      const backButton = screen.getByText('← Back')
      return user.click(backButton)
    })
    
    await waitFor(() => {
      expect(screen.getByText('Transform Your')).toBeInTheDocument()
    })
  })

  it('shows processing animation during upload simulation', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    // Navigate through upload flow
    const tryDemoButton = screen.getAllByText(/Try Demo/)[0]
    await user.click(tryDemoButton)
    
    await waitFor(async () => {
      const sampleDataButton = screen.getByText('Use Sample Data for Demo')
      await user.click(sampleDataButton)
    })
    
    await waitFor(async () => {
      const startButton = screen.getByText('Start AI Analysis')
      await user.click(startButton)
    })
    
    // Check for processing elements
    await waitFor(() => {
      expect(screen.getByText('Analyzing Your Content')).toBeInTheDocument()
      expect(screen.getByText(/AI is discovering your behavioral patterns/)).toBeInTheDocument()
    })
  })

  it('maintains proper navigation state throughout flow', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    // Start from landing
    expect(screen.getByText('FeedMiner')).toBeInTheDocument()
    
    // Go to results directly
    const viewDemoButton = screen.getAllByText(/View Demo|See Real Analysis Results/)[0]
    await user.click(viewDemoButton)
    
    // Should be in results
    await waitFor(() => {
      expect(screen.getByText('Your Personal Analysis')).toBeInTheDocument()
    })
    
    // Go back to landing
    const backButton = screen.getByText('← Back to Demo')
    await user.click(backButton)
    
    // Should be back at landing
    await waitFor(() => {
      expect(screen.getByText('Transform Your')).toBeInTheDocument()
    })
  })

  it('displays real analysis data in results view', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    // Navigate to results
    const viewDemoButton = screen.getAllByText(/View Demo|See Real Analysis Results/)[0]
    await user.click(viewDemoButton)
    
    await waitFor(() => {
      // Check for real analysis metrics
      expect(screen.getByText('177')).toBeInTheDocument()
      expect(screen.getByText('Posts Analyzed')).toBeInTheDocument()
      expect(screen.getByText('🏋️ Physical Fitness')).toBeInTheDocument()
      expect(screen.getByText('📚 Continuous Learning')).toBeInTheDocument()
      expect(screen.getByText(/27d6ca17/)).toBeInTheDocument() // Content ID
    })
  })

  it('handles tab navigation in analysis dashboard', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    // Navigate to results
    const viewDemoButton = screen.getAllByText(/View Demo|See Real Analysis Results/)[0]
    await user.click(viewDemoButton)
    
    await waitFor(async () => {
      // Should start on Overview tab
      expect(screen.getByText('Interest Distribution Analysis')).toBeInTheDocument()
      
      // Switch to Goals tab
      const goalsTab = screen.getByText('Goal Recommendations')
      await user.click(goalsTab)
    })
    
    await waitFor(() => {
      expect(screen.getByText('Your Personalized Goal Recommendations')).toBeInTheDocument()
    })
  })
})