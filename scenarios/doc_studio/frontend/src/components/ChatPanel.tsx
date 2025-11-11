import { useEffect, useState, useRef } from 'react'
import './ChatPanel.css'

interface ChatMessage {
  sender: 'user' | 'assistant'
  message: string
  timestamp: Date
}

interface ChatPanelProps {
  userId?: string
}

export function ChatPanel({ userId = 'default' }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [eventSource, setEventSource] = useState<EventSource | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Connect to SSE for chat events
    const resourceId = `chat:${userId}`
    const es = new EventSource(`/api/events/${resourceId}`)

    es.onopen = () => {
      setIsConnected(true)
    }

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.event === 'chat') {
          const chatEvent = data.data
          const message = chatEvent.message

          // Parse sender from message format
          if (message.startsWith('You: ')) {
            // User message confirmation - skip (we already added it)
            return
          } else if (message.startsWith('Assistant: ')) {
            const content = message.replace('Assistant: ', '')

            // Update or add assistant message
            setMessages((prev) => {
              const lastMsg = prev[prev.length - 1]
              if (lastMsg && lastMsg.sender === 'assistant') {
                // Update existing message
                return [
                  ...prev.slice(0, -1),
                  { ...lastMsg, message: content },
                ]
              } else {
                // Add new message
                return [
                  ...prev,
                  {
                    sender: 'assistant',
                    message: content,
                    timestamp: new Date(),
                  },
                ]
              }
            })
          }
        }
      } catch (err) {
        console.error('Failed to parse SSE event:', err)
      }
    }

    es.onerror = () => {
      setIsConnected(false)
    }

    setEventSource(es)

    return () => {
      es.close()
    }
  }, [userId])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = input.trim()
    setInput('')

    // Add user message immediately
    setMessages((prev) => [
      ...prev,
      {
        sender: 'user',
        message: userMessage,
        timestamp: new Date(),
      },
    ])

    try {
      await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          user_id: userId,
        }),
      })
    } catch (err) {
      console.error('Failed to send message:', err)
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          message: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        },
      ])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h4>AI Assistant</h4>
        <div className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <p>👋 Hi! I'm your doc-studio assistant.</p>
            <p>Try asking:</p>
            <ul>
              <li>"What can you do?"</li>
              <li>"How do I add files?"</li>
              <li>"How do I generate a document?"</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`chat-message ${msg.sender}`}>
              <div className="message-content">{msg.message}</div>
              <div className="message-time">
                {msg.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          rows={2}
        />
        <button
          className="chat-send-button"
          onClick={handleSend}
          disabled={!input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  )
}
