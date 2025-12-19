import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * WebSocket hook for real-time chat functionality
 * Handles connection, reconnection, and message handling
 */
const useWebSocket = (userId, token) => {
    const wsRef = useRef(null)
    const [isConnected, setIsConnected] = useState(false)
    const [lastMessage, setLastMessage] = useState(null)
    const [typingUsers, setTypingUsers] = useState({}) // { userId: isTyping }
    const [onlineUsers, setOnlineUsers] = useState([])
    const reconnectTimeoutRef = useRef(null)
    const reconnectAttempts = useRef(0)
    const maxReconnectAttempts = 5

    // Get WebSocket URL
    const getWsUrl = useCallback(() => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        return `${protocol}//${host}/ws/chat/${userId}?token=${token}`
    }, [userId, token])

    // Connect to WebSocket
    const connect = useCallback(() => {
        if (!userId || !token) return

        try {
            const ws = new WebSocket(getWsUrl())
            wsRef.current = ws

            ws.onopen = () => {
                console.log('WebSocket connected')
                setIsConnected(true)
                reconnectAttempts.current = 0
            }

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    setLastMessage(data)

                    // Handle typing indicators
                    if (data.type === 'typing') {
                        setTypingUsers(prev => ({
                            ...prev,
                            [data.from_user_id]: data.is_typing
                        }))
                        // Clear typing after 5 seconds
                        if (data.is_typing) {
                            setTimeout(() => {
                                setTypingUsers(prev => ({
                                    ...prev,
                                    [data.from_user_id]: false
                                }))
                            }, 5000)
                        }
                    }

                    // Handle online status updates
                    if (data.type === 'online_status') {
                        const onlineIds = Object.entries(data.status)
                            .filter(([_, isOnline]) => isOnline)
                            .map(([id]) => parseInt(id))
                        setOnlineUsers(onlineIds)
                    }

                    if (data.type === 'user_online') {
                        setOnlineUsers(prev => [...new Set([...prev, data.user_id])])
                    }

                    if (data.type === 'user_offline') {
                        setOnlineUsers(prev => prev.filter(id => id !== data.user_id))
                    }
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e)
                }
            }

            ws.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason)
                setIsConnected(false)
                wsRef.current = null

                // Reconnect logic
                if (event.code !== 4001 && reconnectAttempts.current < maxReconnectAttempts) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
                    console.log(`Reconnecting in ${delay}ms...`)
                    reconnectTimeoutRef.current = setTimeout(() => {
                        reconnectAttempts.current++
                        connect()
                    }, delay)
                }
            }

            ws.onerror = (error) => {
                console.error('WebSocket error:', error)
            }
        } catch (error) {
            console.error('Failed to create WebSocket:', error)
        }
    }, [userId, token, getWsUrl])

    // Disconnect
    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
        }
        if (wsRef.current) {
            wsRef.current.close()
            wsRef.current = null
        }
        setIsConnected(false)
    }, [])

    // Send message
    const sendMessage = useCallback((receiverId, content) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'message',
                receiver_id: receiverId,
                content: content
            }))
            return true
        }
        return false
    }, [])

    // Send typing indicator
    const sendTyping = useCallback((toUserId, isTyping) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'typing',
                to_user_id: toUserId,
                is_typing: isTyping
            }))
        }
    }, [])

    // Mark messages as read
    const markAsRead = useCallback((messageIds, senderId) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'read',
                message_ids: messageIds,
                sender_id: senderId
            }))
        }
    }, [])

    // Request online status of users
    const requestOnlineStatus = useCallback((userIds) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'online_status',
                user_ids: userIds
            }))
        }
    }, [])

    // Broadcast message (admin only)
    const broadcast = useCallback((content, className = null, sectionName = null) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'broadcast',
                content: content,
                class_name: className,
                section_name: sectionName
            }))
        }
    }, [])

    // Connect on mount
    useEffect(() => {
        connect()
        return () => disconnect()
    }, [connect, disconnect])

    return {
        isConnected,
        lastMessage,
        typingUsers,
        onlineUsers,
        sendMessage,
        sendTyping,
        markAsRead,
        requestOnlineStatus,
        broadcast,
        reconnect: connect
    }
}

export default useWebSocket
