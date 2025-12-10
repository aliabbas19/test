import { useState, useEffect } from 'react'
import api from '../../services/api'
import ProfileImage from '../common/ProfileImage'

const ConversationList = ({ onSelectConversation, selectedId }) => {
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchConversations()
    const interval = setInterval(fetchConversations, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchConversations = async () => {
    try {
      const response = await api.get('/api/messages/conversations')
      setConversations(response.data)
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-4 text-gray-400">جاري التحميل...</div>
  }

  if (conversations.length === 0) {
    return <div className="text-center py-8 text-white/50">لا توجد محادثات</div>
  }

  return (
    <div className="space-y-2">
      {conversations.map((conv) => (
        <div
          key={conv.id}
          className={`p-3 rounded-xl cursor-pointer transition-all duration-300 flex items-center gap-3 border ${selectedId === conv.id
              ? 'glass-effect bg-primary/20 border-primary/30 shadow-lg'
              : 'hover:bg-white/10 border-transparent hover:border-white/10'
            }`}
          onClick={() => onSelectConversation(conv)}
        >
          <div className="relative">
            <ProfileImage src={conv.profile_image} size="sm" />
            {conv.unread_count > 0 && (
              <span className="absolute -top-1 -right-1 badge badge-error badge-xs w-4 h-4 flex items-center justify-center p-0 border border-white/20 animate-pulse">
                {conv.unread_count}
              </span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className={`font-bold truncate ${selectedId === conv.id ? 'text-primary' : 'text-gray-200'}`}>
              {conv.full_name || conv.username}
            </p>
            {conv.class_name && (
              <p className="text-xs text-gray-400 truncate">{conv.class_name} - {conv.section_name}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ConversationList

