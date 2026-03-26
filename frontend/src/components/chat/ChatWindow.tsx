import { useEffect, useRef } from 'react'
import { Zap, Package, HelpCircle, ShoppingBag, Sparkles } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { MessageBubble } from './MessageBubble'
import { MessageInput } from './MessageInput'
import { useChat } from '../../hooks/useChat'

const QUICK_PROMPTS = [
  { icon: <HelpCircle size={16} />, text: 'Chính sách đổi trả thế nào ạ?', label: 'Đổi trả' },
  { icon: <Package size={16} />, text: 'Đơn hàng VN12345 ship đến đâu rồi?', label: 'Tra đơn' },
  { icon: <ShoppingBag size={16} />, text: 'Em cao 1m58 nặng 49kg mặc size gì?', label: 'Tư vấn size' },
  { icon: <Sparkles size={16} />, text: 'Có mã giảm giá gì không shop?', label: 'Khuyến mãi' },
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
            {/* Hero */}
            <div className="relative mb-8">
              <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-primary to-purple-500 shadow-lg shadow-primary/25">
                <Zap size={36} className="text-white" />
              </div>
              <div className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full bg-success shadow-md">
                <span className="text-white text-[10px] font-bold">AI</span>
              </div>
            </div>
            <h2 className="text-2xl font-bold mb-2 tracking-tight">Xin chào!</h2>
            <p className="text-sm text-muted mb-10 text-center max-w-md leading-relaxed">
              VANI Copilot sẵn sàng hỗ trợ bạn. Paste tin nhắn khách hàng hoặc chọn một gợi ý bên dưới.
            </p>

            {/* Quick prompts */}
            <div className="grid grid-cols-2 gap-3 max-w-lg w-full">
              {QUICK_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => send(prompt.text)}
                  className="group relative flex flex-col gap-2 rounded-2xl border border-border dark:border-dark-border bg-card dark:bg-dark-card p-4 text-left hover:border-primary/40 hover:shadow-md hover:shadow-primary/5 dark:hover:border-primary/30 transition-all active:scale-[0.98]"
                >
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent dark:bg-dark-accent text-primary group-hover:bg-primary group-hover:text-white transition-colors">
                    {prompt.icon}
                  </div>
                  <div>
                    <p className="text-xs font-semibold mb-0.5">{prompt.label}</p>
                    <p className="text-[11px] text-muted line-clamp-2 leading-relaxed">{prompt.text}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-5">
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
