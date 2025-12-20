import { useState, useEffect, useRef, useCallback } from 'react'
import api from '../../services/api'
import ProfileImage from '../common/ProfileImage'
import useWebSocket from '../../hooks/useWebSocket'

/**
 * Real-time chat window component with WebSocket support
 * Features: typing indicators, read receipts, online status
 */
const ChatWindow = ({
  conversation,
  currentUser,
  onClose,
  onNewMessage
}) => {
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const typingTimeoutRef = useRef(null)

  // Get auth token for WebSocket
  const token = localStorage.getItem('token')

  // WebSocket connection
  const {
    isConnected,
    lastMessage,
    typingUsers,
    onlineUsers,
    sendMessage: wsSendMessage,
    sendTyping,
    markAsRead
  } = useWebSocket(currentUser?.id, token)

  const partnerId = conversation?.id
  const isPartnerOnline = onlineUsers.includes(partnerId)
  const isPartnerTyping = typingUsers[partnerId]

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // Fetch messages
  const fetchMessages = useCallback(async () => {
    if (!partnerId) return
    try {
      const response = await api.get(`/api/messages/conversation/${partnerId}`)
      setMessages(response.data)

      // Mark unread messages as read
      const unreadIds = response.data
        .filter(m => m.sender_id === partnerId && !m.is_read)
        .map(m => m.id)
      if (unreadIds.length > 0 && isConnected) {
        markAsRead(unreadIds, partnerId)
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error)
    } finally {
      setLoading(false)
    }
  }, [partnerId, isConnected, markAsRead])

  // Load messages on mount
  useEffect(() => {
    fetchMessages()
  }, [fetchMessages])

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    if (lastMessage.type === 'new_message') {
      const msg = lastMessage.message
      // Only add if it's from/to current conversation
      if (msg.sender_id === partnerId || msg.receiver_id === partnerId) {
        setMessages(prev => [...prev, msg])
        scrollToBottom()

        // Mark as read if from partner
        if (msg.sender_id === partnerId && isConnected) {
          markAsRead([msg.id], partnerId)
        }

        onNewMessage?.(msg)
      }
    }

    if (lastMessage.type === 'message_sent') {
      // Update local message status if needed
    }

    if (lastMessage.type === 'messages_read') {
      // Update read status of our messages
      if (lastMessage.read_by === partnerId) {
        setMessages(prev => prev.map(msg =>
          lastMessage.message_ids.includes(msg.id)
            ? { ...msg, is_read: true, read_at: lastMessage.read_at }
            : msg
        ))
      }
    }
  }, [lastMessage, partnerId, isConnected, markAsRead, scrollToBottom, onNewMessage])

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // Handle input change with typing indicator
  const handleInputChange = (e) => {
    setNewMessage(e.target.value)

    // Send typing indicator
    if (isConnected) {
      sendTyping(partnerId, true)

      // Clear previous timeout and set new one
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
      typingTimeoutRef.current = setTimeout(() => {
        sendTyping(partnerId, false)
      }, 2000)
    }
  }

  // Send message
  const handleSend = async () => {
    if (!newMessage.trim() || sending) return

    const content = newMessage.trim()
    setNewMessage('')
    setSending(true)

    // Clear typing indicator
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }
    sendTyping(partnerId, false)

    // Try WebSocket first
    if (isConnected && wsSendMessage(partnerId, content)) {
      // Optimistically add message
      const tempMessage = {
        id: Date.now(), // Temporary ID
        sender_id: currentUser.id,
        receiver_id: partnerId,
        content: content,
        timestamp: new Date().toISOString(),
        is_read: false,
        is_sending: true
      }
      setMessages(prev => [...prev, tempMessage])
      setSending(false)
    } else {
      // Fallback to HTTP
      try {
        await api.post('/api/messages/send', {
          receiver_id: partnerId,
          content: content
        })
        fetchMessages()
      } catch (error) {
        console.error('Failed to send message:', error)
        setNewMessage(content) // Restore message
      } finally {
        setSending(false)
      }
    }

    inputRef.current?.focus()
  }

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!conversation) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        <div className="text-center">
          <i className="fa-solid fa-comments text-6xl mb-4 opacity-30"></i>
          <p>اختر محادثة للبدء</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center gap-3 bg-white/5">
        <div className="relative">
          <ProfileImage src={conversation.profile_image} size="sm" />
          {isPartnerOnline && (
            <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-900"></span>
          )}
        </div>
        <div className="flex-1">
          <p className={`font-bold ${conversation.role === 'admin' ? 'admin-username-gradient' : 'text-gray-200'}`}>
            {conversation.role === 'admin' && (
              <i className="fa-solid fa-crown admin-crown-icon"></i>
            )}
            {conversation.full_name || conversation.username}
          </p>
          <p className="text-xs text-gray-400">
            {isPartnerTyping ? (
              <span className="text-primary animate-pulse">جاري الكتابة...</span>
            ) : isPartnerOnline ? (
              <span className="text-green-400">متصل الآن</span>
            ) : (
              conversation.class_name && `${conversation.class_name} - ${conversation.section_name}`
            )}
          </p>
        </div>
        {!isConnected && (
          <span className="badge badge-warning badge-sm">غير متصل</span>
        )}
        {onClose && (
          <button onClick={onClose} className="btn btn-ghost btn-sm btn-circle">
            <i className="fa-solid fa-xmark"></i>
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading ? (
          <div className="flex justify-center py-8">
            <span className="loading loading-spinner loading-md text-primary"></span>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            <i className="fa-solid fa-message text-4xl mb-2 opacity-30"></i>
            <p>لا توجد رسائل بعد</p>
            <p className="text-sm">ابدأ المحادثة الآن!</p>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isMine = msg.sender_id === currentUser.id
            const showAvatar = idx === 0 || messages[idx - 1].sender_id !== msg.sender_id

            return (
              <div
                key={msg.id}
                className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[75%] ${isMine ? 'order-2' : 'order-1'}`}>
                  <div
                    className={`px-4 py-2 rounded-2xl ${isMine
                      ? 'bg-primary text-white rounded-br-md'
                      : 'bg-white/10 text-gray-200 rounded-bl-md'
                      } ${msg.is_sending ? 'opacity-70' : ''}`}
                  >
                    <p className="break-words">{msg.content}</p>
                  </div>
                  <div className={`text-xs text-gray-500 mt-1 flex items-center gap-1 ${isMine ? 'justify-end' : 'justify-start'}`}>
                    <span>{new Date(msg.timestamp).toLocaleTimeString('ar-IQ', { hour: '2-digit', minute: '2-digit' })}</span>
                    {isMine && (
                      <span>
                        {msg.is_sending ? (
                          <i className="fa-solid fa-clock text-gray-400"></i>
                        ) : msg.is_read ? (
                          <i className="fa-solid fa-check-double text-primary"></i>
                        ) : (
                          <i className="fa-solid fa-check text-gray-400"></i>
                        )}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Typing indicator */}
      {isPartnerTyping && (
        <div className="px-4 py-1 text-xs text-gray-400">
          <span className="inline-flex items-center gap-1">
            <span className="flex gap-0.5">
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </span>
            <span>جاري الكتابة...</span>
          </span>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-white/10 bg-white/5">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={newMessage}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="اكتب رسالتك..."
            className="input input-bordered flex-1 bg-white/10 border-white/10 text-white placeholder-gray-400"
            disabled={sending}
          />
          <button
            onClick={handleSend}
            disabled={!newMessage.trim() || sending}
            className="btn btn-primary"
          >
            {sending ? (
              <span className="loading loading-spinner loading-sm"></span>
            ) : (
              <i className="fa-solid fa-paper-plane"></i>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatWindow
