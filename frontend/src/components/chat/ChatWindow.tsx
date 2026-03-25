import { useEffect, useRef } from 'react'
import { Sparkles, MessageSquare, Package, HelpCircle } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { MessageBubble } from './MessageBubble'
import { MessageInput } from './MessageInput'
import { useChat } from '../../hooks/useChat'

const QUICK_PROMPTS = [
  { icon: <HelpCircle size={14} />, text: 'Chính sách đổi trả thế nào ạ?' },
  { icon: <Package size={14} />, text: 'Đơn hàng VN12345 ship đến đâu rồi?' },
  { icon: <MessageSquare size={14} />, text: 'Em cao 1m58 nặng 49kg mặc size gì?' },
  { icon: <Sparkles size={14} />, text: 'Có mã giảm giá gì không shop?' },
]

export function ChatWindow() {
  const { messages, currentConversationId } = useChatStore()
  const { send } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-accent">
              <Sparkles size={28} className="text-primary" />
            </div>
            <h2 className="text-xl font-semibold mb-1">VANI Copilot</h2>
            <p className="text-sm text-muted mb-8 text-center max-w-md">
              AI Customer Support Assistant — paste tin nhắn khách hàng để nhận gợi ý trả lời
            </p>

            <div className="grid grid-cols-2 gap-2 max-w-lg w-full">
              {QUICK_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => send(prompt.text)}
                  className="flex items-center gap-2 rounded-xl border border-border dark:border-dark-border bg-card dark:bg-dark-card px-4 py-3 text-left text-sm hover:border-primary/50 hover:bg-accent/30 dark:hover:bg-dark-secondary transition-all"
                >
                  <span className="text-primary shrink-0">{prompt.icon}</span>
                  <span className="line-clamp-2">{prompt.text}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} conversationId={currentConversationId} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
      <div className="mx-auto w-full max-w-3xl">
        <MessageInput />
      </div>
    </div>
  )
}
