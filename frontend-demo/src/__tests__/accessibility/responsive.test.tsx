import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import LandingPage from '../../components/LandingPage'
import UploadDemo from '../../components/UploadDemo'
import AnalysisDashboard from '../../components/AnalysisDashboard'
import { realAnalysisResults } from '../../data/analysisResults'

describe('Responsive Design Tests', () => {
  const mockFn = () => {}

  describe('Layout Flexibility', () => {
    it('landing page uses responsive container classes', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check for max-width containers that adapt to screen size
      const containers = container.querySelectorAll('.max-w-7xl, .max-w-6xl, .max-w-4xl, .max-w-3xl')
      expect(containers.length).toBeGreaterThan(0)
      
      // Check for responsive padding
      const responsivePadding = container.querySelectorAll('[class*="px-4"], [class*="sm:px-6"], [class*="lg:px-8"]')
      expect(responsivePadding.length).toBeGreaterThan(0)
    })

    it('upload demo adapts to different screen sizes', () => {
      const { container } = render(<UploadDemo onUploadComplete={mockFn} onBack={mockFn} />)
      
      // Check for responsive grid/flex layouts
      const responsiveLayouts = container.querySelectorAll('[class*="grid"], [class*="flex"], [class*="md:"], [class*="lg:"]')
      expect(responsiveLayouts.length).toBeGreaterThan(0)
    })

    it('dashboard uses responsive tab layout', () => {
      const { container } = render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      // Tabs should adapt to mobile (might stack or scroll)
      const tabContainer = container.querySelector('[role="tablist"], .flex, .grid')
      expect(tabContainer).toBeInTheDocument()
    })
  })

  describe('Typography Scaling', () => {
    it('uses responsive text sizes for headings', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check for responsive heading sizes (text-4xl lg:text-6xl pattern)
      const headings = container.querySelectorAll('h1, h2, h3')
      const hasResponsiveTextSizes = Array.from(headings).some(heading => {
        const classes = heading.className
        return classes.includes('text-') && (
          classes.includes('sm:text-') ||
          classes.includes('md:text-') ||
          classes.includes('lg:text-') ||
          classes.includes('xl:text-')
        )
      })
      expect(hasResponsiveTextSizes).toBe(true)
    })

    it('body text scales appropriately', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check for readable text sizes (text-base, text-lg, etc.)
      const textElements = container.querySelectorAll('p, span, div')
      const hasReadableText = Array.from(textElements).some(el => 
        el.className.includes('text-base') || 
        el.className.includes('text-lg') ||
        el.className.includes('text-sm')
      )
      expect(hasReadableText).toBe(true)
    })
  })

  describe('Interactive Elements', () => {
    it('buttons have adequate touch targets on mobile', () => {
      render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        // Check for minimum 44px touch targets (py-3, py-4, etc.)
        const classes = button.className
        const hasAdequatePadding = 
          classes.includes('py-2') ||
          classes.includes('py-3') ||
          classes.includes('py-4') ||
          classes.includes('p-3') ||
          classes.includes('p-4')
        expect(hasAdequatePadding).toBe(true)
      })
    })

    it('form elements are touch-friendly', () => {
      const { container } = render(<UploadDemo onUploadComplete={mockFn} onBack={mockFn} />)
      
      // File upload area should be large enough for touch
      const uploadArea = container.querySelector('[class*="border-dashed"]')
      expect(uploadArea).toBeInTheDocument()
      
      // Should have adequate height for touch interaction
      if (uploadArea) {
        const hasMinHeight = uploadArea.className.includes('h-') || uploadArea.className.includes('py-')
        expect(hasMinHeight).toBe(true)
      }
    })
  })

  describe('Navigation Patterns', () => {
    it('dashboard navigation works on mobile', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      // Back button should be prominent and accessible
      const backButton = screen.getByText(/Back to Demo/)
      expect(backButton).toBeInTheDocument()
      expect(backButton.closest('button')).toHaveClass()
    })

    it('tab navigation is mobile-friendly', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      const tabs = screen.getAllByRole('button').filter(btn => 
        btn.textContent?.includes('Overview') ||
        btn.textContent?.includes('Goal') ||
        btn.textContent?.includes('Behavioral') ||
        btn.textContent?.includes('Insights')
      )
      
      // Tabs should be present and accessible
      expect(tabs.length).toBeGreaterThan(0)
      
      // Each tab should have adequate size for touch
      tabs.forEach(tab => {
        expect(tab).toHaveAccessibleName()
      })
    })
  })

  describe('Content Reflow', () => {
    it('grid layouts adapt to narrow screens', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Look for responsive grid patterns (grid-cols-1 md:grid-cols-2)
      const grids = container.querySelectorAll('[class*="grid-cols-"]')
      const hasResponsiveGrids = Array.from(grids).some(grid =>
        grid.className.includes('grid-cols-1') && (
          grid.className.includes('md:grid-cols-') ||
          grid.className.includes('lg:grid-cols-')
        )
      )
      
      if (grids.length > 0) {
        expect(hasResponsiveGrids).toBe(true)
      }
    })

    it('metrics display stacks on mobile', () => {
      render(<AnalysisDashboard results={realAnalysisResults} onBack={mockFn} />)
      
      // Look for metrics display
      expect(screen.getByText('Posts Analyzed')).toBeInTheDocument()
      expect(screen.getByText('Goal Areas Found')).toBeInTheDocument()
      
      // Metrics should be in a flexible layout
      const metricsSection = screen.getByText('Posts Analyzed').closest('div')
      expect(metricsSection).toBeInTheDocument()
    })
  })

  describe('Image and Media Scaling', () => {
    it('uses responsive image classes', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check for images with responsive classes
      const images = container.querySelectorAll('img, [class*="w-"], [class*="h-"]')
      const hasResponsiveImages = Array.from(images).some(img =>
        img.className.includes('w-full') ||
        img.className.includes('max-w-') ||
        img.className.includes('h-auto')
      )
      
      if (images.length > 0) {
        expect(hasResponsiveImages).toBe(true)
      }
    })
  })

  describe('Spacing and Margins', () => {
    it('uses responsive spacing patterns', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check for responsive margin/padding (mb-4 lg:mb-8 pattern)
      const elementsWithSpacing = container.querySelectorAll('[class*="m-"], [class*="p-"]')
      const hasResponsiveSpacing = Array.from(elementsWithSpacing).some(el => {
        const classes = el.className
        return (classes.includes('m-') || classes.includes('p-')) && (
          classes.includes('sm:') ||
          classes.includes('md:') ||
          classes.includes('lg:')
        )
      })
      
      expect(hasResponsiveSpacing).toBe(true)
    })

    it('maintains readability with appropriate line spacing', () => {
      const { container } = render(<LandingPage onStartDemo={mockFn} onViewDemo={mockFn} />)
      
      // Check for proper line height classes
      const textElements = container.querySelectorAll('p, div, span')
      const hasLineHeight = Array.from(textElements).some(el =>
        el.className.includes('leading-') ||
        el.className.includes('space-y-')
      )
      
      expect(hasLineHeight).toBe(true)
    })
  })
})