import { useState, useEffect, useRef } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import MessageBubble from './MessageBubble'

const ChatWindow = ({ conversation }) => {
  const { user } = useAuth()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (conversation) {
      fetchMessages()
      const interval = setInterval(fetchMessages, 3000) // Poll every 3 seconds
      return () => clearInterval(interval)
    }
  }, [conversation])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchMessages = async () => {
    if (!conversation) return

    try {
      const response = await api.get(`/api/messages/${conversation.id}`)
      setMessages(response.data)
    } catch (error) {
      console.error('Failed to fetch messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!newMessage.trim()) return

    try {
      await api.post('/api/messages', {
        receiver_id: conversation.id,
        content: newMessage,
        type: 'user'
      })
      setNewMessage('')
      fetchMessages()
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">اختر محادثة</p>
      </div>
    )
  }

  if (loading) {
    return <div className="text-center py-4">جاري التحميل...</div>
  }

  return (
    <div className="flex flex-col h-full bg-transparent">
      <div className="p-4 border-b border-white/10 bg-white/5 backdrop-blur-sm shadow-sm flex items-center justify-between z-10">
        <div>
          <h3 className="font-bold text-lg text-gray-800 flex items-center gap-2">
            <i className="fa-solid fa-user-circle text-primary"></i> {conversation.full_name || conversation.username}
          </h3>
          {conversation.class_name && (
            <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
              <i className="fa-solid fa-graduation-cap text-xs"></i> {conversation.class_name} - {conversation.section_name}
            </p>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-primary/20 scrollbar-track-transparent">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isOwn={message.sender_id === user?.id}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-4 border-t border-white/10 bg-white/5 backdrop-blur-md">
        <div className="flex gap-2 items-center relative">
          <input
            type="text"
            className="input input-bordered flex-1 bg-white/50 backdrop-blur-sm border-white/30 focus:bg-white focus:border-primary/50 transition-all rounded-full pl-4 pr-12 shadow-inner"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="اكتب رسالتك..."
          />
          <button
            type="submit"
            className="btn btn-circle btn-primary absolute left-1 top-1 bottom-1 w-10 h-10 min-h-0 shadow-lg border-2 border-white/20"
          >
            <i className="fa-solid fa-paper-plane text-sm"></i>
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatWindow

