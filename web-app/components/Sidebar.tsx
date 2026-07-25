'use client'

import { useState } from 'react'
import {
  MessageSquare,
  Search,
  Settings,
  LogOut,
  Plus,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { User } from '@/types'

interface SidebarProps {
  user: User
  activeTab: 'chat' | 'search' | 'settings'
  onTabChange: (tab: 'chat' | 'search' | 'settings') => void
  onLogout: () => void
  isCollapsed: boolean
  onToggleCollapse: () => void
}

export default function Sidebar({
  user,
  activeTab,
  onTabChange,
  onLogout,
  isCollapsed,
  onToggleCollapse,
}: SidebarProps) {
  const menuItems = [
    { id: 'chat' as const, label: 'Chat', icon: MessageSquare },
    { id: 'search' as const, label: 'Search', icon: Search },
    { id: 'settings' as const, label: 'Settings', icon: Settings },
  ]

  return (
    <div
      className={`flex flex-col h-full bg-gray-900 text-white transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="font-bold">KE</span>
            </div>
            <span className="font-semibold">Knowledge Engine</span>
          </div>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <button
          className={`w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors ${
            isCollapsed ? 'px-2' : ''
          }`}
        >
          <Plus className="w-5 h-5" />
          {!isCollapsed && <span>New Chat</span>}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 space-y-1">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
              activeTab === item.id
                ? 'bg-gray-700 text-white'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            } ${isCollapsed ? 'justify-center' : ''}`}
          >
            <item.icon className="w-5 h-5" />
            {!isCollapsed && <span>{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* User Info */}
      <div className="p-4 border-t border-gray-700">
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'space-x-3'}`}>
          <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
            <span className="font-semibold">
              {user.username.charAt(0).toUpperCase()}
            </span>
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.username}</p>
              <p className="text-xs text-gray-400 truncate">{user.email}</p>
            </div>
          )}
          {!isCollapsed && (
            <button
              onClick={onLogout}
              className="p-2 rounded-lg hover:bg-gray-700 transition-colors text-gray-400 hover:text-white"
            >
              <LogOut className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
