'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: any[]
  intent?: string
  isStreaming?: boolean
}

export default function WcoreChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    // Check API connection
    checkConnection()
  }, [])

  const checkConnection = async () => {
    try {
      const response = await fetch('/api/health')
      setIsConnected(response.ok)
    } catch {
      setIsConnected(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Create placeholder for streaming response
    const assistantMessageId = (Date.now() + 1).toString()
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    }
    setMessages(prev => [...prev, assistantMessage])

    try {
      // Use SSE streaming
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          history: messages.slice(-5).map(m => ({
            role: m.role,
            content: m.content,
          })),
        }),
      })

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        let fullContent = ''
        let sources: any[] = []
        let intent = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))

                if (data.type === 'token') {
                  fullContent += data.data
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === assistantMessageId
                        ? { ...m, content: fullContent }
                        : m
                    )
                  )
                } else if (data.type === 'sources') {
                  sources = data.data
                } else if (data.type === 'intent') {
                  intent = data.data?.type || ''
                } else if (data.type === 'done') {
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === assistantMessageId
                        ? { ...m, isStreaming: false, sources, intent }
                        : m
                    )
                  )
                }
              } catch (e) {
                // Ignore parse errors
              }
            }
          }
        }
      }
    } catch (error) {
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantMessageId
            ? {
                ...m,
                content: 'Xin lỗi, tôi gặp lỗi khi xử lý. Vui lòng thử lại.',
                isStreaming: false,
              }
            : m
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Header */}
      <div className="bg-gray-800/80 backdrop-blur-sm border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Wcore X</h1>
              <p className="text-xs text-gray-400">AI Knowledge Assistant</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-20 h-20 bg-blue-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Bot className="w-10 h-10 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Xin chào! Tôi là Wcore X
              </h2>
              <p className="text-gray-400 max-w-md mx-auto">
                Tôi có thể giúp bạn trả lời câu hỏi, tìm kiếm kiến thức, và học hỏi từ kho dữ liệu.
              </p>
              <div className="mt-8 grid grid-cols-2 gap-4 max-w-lg mx-auto">
                <button
                  onClick={() => setInput('Giải thích về machine learning')}
                  className="p-4 bg-gray-800/50 rounded-xl text-left hover:bg-gray-700/50 transition-colors"
                >
                  <p className="text-white text-sm">Giải thích về</p>
                  <p className="text-blue-400 text-sm font-medium">Machine Learning</p>
                </button>
                <button
                  onClick={() => setInput('Hướng dẫn viết văn nghị luận')}
                  className="p-4 bg-gray-800/50 rounded-xl text-left hover:bg-gray-700/50 transition-colors"
                >
                  <p className="text-white text-sm">Hướng dẫn</p>
                  <p className="text-blue-400 text-sm font-medium">Viết văn nghị luận</p>
                </button>
                <button
                  onClick={() => setInput('Phân tích lịch sử Việt Nam')}
                  className="p-4 bg-gray-800/50 rounded-xl text-left hover:bg-gray-700/50 transition-colors"
                >
                  <p className="text-white text-sm">Phân tích</p>
                  <p className="text-blue-400 text-sm font-medium">Lịch sử Việt Nam</p>
                </button>
                <button
                  onClick={() => setInput('Toán học cơ bản')}
                  className="p-4 bg-gray-800/50 rounded-xl text-left hover:bg-gray-700/50 transition-colors"
                >
                  <p className="text-white text-sm">Học về</p>
                  <p className="text-blue-400 text-sm font-medium">Toán học cơ bản</p>
                </button>
              </div>
            </div>
          ) : (
            messages.map(message => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex space-x-3 max-w-3xl ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                    message.role === 'user' ? 'bg-blue-500' : 'bg-purple-500'
                  }`}>
                    {message.role === 'user' ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-white" />
                    )}
                  </div>

                  {/* Content */}
                  <div className={`rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white rounded-br-md'
                      : 'bg-gray-800 text-gray-100 rounded-bl-md'
                  }`}>
                    {message.isStreaming && !message.content ? (
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                        <span className="text-gray-400">Đang suy nghĩ...</span>
                      </div>
                    ) : (
                      <div className="prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    )}

                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-700">
                        <p className="text-xs text-gray-400 mb-2">Nguồn tham khảo:</p>
                        <div className="flex flex-wrap gap-2">
                          {message.sources.slice(0, 3).map((source, i) => (
                            <span
                              key={i}
                              className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300"
                            >
                              {source.source_type || 'knowledge'}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                      <span>{message.timestamp.toLocaleTimeString()}</span>
                      {message.intent && (
                        <span className="px-2 py-0.5 rounded bg-gray-700 text-gray-400">
                          {message.intent}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-gray-800/80 backdrop-blur-sm border-t border-gray-700 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nhập câu hỏi của bạn..."
              rows={1}
              className="w-full bg-gray-700 text-white placeholder-gray-400 rounded-xl px-4 py-3 pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="absolute right-2 bottom-2 p-2 bg-blue-500 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 text-white animate-spin" />
              ) : (
                <Send className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 text-center mt-2">
            Nhấn Enter để gửi, Shift+Enter để xuống dòng
          </p>
        </div>
      </div>
    </div>
  )
}
