import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles } from 'lucide-react'
import { useChat } from '../../hooks/useChat'

export function MessageInput() {
  const [input, setInput] = useState('')
  const { send, isLoading } = useChat()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return
    send(input.trim())
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  useEffect(() => {
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 120) + 'px'
    }
  }, [input])

  return (
    <div className="border-t border-border dark:border-dark-border bg-card dark:bg-dark-card px-4 py-3">
      <div className="flex items-end gap-2 rounded-2xl border border-border dark:border-dark-border bg-background dark:bg-dark-background px-4 py-2 shadow-sm focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20 transition-all">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Paste tin nhắn khách hàng vào đây..."
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted dark:text-dark-foreground"
        />
        <button
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition-all disabled:opacity-30 hover:opacity-90 hover:scale-105 active:scale-95"
        >
          {isLoading ? (
            <Sparkles size={16} className="animate-pulse" />
          ) : (
            <Send size={16} />
          )}
        </button>
      </div>
      <p className="mt-1.5 text-center text-[11px] text-muted">
        AI Copilot gợi ý trả lời dựa trên Knowledge Base của VANI Store
      </p>
    </div>
  )
}
