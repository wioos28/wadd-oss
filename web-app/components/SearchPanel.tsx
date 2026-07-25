'use client'

import { useState } from 'react'
import { Search, Filter, ExternalLink } from 'lucide-react'
import { QueryResult, SearchMode } from '@/types'

interface SearchPanelProps {
  onSearch: (query: string, mode: SearchMode) => Promise<QueryResult[]>
}

export default function SearchPanel({ onSearch }: SearchPanelProps) {
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState<SearchMode>('hybrid')
  const [results, setResults] = useState<QueryResult[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return

    setIsLoading(true)
    try {
      const searchResults = await onSearch(query, mode)
      setResults(searchResults)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-500 bg-green-100 dark:bg-green-900'
    if (score >= 0.4) return 'text-yellow-500 bg-yellow-100 dark:bg-yellow-900'
    return 'text-red-500 bg-red-100 dark:bg-red-900'
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Search Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
          Search Knowledge Base
        </h2>

        {/* Search Input */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search knowledge..."
            className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        {/* Mode Selector */}
        <div className="flex space-x-2">
          {(['hybrid', 'semantic', 'keyword', 'code_similarity'] as SearchMode[]).map(
            (m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  mode === m
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {m.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
              </button>
            )
          )}
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">Searching...</p>
            </div>
          </div>
        ) : results.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <Search className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">No results yet</p>
              <p className="text-sm">Enter a query to search your knowledge base</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Found {results.length} results
            </p>
            {results.map((result) => (
              <div
                key={result.id}
                className="p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                      {result.entry.sourceType}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {result.retrievalMode}
                    </span>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded ${getScoreColor(result.score)}`}
                  >
                    {(result.score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-gray-900 dark:text-gray-100 mb-2 line-clamp-3">
                  {result.entry.content}
                </p>
                {result.entry.sourcePath && (
                  <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                    <ExternalLink className="w-3 h-3 mr-1" />
                    <span className="truncate">{result.entry.sourcePath}</span>
                  </div>
                )}
                {result.entry.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {result.entry.tags.slice(0, 5).map((tag, i) => (
                      <span
                        key={i}
                        className="text-xs px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
