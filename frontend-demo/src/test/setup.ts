import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock window.matchMedia which is used by Recharts
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock ResizeObserver which is used by Recharts
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock fetch for API tests
global.fetch = vi.fn()

// Mock WebSocket constants
Object.defineProperty(global, 'WebSocket', {
  value: vi.fn().mockImplementation(() => ({
    readyState: 1, // WebSocket.OPEN
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    onopen: null,
    onmessage: null,
    onerror: null,
    onclose: null,
  })),
  writable: true,
})

// Add WebSocket constants
Object.assign(global.WebSocket, {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
})

// Suppress chart dimension warnings in tests
const originalError = console.error
console.error = (...args: any[]) => {
  if (typeof args[0] === 'string' && args[0].includes('width(0) and height(0)')) {
    return
  }
  originalError(...args)
}