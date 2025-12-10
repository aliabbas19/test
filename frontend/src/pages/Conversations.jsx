import { useState } from 'react'
import ConversationList from '../components/messages/ConversationList'
import ChatWindow from '../components/messages/ChatWindow'

const Conversations = () => {
  const [selectedConversation, setSelectedConversation] = useState(null)

  return (
    <div className="h-[calc(100vh-140px)] glass-effect rounded-2xl overflow-hidden flex flex-col md:flex-row shadow-2xl relative">
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
        <ChatWindow conversation={selectedConversation} />
      </div>
    </div>
  )
}

export default Conversations

