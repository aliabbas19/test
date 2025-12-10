import { useState, useEffect } from 'react'
import api from '../services/api'

export const useMessages = (conversationId) => {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (conversationId) {
      fetchMessages()
      const interval = setInterval(fetchMessages, 3000)
      return () => clearInterval(interval)
    }
  }, [conversationId])

  const fetchMessages = async () => {
    try {
      const response = await api.get(`/api/messages/${conversationId}`)
      setMessages(response.data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async (content) => {
    try {
      await api.post('/api/messages', {
        receiver_id: conversationId,
        content,
        type: 'user'
      })
      fetchMessages()
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  return { messages, loading, error, sendMessage, refresh: fetchMessages }
}

