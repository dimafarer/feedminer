import { describe, it, expect, vi, beforeEach } from 'vitest'
import { feedminerApi, demoMode } from '../../services/feedminerApi'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock WebSocket
const mockWebSocket = vi.fn()
global.WebSocket = mockWebSocket

describe('FeedMiner API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockClear()
    mockWebSocket.mockClear()
  })

  describe('uploadContent', () => {
    it('sends correct request for content upload', async () => {
      const mockResponse = {
        contentId: 'test-id',
        message: 'Content uploaded successfully',
        s3Key: 'uploads/test-id.json',
        status: 'uploaded',
        type: 'instagram_saved'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const testContent = { test: 'data' }
      const result = await feedminerApi.uploadContent(testContent, 'instagram_saved', 'test-user')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev/upload',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'instagram_saved',
            user_id: 'test-user',
            content: testContent,
          }),
        }
      )

      expect(result).toEqual(mockResponse)
    })

    it('handles upload errors correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Bad Request'
      })

      await expect(
        feedminerApi.uploadContent({ test: 'data' })
      ).rejects.toThrow('Upload failed: Bad Request')
    })

    it('uses default parameters when not provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({})
      })

      await feedminerApi.uploadContent({ test: 'data' })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({
            type: 'instagram_saved',
            user_id: 'demo-user',
            content: { test: 'data' },
          }),
        })
      )
    })
  })

  describe('listContent', () => {
    it('sends correct request for listing content', async () => {
      const mockResponse = {
        items: [],
        count: 0,
        hasMore: false
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const result = await feedminerApi.listContent('test-user', 10)

      expect(mockFetch).toHaveBeenCalledWith(
        'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev/content?userId=test-user&limit=10',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      expect(result).toEqual(mockResponse)
    })

    it('works without userId parameter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ items: [], count: 0, hasMore: false })
      })

      await feedminerApi.listContent(undefined, 5)

      expect(mockFetch).toHaveBeenCalledWith(
        'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev/content?limit=5',
        expect.any(Object)
      )
    })
  })

  describe('getContent', () => {
    it('sends correct request for getting specific content', async () => {
      const mockResponse = {
        contentId: 'test-id',
        type: 'instagram_saved',
        status: 'analyzed',
        createdAt: '2025-07-14T10:00:00Z'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const result = await feedminerApi.getContent('test-id', true)

      expect(mockFetch).toHaveBeenCalledWith(
        'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev/content/test-id?includeRaw=true',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      expect(result).toEqual(mockResponse)
    })
  })

  describe('WebSocket integration', () => {
    it('creates WebSocket connection with correct URL', () => {
      const mockWsInstance = {
        onopen: null,
        onmessage: null,
        onerror: null,
        onclose: null,
        readyState: 1,
        send: vi.fn(),
        close: vi.fn()
      }

      mockWebSocket.mockReturnValueOnce(mockWsInstance)

      const onMessage = vi.fn()
      const onError = vi.fn()

      const ws = feedminerApi.createWebSocketConnection(onMessage, onError)

      expect(mockWebSocket).toHaveBeenCalledWith(
        'wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev'
      )

      expect(ws).toBe(mockWsInstance)
    })

    it('sends WebSocket messages correctly', () => {
      const mockWsInstance = {
        readyState: 1, // WebSocket.OPEN
        send: vi.fn()
      }

      // Mock WebSocket.OPEN constant
      Object.defineProperty(global.WebSocket, 'OPEN', { value: 1 })

      feedminerApi.sendWebSocketMessage(mockWsInstance as any, 'analyze_content', {
        content_id: 'test-id',
        data: { test: 'data' }
      })

      expect(mockWsInstance.send).toHaveBeenCalledTimes(1)
      expect(mockWsInstance.send).toHaveBeenCalledWith(
        JSON.stringify({
          action: 'analyze_content',
          content_id: 'test-id',
          data: { test: 'data' }
        })
      )
    })

    it('handles closed WebSocket correctly', () => {
      const mockWsInstance = {
        readyState: 3, // WebSocket.CLOSED
        send: vi.fn()
      }

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      feedminerApi.sendWebSocketMessage(mockWsInstance as any, 'test', {})

      expect(mockWsInstance.send).not.toHaveBeenCalled()
      expect(consoleSpy).toHaveBeenCalledWith('WebSocket not open. Ready state:', 3)

      consoleSpy.mockRestore()
    })
  })
})

describe('Demo Mode', () => {
  it('simulates upload correctly', async () => {
    const result = await demoMode.simulateUpload({ test: 'data' })

    expect(result).toMatchObject({
      message: 'Content uploaded successfully (demo mode)',
      s3Key: 'demo/uploads/sample-data.json',
      status: 'uploaded',
      type: 'instagram_saved'
    })
    expect(result.contentId).toMatch(/^demo-[a-z0-9]+$/)
  })

  it('simulates processing with progress updates', async () => {
    const progressUpdates: Array<{ progress: number; message: string }> = []
    const onUpdate = (progress: number, message: string) => {
      progressUpdates.push({ progress, message })
    }

    await demoMode.simulateProcessing(onUpdate)

    expect(progressUpdates).toHaveLength(6)
    expect(progressUpdates[0]).toMatchObject({
      progress: 0.1,
      message: 'Uploading content to secure storage...'
    })
    expect(progressUpdates[5]).toMatchObject({
      progress: 1.0,
      message: 'Analysis complete!'
    })
  })

  it('progresses through all processing steps', async () => {
    const messages: string[] = []
    const onUpdate = (_progress: number, message: string) => {
      messages.push(message)
    }

    await demoMode.simulateProcessing(onUpdate)

    expect(messages).toContain('Uploading content to secure storage...')
    expect(messages).toContain('Analyzing content structure and format...')
    expect(messages).toContain('Identifying behavioral patterns...')
    expect(messages).toContain('Extracting interest categories...')
    expect(messages).toContain('Generating personalized goals...')
    expect(messages).toContain('Analysis complete!')
  })
})