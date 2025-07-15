// FeedMiner API Integration
const API_BASE_URL = 'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev';
const WEBSOCKET_URL = 'wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev';

export interface UploadResponse {
  contentId: string;
  message: string;
  s3Key: string;
  status: string;
  type: string;
}

export interface ContentItem {
  contentId: string;
  type: string;
  status: string;
  createdAt: string;
  analysis?: any;
  rawContent?: any;
}

export interface ListResponse {
  items: ContentItem[];
  count: number;
  hasMore: boolean;
}

export interface JobStatus {
  jobId: string;
  contentId: string;
  status: string;
  result?: any;
}

class FeedMinerAPI {
  private baseUrl: string;
  private websocketUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.websocketUrl = WEBSOCKET_URL;
  }

  // Upload content for analysis
  async uploadContent(content: any, type: string = 'instagram_saved', userId: string = 'demo-user'): Promise<UploadResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          user_id: userId,
          content,
        }),
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  // List all content for a user
  async listContent(userId?: string, limit: number = 20): Promise<ListResponse> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('userId', userId);
      params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/content?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`List content failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('List content error:', error);
      throw error;
    }
  }

  // Get specific content item
  async getContent(contentId: string, includeRaw: boolean = false): Promise<ContentItem> {
    try {
      const params = new URLSearchParams();
      if (includeRaw) params.append('includeRaw', 'true');

      const response = await fetch(`${this.baseUrl}/content/${contentId}?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Get content failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get content error:', error);
      throw error;
    }
  }

  // Get job status
  async getJobStatus(jobId: string): Promise<JobStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/jobs/${jobId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Get job status failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get job status error:', error);
      throw error;
    }
  }

  // Create WebSocket connection for real-time updates
  createWebSocketConnection(onMessage?: (data: any) => void, onError?: (error: Event) => void): WebSocket {
    const ws = new WebSocket(this.websocketUrl);

    ws.onopen = () => {
      console.log('WebSocket connected to FeedMiner');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        if (onMessage) {
          onMessage(data);
        }
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) {
        onError(error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return ws;
  }

  // Send message via WebSocket
  sendWebSocketMessage(ws: WebSocket, action: string, data: any): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        action,
        ...data,
      }));
    } else {
      console.error('WebSocket not open. Ready state:', ws.readyState);
    }
  }
}

// Create singleton instance
export const feedminerApi = new FeedMinerAPI();

// Hook for React components
export const useFeedMinerAPI = () => {
  return {
    uploadContent: feedminerApi.uploadContent.bind(feedminerApi),
    listContent: feedminerApi.listContent.bind(feedminerApi),
    getContent: feedminerApi.getContent.bind(feedminerApi),
    getJobStatus: feedminerApi.getJobStatus.bind(feedminerApi),
    createWebSocketConnection: feedminerApi.createWebSocketConnection.bind(feedminerApi),
    sendWebSocketMessage: feedminerApi.sendWebSocketMessage.bind(feedminerApi),
  };
};

// Demo mode utilities
export const demoMode = {
  enabled: true,
  
  // Simulate API responses for demo
  async simulateUpload(_content: any): Promise<UploadResponse> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          contentId: 'demo-' + Math.random().toString(36).substr(2, 9),
          message: 'Content uploaded successfully (demo mode)',
          s3Key: 'demo/uploads/sample-data.json',
          status: 'uploaded',
          type: 'instagram_saved',
        });
      }, 1000);
    });
  },

  // Simulate processing updates
  simulateProcessing(onUpdate: (progress: number, message: string) => void): Promise<void> {
    return new Promise((resolve) => {
      const steps = [
        { progress: 0.1, message: 'Uploading content to secure storage...' },
        { progress: 0.3, message: 'Analyzing content structure and format...' },
        { progress: 0.5, message: 'Identifying behavioral patterns...' },
        { progress: 0.7, message: 'Extracting interest categories...' },
        { progress: 0.9, message: 'Generating personalized goals...' },
        { progress: 1.0, message: 'Analysis complete!' },
      ];

      let currentStep = 0;
      const interval = setInterval(() => {
        if (currentStep < steps.length) {
          const step = steps[currentStep];
          onUpdate(step.progress, step.message);
          currentStep++;
        } else {
          clearInterval(interval);
          resolve();
        }
      }, 500);
    });
  },
};

export default feedminerApi;