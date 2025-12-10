import { formatTime } from '../../utils/helpers'

const MessageBubble = ({ message, isOwn }) => {
  return (
    <div className={`chat ${isOwn ? 'chat-end' : 'chat-start'} animate-fade-in-up`}>
      <div
        className={`chat-bubble shadow-md backdrop-blur-sm transition-all duration-300 ${isOwn
          ? 'glass-effect bg-gradient-to-r from-primary to-primary/80 text-white border-none'
          : 'bg-white/80 text-gray-800 border border-white/40'
          }`}
      >
        {message.content}
      </div>
      <div className="chat-footer opacity-0 group-hover:opacity-50 transition-opacity text-xs mt-1 text-gray-500 font-mono">
        {formatTime(message.timestamp)}
      </div>
    </div>
  )
}

export default MessageBubble
