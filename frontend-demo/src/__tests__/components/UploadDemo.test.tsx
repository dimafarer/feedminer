import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import JSZip from 'jszip'
import UploadDemo from '../../components/UploadDemo'

describe('UploadDemo', () => {
  const mockOnUploadComplete = vi.fn()
  const mockOnBack = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock window.alert
    vi.stubGlobal('alert', vi.fn())
    // Mock fetch for API calls
    vi.stubGlobal('fetch', vi.fn(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ contentId: 'test-123', message: 'success' })
      })
    ))
  })

  it('renders upload instructions correctly', () => {
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    expect(screen.getByText('Upload Your Instagram Data Export')).toBeInTheDocument()
    expect(screen.getByText('📱 How to Export Your Instagram Data')).toBeInTheDocument()
    expect(screen.getByText(/Go to Instagram.*Settings.*Privacy and Security/)).toBeInTheDocument()
  })

  it('shows upload area with proper messaging', () => {
    render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
    
    expect(screen.getByText('Drag & drop your Instagram export file here')).toBeInTheDocument()
    expect(screen.getByText('or click to browse')).toBeInTheDocument()
    expect(screen.getByText('Supports: Complete ZIP exports (recommended) or individual .json files')).toBeInTheDocument()
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

  // Helper function to create a mock Instagram ZIP file
  const createMockInstagramZip = async (dataTypes: Record<string, any> = {}) => {
    const zip = new JSZip()
    const basePath = 'instagram-testuser-2025-07-25-abc123/'
    
    // Add default saved posts if not specified
    if (!dataTypes.saved_posts) {
      dataTypes.saved_posts = {
        saved_saved_media: [
          {
            title: 'test_user',
            string_map_data: {
              'Saved on': {
                href: 'https://www.instagram.com/p/test123/',
                timestamp: 1640995200
              }
            }
          }
        ]
      }
    }

    // Add data files based on what's provided
    if (dataTypes.saved_posts) {
      zip.file(`${basePath}your_instagram_activity/saved/saved_posts.json`, JSON.stringify(dataTypes.saved_posts))
    }
    if (dataTypes.liked_posts) {
      zip.file(`${basePath}your_instagram_activity/likes/liked_posts.json`, JSON.stringify(dataTypes.liked_posts))
    }
    if (dataTypes.comments) {
      zip.file(`${basePath}your_instagram_activity/comments/post_comments_1.json`, JSON.stringify(dataTypes.comments))
    }
    if (dataTypes.user_posts) {
      zip.file(`${basePath}your_instagram_activity/media/posts_1.json`, JSON.stringify(dataTypes.user_posts))
    }
    if (dataTypes.following) {
      zip.file(`${basePath}connections/followers_and_following/following.json`, JSON.stringify(dataTypes.following))
    }

    const zipBlob = await zip.generateAsync({ type: 'blob' })
    return new File([zipBlob], 'instagram-export.zip', { type: 'application/zip' })
  }

  describe('ZIP Upload Functionality', () => {
    beforeEach(() => {
      vi.clearAllMocks()
    })

    it('detects Instagram ZIP files and shows data selection step', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip({
        saved_posts: { saved_saved_media: Array(50).fill(null).map((_, i) => ({ title: `user${i}` })) },
        liked_posts: { likes_media_likes: Array(100).fill(null).map((_, i) => ({ title: `user${i}` })) }
      })

      const dropzone = screen.getByText(/Drag & drop your Instagram export file here/i).closest('div')
      
      // Simulate file drop
      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      // Should show data selection step
      await waitFor(() => {
        expect(screen.getByText('Select Data to Analyze')).toBeInTheDocument()
      }, { timeout: 3000 })

      // Should show detected data types in checkboxes
      expect(screen.getByRole('checkbox', { name: /saved posts/i })).toBeInTheDocument()
      expect(screen.getByRole('checkbox', { name: /liked posts/i })).toBeInTheDocument()
      expect(screen.getAllByText('50 items')[0]).toBeInTheDocument()
      expect(screen.getAllByText('100 items')[0]).toBeInTheDocument()
    })

    it('shows ZIP analysis summary correctly', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip()

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      await waitFor(() => {
        expect(screen.getByText('Instagram Export Detected')).toBeInTheDocument()
        expect(screen.getByText(/files.*data types found/)).toBeInTheDocument()
      })
    })

    it('allows selecting and deselecting data types', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip({
        saved_posts: { saved_saved_media: [{ title: 'user1' }] },
        liked_posts: { likes_media_likes: [{ title: 'user2' }] }
      })

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      await waitFor(() => {
        expect(screen.getByText('Select Data to Analyze')).toBeInTheDocument()
      })

      // Should have saved posts selected by default
      const savedPostsCheckbox = screen.getByRole('checkbox', { name: /saved posts/i })
      expect(savedPostsCheckbox).toBeChecked()

      // Liked posts should not be selected
      const likedPostsCheckbox = screen.getByRole('checkbox', { name: /liked posts/i })
      expect(likedPostsCheckbox).not.toBeChecked()

      // Select liked posts
      await user.click(likedPostsCheckbox)
      expect(likedPostsCheckbox).toBeChecked()

      // Should show analysis preview with both selected
      expect(screen.getByText('Selected 2 data types for analysis:')).toBeInTheDocument()
    })

    it('shows analysis preview with correct totals', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip({
        saved_posts: { saved_saved_media: Array(25).fill({ title: 'user' }) },
        liked_posts: { likes_media_likes: Array(75).fill({ title: 'user' }) }
      })

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      await waitFor(() => {
        const likedPostsCheckbox = screen.getByRole('checkbox', { name: /liked posts/i })
        return user.click(likedPostsCheckbox)
      })

      // Should show total items
      expect(screen.getByText('Total items to analyze: 100')).toBeInTheDocument()
    })

    it('prevents proceeding without data type selection', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip()

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      await waitFor(() => {
        expect(screen.getByText('Select Data to Analyze')).toBeInTheDocument()
      })

      // Unselect the default saved posts
      const savedPostsCheckbox = screen.getByRole('checkbox', { name: /saved posts/i })
      await user.click(savedPostsCheckbox)

      // Continue button should be disabled
      const continueButton = screen.getByText('Continue to Preview')
      expect(continueButton).toBeDisabled()
    })

    it('proceeds to preview step with selected data types', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip({
        saved_posts: { saved_saved_media: Array(30).fill({ title: 'user' }) }
      })

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      await waitFor(() => {
        expect(screen.getByText('Select Data to Analyze')).toBeInTheDocument()
      })

      // Continue to preview
      const continueButton = screen.getByText('Continue to Preview')
      await user.click(continueButton)

      await waitFor(() => {
        expect(screen.getByText('Preview Your Data')).toBeInTheDocument()
        expect(screen.getByText(/Ready to analyze 1 data type.*Instagram export/)).toBeInTheDocument()
      })
    })

    it('shows correct preview for ZIP files', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip({
        saved_posts: { saved_saved_media: Array(45).fill({ title: 'user' }) }
      })

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      // Go through data selection
      await waitFor(() => {
        const continueButton = screen.getByText('Continue to Preview')
        return user.click(continueButton)
      })

      await waitFor(() => {
        // Should show ZIP format
        expect(screen.getByText(/Format: Instagram Export \(ZIP\)/)).toBeInTheDocument()
        // Should show data type selection confirmation
        expect(screen.getByText(/1 data type selected for analysis/)).toBeInTheDocument()
        // Should show what will be analyzed in the preview
        expect(screen.getByText('Posts you saved on Instagram')).toBeInTheDocument()
        const itemCounts = screen.getAllByText('45')
        expect(itemCounts.length).toBeGreaterThan(0)
      })
    })

    it('handles invalid ZIP files gracefully', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      // Create a ZIP file without Instagram structure
      const zip = new JSZip()
      zip.file('random-file.txt', 'This is not an Instagram export')
      const zipBlob = await zip.generateAsync({ type: 'blob' })
      const invalidZip = new File([zipBlob], 'not-instagram.zip', { type: 'application/zip' })

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, invalidZip)

      // Should go to regular preview (not data selection)
      await waitFor(() => {
        expect(screen.getByText('Preview Your Data')).toBeInTheDocument()
        // Should not show ZIP-specific messaging
        expect(screen.queryByText('Select Data to Analyze')).not.toBeInTheDocument()
      })
    })

    it('updates step indicators for ZIP files', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip()

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      await waitFor(() => {
        expect(screen.getByText('Select Data to Analyze')).toBeInTheDocument()
      })

      // Should show 4 steps for ZIP files (upload, data-selection, preview, confirm)
      const header = screen.getByRole('banner')
      const stepIndicators = header.querySelectorAll('.w-8.h-8.rounded-full')
      expect(stepIndicators).toHaveLength(4)
      
      // Step 2 should be active (data selection)
      expect(stepIndicators[1]).toHaveClass('bg-primary-600')
    })

    it('allows going back to upload from data selection', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      const zipFile = await createMockInstagramZip()

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, zipFile)

      await waitFor(() => {
        expect(screen.getByText('Select Data to Analyze')).toBeInTheDocument()
      })

      // Go back to upload
      const backButton = screen.getByText('Choose Different File')
      await user.click(backButton)

      await waitFor(() => {
        expect(screen.getByText('Upload Your Instagram Data Export')).toBeInTheDocument()
      })
    })

    it('maintains existing JSON file functionality', async () => {
      const user = userEvent.setup()
      render(<UploadDemo onUploadComplete={mockOnUploadComplete} onBack={mockOnBack} />)
      
      // Create a regular JSON file
      const jsonData = JSON.stringify({ saved_saved_media: [{ title: 'test' }] })
      const jsonFile = new File([jsonData], 'saved_posts.json', { type: 'application/json' })

      const fileInput = screen.getByRole('presentation').querySelector('input[type="file"]') as HTMLInputElement
      await user.upload(fileInput, jsonFile)

      // Should go directly to preview (skip data selection)
      await waitFor(() => {
        expect(screen.getByText('Preview Your Data')).toBeInTheDocument()
        expect(screen.queryByText('Select Data to Analyze')).not.toBeInTheDocument()
      })
    })
  })
})