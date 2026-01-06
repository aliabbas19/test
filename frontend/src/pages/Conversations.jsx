import { useState } from 'react'
import ConversationList from '../components/messages/ConversationList'
import ChatWindow from '../components/messages/ChatWindow'
import GroupMessageSender from '../components/messages/GroupMessageSender'
import { useAuth } from '../context/AuthContext'

const Conversations = () => {
  const { isAdmin, user } = useAuth()
  const [selectedConversation, setSelectedConversation] = useState(null)
  const [showGroupMessage, setShowGroupMessage] = useState(false)

  return (
    <div className="space-y-4">
      {/* Group Message Section - Admin Only */}
      {isAdmin && (
        <div className="glass-effect rounded-2xl overflow-hidden shadow-xl">
          <button
            className="w-full p-4 flex items-center justify-between hover:bg-white/10 transition-colors"
            onClick={() => setShowGroupMessage(!showGroupMessage)}
          >
            <span className="font-bold flex items-center gap-2 text-gray-800">
              <i className="fa-solid fa-users text-purple-500"></i>
              إرسال رسالة جماعية
            </span>
            <i className={`fa-solid fa-chevron-down transition-transform ${showGroupMessage ? 'rotate-180' : ''}`}></i>
          </button>

          {showGroupMessage && (
            <div className="p-4 border-t border-white/20">
              <GroupMessageSender onClose={() => setShowGroupMessage(false)} />
            </div>
          )}
        </div>
      )}

      {/* Chat Section */}
      <div className="h-[calc(100vh-220px)] glass-effect rounded-2xl overflow-hidden flex flex-col md:flex-row shadow-2xl relative">
        <div className="w-full md:w-1/3 lg:w-1/4 border-b md:border-b-0 md:border-l border-white/20 p-4 overflow-y-auto bg-white/10 backdrop-blur-sm">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-primary drop-shadow-sm">
            <i className="fa-solid fa-comments"></i> المحادثات
          </h2>
          <ConversationList
            onSelectConversation={setSelectedConversation}
            selectedId={selectedConversation?.id}
          />
        </div>

        <div className="flex-1 bg-white/5 relative">
          {/* Background decorative element */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none"></div>
          <ChatWindow
            conversation={selectedConversation}
            currentUser={user}
          />
        </div>
      </div>
    </div>
  )
}

export default Conversations
