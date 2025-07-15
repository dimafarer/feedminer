import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import LandingPage from '../../components/LandingPage'
import UploadDemo from '../../components/UploadDemo'
import AnalysisDashboard from '../../components/AnalysisDashboard'
import { realAnalysisResults } from '../../data/analysisResults'

describe('Accessibility Tests', () => {
  const mockFn = () => {}

  describe('LandingPage', () => {
    it('has proper heading hierarchy', () => {
      render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Should have h1 as main heading
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
      
      // Should have h2 as secondary headings
      const h2Elements = screen.getAllByRole('heading', { level: 2 })
      expect(h2Elements.length).toBeGreaterThan(0)
    })

    it('has accessible buttons with proper labels', () => {
      render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        expect(button).toHaveAccessibleName()
      })
    })

    it('uses semantic HTML elements', () => {
      render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      expect(screen.getByRole('banner')).toBeInTheDocument() // header
      expect(screen.getByRole('main')).toBeInTheDocument() // main
      expect(screen.getByRole('contentinfo')).toBeInTheDocument() // footer
    })

    it('has proper link accessibility', () => {
      render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      const links = screen.getAllByRole('link')
      links.forEach(link => {
        expect(link).toHaveAccessibleName()
      })
    })
  })

  describe('UploadDemo', () => {
    it('has accessible form elements', () => {
      render(<UploadDemo onUploadComplete={mockFn} onBack={mockFn} />)
      
      // File input should be accessible
      const fileInput = screen.getByRole('button', { name: /drag.*drop.*click to browse/i })
      expect(fileInput).toBeInTheDocument()
    })

    it('provides clear instructions and feedback', () => {
      render(<UploadDemo onUploadComplete={mockFn} onBack={mockFn} />)
      
      expect(screen.getByText(/Upload Your Instagram Data Export/)).toBeInTheDocument()
      expect(screen.getByText(/How to Export Your Instagram Data/)).toBeInTheDocument()
    })

    it('has proper button labeling', () => {
      render(<UploadDemo onUploadComplete={mockFn} onBack={mockFn} />)
      
      const backButton = screen.getByRole('button', { name: /back/i })
      expect(backButton).toBeInTheDocument()
      
      const sampleButton = screen.getByRole('button', { name: /use sample data/i })
      expect(sampleButton).toBeInTheDocument()
    })
  })

  describe('AnalysisDashboard', () => {
    it('has accessible navigation tabs', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      const tabs = screen.getAllByRole('button')
      const tabButtons = tabs.filter(button => 
        button.textContent?.includes('Overview') ||
        button.textContent?.includes('Goal Recommendations') ||
        button.textContent?.includes('Behavioral Patterns') ||
        button.textContent?.includes('Deep Insights')
      )
      
      expect(tabButtons.length).toBeGreaterThan(0)
      tabButtons.forEach(tab => {
        expect(tab).toHaveAccessibleName()
      })
    })

    it('has proper heading structure in dashboard', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      // Should have clear heading hierarchy
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
      
      const h2Elements = screen.getAllByRole('heading', { level: 2 })
      expect(h2Elements.length).toBeGreaterThan(0)
    })

    it('provides descriptive text for metrics', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      // Metrics should have descriptive labels
      expect(screen.getByText('Posts Analyzed')).toBeInTheDocument()
      expect(screen.getByText('Goal Areas Found')).toBeInTheDocument()
      expect(screen.getByText('High-Evidence Goals')).toBeInTheDocument()
    })
  })

  describe('Keyboard Navigation', () => {
    it('landing page elements are focusable', () => {
      render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      const interactiveElements = [
        ...screen.getAllByRole('button'),
        ...screen.getAllByRole('link')
      ]
      
      interactiveElements.forEach(element => {
        expect(element).not.toHaveAttribute('tabindex', '-1')
      })
    })

    it('dashboard tabs are keyboard accessible', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      const tabButtons = screen.getAllByRole('button').filter(button => 
        button.textContent?.includes('Overview') ||
        button.textContent?.includes('Goal Recommendations') ||
        button.textContent?.includes('Behavioral Patterns') ||
        button.textContent?.includes('Deep Insights')
      )
      
      tabButtons.forEach(tab => {
        expect(tab).not.toHaveAttribute('tabindex', '-1')
      })
    })
  })

  describe('Color and Contrast', () => {
    it('uses semantic color classes for different states', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      // Check for evidence level indicators with proper styling
      const highEvidenceElements = screen.getAllByText(/HIGH EVIDENCE/)
      expect(highEvidenceElements.length).toBeGreaterThan(0)
    })

    it('provides non-color indicators for important information', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      // Evidence levels should have text labels, not just colors
      expect(screen.getByText(/HIGH EVIDENCE/)).toBeInTheDocument()
      
      // Success probability should have percentage text
      expect(screen.getByText(/Success Probability/)).toBeInTheDocument()
    })
  })

  describe('Responsive Design', () => {
    it('uses responsive CSS classes', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check for responsive classes (Tailwind)
      const responsiveElements = container.querySelectorAll('[class*="sm:"], [class*="md:"], [class*="lg:"]')
      expect(responsiveElements.length).toBeGreaterThan(0)
    })

    it('has mobile-friendly navigation', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      // Back button should be easily accessible
      const backButton = screen.getByText(/Back to Demo/)
      expect(backButton).toBeInTheDocument()
    })

    it('has proper viewport meta configuration', () => {
      // This would be set in index.html, but we can test component flexibility
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check that main content uses flexible layout classes
      const mainContent = container.querySelector('main')
      expect(mainContent).toHaveClass('px-4', 'sm:px-6', 'lg:px-8')
    })

    it('uses appropriate text sizes for different screen sizes', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check for responsive text sizing
      const headings = container.querySelectorAll('h1, h2, h3')
      const hasResponsiveText = Array.from(headings).some(el => 
        el.className.includes('text-') && (
          el.className.includes('sm:') || 
          el.className.includes('md:') || 
          el.className.includes('lg:')
        )
      )
      expect(hasResponsiveText).toBe(true)
    })
  })

  describe('Content Structure', () => {
    it('has meaningful page titles and descriptions', () => {
      render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      expect(screen.getByText(/Transform Your.*Social Media Data.*Into Personal Goals/)).toBeInTheDocument()
      expect(screen.getByText(/FeedMiner uses AI to analyze/)).toBeInTheDocument()
    })

    it('provides clear instructions and feedback', () => {
      render(<UploadDemo onUploadComplete={mockFn} onBack={mockFn} />)
      
      expect(screen.getByText(/How to Export Your Instagram Data/)).toBeInTheDocument()
      expect(screen.getByText(/Supports: .json, .zip files/)).toBeInTheDocument()
    })

    it('displays data with context and explanations', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      expect(screen.getByText(/Based on 177 Instagram saves/)).toBeInTheDocument()
      expect(screen.getByText(/Evidence from Your Data/)).toBeInTheDocument()
    })
  })
})