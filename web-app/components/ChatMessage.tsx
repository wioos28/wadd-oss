'use client'

import { ChatMessage as ChatMessageType } from '@/types'
import ReactMarkdown from 'react-markdown'

interface ChatMessageProps {
  message: ChatMessageType
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-md'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-md'
        }`}
      >
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown
            components={{
              code: ({ className, children, ...props }) => {
                const match = /language-(\w+)/.exec(className || '')
                const isInline = !match

                if (isInline) {
                  return (
                    <code
                      className={`px-1.5 py-0.5 rounded ${
                        isUser ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                      }`}
                      {...props}
                    >
                      {children}
                    </code>
                  )
                }

                return (
                  <div className="relative">
                    <div className="absolute top-2 right-2 text-xs text-gray-400">
                      {match?.[1]}
                    </div>
                    <pre className={`p-4 rounded-lg overflow-x-auto ${
                      isUser ? 'bg-blue-600' : 'bg-gray-800 dark:bg-gray-900'
                    }`}>
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                  </div>
                )
              },
              p: ({ children }) => (
                <p className="mb-2 last:mb-0">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="list-disc list-inside mb-2">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-inside mb-2">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="mb-1">{children}</li>
              ),
              h1: ({ children }) => (
                <h1 className="text-xl font-bold mb-2">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-lg font-bold mb-2">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-base font-bold mb-2">{children}</h3>
              ),
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:underline"
                >
                  {children}
                </a>
              ),
              blockquote: ({ children }) => (
                <blockquote className={`border-l-4 pl-4 ${
                  isUser ? 'border-blue-400' : 'border-gray-400'
                }`}>
                  {children}
                </blockquote>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Sources:</p>
            <div className="flex flex-wrap gap-2">
              {message.sources.map((source, i) => (
                <span
                  key={i}
                  className={`text-xs px-2 py-1 rounded ${
                    isUser
                      ? 'bg-blue-600 text-blue-100'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  {source.sourceType}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className={`text-xs mt-2 ${
          isUser ? 'text-blue-200' : 'text-gray-500 dark:text-gray-400'
        }`}>
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}
