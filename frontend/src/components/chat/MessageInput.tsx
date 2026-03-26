import { useState, useRef, useEffect } from 'react'
import { Send, Square } from 'lucide-react'
import { useChat } from '../../hooks/useChat'
import { useChatStore } from '../../store/chatStore'

export function MessageInput() {
  const [input, setInput] = useState('')
  const { send, isLoading } = useChat()
  const { stopGeneration } = useChatStore()
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
      el.style.height = Math.min(el.scrollHeight, 150) + 'px'
    }
  }, [input])

  const charCount = input.length
  const maxChars = 2000

  return (
    <div className="border-t border-border dark:border-dark-border bg-card/80 dark:bg-dark-card/80 backdrop-blur-sm px-4 py-3">
      <div className={`flex items-end gap-2 rounded-2xl border bg-background dark:bg-dark-background px-4 py-2 shadow-sm transition-all ${
        input.trim()
          ? 'border-primary/40 ring-1 ring-primary/10 shadow-md shadow-primary/5'
          : 'border-border dark:border-dark-border'
      }`}>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value.slice(0, maxChars))}
          onKeyDown={handleKeyDown}
          placeholder="Paste tin nhắn khách hàng vào đây..."
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted dark:text-dark-foreground leading-relaxed py-1"
        />
        {isLoading ? (
          <button
            onClick={stopGeneration}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-destructive text-white transition-all hover:opacity-90 active:scale-95 shadow-sm"
            title="Stop generation"
          >
            <Square size={14} fill="currentColor" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-500 text-white transition-all disabled:opacity-20 disabled:cursor-not-allowed hover:shadow-md hover:shadow-primary/25 active:scale-95"
            title="Send message"
          >
            <Send size={15} />
          </button>
        )}
      </div>
      <div className="mt-1.5 flex items-center justify-between px-1">
        <p className="text-[10px] text-muted">
          AI Copilot gợi ý dựa trên Knowledge Base • <kbd className="px-1 py-0.5 rounded bg-secondary dark:bg-dark-secondary text-[9px]">Enter</kbd> để gửi
        </p>
        {charCount > 0 && (
          <p className={`text-[10px] ${charCount > maxChars * 0.9 ? 'text-warning' : 'text-muted'}`}>
            {charCount}/{maxChars}
          </p>
        )}
      </div>
    </div>
  )
}
