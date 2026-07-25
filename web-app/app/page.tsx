'use client'

import { useState, useEffect } from 'react'
import { User, ChatMessage, QueryResult, SearchMode } from '@/types'
import { api } from '@/lib/api'
import LoginForm from '@/components/LoginForm'
import Sidebar from '@/components/Sidebar'
import ChatPanel from '@/components/ChatPanel'
import SearchPanel from '@/components/SearchPanel'

export default function Home() {
  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // UI state
  const [activeTab, setActiveTab] = useState<'chat' | 'search' | 'settings'>('chat')
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isChatLoading, setIsChatLoading] = useState(false)

  // Check for existing session
  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
        setIsAuthenticated(true)
      } catch {
        localStorage.removeItem('user')
      }
    }
  }, [])

  // Auth handlers
  const handleLogin = async (username: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      // For demo, use hardcoded credentials
      if (username === 'admin' && password === 'test123') {
        const demoUser: User = {
          id: 'demo-user',
          username: 'admin',
          email: 'admin@example.com',
          createdAt: new Date().toISOString(),
        }
        setUser(demoUser)
        setIsAuthenticated(true)
        localStorage.setItem('user', JSON.stringify(demoUser))
      } else {
        // Try API
        const result = await api.login(username, password)
        setUser(result.user)
        setIsAuthenticated(true)
        localStorage.setItem('user', JSON.stringify(result.user))
      }
    } catch (err) {
      setError('Invalid credentials. Try admin/test123')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegister = async (username: string, email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await api.register(username, email, password)
      setUser(result.user)
      setIsAuthenticated(true)
      localStorage.setItem('user', JSON.stringify(result.user))
    } catch (err) {
      setError('Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    setUser(null)
    setIsAuthenticated(false)
    setMessages([])
    localStorage.removeItem('user')
  }

  // Chat handler
  const handleSendMessage = async (content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsChatLoading(true)

    try {
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const result = await api.sendMessage(content, history)

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.response,
        timestamp: new Date(),
        sources: result.sources,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsChatLoading(false)
    }
  }

  // Search handler
  const handleSearch = async (query: string, mode: SearchMode) => {
    const result = await api.query(query, mode)
    return result
  }

  // Not authenticated
  if (!isAuthenticated || !user) {
    return (
      <LoginForm
        onLogin={handleLogin}
        onRegister={handleRegister}
        isLoading={isLoading}
        error={error}
      />
    )
  }

  // Authenticated
  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-950">
      {/* Sidebar */}
      <Sidebar
        user={user}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onLogout={handleLogout}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'chat' && (
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isChatLoading}
          />
        )}
        {activeTab === 'search' && <SearchPanel onSearch={handleSearch} />}
        {activeTab === 'settings' && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <h2 className="text-2xl font-bold mb-2">Settings</h2>
              <p>Settings panel coming soon</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
