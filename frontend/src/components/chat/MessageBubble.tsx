import { useState } from 'react'
import { Copy, Check, ThumbsUp, ThumbsDown, FileText, AlertTriangle, Zap, User } from 'lucide-react'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { toast } from 'sonner'
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
    toast.success('Copied to clipboard')
    setTimeout(() => setCopied(false), 2000)
  }

  const handleFeedback = async (rating: number) => {
    setFeedback(rating)
    toast.success(rating > 0 ? 'Thanks for the feedback!' : 'Noted, we\'ll improve')
    if (conversationId && message.id) {
      sendFeedback(conversationId, message.id, rating).catch(() => {})
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-sm font-medium shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-slate-600 to-slate-800 text-white'
            : 'bg-gradient-to-br from-primary to-purple-500 text-white shadow-primary/20'
        }`}
      >
        {isUser ? <User size={14} /> : <Zap size={14} />}
      </div>

      {/* Content */}
      <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Label */}
        <span className={`text-[10px] font-medium text-muted mb-1 px-1 ${isUser ? 'text-right' : ''}`}>
          {isUser ? 'Khách hàng' : 'VANI Copilot'}
        </span>

        {/* Bubble */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-gradient-to-br from-slate-700 to-slate-800 text-white rounded-tr-md shadow-md'
              : 'bg-card dark:bg-dark-card border border-border dark:border-dark-border rounded-tl-md shadow-sm'
          }`}
        >
          {isStreaming ? (
            <TypingIndicator />
          ) : isUser ? (
            <p className="whitespace-pre-wrap text-sm leading-relaxed">
              {message.content}
            </p>
          ) : (
            <div className="prose-chat">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Actions bar */}
        {!isUser && message.content && !message.isStreaming && (
          <div className="mt-1.5 flex items-center gap-0.5 px-1">
            <ActionButton
              onClick={handleCopy}
              title="Copy"
              active={copied}
              activeClass="text-primary"
            >
              {copied ? <Check size={13} /> : <Copy size={13} />}
            </ActionButton>
            <ActionButton
              onClick={() => handleFeedback(1)}
              title="Good"
              active={feedback === 1}
              activeClass="text-success"
            >
              <ThumbsUp size={13} />
            </ActionButton>
            <ActionButton
              onClick={() => handleFeedback(-1)}
              title="Bad"
              active={feedback === -1}
              activeClass="text-destructive"
            >
              <ThumbsDown size={13} />
            </ActionButton>

            {/* Confidence indicator */}
            {message.confidence != null && message.confidence < 1 && (
              <div className="ml-2 flex items-center gap-1.5">
                <div className="h-1 w-12 rounded-full bg-secondary dark:bg-dark-secondary overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      message.confidence >= 0.8 ? 'bg-success' :
                      message.confidence >= 0.5 ? 'bg-warning' : 'bg-destructive'
                    }`}
                    style={{ width: `${message.confidence * 100}%` }}
                  />
                </div>
                <span className="text-[10px] text-muted">{Math.round(message.confidence * 100)}%</span>
              </div>
            )}
          </div>
        )}

        {/* Handoff banner */}
        {message.handoff_suggested && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-2 flex items-center gap-2 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 px-3 py-2 text-xs text-amber-700 dark:text-amber-300"
          >
            <AlertTriangle size={14} />
            <span>Khuyến nghị chuyển cho nhân viên hỗ trợ trực tiếp.</span>
          </motion.div>
        )}

        {/* Intent badge */}
        {!isUser && message.intent && !message.isStreaming && (
          <IntentBadge intent={message.intent} tools={message.used_tools} />
        )}

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 space-y-1 w-full"
          >
            <p className="text-[10px] font-medium text-muted flex items-center gap-1 px-1">
              <FileText size={10} /> Knowledge Base Sources
            </p>
            {message.sources.map((src, i) => (
              <div
                key={i}
                className="rounded-xl bg-accent/30 dark:bg-dark-accent/30 border border-border/50 dark:border-dark-border/50 px-3 py-2 text-[11px] text-muted-foreground dark:text-dark-muted"
              >
                <span className="font-semibold text-foreground dark:text-dark-foreground">{src.source_file}</span>
                <span className="mx-1.5 text-border dark:text-dark-border">|</span>
                {src.content.length > 120
                  ? src.content.slice(0, 120) + '...'
                  : src.content}
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

function ActionButton({
  onClick,
  title,
  active,
  activeClass,
  children,
}: {
  onClick: () => void
  title: string
  active: boolean
  activeClass: string
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg p-1.5 transition-all active:scale-90 ${
        active
          ? activeClass
          : 'text-muted hover:text-foreground dark:hover:text-dark-foreground hover:bg-secondary dark:hover:bg-dark-secondary'
      }`}
      title={title}
    >
      {children}
    </button>
  )
}
