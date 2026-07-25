export interface User {
  id: string
  username: string
  email: string
  createdAt: string
}

export interface KnowledgeEntry {
  id: string
  content: string
  sourceType: string
  sourcePath?: string
  tags: string[]
  createdAt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  sources?: KnowledgeEntry[]
}

export interface QueryResult {
  id: string
  entry: KnowledgeEntry
  score: number
  retrievalMode: string
}

export interface AppState {
  isAuthenticated: boolean
  currentUser: User | null
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
}

export type SearchMode = 'hybrid' | 'semantic' | 'keyword' | 'code_similarity'

export interface SearchResult {
  query: string
  results: QueryResult[]
  mode: SearchMode
}
