import { useState } from 'react'
import { Copy, Check, ThumbsUp, ThumbsDown, FileText, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'
import type { ChatMessage } from '../../types'
import { sendFeedback } from '../../services/api'
import { TypingIndicator } from './TypingIndicator'
import { IntentBadge } from './IntentBadge'

interface Props {
  message: ChatMessage
  conversationId?: string | null
}

export function MessageBubble({ message, conversationId }: Props) {
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState<number | null>(null)
  const isUser = message.role === 'user'
  const isStreaming = message.isStreaming && !message.content

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-medium ${
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-accent text-primary'
        }`}
      >
        {isUser ? 'KH' : 'AI'}
      </div>

      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-primary text-primary-foreground rounded-br-md'
              : 'bg-secondary dark:bg-dark-secondary text-foreground dark:text-dark-foreground rounded-bl-md'
          }`}
        >
          {isStreaming ? (
            <TypingIndicator />
          ) : (
            <p className="whitespace-pre-wrap text-sm leading-relaxed">
              {message.content}
            </p>
          )}
        </div>

        {!isUser && message.content && !message.isStreaming && (
          <div className="mt-1 flex items-center gap-1">
            <button
              onClick={handleCopy}
              className="rounded p-1 text-muted hover:bg-secondary dark:hover:bg-dark-secondary transition-colors"
              title="Copy"
            >
              {copied ? <Check size={14} /> : <Copy size={14} />}
            </button>
            <button
              onClick={() => {
                setFeedback(1)
                if (conversationId && message.id) {
                  sendFeedback(conversationId, message.id, 1).catch(() => {})
                }
              }}
              className={`rounded p-1 transition-colors ${
                feedback === 1
                  ? 'text-green-500'
                  : 'text-muted hover:bg-secondary dark:hover:bg-dark-secondary'
              }`}
              title="Good response"
            >
              <ThumbsUp size={14} />
            </button>
            <button
              onClick={() => {
                setFeedback(-1)
                if (conversationId && message.id) {
                  sendFeedback(conversationId, message.id, -1).catch(() => {})
                }
              }}
              className={`rounded p-1 transition-colors ${
                feedback === -1
                  ? 'text-destructive'
                  : 'text-muted hover:bg-secondary dark:hover:bg-dark-secondary'
              }`}
              title="Bad response"
            >
              <ThumbsDown size={14} />
            </button>
          </div>
        )}

        {message.handoff_suggested && (
          <div className="mt-2 flex items-center gap-2 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 px-3 py-2 text-xs text-amber-700 dark:text-amber-300">
            <AlertTriangle size={14} />
            <span>AI suggests contacting support directly for this request.</span>
          </div>
        )}

        {!isUser && message.intent && !message.isStreaming && (
          <IntentBadge intent={message.intent} tools={message.used_tools} />
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs font-medium text-muted flex items-center gap-1">
              <FileText size={12} /> Sources
            </p>
            {message.sources.map((src, i) => (
              <div
                key={i}
                className="rounded-lg bg-accent/50 dark:bg-dark-card px-3 py-1.5 text-xs text-muted"
              >
                <span className="font-medium">{src.source_file}</span>
                {' — '}
                {src.content.length > 100
                  ? src.content.slice(0, 100) + '...'
                  : src.content}
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
