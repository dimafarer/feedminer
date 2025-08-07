import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useFeedMinerAPI } from '../../services/feedminerApi'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock WebSocket
const mockWebSocket = vi.fn() as any
global.WebSocket = mockWebSocket

describe('Reprocessing API Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockClear()
  })

  describe('reprocessContent', () => {
    it('sends correct request for reprocessing with Anthropic model', async () => {
      const mockResponse = {
        message: 'Reprocessing started successfully',
        jobId: 'job-123',
        estimatedCost: 0.015,
        estimatedTime: 20,
        analysisId: 'anthropic#claude-3-5-sonnet-20241022#2025-08-07T12:00:00Z'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const api = useFeedMinerAPI()
      const contentId = 'test-content-123'
      const request = {
        model_provider: 'anthropic',
        model_name: 'claude-3-5-sonnet-20241022',
        temperature: 0.7,
        force: false
      }

      const result = await api.reprocessContent(contentId, request)

      expect(mockFetch).toHaveBeenCalledWith(
        `https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev/content/${contentId}/reprocess`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        }
      )

      expect(result).toEqual(mockResponse)
    })

    it('sends correct request for reprocessing with Bedrock model', async () => {
      const mockResponse = {
        message: 'Reprocessing started successfully',
        jobId: 'job-456',
        estimatedCost: 0.012,
        estimatedTime: 18,
        analysisId: 'bedrock#anthropic.claude-3-5-sonnet-20241022-v2:0#2025-08-07T12:00:00Z'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const api = useFeedMinerAPI()
      const contentId = 'test-content-456'
      const request = {
        model_provider: 'bedrock',
        model_name: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        temperature: 0.5,
        force: true
      }

      const result = await api.reprocessContent(contentId, request)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`/content/${contentId}/reprocess`),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(request)
        })
      )

      expect(result).toEqual(mockResponse)
    })

    it('handles reprocessing API errors correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: () => Promise.resolve({
          error: 'Invalid model_provider: unsupported'
        })
      })

      const api = useFeedMinerAPI()
      
      await expect(
        api.reprocessContent('test-content', {
          model_provider: 'unsupported',
          model_name: 'test-model'
        } as any)
      ).rejects.toThrow('Reprocessing failed: Bad Request')
    })

    it('handles content not found error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({
          error: 'Content not found: nonexistent-content'
        })
      })

      const api = useFeedMinerAPI()
      
      await expect(
        api.reprocessContent('nonexistent-content', {
          model_provider: 'anthropic',
          model_name: 'claude-3-5-sonnet-20241022'
        })
      ).rejects.toThrow('Reprocessing failed: Not Found')
    })

    it('validates request parameters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ message: 'Success' })
      })

      const api = useFeedMinerAPI()
      
      // Missing model_name should be handled by the API
      const invalidRequest = {
        model_provider: 'anthropic',
        // missing model_name
      } as any

      // Should still make the request and let API handle validation
      await api.reprocessContent('test-content', invalidRequest)
      expect(mockFetch).toHaveBeenCalled()
    })
  })

  describe('getAnalysisHistory', () => {
    it('retrieves analysis history for content', async () => {
      const mockResponse = {
        analyses: [
          {
            analysisId: 'anthropic#claude-3-5-sonnet-20241022#2025-08-07T12:00:00Z',
            modelProvider: 'anthropic',
            modelName: 'claude-3-5-sonnet-20241022',
            createdAt: '2025-08-07T12:00:00Z',
            metadata: {
              processingTime: 18.5,
              estimatedCost: 0.015
            }
          },
          {
            analysisId: 'bedrock#anthropic.claude-3-5-sonnet-20241022-v2:0#2025-08-07T11:30:00Z',
            modelProvider: 'bedrock',
            modelName: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
            createdAt: '2025-08-07T11:30:00Z',
            metadata: {
              processingTime: 22.1,
              estimatedCost: 0.012
            }
          }
        ]
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const api = useFeedMinerAPI()
      const result = await api.getAnalysisHistory('test-content-123')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev/content/test-content-123/analyses',
        expect.objectContaining({
          method: 'GET'
        })
      )

      expect(result).toEqual(mockResponse)
      expect(result.analyses).toHaveLength(2)
    })

    it('handles empty analysis history', async () => {
      const mockResponse = { analyses: [] }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const api = useFeedMinerAPI()
      const result = await api.getAnalysisHistory('new-content')

      expect(result.analyses).toHaveLength(0)
    })
  })

  describe('cancelReprocessing', () => {
    it('cancels active reprocessing job', async () => {
      const mockResponse = {
        message: 'Reprocessing job cancelled successfully',
        jobId: 'job-789',
        status: 'cancelled'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const api = useFeedMinerAPI()
      const result = await api.cancelReprocessing('test-content-123', 'job-789')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev/jobs/job-789/cancel',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ contentId: 'test-content-123' }),
          headers: {
            'Content-Type': 'application/json'
          }
        })
      )

      expect(result).toEqual(mockResponse)
    })

    it('handles job not found error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({
          error: 'Job not found or already completed'
        })
      })

      const api = useFeedMinerAPI()
      
      await expect(
        api.cancelReprocessing('test-content', 'nonexistent-job')
      ).rejects.toThrow('Cancel reprocessing failed: Not Found')
    })
  })

  describe('WebSocket Progress Integration', () => {
    it('creates WebSocket connection for reprocessing progress', () => {
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

      const api = useFeedMinerAPI()
      const onMessage = vi.fn()
      const onError = vi.fn()

      const ws = api.createWebSocketConnection(onMessage, onError)

      expect(mockWebSocket).toHaveBeenCalledWith(
        'wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev'
      )

      expect(ws).toBe(mockWsInstance)
    })

    it('handles analysis progress messages correctly', () => {
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

      const api = useFeedMinerAPI()
      const onMessage = vi.fn()
      const onError = vi.fn()

      const ws = api.createWebSocketConnection(onMessage, onError)
      
      // Simulate WebSocket message
      const progressMessage = {
        type: 'analysis_progress',
        contentId: 'test-content-123',
        jobId: 'job-456',
        data: {
          progress: 50,
          currentStep: 'Analyzing content with Claude 3.5 Sonnet...',
          estimatedTimeRemaining: 15
        }
      }

      // Trigger onmessage
      if (ws.onmessage) {
        ws.onmessage({ data: JSON.stringify(progressMessage) } as MessageEvent)
      }

      expect(onMessage).toHaveBeenCalledWith(progressMessage)
    })

    it('handles analysis completion messages', () => {
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

      const api = useFeedMinerAPI()
      const onMessage = vi.fn()
      const onError = vi.fn()

      const ws = api.createWebSocketConnection(onMessage, onError)
      
      const completionMessage = {
        type: 'analysis_complete',
        contentId: 'test-content-123',
        jobId: 'job-456',
        data: {
          result: {
            total_posts: 177,
            categories: [],
            insights: []
          }
        }
      }

      if (ws.onmessage) {
        ws.onmessage({ data: JSON.stringify(completionMessage) } as MessageEvent)
      }

      expect(onMessage).toHaveBeenCalledWith(completionMessage)
    })

    it('handles WebSocket errors', () => {
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

      const api = useFeedMinerAPI()
      const onMessage = vi.fn()
      const onError = vi.fn()

      const ws = api.createWebSocketConnection(onMessage, onError)
      
      const error = new Error('WebSocket connection failed')

      if (ws.onerror) {
        ws.onerror(error as Event)
      }

      expect(onError).toHaveBeenCalledWith(error)
    })
  })

  describe('Phase 1 Model Support', () => {
    it('supports Anthropic API models', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ message: 'Success' })
      })

      const api = useFeedMinerAPI()
      
      await api.reprocessContent('test-content', {
        model_provider: 'anthropic',
        model_name: 'claude-3-5-sonnet-20241022',
        temperature: 0.7
      })

      expect(mockFetch).toHaveBeenCalled()
    })

    it('supports AWS Bedrock models', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ message: 'Success' })
      })

      const api = useFeedMinerAPI()
      
      await api.reprocessContent('test-content', {
        model_provider: 'bedrock',
        model_name: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        temperature: 0.5
      })

      expect(mockFetch).toHaveBeenCalled()
    })

    it('handles temperature parameter correctly', async () => {
      const api = useFeedMinerAPI()
      const temperatures = [0.0, 0.3, 0.7, 1.0]

      for (const temperature of temperatures) {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ message: 'Success' })
        })

        await api.reprocessContent('test-content', {
          model_provider: 'anthropic',
          model_name: 'claude-3-5-sonnet-20241022',
          temperature
        })

        expect(mockFetch).toHaveBeenLastCalledWith(
          expect.any(String),
          expect.objectContaining({
            body: JSON.stringify({
              model_provider: 'anthropic',
              model_name: 'claude-3-5-sonnet-20241022',
              temperature
            })
          })
        )
      }
    })
  })
})