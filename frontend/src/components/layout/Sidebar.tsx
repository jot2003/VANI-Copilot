import { useEffect } from 'react'
import { Plus, MessageSquare, X, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useChatStore } from '../../store/chatStore'
import { fetchConversations, fetchConversation } from '../../services/api'

export function Sidebar() {
  const {
    conversations,
    currentConversationId,
    sidebarOpen,
    setConversations,
    setCurrentConversation,
    setMessages,
    newConversation,
    toggleSidebar,
    setPage,
  } = useChatStore()

  useEffect(() => {
    fetchConversations()
      .then(setConversations)
      .catch(() => {})
  }, [setConversations])

  const handleSelectConversation = async (id: string) => {
    try {
      const detail = await fetchConversation(id)
      setCurrentConversation(id)
      setMessages(detail.messages)
      setPage('chat')
    } catch {
      // ignore
    }
  }

  return (
    <AnimatePresence>
      {sidebarOpen && (
        <motion.aside
          initial={{ x: -280 }}
          animate={{ x: 0 }}
          exit={{ x: -280 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="flex h-full w-[280px] shrink-0 flex-col border-r border-border dark:border-dark-border bg-card dark:bg-dark-card"
        >
          <div className="flex items-center gap-2.5 p-4 pb-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary/70">
              <Sparkles size={16} className="text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-sm font-bold tracking-tight">VANI Copilot</h1>
              <p className="text-[10px] text-muted">v2.0 — Agent + RAG</p>
            </div>
            <button
              onClick={toggleSidebar}
              className="rounded p-1 hover:bg-secondary dark:hover:bg-dark-secondary transition-colors lg:hidden"
            >
              <X size={18} />
            </button>
          </div>

          <div className="px-3 mb-3">
            <button
              onClick={() => { newConversation(); setPage('chat') }}
              className="flex w-full items-center gap-2 rounded-xl border border-dashed border-border dark:border-dark-border px-3 py-2.5 text-sm text-muted hover:text-foreground dark:hover:text-dark-foreground hover:border-primary/50 hover:bg-accent/20 transition-all"
            >
              <Plus size={16} />
              New Conversation
            </button>
          </div>

          <div className="px-3 mb-2">
            <p className="text-[10px] font-medium uppercase tracking-wider text-muted px-1">
              Recent chats
            </p>
          </div>

          <div className="flex-1 overflow-y-auto px-3 pb-3">
            {conversations.length === 0 ? (
              <p className="px-3 py-4 text-xs text-muted text-center">No conversations yet</p>
            ) : (
              conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`mb-0.5 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-all ${
                    currentConversationId === conv.id
                      ? 'bg-primary/10 text-primary font-medium'
                      : 'text-foreground/70 dark:text-dark-foreground/70 hover:bg-secondary dark:hover:bg-dark-secondary'
                  }`}
                >
                  <MessageSquare size={14} className="shrink-0 opacity-50" />
                  <span className="truncate">{conv.title}</span>
                </button>
              ))
            )}
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
