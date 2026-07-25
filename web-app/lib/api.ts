const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // Auth
  async login(username: string, password: string) {
    return this.request<{ user: User; token: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  }

  async register(username: string, email: string, password: string) {
    return this.request<{ user: User }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    })
  }

  // Knowledge
  async query(text: string, mode: string = 'hybrid', limit: number = 10) {
    return this.request<QueryResult[]>(
      `/api/query?text=${encodeURIComponent(text)}&mode=${mode}&limit=${limit}`
    )
  }

  async getEntries(sourceType?: string, limit: number = 20) {
    const params = new URLSearchParams({ limit: String(limit) })
    if (sourceType) params.append('source_type', sourceType)
    return this.request<KnowledgeEntry[]>(`/api/entries?${params}`)
  }

  async getEntry(id: string) {
    return this.request<KnowledgeEntry>(`/api/entries/${id}`)
  }

  // Chat
  async sendMessage(message: string, history: { role: string; content: string }[]) {
    return this.request<{ response: string; sources: KnowledgeEntry[] }>(
      '/api/chat',
      {
        method: 'POST',
        body: JSON.stringify({ message, history }),
      }
    )
  }

  // Status
  async getStatus() {
    return this.request<{
      entries: number
      vectors: number
      cloud: number
      network: string
    }>('/api/status')
  }
}

export const api = new APIClient()

// Types for API
import type { User, KnowledgeEntry, QueryResult } from '@/types'
